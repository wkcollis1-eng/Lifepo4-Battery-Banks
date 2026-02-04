# 📊 Data Directory

This folder contains the raw and processed datasets for the LiFePO₄ battery monitoring study.

---

## Contents

- [Files Overview](#files-overview)
- [Hourly Voltage Data](#hourly-voltage-data)
- [Hourly Temperature Data](#hourly-temperature-data)
- [High-Frequency Voltage Data](#high-frequency-voltage-data)
- [Units & Conventions](#units--conventions)
- [How to Load](#how-to-load)
- [Data Quality](#data-quality)
- [Schema Diagram](#schema-diagram)

---

## Files Overview

| File | Description | Records | Coverage |
|:-----|:------------|--------:|:---------|
| `combined_output.csv` | Hourly voltage (min/max) | 2,222 | Oct 29, 2025 – Jan 31, 2026 |
| `combined_temperature.csv` | Hourly temperature (min/max) | 816 | Dec 29, 2025 – Jan 31, 2026 |
| `history.csv` | High-frequency voltage samples | ~67,000 | Partial (see releases) |
| `High Freq Voltage Data *.csv` | Extended high-freq datasets | ~328,000 | Dec 26, 2025 – Feb 1, 2026 |

> [!NOTE]
> For the complete high-frequency dataset (~328,000 samples), see [GitHub Releases](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases).

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
| Coverage | Oct 29, 2025 → Jan 31, 2026 |
| Records | 2,222 |
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
| Coverage | Dec 29, 2025 → Jan 31, 2026 |
| Records | 816 |
| Cadence | Hourly aggregates |
| Source | Co-located basement temperature sensor |
| Location | Same room as battery bank (~3 ft distance) |
| Temperature Range | 51.5°F – 55.95°F |

> [!IMPORTANT]
> Temperature sensor was added mid-study. No temperature data is available before Dec 29, 2025.

---

## High-Frequency Voltage Data

### `history.csv` (Partial)

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `entity_id` | string | — | Home Assistant entity identifier |
| `state` | float | V | Instantaneous voltage reading |
| `last_changed` | datetime | ISO 8601 UTC | Timestamp of measurement |

**Metadata:**

| Property | Value |
|:---------|:------|
| Coverage | Jan 27, 2026 → Feb 1, 2026 (partial) |
| Records | ~67,000 in this file |
| Cadence | ~3 seconds median (variable) |
| Mean Interval | ~10 seconds (gaps inflate average) |
| Source | Shelly Plus Uni, state-change logging |

### Full High-Frequency Datasets

Available in [GitHub Releases](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases):

| File | Samples | Coverage |
|:-----|--------:|:---------|
| `High Freq Voltage Data 1-18-2026.csv` | ~115,000 | Dec 26, 2025 – Jan 18, 2026 |
| `High Freq Voltage Data 1-27-2026.csv` | ~142,000 | Jan 19, 2026 – Jan 27, 2026 |
| Combined total | ~328,000 | Dec 26, 2025 – Feb 1, 2026 |

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
# High-frequency data
# ============================================================
hf = pd.read_csv('data/history.csv')
hf.columns = ['entity_id', 'voltage', 'timestamp']
hf['timestamp'] = pd.to_datetime(hf['timestamp'])
hf['voltage'] = pd.to_numeric(hf['voltage'], errors='coerce')

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
┌─────────────────────────────────────────────────────────────────┐
│                        DATA RELATIONSHIPS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   combined_output.csv          combined_temperature.csv          │
│   ┌──────────────────┐         ┌──────────────────┐             │
│   │ Date    (PK)     │         │ Date    (PK)     │             │
│   │ Time    (PK)     │◄───────►│ Time    (PK)     │             │
│   │ Min     (V)      │  JOIN   │ Min     (°F)     │             │
│   │ Max     (V)      │   ON    │ Max     (°F)     │             │
│   └──────────────────┘ Date+   └──────────────────┘             │
│          │              Time                                     │
│          │                                                       │
│          │ Derived from                                          │
│          ▼                                                       │
│   ┌──────────────────┐                                          │
│   │ history.csv      │                                          │
│   │ (high-frequency) │                                          │
│   ├──────────────────┤                                          │
│   │ entity_id        │                                          │
│   │ state     (V)    │                                          │
│   │ last_changed(UTC)│                                          │
│   └──────────────────┘                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Legend:
  (PK) = Part of composite primary key
  ◄──► = Join relationship
```

---

## See Also

- [Methodology](../docs/methodology.md) — How data is analyzed
- [Evidence Map](../docs/evidence_map.md) — Claim-to-data traceability
- [Replication Guide](../docs/replication.md) — How to collect similar data
