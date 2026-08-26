#!/usr/bin/env python3
"""
update_monthly_metrics.py - rebuild data/monthly_metrics.csv from repo data.

One row per calendar month across both instrument eras. Rows before 2026-03 are
carried through unchanged from the existing file (they were computed from source
data that is no longer all in the repository); 2026-03 onward are recomputed
here, so the file can be regenerated after any data update.

The `instrument` column is the era marker. It exists because the two instruments
do not share a scale: the Shelly reads 30.6 mV low against the INA228 (n = 148
gated pairs). Comparing a `shelly` row's voltage with an `ina228` row's without
applying that offset is the single most likely mistake a reader can make with
this file, so the column is here rather than in a reader's head.

Run:  python scripts/update_monthly_metrics.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"
START = pd.Timestamp("2025-10-29")  # study day 1
FIRST_RECOMPUTED = "2026-03"


def ols(x, y):
    if len(x) < 3:
        return np.nan, np.nan
    r = stats.linregress(x, y)
    return r.slope, r.rvalue**2


def main():
    h = pd.read_csv(DATA / "combined_output.csv")
    h["dt"] = pd.to_datetime(h["Date"] + " " + h["Time"], format="%d/%m/%Y %H:%M")
    h["mid"] = (h["Min"] + h["Max"]) / 2
    h["spread"] = (h["Max"] - h["Min"]) * 1000

    dm = pd.read_csv(
        DATA / "shelly_daily_min_2026-04-01_2026-07-16.csv", parse_dates=["date"]
    )

    ina = pd.read_csv(min((DATA / "ina228").glob("ina228_daily_*.csv")))
    ina["dt"] = pd.to_datetime(
        ina["time_utc"], utc=True, format="ISO8601"
    ).dt.tz_localize(None)

    rows = []

    # -- March 2026: the hourly file now runs to Mar 31, not Mar 6
    m = h[(h.dt >= "2026-03-01") & (h.dt < "2026-04-01")]
    d = m.groupby(m.dt.dt.date)["mid"].mean()
    sl, r2 = ols(np.arange(len(d)), d.to_numpy() * 1000)
    rows.append(
        {
            "month": "2026-03",
            "study_day_end": (pd.Timestamp("2026-03-31") - START).days + 1,
            "instrument": "shelly",
            "mean_voltage_v": round(m["mid"].mean(), 4),
            "min_voltage_v": round(m["Min"].min(), 2),
            "max_voltage_v": round(m["Max"].max(), 2),
            "mean_spread_mv": round(m["spread"].mean(), 2),
            "drift_rate_mv_day": round(sl, 2),
            "drift_r2": round(r2, 3),
            "hf_samples": 74288,
            "hourly_records": len(m),
            "charge_events": 0,
            "regime": "POST_ECO+POST_CHARGE",
            "notes": "Full month now published (prior row covered Mar 2-6 only). "
            "Post-charge stasis sustained; hourly Min=Max from Mar 27 "
            "(10 mV quantisation floor)",
        }
    )

    # -- April to June 2026: only daily minima were exported
    for mo, end, hf in (
        ("2026-04", "2026-04-30", 0),
        ("2026-05", "2026-05-31", 0),
        ("2026-06", "2026-06-30", 3360),
    ):
        q = dm[(dm.date >= mo + "-01") & (dm.date <= end)]
        x = (q.date - q.date.iloc[0]).dt.days.to_numpy().astype(float)
        sl, r2 = ols(x, q["v_min"].to_numpy() * 1000)
        rows.append(
            {
                "month": mo,
                "study_day_end": (pd.Timestamp(end) - START).days + 1,
                "instrument": "shelly",
                "mean_voltage_v": round(q["v_min"].mean(), 4),
                "min_voltage_v": round(q["v_min"].min(), 2),
                "max_voltage_v": round(q["v_min"].max(), 2),
                "mean_spread_mv": "",
                "drift_rate_mv_day": round(sl, 3),
                "drift_r2": round(r2, 3),
                "hf_samples": hf,
                "hourly_records": 0,
                "charge_events": 0,
                "regime": "STORAGE_STASIS",
                "notes": "Daily minima only (no hourly export). Deep storage stasis; "
                "drift below the Shelly detection limit",
            }
        )

    # -- July 2026: the instrument changed mid-month
    i = ina[(ina.dt >= "2026-07-14") & (ina.dt < "2026-08-01")]
    rows.append(
        {
            "month": "2026-07",
            "study_day_end": (pd.Timestamp("2026-07-31") - START).days + 1,
            "instrument": "shelly->ina228",
            "mean_voltage_v": round(i["v_mean"].mean(), 4),
            "min_voltage_v": round(i["v_min"].min(), 4),
            "max_voltage_v": round(i["v_max"].max(), 4),
            "mean_spread_mv": round(((i["v_max"] - i["v_min"]) * 1000).mean(), 2),
            "drift_rate_mv_day": "",
            "drift_r2": "",
            "hf_samples": int(i["n_current"].sum()),
            "hourly_records": 0,
            "charge_events": 3,
            "regime": "INSTRUMENT_CHANGE+COMMISSIONING",
            "notes": "Shelly retired Jul 16. Jul 5 and Jul 11 charges (Shelly-observed); "
            "Jul 14-16 INA228 commissioning campaign: 110.65 Ah discharged, "
            "115.38 Ah recharged, first full-charge anchor Jul 16 19:50 UTC. "
            "Voltage columns are INA228 from Jul 14; add 30.6 mV to earlier "
            "Shelly values to compare",
        }
    )

    # -- August 2026: full days only (coverage guard drops the partial final day)
    i = ina[
        (ina.dt >= "2026-08-01") & (ina.dt < "2026-09-01") & (ina["coverage_s"] > 80000)
    ]
    sl, r2 = ols(np.arange(len(i)), i["v_mean"].to_numpy() * 1000)
    rows.append(
        {
            "month": "2026-08",
            "study_day_end": (i.dt.max() - START).days + 1,
            "instrument": "ina228",
            "mean_voltage_v": round(i["v_mean"].mean(), 4),
            "min_voltage_v": round(i["v_min"].min(), 4),
            "max_voltage_v": round(i["v_max"].max(), 4),
            "mean_spread_mv": round(((i["v_max"] - i["v_min"]) * 1000).mean(), 3),
            "drift_rate_mv_day": round(sl, 4),
            "drift_r2": round(r2, 3),
            "hf_samples": int(i["n_current"].sum()),
            "hourly_records": 0,
            "charge_events": 0,
            "regime": "INA228+STASIS",
            "notes": "Deep stasis. Quiescent drain measured directly at 7.49 mA "
            "(41-day mean); within-day voltage sd 0.131 mV on Aug 26. "
            "Aug 4 ~18:30 UTC: +2.9 mA unexplained step in drain (see report S7). "
            "Through Aug 26 only",
        }
    )

    old = pd.read_csv(DATA / "monthly_metrics.csv")
    if "instrument" not in old.columns:
        old.insert(2, "instrument", "shelly")
    old = old[old["month"] < FIRST_RECOMPUTED]

    cols = [
        "month",
        "study_day_end",
        "instrument",
        "mean_voltage_v",
        "min_voltage_v",
        "max_voltage_v",
        "mean_spread_mv",
        "drift_rate_mv_day",
        "drift_r2",
        "hf_samples",
        "hourly_records",
        "charge_events",
        "regime",
        "notes",
    ]
    new = pd.concat([old, pd.DataFrame(rows)], ignore_index=True)[cols]
    new.to_csv(DATA / "monthly_metrics.csv", index=False)
    print(new.to_string(index=False, max_colwidth=44))


if __name__ == "__main__":
    main()
