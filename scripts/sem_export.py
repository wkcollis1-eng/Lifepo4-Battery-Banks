#!/usr/bin/env python3
"""
sem_export.py - publish the SEM-meter datasets behind the outage and the
coincident-peak failure mode.

Two unrelated windows, both from the 16-CT SEM (Fusion Energy/Sense) via MQTT:

  data/sem/sem_whole_home_hourly_*.csv    the 2026-07-04/05 outage, hourly
  data/sem/circuit_peaks_*.csv            per-circuit peak / running / inrush
  data/sem/coincident_peaks_*.csv         every 2 s sample where fridge+coffee
                                          exceeded the inverter's nameplate
  data/sem/events/fridge_coffee_worst_*.csv   the worst event at 2 s

IMPORTANT - the SEM's own coverage, which is why the outage and the peak
analysis come from different windows:

  Jun 27 - Jul 1 07:00   hourly backfill only (~23 rows/day)
  Jul 1 - Jul 12 11:02   NOTHING. An 11-day blackout.
  Jul 12 11:02 onward    live 2 s MQTT feed (~240k samples/week)

The 2026-07-04 outage falls inside the blackout, so no circuit-level data
exists for it. Only `sem_whole_home_power` survives, because its hourly
backfill kept running - and it reads 0.0 W throughout, which is correct
behaviour, not a fault: see the note in outage_analysis.py.

Run:  HA_CONFIG=H:/ python scripts/sem_export.py
"""

import gzip
import io
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

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

OUT = Path(__file__).resolve().parent.parent / "data" / "sem"

# The live-feed window. Deliberately pinned, like ina228_export.py: an
# open-ended end date would give different headline numbers on every run.
LIVE_A, LIVE_B = "2026-07-12T16:00:00Z", "2026-08-26T20:00:00Z"
OUTAGE_A, OUTAGE_B = "2026-07-03T00:00:00Z", "2026-07-07T00:00:00Z"

INVERTER_W = 1500.0  # Giandel nameplate - the threshold that matters


def query(entity_id, measurement, start, end):
    if not URL:
        sys.exit("no influxdb_url - set HA_CONFIG, or INFLUXDB_URL")
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
        return pd.DataFrame(columns=["t", "v"])
    df["t"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    return (
        df[["t", "value"]]
        .rename(columns={"value": "v"})
        .dropna()
        .sort_values("t")
        .reset_index(drop=True)
    )


def main():
    (OUT / "events").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------ 1. the outage, hourly
    wh = query("sem_whole_home_power", "W", OUTAGE_A, OUTAGE_B)
    wh = wh.rename(columns={"t": "time_utc", "v": "whole_home_W"})
    wh["time_et"] = wh["time_utc"].dt.tz_convert("America/New_York")
    p = OUT / "sem_whole_home_hourly_2026-07-03_2026-07-07.csv"
    wh.round(1).to_csv(p, index=False)
    print(f"  {p.name}  {len(wh)} rows")

    # ------------------------------------- 2. circuits over the live window
    circuits = {
        "fridge": "sem_fridge_power",
        "coffee": "sem_counter_2_power",
        "furnace": "sem_furnace_power",
        "hwh_recirc": "hwh_current_consumption",
    }
    raw = {}
    rows = []
    for label, eid in circuits.items():
        d = query(eid, "W", LIVE_A, LIVE_B)
        raw[label] = d
        run = d.loc[d.v > 5, "v"]
        rows.append(
            {
                "circuit": label,
                "entity_id": eid,
                "n_samples": len(d),
                "peak_W": round(d.v.max(), 1),
                "running_median_W": round(run.median(), 1) if len(run) else 0.0,
                "inrush_ratio": round(d.v.max() / run.median(), 1)
                if len(run) and run.median() > 0
                else None,
            }
        )
        print(f"  {label:11s} n={len(d):>9,}  peak {d.v.max():7.1f} W")
    p = OUT / f"circuit_peaks_{LIVE_A[:10]}_{LIVE_B[:10]}.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    print(f"  {p.name}")

    # ----------------------------- 3. fridge+coffee coincidence on a 2 s grid
    # ffill(limit=5) carries a value at most 10 s: HA writes on state change,
    # so a circuit that stops writing is steady, not absent. Beyond 10 s the
    # assumption stops being safe and the sample is dropped instead.
    f = raw["fridge"].set_index("t")["v"].resample("2s").max()
    c = raw["coffee"].set_index("t")["v"].resample("2s").max()
    j = pd.concat([f.rename("fridge_W"), c.rename("coffee_W")], axis=1)
    j = j.ffill(limit=5).dropna()
    j["sum_W"] = j["fridge_W"] + j["coffee_W"]

    ex = j[j["sum_W"] > INVERTER_W].copy()
    ex.index.name = "time_utc"
    ex["time_et"] = ex.index.tz_convert("America/New_York")
    ex["over_nameplate_x"] = (ex["sum_W"] / INVERTER_W).round(2)
    p = OUT / f"coincident_peaks_{LIVE_A[:10]}_{LIVE_B[:10]}.csv"
    ex.round(1).to_csv(p)
    print(f"  {p.name}  {len(ex)} samples over {INVERTER_W:.0f} W")

    # ------------------------------------ 4. the worst event at full 2 s res
    worst = j["sum_W"].idxmax()
    w = j.loc[worst - pd.Timedelta("3min") : worst + pd.Timedelta("3min")].copy()
    w.index.name = "time_utc"
    p = OUT / "events" / f"fridge_coffee_worst_{worst:%Y-%m-%d}.csv"
    w.round(1).to_csv(p)
    print(
        f"  {p.name}  {len(w)} rows, peak {j['sum_W'].max():.1f} W at "
        f"{worst.tz_convert('America/New_York'):%Y-%m-%d %H:%M:%S ET}"
    )


if __name__ == "__main__":
    main()
