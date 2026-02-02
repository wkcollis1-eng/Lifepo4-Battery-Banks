# Data Directory

This folder contains the raw and processed datasets for the LiFePO₄ battery monitoring study.

---

## Files

### `combined_output.csv` — Hourly Voltage Data

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `Date` | string | DD/MM/YYYY | Date of measurement |
| `Time` | string | HH:MM | Hour of measurement (local time) |
| `Min` | float | V | Minimum voltage recorded in that hour |
| `Max` | float | V | Maximum voltage recorded in that hour |

**Coverage:** Oct 29, 2025 → Jan 31, 2026  
**Records:** 2,222  
**Cadence:** Hourly aggregates  
**Source:** Shelly Plus Uni voltmeter via Home Assistant  
**Quantization:** 10 mV (sensor resolution)

**Derived fields (computed in analysis):**
- `Mid = (Min + Max) / 2` — Hourly mid-voltage
- `Spread = Max - Min` — Hourly voltage range

---

### `combined_temperature.csv` — Hourly Temperature Data

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `Date` | string | DD/MM/YYYY | Date of measurement |
| `Time` | string | HH:MM | Hour of measurement (local time) |
| `Min` | float | °F | Minimum temperature in that hour |
| `Max` | float | °F | Maximum temperature in that hour |

**Coverage:** Dec 29, 2025 → Jan 31, 2026  
**Records:** 816  
**Cadence:** Hourly aggregates  
**Source:** Co-located basement temperature sensor  
**Location:** Same room as battery bank (~3 ft distance)

---

### `high_freq/` — High-Frequency Voltage Data

Due to file size (~25+ MB combined), high-frequency data is distributed via [GitHub Releases](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases).

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `entity_id` | string | — | Home Assistant entity identifier |
| `state` | float | V | Instantaneous voltage reading |
| `last_changed` | datetime | ISO 8601 UTC | Timestamp of measurement |

**Coverage:** Dec 26, 2025 → Feb 1, 2026  
**Records:** ~328,000 (combined from multiple exports)  
**Cadence:** ~3 seconds median (variable; gaps inflate mean to ~10s)  
**Source:** Shelly Plus Uni voltmeter, state-change logging

**Note:** Some files contain hourly pre-aggregated means (identified by timestamps at :00:00.000Z); raw sub-minute samples have millisecond-resolution timestamps.

---

## Missingness & Gaps

- **Hourly data:** No significant gaps; continuous coverage
- **Temperature data:** Starts Dec 29 (sensor added mid-study)
- **High-frequency data:** Variable gaps due to:
  - Home Assistant state-change-only logging (no change = no record)
  - Export window boundaries
  - Brief network interruptions

---

## Units & Conventions

| Quantity | Unit | Notes |
|----------|------|-------|
| Voltage | V (Volts) | Pack-level bus voltage (4S configuration) |
| Temperature | °F (Fahrenheit) | Basement ambient |
| Time | Local (EST/EDT) | Hourly files; UTC for high-freq |
| Current | mA | Inferred only; no direct measurement |

---

## How to Load

```python
import pandas as pd

# Hourly voltage
voltage = pd.read_csv('data/combined_output.csv')
voltage['datetime'] = pd.to_datetime(voltage['Date'] + ' ' + voltage['Time'], 
                                      format='%d/%m/%Y %H:%M')

# Hourly temperature
temp = pd.read_csv('data/combined_temperature.csv')
temp['datetime'] = pd.to_datetime(temp['Date'] + ' ' + temp['Time'], 
                                   format='%d/%m/%Y %H:%M')

# High-frequency (from release download)
hf = pd.read_csv('data/high_freq/history.csv')
hf.columns = ['entity_id', 'voltage', 'timestamp']
hf['timestamp'] = pd.to_datetime(hf['timestamp'])
```

---

## Data Quality Notes

1. **10 mV quantization** in hourly data is a sensor limitation, not rounding
2. **Eco Mode transition** (Dec 23, 2025 ~15:40 local) affects spread measurements
3. **Extreme minutes** (>60 mV spread): 3 occurrences identified — likely EMI/ADC artifacts
4. **Temperature sensor** was added mid-study; no temperature data before Dec 29
