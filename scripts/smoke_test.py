#!/usr/bin/env python3
import os
import sys
import tempfile
import subprocess
import pandas as pd
import numpy as np

# Get the directory where this script lives (the 'scripts' folder)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(REPO_ROOT, "data")
HF_DIR = os.path.join(DATA_DIR, "high_freq_voltage")
os.makedirs(HF_DIR, exist_ok=True)

print("=== Creating minimal dummy data (covers your stasis dates) ===")

# Stasis period dates
dates = pd.date_range(start="2025-11-22", end="2026-02-21", freq="7D")

# Voltage CSV
voltage_df = pd.DataFrame({
    "Date": dates.strftime("%d/%m/%Y"),
    "Time": "12:00",
    "Min": np.round(13.20 + np.random.normal(0, 0.03, len(dates)), 4),
    "Max": np.round(13.25 + np.random.normal(0, 0.03, len(dates)), 4),
})
voltage_df.to_csv(os.path.join(DATA_DIR, "combined_output.csv"), index=False)

# Temperature CSV
temp_df = pd.DataFrame({
    "Date": dates.strftime("%d/%m/%Y"),
    "Time": "12:00",
    "Min": 55.0,
    "Max": 58.0,
})
temp_df.to_csv(os.path.join(DATA_DIR, "combined_temperature.csv"), index=False)

# One HF file
hf_dates = pd.date_range("2025-11-22", "2026-02-21", freq="5min", tz="UTC")[:500]
hf_df = pd.DataFrame({
    "entity_id": "shelly",
    "voltage": np.round(13.22 + np.random.normal(0, 0.01, len(hf_dates)), 4),
    "timestamp": hf_dates,
})
hf_df.to_csv(os.path.join(HF_DIR, "dummy_hf.csv"), index=False)

print(f"✅ Dummy data ready: {len(dates)} days voltage/temp + {len(hf_dates)} HF samples")

# Test 1: parse_shelly_export.py (located in the same folder)
print("\n=== Testing parse_shelly_export.py ===")
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
    f.write("""Min. voltage
21/03/2026 08:00,3.300
Max. voltage
21/03/2026 08:00,3.400
""")
    test_file = f.name

try:
    subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "parse_shelly_export.py"), test_file, "--dry-run"],
        check=True,
        cwd=REPO_ROOT
    )
finally:
    os.unlink(test_file)

print("✅ parse_shelly_export.py passed")

# Test 2: lifepo4_analysis.py (same folder)
print("\n=== Testing lifepo4_analysis.py ===")
result = subprocess.run(
    [sys.executable, os.path.join(SCRIPT_DIR, "lifepo4_analysis.py")],
    check=True,
    capture_output=True,
    text=True,
    cwd=REPO_ROOT
)
print(result.stdout.split("Analysis complete!")[0][-300:])
print("✅ lifepo4_analysis.py passed")

# Test 3: update_voltage_chart.py (same folder)
print("\n=== Testing update_voltage_chart.py ===")
subprocess.run(
    [sys.executable, os.path.join(SCRIPT_DIR, "update_voltage_chart.py")],
    check=True,
    cwd=REPO_ROOT
)
print("✅ update_voltage_chart.py passed")

print("\n🎉 ALL SCRIPTS PASSED SMOKE TEST!")
