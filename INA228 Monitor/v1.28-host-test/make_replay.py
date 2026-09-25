"""Write replay.inc from the diag2 HW Net Charge export (the 09-25 idle record)."""

import csv
import datetime as dt
import sys

SRC = (
    sys.argv[1]
    if len(sys.argv) > 1
    else (
        "../diag2-export-2026-09-25/sensor.basement_battery_bank_monitor_hw_net_charge_ina228.csv"
    )
)
rows = [
    r for r in csv.DictReader(open(SRC)) if r["state"] not in ("unknown", "unavailable")
]
t0 = dt.datetime.fromisoformat(rows[0]["last_changed_utc"])
with open("replay.inc", "w") as f:
    f.write(f"static const long REPLAY_T0_EPOCH = {int(t0.timestamp())};\n")
    f.write("static const double REPLAY[][2] = {\n")
    for r in rows:
        t = dt.datetime.fromisoformat(r["last_changed_utc"])
        f.write(f"  {{{(t - t0).total_seconds():.3f}, {float(r['state']):.9f}}},\n")
    f.write("};\n")
print(f"replay.inc: {len(rows)} rows from {t0}")
