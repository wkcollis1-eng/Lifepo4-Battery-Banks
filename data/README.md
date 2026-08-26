# 📊 Data Directory

This folder contains the raw and processed datasets for the LiFePO₄ battery monitoring study.

---

> [!IMPORTANT]
> **This study spans two instruments.** Everything dated on or before
> **2026-07-16** comes from the Shelly Plus Uni voltmeter — voltage only, 10 mV
> quantisation. Everything from **2026-07-14** onward comes from the INA228
> monitor — voltage *and* current, 195.3 µV bus LSB, 2 s cadence — and lives
> under [`ina228/`](ina228/). The two overlap for two days, and quantifying that
> overlap is what [`ina228/shelly_ina228_crosscheck.csv`](ina228/shelly_ina228_crosscheck.csv)
> is for: **the Shelly reads 30.6 mV low** (n = 148 gated pairs, 95% CI ±1.3 mV;
> usable uncertainty ±3 mV). **Add 30.6 mV to any Shelly-era voltage before
> comparing it with an INA228-era one.**

## Contents

- [Files Overview](#files-overview)
- [INA228 Data — 2026-07 onward](#ina228-data--2026-07-onward)
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

### INA228 era (current instrument)

| File | Description | Records | Coverage |
|:-----|:------------|--------:|:---------|
| `ina228/ina228_daily_*.csv` | Daily V/I/P aggregates, Ah, Wh, temps, coverage | 44 | Jul 14 – Aug 26, 2026 |
| `ina228/ina228_hourly_*.csv` | Same, hourly | 1,052 | Jul 14 – Aug 26, 2026 |
| `ina228/stasis_ma60_*.csv.gz` | 1-minute MA-60s voltage means, stasis window | 55,691 | Jul 16 – Aug 26, 2026 |
| `ina228/coulomb_ledger_hourly.csv` | Hardware vs software vs independent coulomb counts | 968 | Jul 17 – Aug 26, 2026 |
| `ina228/shelly_ina228_crosscheck.csv` | Paired two-instrument samples | 817 | Jul 14 – Jul 16, 2026 |
| `ina228/events/*.csv[.gz]` | **Full 2 s resolution**, four charge/discharge windows | 32,486 | Jul 15 – Jul 16, 2026 |

### Shelly era (retired 2026-07-16)

| File | Description | Records | Coverage |
|:-----|:------------|--------:|:---------|
| `combined_output.csv` | Hourly voltage (min/max) | 3,636 | Oct 29, 2025 – Mar 31, 2026 |
| `combined_temperature.csv` | Hourly temperature (min/max) | 1,608 | Dec 29, 2025 – Mar 5, 2026 |
| `Combined_Temperature_Data.csv` | Hourly temperature, extended | 2,230 | Dec 29, 2025 – Mar 31, 2026 |
| `combined_humidity.csv` | Hourly humidity | 1,608 | Dec 29, 2025 – Mar 5, 2026 |
| `high_freq_voltage/*.csv[.gz]` | Weekly high-freq voltage files | 766,897 | Dec 26, 2025 – Jul 16, 2026 |
| `shelly_daily_min_2026-04-01_2026-07-16.csv` | Daily minimum voltage — **bridges the Apr–Jul gap** | 107 | Apr 1 – Jul 16, 2026 |
| `Shelly Voltage.csv` | Raw state-change log, commissioning overlap | 1,089 | Jul 15 – Jul 16, 2026 |
| `monthly_metrics.csv` | Monthly summary metrics (one row/month) | 7 | Oct 2025 – Aug 2026 |
| `ina228 *.csv` | HA recorder exports, superseded by `ina228/` | — | Jul 15 – Jul 16, 2026 |

> [!NOTE]
> The `ina228 Amperage/Slope/Temp/Voltage/Wattage.csv` files at the top level are
> raw two-day Home Assistant recorder exports from commissioning. They are kept
> for continuity, but `ina228/` is the maintained source: it is rebuilt from
> InfluxDB (infinite retention) rather than from the recorder (14-day purge), and
> it covers the whole record rather than two days.

---

## INA228 Data — 2026-07 onward

The monitor publishes at 2 s. Over the reporting window that is ~1.8 M current
samples, ~130 MB — too large to version, and at full resolution it carries no
information outside the event windows that the hourly aggregate does not. Four
tiers ship instead, and `scripts/ina228_export.py` rebuilds all of them from
InfluxDB over any window.

> [!NOTE]
> **Three files ship gzipped**, because plain they exceed this repository's
> 500 KB `check-added-large-files` pre-commit gate:
> `ina228/stasis_ma60_*.csv.gz` (2.6 MB → 307 KB),
> `ina228/events/discharge_2026-07-15_70W_overnight.csv.gz` (1.8 MB → 321 KB),
> and `high_freq_voltage/voltage_data_2026-06-17_to_2026-07-16.csv.gz`
> (638 KB → 43 KB). They are compressed rather than downsampled so no sample is
> lost from a DOI-archived dataset. **pandas reads them with no extra argument** —
> `pd.read_csv("...csv.gz")` — as does R's `readr::read_csv()`. On the command
> line, `gunzip -c file.csv.gz | head`.
>
> The uncompressed files above 500 KB in `high_freq_voltage/` and the
> `ina228 *.csv` recorder exports predate this convention; they were added
> through the GitHub web UI, which does not run pre-commit hooks.

### `ina228/ina228_hourly_*.csv` and `ina228/ina228_daily_*.csv`

| Column | Unit | Description |
|:-------|:-----|:------------|
| `time_utc` | ISO 8601 UTC | Bucket start |
| `v_mean` / `v_min` / `v_max` | V | Bus voltage |
| `v_sd_mV` | mV | Within-bucket voltage standard deviation |
| `i_mean_A` / `i_min_A` / `i_max_A` | A | Current; **positive = charging** |
| `p_mean_W` / `p_min_W` / `p_max_W` | W | Power, same sign convention |
| `ah_net` / `wh_net` | Ah / Wh | Net charge and energy over the bucket |
| `coverage_s` | s | Seconds of the bucket actually integrated |
| `pack_F` / `die_F` | °F | DS18B20 pack, INA228 die |
| `n_current` | count | Current samples in the bucket |
| `i_timemean_mA` | mA | **Time-weighted** mean current — use this, not `i_mean_A` |

> [!WARNING]
> `i_mean_A` is the mean **over samples**; `i_timemean_mA` is the mean **over
> time**. Home Assistant writes to InfluxDB on state change, not on a sample
> clock, so busy periods contribute more samples per second than quiet ones and
> the sample mean over-weights them. For anything integrated — drain, energy,
> SOC — use `i_timemean_mA` or `ah_net`.

### `ina228/events/*.csv`

Full 2 s resolution over four windows. Voltage and power are matched to the
current timestamps **backward** (last known value), because a state-change series
that stops writing has stopped *changing* — bus voltage quantised to the 195.3 µV
LSB genuinely holds for minutes under a steady load, so a flat line is data, not
a gap.

| File | Rows | What it is |
|:-----|-----:|:-----------|
| `charge_2026-07-16_litime_80A.csv` | 3,103 | Full CC/CV charge; sets the first SOC anchor. BMS balancing visible above 14.4 V |
| `discharge_2026-07-15_70W_overnight.csv.gz` | 28,084 | 15.6 h light-load leg, 76.1 Ah |
| `discharge_2026-07-16_1kW_heater.csv` | 702 | 81.8 A peak, Kill-A-Watt companion test |
| `discharge_2026-07-16_inverter_trip.csv` | 597 | 130.1 A recorded peak; two inverter-overload trips |

### `ina228/coulomb_ledger_hourly.csv`

Three independent counts of the same current — the basis of §6 of the
[2026-08-26 report](../reports/LiFePO4_Report_2026-08-26.md).

| Column | Unit | Description |
|:-------|:-----|:------------|
| `hw_ah` | Ah | The INA228's own 40-bit CHARGE register, accumulated in silicon every 1.58 s conversion. **Resets on device reboot** — see the caution below |
| `own_ah` | Ah | Left-rectangle integration of the published 2 s series, 10 s stale guard, no deadband |
| `sw_charged_ah` / `sw_discharged_ah` | Ah | The firmware's own per-cycle accumulators, which apply a ±0.05 A deadband |
| `sw_net_ah` | Ah | `sw_charged_ah − sw_discharged_ah` |

> [!CAUTION]
> `hw_ah` is absolute since the chip last powered up, so **it must be differenced
> within a single uptime span, never across a reboot.** Reboots in this dataset:
> 2026-07-16 16:54 and 23:04; 2026-07-17 12:30, 15:58, 19:05, 23:32 and 23:47;
> 2026-07-22 01:45; 2026-07-25 19:28. The analysis script uses the continuous
> span from 2026-07-25 20:00 onward for exactly this reason.

### `ina228/shelly_ina228_crosscheck.csv`

| Column | Unit | Description |
|:-------|:-----|:------------|
| `time_utc` | ISO 8601 UTC | Timestamp of the Shelly sample |
| `shelly_V` | V | Shelly Plus Uni reading |
| `ina228_ma60s` | V | INA228 60 s trailing mean at that instant |
| `current_A` | A | Bank current at that instant |
| `dvdt_mV_per_min` | mV/min | Local rate of change of the INA228 signal, ±5 min |
| `delta_mV` | mV | `(shelly_V − ina228_ma60s) × 1000` |

Gate on **both** `|current_A| < 0.5` **and** `|dvdt_mV_per_min| < 1` for the
quiescent offset. Without the second gate the spread inflates from 7.8 mV to
33.1 mV, because pairing a 2-minute instrument against a 2-second one during
post-charge relaxation measures the relaxation, not the offset.

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
| Current | A | INA228 on a 375 µΩ shunt from Jul 2026; **positive = charging, negative = discharging**. Inferred only before that |

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

## Monthly Metrics

### `monthly_metrics.csv`

One row per calendar month. Primary source for Claude Code monthly validation (V-BATT-1 through V-BATT-5 range checks). Updated at end of each monthly data session.

| Column | Type | Unit | Description |
|:-------|:-----|:-----|:------------|
| `month` | string | YYYY-MM | Calendar month |
| `study_day_end` | int | days | Study day count at end of month (day 1 = Oct 29, 2025) |
| `mean_voltage_v` | float | V | Monthly mean of hourly mid-voltage |
| `min_voltage_v` | float | V | Monthly minimum voltage |
| `max_voltage_v` | float | V | Monthly maximum voltage (includes charge events) |
| `mean_spread_mv` | float | mV | Monthly mean hourly spread (Max−Min) |
| `drift_rate_mv_day` | float | mV/day | OLS drift rate computed on daily means for the month |
| `drift_r2` | float | — | R² for monthly drift OLS (low = noisy/transitional period) |
| `hf_samples` | int | count | High-frequency samples in month (0 before Dec 2025) |
| `hourly_records` | int | count | Hourly voltage records in month |
| `charge_events` | int | count | Confirmed charge events in month |
| `regime` | string | — | Data regime tags: PRE_ECO, POST_ECO, CHARGE, POST_CHARGE |
| `notes` | string | — | Context for anomalies, milestones, or regime transitions |

**Update procedure (monthly):**
1. Append one new row for the completed month
2. Compute `mean_voltage_v`, `drift_rate_mv_day`, `hf_samples` from raw data
3. Set `regime` tags based on ECO_MODE_DATETIME (Dec 23, 2025) and charge event dates
4. Run V-BATT range checks against prior 3-month trailing average before committing

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
