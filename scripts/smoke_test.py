import os
import pandas as pd
import numpy as np
import tempfile
import subprocess

print("=== Creating minimal dummy data (covers your stasis dates) ===")
data_dir = "data"
hf_dir = os.path.join(data_dir, "high_freq_voltage")
os.makedirs(hf_dir, exist_ok=True)

# Stasis period dates (exactly matches your config)
dates = pd.date_range(start="2025-11-22", end="2026-02-21", freq="7D")

# Voltage CSV
voltage_df = pd.DataFrame({
    "Date": dates.strftime("%d/%m/%Y"),
    "Time": "12:00",
    "Min": np.round(13.20 + np.random.normal(0, 0.03, len(dates)), 4),
    "Max": np.round(13.25 + np.random.normal(0, 0.03, len(dates)), 4),
})
voltage_df.to_csv(os.path.join(data_dir, "combined_output.csv"), index=False)

# Temperature CSV
temp_df = pd.DataFrame({
    "Date": dates.strftime("%d/%m/%Y"),
    "Time": "12:00",
    "Min": 55.0,
    "Max": 58.0,
})
temp_df.to_csv(os.path.join(data_dir, "combined_temperature.csv"), index=False)

# One HF file
hf_dates = pd.date_range("2025-11-22", "2026-02-21", freq="5min", tz="UTC")[:500]
hf_df = pd.DataFrame({
    "entity_id": "shelly",
    "voltage": np.round(13.22 + np.random.normal(0, 0.01, len(hf_dates)), 4),
    "timestamp": hf_dates,
})
hf_df.to_csv(os.path.join(hf_dir, "dummy_hf.csv"), index=False)

print(f"✅ Dummy data ready: {len(dates)} days voltage/temp + {len(hf_dates)} HF samples")

# Test 1: parse_shelly_export.py
print("\n=== Testing parse_shelly_export.py ===")
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
    f.write("""Min. voltage
21/03/2026 08:00,3.300
Max. voltage
21/03/2026 08:00,3.400
""")
    test_file = f.name
subprocess.run(["python", "parse_shelly_export.py", test_file, "--dry-run"], check=True)
os.unlink(test_file)
print("✅ parse_shelly_export.py passed")

# Test 2: lifepo4_analysis.py
print("\n=== Testing lifepo4_analysis.py ===")
result = subprocess.run(["python", "scripts/lifepo4_analysis.py"], check=True, capture_output=True, text=True)
print(result.stdout.split("Analysis complete!")[0][-300:])
print("✅ lifepo4_analysis.py passed")

# Test 3: update_voltage_chart.py
print("\n=== Testing update_voltage_chart.py ===")
subprocess.run(["python", "scripts/update_voltage_chart.py"], check=True)
print("✅ update_voltage_chart.py passed")

print("\n🎉 ALL SCRIPTS PASSED SMOKE TEST!")