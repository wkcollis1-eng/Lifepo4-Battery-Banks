# 📊 Data Directory

This folder contains the raw and processed datasets for the LiFePO₄ battery monitoring study.

---

## Contents

- [Files Overview](#files-overview)
- [Hourly Voltage Data](#hourly-voltage-data)
- [Hourly Temperature Data](#hourly-temperature-data)
- [Hourly Humidity Data](#hourly-humidity-data)
- [High-Frequency Voltage Data](#high-frequency-voltage-data)
- [Units & Conventions](#units--conventions)
- [How to Load](#how-to-load)
- [Data Quality](#data-quality)
- [Schema Diagram](#schema-diagram)

---

## Files Overview

| File | Description | Records | Coverage |
|:-----|:------------|--------:|:---------|
| `combined_output.csv` | Hourly voltage (min/max) | 3,095 | Oct 29, 2025 – Mar 5, 2026 |
| `combined_temperature.csv` | Hourly temperature (min/max) | 1,560 | Jan 1, 2026 – Mar 6, 2026 |
| `combined_humidity.csv` | Hourly humidity | 1,560 | Jan 1, 2026 – Mar 6, 2026 |
| `high_freq_voltage/*.csv` | Weekly high-freq voltage files | 712,197 | Dec 26, 2025 – Mar 6, 2026 |

> [!NOTE]
> High-frequency data is now organized in weekly consolidated files within the `high_freq_voltage/` subdirectory.

---

## Hourly Voltage Data

### `combined_output.csv`

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `Date` | string | DD/MM/YYYY | Date of measurement |
| `Time` | string | HH:MM | Hour of measurement (local time, EST/EDT) |
| `Min` | float | V | Minimum voltage recorded in that hour |
| `Max` | float | V | Maximum voltage recorded in that hour |

**Metadata:**

| Property | Value |
|:---------|:------|
| Coverage | Oct 29, 2025 → Mar 5, 2026 |
| Records | 3,095 |
| Cadence | Hourly aggregates |
| Source | Shelly Plus Uni voltmeter via Home Assistant |
| Quantization | ~10 mV (sensor resolution) |
| Completeness | 99.8% (minimal gaps) |

**Derived fields** (computed in analysis, not stored):

| Field | Formula | Description |
|:------|:--------|:------------|
| `Mid` | `(Min + Max) / 2` | Hourly mid-voltage |
| `Spread` | `Max - Min` | Hourly voltage range |
| `datetime` | `Date + Time` | Combined timestamp |

---

## Hourly Temperature Data

### `combined_temperature.csv`

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `Date` | string | DD/MM/YYYY | Date of measurement |
| `Time` | string | HH:MM | Hour of measurement (local time, EST/EDT) |
| `Min` | float | °F | Minimum temperature in that hour |
| `Max` | float | °F | Maximum temperature in that hour |

**Metadata:**

| Property | Value |
|:---------|:------|
| Coverage | Jan 1, 2026 → Mar 6, 2026 |
| Records | 1,560 |
| Cadence | Hourly aggregates |
| Source | Co-located basement temperature sensor |
| Location | Same room as battery bank (~3 ft distance) |
| Temperature Range | 51.2°F – 56.0°F |

> [!IMPORTANT]
> Temperature sensor was added mid-study. No temperature data is available before Dec 29, 2025.

---

## Hourly Humidity Data

### `combined_humidity.csv`

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `Date` | string | DD/MM/YYYY | Date of measurement |
| `Time` | string | HH:MM | Hour of measurement (local time, EST/EDT) |
| `Humidity` | float | % | Relative humidity reading |

**Metadata:**

| Property | Value |
|:---------|:------|
| Coverage | Jan 1, 2026 → Mar 6, 2026 |
| Records | 1,560 |
| Cadence | Hourly aggregates |
| Source | Co-located basement humidity sensor |
| Location | Same room as battery bank |

---

## High-Frequency Voltage Data

### `high_freq_voltage/` Directory

Contains weekly consolidated CSV files with ~3-second cadence voltage readings.

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `entity_id` | string | — | Home Assistant entity identifier |
| `state` | float | V | Instantaneous voltage reading |
| `last_changed` | datetime | ISO 8601 UTC | Timestamp of measurement |

### Weekly Files

| File | Samples | Coverage |
|:-----|--------:|:---------|
| `voltage_data_2025-12-26_to_2025-12-28.csv` | 54 | Dec 26-28, 2025 |
| `voltage_data_2025-12-29_to_2026-01-04.csv` | 168 | Dec 29 - Jan 4 |
| `voltage_data_2026-01-05_to_2026-01-11.csv` | 70,627 | Jan 5-11 |
| `voltage_data_2026-01-12_to_2026-01-18.csv` | 82,939 | Jan 12-18 |
| `voltage_data_2026-01-19_to_2026-01-25.csv` | 89,669 | Jan 19-25 |
| `voltage_data_2026-01-26_to_2026-02-01.csv` | 94,416 | Jan 26 - Feb 1 |
| `voltage_data_2026-02-02_to_2026-02-08.csv` | 87,824 | Feb 2-8 |
| `voltage_data_2026-02-09_to_2026-02-15.csv` | 95,804 | Feb 9-15 |
| `voltage_data_2026-02-16_to_2026-02-22.csv` | 98,324 | Feb 16-22 |
| `voltage_data_2026-02-23_to_2026-03-01.csv` | 43,870 | Feb 23 - Mar 1 |
| `voltage_data_2026-03-02_to_2026-03-06.csv` | 48,514 | Mar 2-6 |
| **Total** | **712,197** | **Dec 26, 2025 – Mar 6, 2026** |

**Metadata:**

| Property | Value |
|:---------|:------|
| Coverage | Dec 26, 2025 → Mar 6, 2026 |
| Total Records | 712,197 |
| Cadence | ~3 seconds median (variable) |
| Source | Shelly Plus Uni, state-change logging |
| Organization | Weekly consolidated files, deduplicated |

---

## Units & Conventions

### Measurement Units

| Quantity | Unit | Notes |
|:---------|:-----|:------|
| Voltage | V (Volts) | Pack-level bus voltage (4S configuration) |
| Temperature | °F (Fahrenheit) | Basement ambient |
| Current | mA | Inferred only; no direct measurement |

### Time Conventions

| Data Type | Timezone | Format |
|:----------|:---------|:-------|
| Hourly files | Local (EST/EDT) | DD/MM/YYYY HH:MM |
| High-frequency | UTC | ISO 8601 |

### Date Format Note

> [!WARNING]
> CSV files use **DD/MM/YYYY** format (British convention). Ensure correct parsing in your analysis.

```python
# Correct parsing
df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                 format='%d/%m/%Y %H:%M')

# WRONG - will misinterpret dates
df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])  # Don't do this
```

---

## How to Load

### Python (Recommended)

```python
import pandas as pd

# ============================================================
# Hourly voltage data
# ============================================================
voltage = pd.read_csv('data/combined_output.csv')
voltage['datetime'] = pd.to_datetime(
    voltage['Date'] + ' ' + voltage['Time'], 
    format='%d/%m/%Y %H:%M'
)
voltage['Mid'] = (voltage['Min'] + voltage['Max']) / 2
voltage['Spread'] = voltage['Max'] - voltage['Min']

print(f"Voltage: {len(voltage)} records, "
      f"{voltage['datetime'].min()} to {voltage['datetime'].max()}")

# ============================================================
# Hourly temperature data
# ============================================================
temp = pd.read_csv('data/combined_temperature.csv')
temp['datetime'] = pd.to_datetime(
    temp['Date'] + ' ' + temp['Time'], 
    format='%d/%m/%Y %H:%M'
)
temp['Mid'] = (temp['Min'] + temp['Max']) / 2

print(f"Temperature: {len(temp)} records, "
      f"{temp['datetime'].min()} to {temp['datetime'].max()}")

# ============================================================
# Hourly humidity data
# ============================================================
humidity = pd.read_csv('data/combined_humidity.csv')
humidity['datetime'] = pd.to_datetime(
    humidity['Date'] + ' ' + humidity['Time'],
    format='%d/%m/%Y %H:%M'
)

print(f"Humidity: {len(humidity)} records, "
      f"{humidity['datetime'].min()} to {humidity['datetime'].max()}")

# ============================================================
# High-frequency data (load all weekly files)
# ============================================================
import glob

hf_files = glob.glob('data/high_freq_voltage/*.csv')
hf_list = []
for f in hf_files:
    df = pd.read_csv(f)
    df.columns = ['entity_id', 'voltage', 'timestamp']
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['voltage'] = pd.to_numeric(df['voltage'], errors='coerce')
    hf_list.append(df)

hf = pd.concat(hf_list, ignore_index=True).sort_values('timestamp')

print(f"High-freq: {len(hf)} records, "
      f"{hf['timestamp'].min()} to {hf['timestamp'].max()}")
```

### R

```r
library(tidyverse)
library(lubridate)

# Hourly voltage
voltage <- read_csv("data/combined_output.csv") %>%
  mutate(datetime = dmy_hm(paste(Date, Time)),
         Mid = (Min + Max) / 2,
         Spread = Max - Min)

# Hourly temperature
temp <- read_csv("data/combined_temperature.csv") %>%
  mutate(datetime = dmy_hm(paste(Date, Time)),
         Mid = (Min + Max) / 2)

# Hourly humidity
humidity <- read_csv("data/combined_humidity.csv") %>%
  mutate(datetime = dmy_hm(paste(Date, Time)))

# High-frequency (all weekly files)
hf_files <- list.files("data/high_freq_voltage", pattern = "*.csv", full.names = TRUE)
hf <- map_dfr(hf_files, read_csv) %>%
  rename(voltage = state, timestamp = last_changed) %>%
  mutate(timestamp = ymd_hms(timestamp))
```

---

## Data Quality

### Quality Summary

| Dataset | Completeness | Known Issues |
|:--------|:-------------|:-------------|
| Hourly voltage | 99.8% | Minor gaps during exports |
| Hourly temperature | 100% | Starts Dec 29 only |
| High-frequency | Variable | State-change gaps |

### Known Data Quality Events

| Date | Time (Local) | Event | Impact | Handling |
|:-----|:-------------|:------|:-------|:---------|
| Dec 23, 2025 | ~15:40 | Eco Mode enabled | Spread measurement change | Note regime; analyze separately |
| Jan 14, 2026 | 02:13 UTC | EMI spike | Single outlier (>60 mV spread) | Exclude from MA-60s |
| Jan 20, 2026 | 18:35 UTC | EMI spike | Single outlier | Exclude from MA-60s |
| Jan 23, 2026 | 08:37 UTC | EMI spike | Single outlier | Exclude from MA-60s |
| Feb 22, 2026 | 10:00-12:00 | Charge event | Voltage rise to 14.51V | Analyze separately; marks end of stasis period |

### Data Quality Flags

When processing data, consider flagging:

| Condition | Flag | Action |
|:----------|:-----|:-------|
| Spread > 60 mV | `EMI` | Likely artifact; review or exclude |
| Gap > 1 hour (hourly) | `GAP` | Note missing data |
| Gap > 60s (high-freq) | `SPARSE` | Affects MA-60s calculation |
| Before Dec 23, 2025 15:40 | `PRE_ECO` | Different measurement regime |
| After Dec 23, 2025 15:40 | `POST_ECO` | Different measurement regime |

### Quantization Note

The 10 mV quantization in hourly data is a **sensor limitation**, not rounding. Values like 13.27V and 13.28V are actual distinct readings; values like 13.271V or 13.279V are not possible with this sensor.

---

## Schema Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA RELATIONSHIPS                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   combined_output.csv     combined_temperature.csv  combined_humidity │
│   ┌──────────────────┐    ┌──────────────────┐     ┌───────────────┐ │
│   │ Date    (PK)     │    │ Date    (PK)     │     │ Date   (PK)   │ │
│   │ Time    (PK)     │◄──►│ Time    (PK)     │◄───►│ Time   (PK)   │ │
│   │ Min     (V)      │    │ Min     (°F)     │     │ Humidity (%)  │ │
│   │ Max     (V)      │    │ Max     (°F)     │     └───────────────┘ │
│   └──────────────────┘    └──────────────────┘                       │
│          │                      JOIN ON Date+Time                     │
│          │                                                            │
│          │ Derived from                                               │
│          ▼                                                            │
│   ┌────────────────────────────────────────┐                         │
│   │ high_freq_voltage/                     │                         │
│   │   voltage_data_YYYY-MM-DD_*.csv        │                         │
│   ├────────────────────────────────────────┤                         │
│   │ entity_id                              │                         │
│   │ state          (V)                     │                         │
│   │ last_changed   (UTC, ISO 8601)         │                         │
│   └────────────────────────────────────────┘                         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

Legend:
  (PK) = Part of composite primary key
  ◄──► = Join relationship
```

---

## See Also

- [Methodology](../docs/methodology.md) — How data is analyzed
- [Evidence Map](../docs/evidence_map.md) — Claim-to-data traceability
- [Replication Guide](../docs/replication.md) — How to collect similar data
