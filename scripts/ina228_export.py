#!/usr/bin/env python3
"""
ina228_export.py - build the published INA228-era datasets from InfluxDB.

The INA228 monitor publishes at a 2 s cadence, which is ~1.8 M current samples
over the reporting window - too large to version in git, and of no analytical
value at full resolution outside the event windows. This script therefore
publishes four tiers:

  data/ina228/ina228_hourly_*.csv     hourly aggregates, full window
  data/ina228/ina228_daily_*.csv      daily aggregates, full window
  data/ina228/stasis_ma60_*.csv.gz    1-minute MA-60s voltage means, stasis only
  data/ina228/events/*.csv[.gz]       full 2 s resolution, event windows only

Anything larger than the repo's 500 KB pre-commit gate is written gzipped
rather than downsampled, so no sample is lost; pandas reads .csv.gz by
extension with no extra argument.

Source : InfluxDB 1.x on the Home Assistant host, database "Home Assistant".
         Retention is infinite, so this script is re-runnable over any window.
Auth   : reads influxdb_* from the HA secrets.yaml (env vars win). Use a
         READ-ONLY influx user; every query here is a SELECT.

Run (the default window is the pinned cutoff for the 2026-08-26 report):
    HA_CONFIG=H:/ python scripts/ina228_export.py
"""

import argparse
import gzip
import io
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# ---------------------------------------------------------------- credentials
_CFG = os.environ.get("HA_CONFIG", "/config").rstrip("/") + "/"
try:
    with open(_CFG + "secrets.yaml", encoding="utf-8") as _f:
        _S = yaml.safe_load(_f) or {}
except OSError:
    _S = {}
USER = os.environ.get("INFLUXDB_USER") or _S.get("influxdb_user", "")
PASS = os.environ.get("INFLUXDB_PASS") or _S.get("influxdb_pass", "")
URL = os.environ.get("INFLUXDB_URL") or _S.get("influxdb_url", "")
DB = os.environ.get("INFLUXDB_DB") or _S.get("influxdb_db", "Home Assistant")

# The InfluxDB measurement name is the unit of measure; the tag is entity_id.
SERIES = {
    "voltage": ("V", "battery_bank_monitor_battery_voltage"),
    "current": ("A", "battery_bank_monitor_battery_current"),
    "power": ("W", "battery_bank_monitor_battery_power"),
    "packtemp": ("\u00b0F", "battery_bank_monitor_battery_pack_temperature"),
    "dietemp": ("\u00b0F", "battery_bank_monitor_ina228_die_temperature"),
    "soc": ("%", "battery_bank_monitor_state_of_charge"),
    "hw_net_ah": ("Ah", "basement_battery_bank_monitor_hw_net_charge_ina228"),
    # The firmware's own software coulomb ledger, for the three-way comparison
    # in the report: silicon accumulator vs independent integration vs firmware.
    "sw_ah_chg": ("Ah", "battery_bank_monitor_ah_charged_this_cycle"),
    "sw_ah_dis": ("Ah", "battery_bank_monitor_ah_discharged_this_cycle"),
}

# Event windows, UTC. These are the commissioning discharge legs plus the charge
# that set the SOC anchor; everything outside them is quiescent.
EVENTS = {
    "discharge_2026-07-15_70W_overnight": (
        "2026-07-15T19:50:00Z",
        "2026-07-16T11:40:00Z",
    ),
    "discharge_2026-07-16_1kW_heater": ("2026-07-16T14:18:00Z", "2026-07-16T14:42:00Z"),
    "discharge_2026-07-16_inverter_trip": (
        "2026-07-16T17:38:00Z",
        "2026-07-16T17:58:00Z",
    ),
    "charge_2026-07-16_litime_80A": ("2026-07-16T18:10:00Z", "2026-07-16T19:55:00Z"),
}

STASIS_START = "2026-07-16T19:50:00Z"  # charger-stop edge; the SOC anchor fired here


def query_csv(measurement, entity_id, start, end):
    """Return a DataFrame of (t, value) for one entity over [start, end)."""
    if not URL:
        sys.exit(
            "no influxdb_url - set HA_CONFIG to the HA config dir, or INFLUXDB_URL"
        )
    q = (
        f'SELECT "value" FROM "{measurement}" WHERE "entity_id"=\'{entity_id}\' '
        f"AND time >= '{start}' AND time < '{end}'"
    )
    params = {
        "db": DB,
        "q": q,
        "u": USER,
        "p": PASS,
        "epoch": "ms",
        "chunked": "true",
        "chunk_size": "20000",
    }
    req = urllib.request.Request(
        URL.rstrip("/") + "/query?" + urllib.parse.urlencode(params),
        headers={"Accept": "application/csv", "Accept-Encoding": "gzip"},
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    df = pd.read_csv(io.BytesIO(raw))
    if df.empty:
        return pd.DataFrame(columns=["t", "value"])
    df["t"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    return df[["t", "value"]].dropna().sort_values("t").reset_index(drop=True)


def integrate(df, cap_s=10.0):
    """Left-rectangle integral with a stale-sample guard.

    Mirrors the firmware's `integration_method: left` and its 10 s stale-bus
    watchdog, so the result is directly comparable to the on-device
    accumulators. Returns per-sample area (value-seconds) and the dt used.
    """
    dt = df["t"].diff().shift(-1).dt.total_seconds().fillna(0).clip(0, cap_s)
    return df["value"].to_numpy() * dt.to_numpy(), dt.to_numpy()


def load_shelly():
    """Every Shelly Plus Uni voltage sample that overlaps the INA228 record.

    Both files ship in data/; the Shelly was retired 2026-07-16, so this is the
    complete overlap and it can never grow.
    """
    root = Path(__file__).resolve().parent.parent / "data"
    parts = []
    for p in (
        root / "Shelly Voltage.csv",
        root / "high_freq_voltage" / "voltage_data_2026-06-17_to_2026-07-16.csv.gz",
    ):
        if not p.exists():
            continue
        s = pd.read_csv(p)
        s = s[pd.to_numeric(s["state"], errors="coerce").notna()]
        parts.append(
            pd.DataFrame(
                {
                    "t": pd.to_datetime(s["last_changed"], utc=True, format="ISO8601"),
                    "shelly": s["state"].astype(float),
                }
            )
        )
    if not parts:
        return None
    return pd.concat(parts).drop_duplicates("t").sort_values("t").reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-07-13")
    # A FIXED cutoff, deliberately not "now". InfluxDB retention here is
    # infinite and the bank keeps logging, so an open-ended window would give a
    # different dataset - and different headline numbers - on every run, and the
    # published report would stop matching the published data within the hour.
    # Bump this when a new report is cut; never leave it floating.
    ap.add_argument("--end", default="2026-08-26T20:00:00Z")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    def _stamp(x):
        """Accept either a bare date or a full ISO timestamp."""
        return x if "T" in x else x + "T00:00:00Z"

    start, end = _stamp(a.start), _stamp(a.end)
    # Filenames carry dates only - ":" is not legal in a Windows filename.
    start_slug, end_slug = a.start[:10], a.end[:10]
    out = (
        Path(a.out)
        if a.out
        else Path(__file__).resolve().parent.parent / "data" / "ina228"
    )
    (out / "events").mkdir(parents=True, exist_ok=True)

    d = {}
    for name, (meas, eid) in SERIES.items():
        d[name] = query_csv(meas, eid, start, end)
        print(f"  {name:<10s} n={len(d[name]):9d}")

    # ---------------------------------------------------------- event windows
    # Current is the densest series and carries the true 2 s cadence; voltage and
    # power are matched onto its timestamps rather than unioned with them, which
    # would triple the row count with two-thirds NaN.
    #
    # The match is BACKWARD, i.e. last-known-value. Home Assistant writes to
    # InfluxDB on state change, not on a sample clock, so a series that stops
    # writing has stopped *changing* - a flat line looks like a gap and is not
    # one. Voltage quantised to the 195.3 uV bus LSB genuinely holds for minutes
    # at a steady load, and carrying the last value forward is the correct
    # reconstruction of the signal.
    for label, (t0, t1) in EVENTS.items():
        t0, t1 = pd.Timestamp(t0), pd.Timestamp(t1)
        base = d["current"]
        base = (
            base[(base.t >= t0) & (base.t <= t1)][["t", "value"]]
            .rename(columns={"value": "current"})
            .reset_index(drop=True)
        )
        for k in ("voltage", "power"):
            s = d[k]
            s = (
                s[s.t <= t1 + pd.Timedelta("5s")][["t", "value"]]
                .rename(columns={"value": k})
                .reset_index(drop=True)
            )
            base = pd.merge_asof(base, s, on="t", direction="backward")
        ev = base.rename(columns={"t": "time_utc"}).set_index("time_utc")
        ev = ev[["voltage", "current", "power"]]
        # gzip only what exceeds the repo's 500 KB pre-commit gate; the
        # short high-current legs stay plain CSV so they stay browsable.
        name = label + (".csv.gz" if len(ev) > 10000 else ".csv")
        ev.round(6).to_csv(out / "events" / name)
        print(
            f"  event {label:<38s} {len(ev):6d} rows  "
            f"(voltage NaN: {int(ev['voltage'].isna().sum())})"
        )

    # ------------------------------------------------------ hourly / daily agg
    a_s, dt_i = integrate(d["current"])
    w_s, _ = integrate(d["power"])
    for freq, fname in (("h", "ina228_hourly"), ("D", "ina228_daily")):
        cur = d["current"].set_index("t")["value"]
        vol = d["voltage"].set_index("t")["value"]
        pw = d["power"].set_index("t")["value"]
        ah = pd.Series(a_s, index=d["current"].t).resample(freq).sum() / 3600.0
        cov = pd.Series(dt_i, index=d["current"].t).resample(freq).sum()
        wh = pd.Series(w_s, index=d["power"].t).resample(freq).sum() / 3600.0
        g = pd.DataFrame(
            {
                "v_mean": vol.resample(freq).mean(),
                "v_min": vol.resample(freq).min(),
                "v_max": vol.resample(freq).max(),
                "v_sd_mV": vol.resample(freq).std() * 1000,
                "i_mean_A": cur.resample(freq).mean(),
                "i_min_A": cur.resample(freq).min(),
                "i_max_A": cur.resample(freq).max(),
                "p_mean_W": pw.resample(freq).mean(),
                "p_min_W": pw.resample(freq).min(),
                "p_max_W": pw.resample(freq).max(),
                "ah_net": ah,
                "wh_net": wh,
                "coverage_s": cov,
                "pack_F": d["packtemp"].set_index("t")["value"].resample(freq).mean(),
                "die_F": d["dietemp"].set_index("t")["value"].resample(freq).mean(),
                "n_current": cur.resample(freq).size(),
            }
        )
        # Time-weighted mean current, not the sample mean: InfluxDB writes on
        # state change, so a sample mean over-weights busy periods.
        g["i_timemean_mA"] = np.where(
            g["coverage_s"] > 0, g["ah_net"] * 3600 / g["coverage_s"] * 1000, np.nan
        )
        g.index.name = "time_utc"
        p = out / (f"{fname}_{start_slug}_{end_slug}.csv")
        g.round(6).to_csv(p)
        print(f"  {p.name}  {len(g)} rows")

    # ------------------------------------------------- three-way coulomb ledger
    # Same charge, three independent accountants:
    #   hw_ah  - the INA228's own 40-bit CHARGE register, accumulated in silicon
    #            every 1.58 s conversion, read raw over I2C once a minute
    #   own_ah - this script's left-rectangle integration of the published 2 s
    #            current series (the method the firmware uses, without its
    #            deadband)
    #   sw_ah  - the firmware's ah_charged_this_cycle minus ah_discharged_this_
    #            cycle, which applies a +/-0.05 A deadband before integrating
    # Divergence between the first two is integration-method error. Divergence
    # of the third from both is the deadband.
    led = (
        pd.DataFrame({"hw_ah": d["hw_net_ah"].set_index("t")["value"]})
        .resample("h")
        .last()
    )
    own = pd.Series(a_s, index=d["current"].t).resample("h").sum().cumsum() / 3600.0
    led["own_ah"] = own
    for col, key in (("sw_charged_ah", "sw_ah_chg"), ("sw_discharged_ah", "sw_ah_dis")):
        led[col] = d[key].set_index("t")["value"].resample("h").last()
    led = led.ffill()
    led["sw_net_ah"] = led["sw_charged_ah"] - led["sw_discharged_ah"]
    led.index.name = "time_utc"
    p = out / "coulomb_ledger_hourly.csv"
    led.round(6).to_csv(p)
    print(f"  {p.name}  {len(led)} rows")

    # --------------------------------- Shelly / INA228 paired cross-calibration
    # The two instruments overlapped only from the INA228's first bus reading to
    # the Shelly's retirement. Pair every Shelly sample with the INA228's 60 s
    # trailing mean at that instant, and carry the current and the local dV/dt
    # so the analysis can gate on "bank quiet and voltage not moving" - matching
    # a 2 min, 10 mV-quantised instrument to a 2 s one during a fast transient
    # measures the transient, not the offset.
    shelly = load_shelly()
    if shelly is not None and not shelly.empty:
        vi = d["voltage"].set_index("t")["value"]
        ina60 = vi.rolling("60s").mean().rename("ina228_ma60s").reset_index()
        rate = ((vi.shift(-150) - vi.shift(150)) / 10.0 * 1000).rename(
            "dvdt_mV_per_min"
        )
        rate = rate.reset_index()
        for frame in (shelly, ina60, rate):
            frame["t"] = frame["t"].astype("datetime64[ms, UTC]")
        cur = d["current"][["t", "value"]].rename(columns={"value": "current_A"})
        cur["t"] = cur["t"].astype("datetime64[ms, UTC]")
        m = pd.merge_asof(
            shelly.sort_values("t"),
            ina60,
            on="t",
            direction="nearest",
            tolerance=pd.Timedelta("30s"),
        )
        m = pd.merge_asof(
            m, cur, on="t", direction="nearest", tolerance=pd.Timedelta("5s")
        )
        m = pd.merge_asof(
            m, rate, on="t", direction="nearest", tolerance=pd.Timedelta("30s")
        )
        m = m.dropna(subset=["ina228_ma60s", "current_A"])
        m["delta_mV"] = (m["shelly"] - m["ina228_ma60s"]) * 1000
        m = m.rename(columns={"t": "time_utc", "shelly": "shelly_V"})
        p = out / "shelly_ina228_crosscheck.csv"
        m.set_index("time_utc").round(6).to_csv(p)
        print(f"  {p.name}  {len(m)} paired rows")

    # ------------------------------------------- stasis MA-60s, 1-minute means
    v = d["voltage"]
    v = v[v.t >= pd.Timestamp(STASIS_START)].set_index("t")["value"]
    ma = v.rolling("60s").mean()
    m = pd.DataFrame(
        {
            "v_ma60s_mean": ma.resample("1min").mean(),
            "v_raw_sd_mV": v.resample("1min").std() * 1000,
            "n": v.resample("1min").size(),
        }
    ).dropna(subset=["v_ma60s_mean"])
    m.index.name = "time_utc"
    # Gzipped: 55 k rows of 1-minute means is 2.6 MB plain, over the repo's
    # 500 KB pre-commit gate. pandas reads .csv.gz by extension, no flag needed.
    p = out / (f"stasis_ma60_{STASIS_START[:10]}_{end_slug}.csv.gz")
    m.round(6).to_csv(p)
    print(f"  {p.name}  {len(m)} rows")


if __name__ == "__main__":
    main()
