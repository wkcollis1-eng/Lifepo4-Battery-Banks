# 🔁 Replication Protocol

This document provides the hardware configuration, calibration notes, and environmental conditions necessary to replicate or extend this study.

---

## Contents

1. [Hardware Configuration](#1-hardware-configuration)
2. [Environmental Conditions](#2-environmental-conditions)
3. [Calibration Notes](#3-calibration-notes)
4. [Sampling Characteristics](#4-sampling-characteristics)
5. [Replication Checklist](#5-replication-checklist)
6. [Known Limitations](#6-known-limitations)
7. [Extending This Study](#7-extending-this-study)

---

## 1. Hardware Configuration

### 1.1 Battery Bank

| Component | Specification |
|:----------|:--------------|
| Chemistry | LiFePO₄ (Lithium Iron Phosphate) |
| Configuration | 4S (4 cells in series) × parallel blocks |
| Nominal Voltage | 12.8V (3.2V/cell × 4) |
| Capacity | 500Ah nominal |
| Brands | Mixed (architectural immunity test) |
| BMS | Yes (cell-level protection) |

### 1.2 Voltage Monitoring

| Component | Specification |
|:----------|:--------------|
| Sensor | Shelly Plus Uni |
| Input Range | DC voltage (0–30V) |
| Resolution | ~10 mV (ADC-limited) |
| Connection | Direct to bus terminals |
| Firmware | Stock (Eco Mode enabled Dec 23, 2025) |

> [!NOTE]
> **Eco Mode** reduces power consumption but triggers a device reboot when toggled. The transition on Dec 23, 2025 ~15:40 local correlates with observed spread changes.

### 1.3 Data Logging

| Component | Specification |
|:----------|:--------------|
| Platform | Home Assistant |
| Database | InfluxDB (optional; SQLite default) |
| Logging Mode | State-change only (no fixed polling) |
| Export Format | CSV via History panel |

### 1.4 Temperature Sensor

| Component | Specification |
|:----------|:--------------|
| Type | Generic digital temperature sensor |
| Location | Basement, ~3 ft from battery bank |
| Added | Dec 29, 2025 |
| Resolution | ~0.1°F |

---

## 2. Environmental Conditions

| Parameter | Value |
|:----------|:------|
| Location | Basement (below grade) |
| Temperature Range | 51.5°F – 55.95°F (Dec 29 – Jan 31) |
| Mean Temperature | 54.1°F |
| Daily Temperature Swing | 0.6°F – 2.0°F (mean 1.4°F) |
| Humidity | Not measured (typical basement levels) |
| Ventilation | Passive (no forced air) |
| Light Exposure | Minimal (enclosed space) |
| Geographic Region | New England, USA |

> [!TIP]
> The narrow temperature range (Δ4.5°F) limits temperature-voltage analysis but provides stable baseline conditions for drift characterization.

---

## 3. Calibration Notes

### 3.1 Voltage Sensor

The Shelly Plus Uni was used with **factory calibration** (no user adjustment).

**Known characteristics:**
- ESP32-based ADC with nominal 1100 mV reference
- Chip-to-chip Vref variation: 1000–1200 mV
- Temperature-dependent ADC drift (see Espressif documentation)
- Quantization: ~10 mV effective resolution

**For improved accuracy:**
- Apply eFuse calibration values if available
- Perform two-point calibration against a reference voltmeter
- Use external precision voltage reference

### 3.2 Temperature Sensor

Factory calibration assumed. No cross-reference against calibrated thermometer was performed.

**Recommended improvement:**
- Compare against NIST-traceable thermometer
- Note any offset for correction in analysis

---

## 4. Sampling Characteristics

### 4.1 Hourly Data

| Parameter | Value |
|:----------|:------|
| Method | Home Assistant min/max aggregation |
| Cadence | 1 sample/hour (aggregated) |
| Timezone | Local (EST/EDT) |
| Format | CSV with Date, Time, Min, Max columns |

### 4.2 High-Frequency Data

| Parameter | Value |
|:----------|:------|
| Method | State-change logging |
| Observed Cadence | ~3 seconds median |
| Mean Interval | ~10 seconds (gaps inflate average) |
| Timezone | UTC (ISO 8601) |
| Format | CSV with entity_id, state, last_changed |

**Gaps occur when:**
- Voltage is stable (no state change triggers logging)
- Network connectivity issues
- Sensor reboots (e.g., Eco Mode transition)

---

## 5. Replication Checklist

### 5.1 Hardware Setup

- [ ] **LiFePO₄ battery bank** — Any capacity (adjust endurance calculations accordingly)
- [ ] **Voltage sensor** — ≤10 mV resolution recommended
  - Examples: Shelly Plus Uni, INA226, Victron SmartShunt
- [ ] **Temperature sensor** — Co-located with battery
- [ ] **Data logger** — Home Assistant, Node-RED, or similar
- [ ] **Fusing** — Class T fuse at battery terminals

### 5.2 Configuration

- [ ] Connect voltage sensor to bus terminals (not individual cells)
- [ ] Enable state-change logging for high-frequency data
- [ ] Set up hourly min/max aggregation
- [ ] Configure temperature logging
- [ ] Document any firmware/mode changes (e.g., Eco Mode)
- [ ] Note sensor serial numbers for traceability

### 5.3 Data Collection

- [ ] Export hourly data weekly or monthly
- [ ] Export high-frequency data periodically (large files)
- [ ] Record environmental conditions (temperature, humidity if available)
- [ ] Log any system changes or anomalies

### 5.4 Analysis

- [ ] Run `scripts/lifepo4_analysis.py` or adapt to your data
- [ ] Apply MA-60s with **time-based** rolling (not fixed-sample)
- [ ] Report drift with explicit window specifications
- [ ] Document your methodology for reproducibility

---

## 6. Known Limitations

### 6.1 Measurement Limitations

| Limitation | Impact | Mitigation |
|:-----------|:-------|:-----------|
| Single-channel measurement | No per-cell visibility | Add per-cell sensing for definitive immunity confirmation |
| State-change logging | Misses stable periods | Use fixed-interval logging for spectral analysis |
| 10 mV ADC quantization | Limits fine detail | Higher-resolution ADC or smoothing (MA-60s) |
| No direct current measurement | SOC uncertainty | Add calibrated shunt for direct measurement |

### 6.2 Data Gaps

| Gap Type | Cause | Handling |
|:---------|:------|:---------|
| Stable voltage periods | State-change logging behavior | Expected; account in cadence calculations |
| Sensor reboots | Eco Mode, power loss | Note timestamps; exclude transition periods |
| Export delays | Manual export process | Establish regular export schedule |

### 6.3 Environmental Limitations

| Factor | Limitation | Impact |
|:-------|:-----------|:-------|
| Narrow temperature range | Δ4.5°F over study period | Limits temperature coefficient precision |
| No humidity data | Not measured | Cannot assess humidity effects |
| Single location | Basement only | Results may differ in other environments |

---

## 7. Extending This Study

### 7.1 Recommended Additions

| Enhancement | Benefit | Complexity |
|:------------|:--------|:-----------|
| Per-cell voltage monitoring | Confirms/refutes architectural immunity at cell level | Medium |
| DC current shunt | Direct parasitic draw measurement; eliminates SOC uncertainty | Low |
| Higher-resolution ADC | Reduces quantization noise | Medium |
| Fixed-interval logging | Eliminates gaps; enables FFT/spectral analysis | Low |
| Humidity sensor | Environmental correlation | Low |
| Multiple temperature points | Thermal gradient analysis | Low |

### 7.2 Priority Order

1. **DC current shunt** — Highest value, lowest complexity
2. **Fixed-interval logging** — Low effort, enables new analyses
3. **Per-cell voltage** — Definitive architectural immunity test
4. **Higher-resolution ADC** — Diminishing returns vs. complexity

### 7.3 Adapting for Different Hardware

If replicating with different hardware:

```python
# Update these in lifepo4_analysis.py

# File paths
VOLTAGE_FILE = 'path/to/your/voltage_data.csv'
TEMP_FILE = 'path/to/your/temperature_data.csv'

# Column names (adjust to your export format)
VOLTAGE_COL = 'voltage'  # or 'state', 'value', etc.
TIMESTAMP_COL = 'timestamp'  # or 'last_changed', 'datetime', etc.

# Date parsing (adjust format string)
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'  # or '%d/%m/%Y %H:%M', etc.

# Timezone handling
TIMEZONE = 'America/New_York'  # or 'UTC', 'Europe/London', etc.

# Stasis period (adjust to your monitoring timeline)
STASIS_START = '2025-11-22'
STASIS_END = '2026-02-21'
```

### 7.4 Sharing Your Results

If you replicate this study, please consider:

1. **Sharing your data** — Submit via Pull Request (see [CONTRIBUTING.md](../CONTRIBUTING.md))
2. **Opening a Discussion** — Share observations and findings
3. **Citing this study** — Use the provided citation format

---

## See Also

- [Methodology](methodology.md) — Analytical methods and definitions
- [Data Dictionary](../data/README.md) — Dataset documentation
- [FAQ](faq.md) — Common questions answered
- [CONTRIBUTING.md](../CONTRIBUTING.md) — How to contribute data
