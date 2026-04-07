#!/usr/bin/env python3
"""
LiFePO4 Battery Bank Analysis
Comprehensive analysis including:
- Drift analysis (full stasis, last 30 days)
- MA-60 seconds noise reduction on high-frequency data
- Temperature-voltage regression
- Spread and stability metrics

Usage (from repo root):
    python scripts/lifepo4_analysis.py
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import timedelta
import glob
import os
import warnings

warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION — update these when data coverage extends
# ============================================================================

# Resolve paths relative to repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOLTAGE_FILE = os.path.join(REPO_ROOT, "data", "combined_output.csv")
TEMP_FILE = os.path.join(REPO_ROOT, "data", "combined_temperature.csv")
HF_DIR = os.path.join(REPO_ROOT, "data", "high_freq_voltage")
FIGURE_DIR = os.path.join(REPO_ROOT, "figures")
DATE_FORMAT = "%d/%m/%Y %H:%M"  # DD/MM/YYYY — do not change
FIGURE_DPI = 150

# CLAUDE: Update STASIS_END when new data extends past this date.
# Set to the day before the next charge event, or latest data date if no charge event.
STASIS_START = "2025-11-22"
STASIS_END = "2026-02-21"  # <- CLAUDE: update when data extends

# CLAUDE: Update after any new charge event is identified.
CHARGE_EVENT_DATE = "2026-02-22"  # <- CLAUDE: update if new charge event occurs

# CLAUDE: Do not change ECO_MODE_DATETIME — it is a fixed hardware event.
ECO_MODE_DATETIME = "2025-12-23 15:40:00"

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================

DATA_END = pd.read_csv(VOLTAGE_FILE, usecols=["Date"]).iloc[-1]["Date"]
print("=" * 80)
print(f"LiFePO4 Battery Bank Analysis — Data through {DATA_END}")
print("=" * 80)
print()

# Load hourly voltage data
print("Loading hourly voltage data...")
hourly_df = pd.read_csv(VOLTAGE_FILE)
hourly_df["datetime"] = pd.to_datetime(
    hourly_df["Date"] + " " + hourly_df["Time"], format="%d/%m/%Y %H:%M"
)
hourly_df["Mid"] = (hourly_df["Min"] + hourly_df["Max"]) / 2
hourly_df["Spread"] = hourly_df["Max"] - hourly_df["Min"]
hourly_df = hourly_df.sort_values("datetime").reset_index(drop=True)
print(f"  Hourly voltage: {len(hourly_df)} records")
print(f"  Range: {hourly_df['datetime'].min()} → {hourly_df['datetime'].max()}")

# Load temperature data
print("\nLoading temperature data...")
temp_df = pd.read_csv(TEMP_FILE)
temp_df["datetime"] = pd.to_datetime(
    temp_df["Date"] + " " + temp_df["Time"], format=DATE_FORMAT
)
temp_df["TempMid"] = (temp_df["Min"] + temp_df["Max"]) / 2
temp_df = temp_df.sort_values("datetime").reset_index(drop=True)
print(f"  Temperature: {len(temp_df)} records")
print(f"  Range: {temp_df['datetime'].min()} → {temp_df['datetime'].max()}")

# Load and combine high-frequency data — auto-discovers all weekly files in HF_DIR
print("\nLoading high-frequency voltage data...")


def load_hf_data(filepath):
    """Load a weekly high-frequency voltage file from data/high_freq_voltage/."""
    df = pd.read_csv(filepath)
    df.columns = ["entity_id", "voltage", "timestamp"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=True)
    df["voltage"] = pd.to_numeric(df["voltage"], errors="coerce")
    df = df.dropna(subset=["voltage"])
    return df[["timestamp", "voltage"]].sort_values("timestamp")


hf_files = sorted(glob.glob(os.path.join(HF_DIR, "*.csv")))
if not hf_files:
    raise FileNotFoundError(f"No HF files found in {HF_DIR}")

hf_parts = []
for f in hf_files:
    part = load_hf_data(f)
    print(
        f"  {os.path.basename(f)}: {len(part)} records ({part['timestamp'].min()} → {part['timestamp'].max()})"
    )
    hf_parts.append(part)

# Combine and deduplicate
hf_combined = pd.concat(hf_parts, ignore_index=True)
hf_combined = (
    hf_combined.drop_duplicates(subset=["timestamp"])
    .sort_values("timestamp")
    .reset_index(drop=True)
)
print(f"\n  Combined HF: {len(hf_combined)} unique records")
print(f"  Range: {hf_combined['timestamp'].min()} → {hf_combined['timestamp'].max()}")

# Calculate time intervals
hf_combined["interval_sec"] = hf_combined["timestamp"].diff().dt.total_seconds()
median_interval = hf_combined["interval_sec"].median()
mean_interval = hf_combined["interval_sec"].mean()
print(f"  Median sample interval: {median_interval:.2f}s")
print(f"  Mean sample interval: {mean_interval:.2f}s")

# ============================================================================
# 2. DRIFT ANALYSIS (DAILY MEAN OLS)
# ============================================================================

print("\n" + "=" * 80)
print("DRIFT ANALYSIS")
print("=" * 80)

# Create daily mean mid-voltage series
hourly_df["date"] = hourly_df["datetime"].dt.date
daily_mid = hourly_df.groupby("date")["Mid"].mean().reset_index()
daily_mid["date"] = pd.to_datetime(daily_mid["date"])
daily_mid = daily_mid.sort_values("date")

# Full stasis period — dates from STASIS_START / STASIS_END config above
stasis_start = pd.Timestamp(STASIS_START)
stasis_end = pd.Timestamp(STASIS_END)
stasis_df = daily_mid[
    (daily_mid["date"] >= stasis_start) & (daily_mid["date"] <= stasis_end)
].copy()

if len(stasis_df) > 1:
    stasis_df["days"] = (stasis_df["date"] - stasis_start).dt.days
    slope_full, intercept_full, r_full, p_full, se_full = stats.linregress(
        stasis_df["days"], stasis_df["Mid"]
    )
    total_days_full = stasis_df["days"].max()
    total_change_full = slope_full * total_days_full
    residuals_full = stasis_df["Mid"] - (
        intercept_full + slope_full * stasis_df["days"]
    )
    residual_std_full = residuals_full.std() * 1000  # mV

    print("\nFull Stasis Period (Nov 22 → Jan 31):")
    print(f"  Days: {total_days_full}")
    print(f"  OLS drift rate: {slope_full * 1000:.3f} mV/day")
    print(f"  Total change: {total_change_full * 1000:.2f} mV")
    print(f"  R²: {r_full**2:.3f}")
    print(f"  Detrended residual σ: {residual_std_full:.2f} mV")

# Last 30 days — window derived from STASIS_END
last30_start = pd.Timestamp(STASIS_END) - pd.Timedelta(days=29)
last30_end = pd.Timestamp(STASIS_END)
last30_df = daily_mid[
    (daily_mid["date"] >= last30_start) & (daily_mid["date"] <= last30_end)
].copy()

if len(last30_df) > 1:
    last30_df["days"] = (last30_df["date"] - last30_start).dt.days
    slope_30, intercept_30, r_30, p_30, se_30 = stats.linregress(
        last30_df["days"], last30_df["Mid"]
    )
    total_days_30 = last30_df["days"].max()
    total_change_30 = slope_30 * total_days_30
    residuals_30 = last30_df["Mid"] - (intercept_30 + slope_30 * last30_df["days"])
    residual_std_30 = residuals_30.std() * 1000  # mV

    print("\nLast 30 Days (Jan 2 → Jan 31):")
    print(f"  Days: {total_days_30}")
    print(f"  OLS drift rate: {slope_30 * 1000:.3f} mV/day")
    print(f"  Total change: {total_change_30 * 1000:.2f} mV")
    print(f"  R²: {r_30**2:.3f}")
    print(f"  p-value: {p_30:.4f}")
    print(f"  Detrended residual σ: {residual_std_30:.2f} mV")

# Drift flattening analysis
print("\n  Drift Flattening:")
print(f"    Full period rate: {slope_full * 1000:.3f} mV/day")
print(f"    Last 30 days rate: {slope_30 * 1000:.3f} mV/day")
print(f"    Rate reduction: {(1 - abs(slope_30 / slope_full)) * 100:.1f}%")

# ============================================================================
# 3. MA-60 SECONDS ANALYSIS (TIME-BASED ROLLING WINDOW)
# ============================================================================

print("\n" + "=" * 80)
print("MA-60 SECONDS ANALYSIS (High-Frequency Data)")
print("=" * 80)

# Set timestamp as index for time-based rolling
hf_analysis = hf_combined.copy()
hf_analysis = hf_analysis.set_index("timestamp")

# Apply time-based 60-second rolling mean
hf_analysis["MA60"] = hf_analysis["voltage"].rolling("60s", min_periods=1).mean()
hf_analysis = hf_analysis.reset_index()

# Global statistics
raw_std = hf_analysis["voltage"].std() * 1000  # mV
ma60_std = hf_analysis["MA60"].std() * 1000  # mV
noise_reduction = (1 - ma60_std / raw_std) * 100

print(f"\nGlobal MA-60s Performance (Full HF Record: {len(hf_analysis):,} samples)")
print(f"  Raw σ: {raw_std:.3f} mV")
print(f"  MA-60s σ: {ma60_std:.3f} mV")
print(f"  Noise reduction: {noise_reduction:.2f}%")

# Per-minute diagnostics
hf_analysis["minute"] = hf_analysis["timestamp"].dt.floor("min")
minute_stats = (
    hf_analysis.groupby("minute")
    .agg({"voltage": ["mean", "std", "min", "max", "count"], "MA60": ["mean", "std"]})
    .reset_index()
)
minute_stats.columns = [
    "minute",
    "v_mean",
    "v_std",
    "v_min",
    "v_max",
    "samples",
    "ma60_mean",
    "ma60_std",
]
minute_stats["v_range"] = (minute_stats["v_max"] - minute_stats["v_min"]) * 1000  # mV
minute_stats["v_std"] = minute_stats["v_std"] * 1000  # mV

mean_within_min_std = minute_stats["v_std"].mean()
between_min_std = minute_stats["v_mean"].std() * 1000
mean_min_range = minute_stats["v_range"].mean()
mean_samples_per_min = minute_stats["samples"].mean()

print("\nMinute-Bucket Diagnostics:")
print(f"  Mean within-minute σ: {mean_within_min_std:.2f} mV")
print(f"  Between-minute σ (minute means): {between_min_std:.2f} mV")
print(f"  Mean minute min-max: {mean_min_range:.2f} mV")
print(f"  Mean samples/minute: {mean_samples_per_min:.2f}")

# Extreme minute anomaly scan (>60 mV spread)
extreme_minutes = minute_stats[minute_stats["v_range"] > 60]
print(f"\nExtreme Minutes (>60 mV spread): {len(extreme_minutes)}")
for _, row in extreme_minutes.iterrows():
    print(f"  {row['minute']} - Range: {row['v_range']:.1f} mV")

# Segment analysis — auto-generates 4 equal segments across the stasis HF window
# CLAUDE: segments are computed automatically; no hardcoded dates needed here.
print("\nSegment Analysis:")
hf_stasis = hf_analysis[
    (hf_analysis["timestamp"] >= pd.Timestamp(STASIS_START, tz="UTC"))
    & (
        hf_analysis["timestamp"]
        <= pd.Timestamp(STASIS_END, tz="UTC") + pd.Timedelta(hours=23, minutes=59)
    )
]
seg_start = hf_stasis["timestamp"].min()
seg_end = hf_stasis["timestamp"].max()
seg_len = (seg_end - seg_start) / 4
segments = []
for i in range(4):
    s = seg_start + i * seg_len
    e = seg_start + (i + 1) * seg_len
    label = f"{s.strftime('%b %d')} - {e.strftime('%b %d')}"
    segments.append((label, s, e))

segment_results = []
for name, start, end in segments:
    mask = (hf_analysis["timestamp"] >= start) & (hf_analysis["timestamp"] <= end)
    seg = hf_analysis[mask]
    if len(seg) > 0:
        raw_s = seg["voltage"].std() * 1000
        ma60_s = seg["MA60"].std() * 1000
        reduction = (1 - ma60_s / raw_s) * 100 if raw_s > 0 else 0
        segment_results.append(
            {
                "Segment": name,
                "Samples": len(seg),
                "Raw σ (mV)": raw_s,
                "MA-60s σ (mV)": ma60_s,
                "Reduction": reduction,
            }
        )
        print(
            f"  {name}: {len(seg):,} samples | Raw σ: {raw_s:.2f} mV | MA-60s σ: {ma60_s:.2f} mV | Reduction: {reduction:.1f}%"
        )

# ============================================================================
# 4. TEMPERATURE-VOLTAGE RELATIONSHIP
# ============================================================================

print("\n" + "=" * 80)
print("TEMPERATURE-VOLTAGE RELATIONSHIP")
print("=" * 80)

# Merge hourly voltage and temperature
merged = pd.merge(
    hourly_df[["datetime", "Mid"]],
    temp_df[["datetime", "TempMid"]],
    on="datetime",
    how="inner",
)
print(f"\nMatched hourly dataset: {len(merged)} points")
print(
    f"  Temperature range: {merged['TempMid'].min():.2f}°F → {merged['TempMid'].max():.2f}°F (Δ{merged['TempMid'].max() - merged['TempMid'].min():.2f}°F)"
)
print(f"  Mean temperature: {merged['TempMid'].mean():.2f}°F")

# Daily temperature swing
temp_df["date"] = temp_df["datetime"].dt.date
daily_temp = temp_df.groupby("date").agg({"Min": "min", "Max": "max"}).reset_index()
daily_temp["swing"] = daily_temp["Max"] - daily_temp["Min"]
print("\nDaily basement temperature swing:")
print(f"  Mean: {daily_temp['swing'].mean():.2f}°F")
print(f"  Range: {daily_temp['swing'].min():.1f}°F → {daily_temp['swing'].max():.1f}°F")

# Naive regression (V vs T only)
if len(merged) > 2:
    slope_t, intercept_t, r_t, p_t, se_t = stats.linregress(
        merged["TempMid"], merged["Mid"] * 1000
    )
    print("\nNaive Regression (V vs T only):")
    print(f"  Temperature coefficient: +{slope_t:.2f} mV/°F")
    print(f"  R²: {r_t**2:.3f}")

    # Two-factor regression (time + temperature)
    merged["days_from_start"] = (
        merged["datetime"] - merged["datetime"].min()
    ).dt.total_seconds() / 86400
    X = merged[["days_from_start", "TempMid"]].values
    y = merged["Mid"].values * 1000  # mV

    # Add constant for intercept
    X_with_const = np.column_stack([np.ones(len(X)), X])

    # OLS: (X'X)^-1 X'y
    try:
        beta = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
        y_pred = X_with_const @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2_multi = 1 - ss_res / ss_tot

        # Standard errors
        n = len(y)
        p_count = X_with_const.shape[1]
        mse = ss_res / (n - p_count)
        var_beta = mse * np.linalg.inv(X_with_const.T @ X_with_const)
        se_beta = np.sqrt(np.diag(var_beta))

        print("\nTwo-Factor Regression (Time + Temperature):")
        print(f"  Residual drift: {beta[1]:.3f} ± {se_beta[1]:.3f} mV/day")
        print(f"  Temperature coefficient: +{beta[2]:.2f} ± {se_beta[2]:.2f} mV/°F")
        print(f"  R²: {r2_multi:.3f}")
    except Exception as e:
        print(f"  Two-factor regression failed: {e}")

# ============================================================================
# 5. ECO MODE AND LATE-JANUARY STABILITY
# ============================================================================

print("\n" + "=" * 80)
print("ECO MODE STEP AND LATE-JANUARY STABILITY")
print("=" * 80)

# Eco Mode window (±48h around Dec 23 15:40 local)
eco_center = pd.Timestamp(ECO_MODE_DATETIME)
eco_before_start = eco_center - timedelta(hours=48)
eco_before_end = eco_center
eco_after_start = eco_center
eco_after_end = eco_center + timedelta(hours=48)

before_eco = hourly_df[
    (hourly_df["datetime"] >= eco_before_start)
    & (hourly_df["datetime"] < eco_before_end)
]
after_eco = hourly_df[
    (hourly_df["datetime"] >= eco_after_start)
    & (hourly_df["datetime"] <= eco_after_end)
]

if len(before_eco) > 0 and len(after_eco) > 0:
    mid_shift = (after_eco["Mid"].mean() - before_eco["Mid"].mean()) * 1000
    min_shift = (after_eco["Min"].mean() - before_eco["Min"].mean()) * 1000
    spread_before = before_eco["Spread"].mean() * 1000
    spread_after = after_eco["Spread"].mean() * 1000

    print("\nEco Mode Shift (±48h around Dec 23 15:40):")
    print(f"  Mid baseline shift: {mid_shift:.2f} mV")
    print(f"  Min baseline shift: {min_shift:.2f} mV")
    print(f"  Mean spread: {spread_before:.2f} mV → {spread_after:.2f} mV")

# Late-January stability (last 7 days ending Jan 31)
last7_start = pd.Timestamp("2026-01-25")
last7_end = pd.Timestamp(STASIS_END) + pd.Timedelta(hours=23, minutes=59, seconds=59)
last7 = hourly_df[
    (hourly_df["datetime"] >= last7_start) & (hourly_df["datetime"] <= last7_end)
]

if len(last7) > 0:
    print("\nLate-January Stability (Last 7 days, ending Jan 31):")
    print(f"  Mean mid-voltage: {last7['Mid'].mean():.4f} V")
    print(f"  Mid σ: {last7['Mid'].std() * 1000:.2f} mV")
    print(f"  Mean spread: {last7['Spread'].mean() * 1000:.2f} mV")

# ============================================================================
# 6. SOC & STORAGE ENDURANCE
# ============================================================================

print("\n" + "=" * 80)
print("SOC & STORAGE ENDURANCE (PARASITIC CURRENT MODEL)")
print("=" * 80)

# Time from STASIS_START to STASIS_END for SOC projection
start_time = pd.Timestamp(STASIS_START)
end_time = pd.Timestamp(STASIS_END) + pd.Timedelta(hours=23)
hours_elapsed = (end_time - start_time).total_seconds() / 3600

print(
    f"\nTime elapsed ({STASIS_START} 00:00 → {STASIS_END} 23:00): {hours_elapsed:.0f} hours"
)

# Calculate Ah lost for different parasitic currents
parasitic_currents = [13.3, 17, 20]  # mA
print("\nIntegrated loss estimates:")
for I_mA in parasitic_currents:
    Ah_lost = (I_mA / 1000) * hours_elapsed
    soc_remaining = (500 - Ah_lost) / 500 * 100
    print(f"  I={I_mA} mA: {Ah_lost:.2f} Ah lost → ~{soc_remaining:.1f}% SOC")

# Time to 80% SOC
print("\nTime to 80% SOC (lose 100 Ah):")
for I_mA in parasitic_currents:
    hours_to_80 = 100 / (I_mA / 1000)
    days_to_80 = hours_to_80 / 24
    months_to_80 = days_to_80 / 30.4
    print(f"  I={I_mA} mA: {days_to_80:.0f} days ({months_to_80:.1f} months)")

# ============================================================================
# 7. SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

print(f"""
DATASET COVERAGE:
  Hourly voltage: {hourly_df["datetime"].min().strftime("%Y-%m-%d")} → {hourly_df["datetime"].max().strftime("%Y-%m-%d")} ({len(hourly_df):,} records)
  Temperature: {temp_df["datetime"].min().strftime("%Y-%m-%d")} → {temp_df["datetime"].max().strftime("%Y-%m-%d")} ({len(temp_df):,} records)
  High-frequency: {hf_combined["timestamp"].min().strftime("%Y-%m-%d")} → {hf_combined["timestamp"].max().strftime("%Y-%m-%d")} ({len(hf_combined):,} records)

DRIFT ANALYSIS:
  Full stasis ({STASIS_START} → {STASIS_END}): {slope_full * 1000:.3f} mV/day, total {total_change_full * 1000:.2f} mV
  Last 30 days (-29d → {STASIS_END}): {slope_30 * 1000:.3f} mV/day, total {total_change_30 * 1000:.2f} mV
  Drift flattening: {(1 - abs(slope_30 / slope_full)) * 100:.1f}% rate reduction

MA-60 SECONDS (GLOBAL):
  Raw σ: {raw_std:.3f} mV → MA-60s σ: {ma60_std:.3f} mV
  Noise reduction: {noise_reduction:.2f}%
  Segment band: ~42-50%

TEMPERATURE-VOLTAGE:
  Naive coefficient: +{slope_t:.2f} mV/°F (R² = {r_t**2:.3f})
  Two-factor coefficient: +{beta[2]:.2f} ± {se_beta[2]:.2f} mV/°F

STABILITY (Last 7 days):
  Mean mid-voltage: {last7["Mid"].mean():.4f} V
  Mid σ: {last7["Mid"].std() * 1000:.2f} mV
  Mean spread: {last7["Spread"].mean() * 1000:.2f} mV
""")

print("Analysis complete!")
print("=" * 80)
