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
voltage_df = pd.DataFrame(
    {
        "Date": dates.strftime("%d/%m/%Y"),
        "Time": "12:00",
        "Min": np.round(13.20 + np.random.normal(0, 0.03, len(dates)), 4),
        "Max": np.round(13.25 + np.random.normal(0, 0.03, len(dates)), 4),
    }
)
voltage_df.to_csv(os.path.join(DATA_DIR, "combined_output.csv"), index=False)

# Temperature CSV – add random variation to avoid constant values
np.random.seed(42)  # for reproducibility
temp_min_base = 55.0
temp_max_base = 58.0
temp_min = temp_min_base + np.random.normal(0, 0.2, len(dates))
temp_max = temp_max_base + np.random.normal(0, 0.2, len(dates))
# ensure min < max
temp_min = np.minimum(temp_min, temp_max - 0.1)
temp_max = np.maximum(temp_max, temp_min + 0.1)

temp_df = pd.DataFrame(
    {
        "Date": dates.strftime("%d/%m/%Y"),
        "Time": "12:00",
        "Min": np.round(temp_min, 1),
        "Max": np.round(temp_max, 1),
    }
)
temp_df.to_csv(os.path.join(DATA_DIR, "combined_temperature.csv"), index=False)

# One HF file (500 samples in stasis window)
hf_dates = pd.date_range("2025-11-22", "2026-02-21", freq="5min", tz="UTC")[:500]
hf_df = pd.DataFrame(
    {
        "entity_id": "shelly",
        "voltage": np.round(13.22 + np.random.normal(0, 0.01, len(hf_dates)), 4),
        "timestamp": hf_dates,
    }
)
hf_df.to_csv(os.path.join(HF_DIR, "dummy_hf.csv"), index=False)

print(
    f"✅ Dummy data ready: {len(dates)} days voltage/temp + {len(hf_dates)} HF samples"
)


def run_script(script_name, args=None, capture_output=True):
    """Run a Python script and print full output on failure."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    cmd = [sys.executable, script_path] + (args or [])
    print(f"\n--- Running {script_name} ---")
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=capture_output, text=True, cwd=REPO_ROOT
        )
        if capture_output:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {script_name} failed with exit code {e.returncode}")
        if capture_output:
            print("STDOUT:")
            print(e.stdout)
            print("STDERR:")
            print(e.stderr)
        raise


# Test 1: parse_shelly_export.py
print("\n=== Testing parse_shelly_export.py ===")
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".csv", delete=False, encoding="utf-8"
) as f:
    f.write("""Min. voltage
21/03/2026 08:00,3.300
Max. voltage
21/03/2026 08:00,3.400
""")
    test_file = f.name

try:
    run_script("parse_shelly_export.py", [test_file, "--dry-run"], capture_output=False)
finally:
    os.unlink(test_file)

# Test 2: lifepo4_analysis.py
print("\n=== Testing lifepo4_analysis.py ===")
run_script("lifepo4_analysis.py")

# Test 3: update_voltage_chart.py
print("\n=== Testing update_voltage_chart.py ===")
run_script("update_voltage_chart.py")

print("\n🎉 ALL SCRIPTS PASSED SMOKE TEST!")
