# Replication Protocol

This document provides the hardware configuration, calibration notes, and environmental conditions necessary to replicate or extend this study.

---

## Hardware Configuration

### Battery Bank

| Component | Specification |
|-----------|---------------|
| Chemistry | LiFePO₄ (Lithium Iron Phosphate) |
| Configuration | 4S (4 cells in series) × parallel blocks |
| Nominal Voltage | 12.8V (3.2V/cell × 4) |
| Capacity | 500Ah nominal |
| Brands | Mixed (architectural immunity test) |
| BMS | Yes (cell-level protection) |

### Voltage Monitoring

| Component | Specification |
|-----------|---------------|
| Sensor | Shelly Plus Uni |
| Input | DC voltage (0–30V range) |
| Resolution | ~10 mV (ADC-limited) |
| Connection | Direct to bus terminals |
| Firmware | Stock (Eco Mode enabled Dec 23, 2025) |

**Note on Eco Mode:** Shelly Eco Mode reduces power consumption but triggers a device reboot when toggled. The transition on Dec 23, 2025 ~15:40 local correlates with observed spread changes.

### Data Logging

| Component | Specification |
|-----------|---------------|
| Platform | Home Assistant |
| Database | InfluxDB (optional; SQLite default) |
| Logging Mode | State-change only (no fixed polling) |
| Export Format | CSV via History panel |

### Temperature Sensor

| Component | Specification |
|-----------|---------------|
| Type | Generic temperature sensor |
| Location | Basement, ~3 ft from battery bank |
| Added | Dec 29, 2025 |

---

## Environmental Conditions

| Parameter | Value |
|-----------|-------|
| Location | Basement (below grade) |
| Temperature Range | 51.5°F – 55.95°F (Dec 29 – Jan 31) |
| Humidity | Not measured (typical basement levels) |
| Ventilation | Passive (no forced air) |
| Light Exposure | Minimal (enclosed space) |

---

## Calibration Notes

### Voltage Sensor

The Shelly Plus Uni was used with **factory calibration** (no user adjustment). Known characteristics:

- ESP32-based ADC with nominal 1100 mV reference
- Chip-to-chip Vref variation: 1000–1200 mV
- Temperature-dependent ADC drift (see Espressif documentation)

**For improved accuracy:** Consider applying eFuse calibration values if available, or perform a two-point calibration against a reference voltmeter.

### Temperature Sensor

Factory calibration assumed. No cross-reference against calibrated thermometer was performed.

---

## Sampling Characteristics

### Hourly Data

- **Method:** Home Assistant aggregates min/max over each hour
- **Cadence:** 1 sample/hour (aggregated)
- **Timezone:** Local (EST/EDT)

### High-Frequency Data

- **Method:** State-change logging (new record only when voltage changes)
- **Observed Cadence:** ~3 seconds median
- **Gaps:** Occur when voltage is stable (no state change) or during network issues
- **Timezone:** UTC (ISO 8601)

---

## Replication Checklist

To replicate this study:

1. **Hardware**
   - [ ] LiFePO₄ battery bank (any capacity; adjust endurance calculations)
   - [ ] Voltage sensor with ≤10 mV resolution
   - [ ] Temperature sensor (co-located)
   - [ ] Data logger (Home Assistant, Node-RED, or similar)

2. **Configuration**
   - [ ] Connect voltage sensor to bus terminals
   - [ ] Enable state-change logging (for high-frequency data)
   - [ ] Set up hourly min/max aggregation
   - [ ] Note any firmware/mode changes (e.g., Eco Mode)

3. **Data Collection**
   - [ ] Export hourly data weekly/monthly
   - [ ] Export high-frequency data periodically (large files)
   - [ ] Record environmental conditions

4. **Analysis**
   - [ ] Run `scripts/lifepo4_analysis.py` or adapt to your data
   - [ ] Apply MA-60s with time-based rolling (not fixed-sample)
   - [ ] Report drift with explicit windows

---

## Known Limitations

1. **Single-channel measurement:** Bus voltage only; no per-cell sensing
2. **State-change logging:** Misses periods of stable voltage
3. **ADC quantization:** 10 mV resolution limits fine detail
4. **No direct current measurement:** Parasitic draw is inferred, not measured

---

## Extending This Study

### Recommended Additions

| Enhancement | Benefit |
|-------------|---------|
| Per-cell voltage monitoring | Confirms/refutes architectural immunity at cell level |
| DC current shunt | Direct parasitic draw measurement; eliminates SOC uncertainty |
| Higher-resolution ADC | Reduces quantization noise |
| Fixed-interval logging | Eliminates gaps; enables FFT/spectral analysis |

### If Replicating with Different Hardware

- Adjust voltage/temperature column names in analysis script
- Verify timezone handling (UTC vs. local)
- Check sensor resolution and adjust noise expectations accordingly
