# Methodology

This document provides detailed methodology for the LiFePO₄ Battery Bank Architectural Immunity Study.

## Table of Contents

1. [Study Design](#study-design)
2. [Equipment Specifications](#equipment-specifications)
3. [Measurement Protocols](#measurement-protocols)
4. [Data Collection](#data-collection)
5. [Calibration Procedures](#calibration-procedures)
6. [Statistical Analysis](#statistical-analysis)
7. [Uncertainty Analysis](#uncertainty-analysis)
8. [Key Equations](#key-equations)

---

## Study Design

### Objectives

1. **Primary:** Determine if mixed-brand LiFePO₄ cells in parallel achieve uniform voltage distribution
2. **Secondary:** Quantify long-term stability and drift rates
3. **Tertiary:** Validate "architectural immunity" hypothesis

### Hypothesis

> In a purely parallel topology with low bus-bar resistance (<1mΩ), the architecture forces cells to behave as a monolithic unit, regardless of manufacturing differences between brands.

### Study Parameters

| Parameter | Value |
|-----------|-------|
| Monitoring Duration | 73+ days |
| Sampling Interval | 60 seconds (raw), 1 hour (aggregated) |
| Temperature Range | 55-70°F (typical basement conditions) |
| Load Conditions | Mixed (standby + periodic loads) |

---

## Equipment Specifications

### Battery Bank

| Component | Specification | Quantity |
|-----------|--------------|----------|
| LIPULS 12V 100Ah LiFePO₄ | Built-in 100A BMS | 3 |
| Cyclenbatt 12V 100Ah LiFePO₄ | Built-in 100A BMS | 2 |
| Interconnects | 2 AWG pure copper, 12" length | 10 |
| Bus Bar | Copper, <1mΩ resistance | 2 |

### Monitoring Equipment

| Equipment | Model | Specifications |
|-----------|-------|----------------|
| Voltage Sensor | Shelly Plus Uni | ESP32-based, Wi-Fi, 0-30V DC input |
| ADC Resolution | Internal | ~1mV effective resolution |
| Temperature Sensor | DS18B20 | ±0.5°C accuracy |
| Data Logger | Home Assistant | SQLite database, 60s polling |

### Sensor Calibration

The Shelly Plus Uni was calibrated against a Fluke 87V multimeter:

| Reference (Fluke) | Shelly Reading | Offset |
|-------------------|----------------|--------|
| 13.280V | 13.278V | -2mV |
| 12.800V | 12.799V | -1mV |
| 12.000V | 12.001V | +1mV |

**Conclusion:** Offset within ±2mV, considered negligible for this study.

---

## Measurement Protocols

### Voltage Monitoring

1. **Sensor Placement:** Directly on main bus bar terminals
2. **Sampling Rate:** 60-second intervals
3. **Aggregation:** Hourly min/max values stored
4. **Data Validation:** Automated range checks (10V-15V)

### Temperature Logging

1. **Sensor Placement:** Ambient basement air, 3 feet from battery bank
2. **Sampling Rate:** 5-minute intervals
3. **Purpose:** Correlation analysis with voltage drift

### Isolation Tests

To measure true parasitic load:

1. Disconnect inverter at DC terminals
2. Wait 24 hours for stabilization
3. Measure voltage decay rate
4. Calculate parasitic current: `I = C × (dV/dt) / (V × k)`

### Discharge Tests

Full capacity verification protocol:

1. Charge to 100% SOC (14.2V, taper to <1A)
2. Rest 24 hours
3. Discharge at constant power (440W average)
4. Record total Wh and time
5. Calculate usable Ah: `Ah = Wh / V_avg`

---

## Data Collection

### Raw Data Structure

**Primary dataset:** `combined_output.csv`

```csv
Timestamp,Voltage_Min,Voltage_Max
2025-10-26 00:00:00,13.271,13.282
```

- **Timestamp:** UTC, ISO 8601 format
- **Voltage_Min:** Minimum reading in the hour
- **Voltage_Max:** Maximum reading in the hour

### Data Quality

| Metric | Value |
|--------|-------|
| Total Hours | 1,752+ |
| Missing Data Points | <0.5% |
| Outlier Rate | <0.1% (removed via 3σ filter) |

### Data Pipeline

```
Shelly Plus Uni → MQTT → Home Assistant → SQLite → CSV Export → Python Analysis
```

---

## Calibration Procedures

### Voltage Calibration

1. **Reference:** Fluke 87V True-RMS Multimeter (calibrated)
2. **Method:** 3-point calibration at 12.0V, 12.8V, 13.3V
3. **Frequency:** Verified monthly
4. **Acceptance Criteria:** ±5mV of reference

### Temperature Calibration

1. **Reference:** Mercury thermometer (±0.1°C)
2. **Method:** Ice bath and ambient comparison
3. **Frequency:** Once at study start
4. **Acceptance Criteria:** ±0.5°C

### Sensor Eco Mode Compensation

The Shelly Plus Uni exhibits a -5.8mV offset in Eco Mode:

| Mode | Typical Reading (100% SOC) |
|------|---------------------------|
| Normal | 13.280V |
| Eco Mode | 13.274V |

**All analysis corrects for this offset when Eco Mode is active.**

---

## Statistical Analysis

### Software

- Python 3.10+
- pandas 2.0+
- numpy 1.24+
- scipy 1.10+
- matplotlib 3.7+

### Key Analyses

#### 1. Descriptive Statistics

```python
mean_voltage = df['Voltage_Avg'].mean()
std_voltage = df['Voltage_Avg'].std()
spread = df['Voltage_Max'] - df['Voltage_Min']
```

#### 2. Trend Analysis

Linear regression for drift detection:

```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
```

#### 3. Temperature Correlation

Pearson correlation coefficient:

```python
correlation = df['Voltage_Avg'].corr(df['Temperature'])
```

#### 4. Moving Average Analysis

60-second moving average for noise reduction:

```python
df['MA_60s'] = df['Voltage'].rolling(window=60, center=True).mean()
```

### Significance Criteria

| Test | Threshold |
|------|-----------|
| Trend p-value | p < 0.05 for significance |
| Correlation | r > 0.5 for strong correlation |
| Outliers | >3σ from mean |

---

## Uncertainty Analysis

### Sources of Uncertainty

| Source | Magnitude | Type |
|--------|-----------|------|
| ADC quantization | ±0.5mV | Random |
| Temperature coefficient | ±0.21mV/°F | Systematic |
| Sensor offset | ±2mV | Systematic |
| EMI interference | ±3mV (occasional) | Random |

### Combined Uncertainty

Using root-sum-square method:

```
u_combined = √(u_ADC² + u_temp² + u_offset²)
u_combined = √(0.5² + 1.0² + 2.0²) = 2.3mV
```

### Confidence Intervals

All key metrics reported with 95% confidence intervals:

```python
from scipy import stats
ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=sem)
```

---

## Key Equations

### Peukert's Law

```
t = C / I^k
```

Where:
- t = discharge time (hours)
- C = rated capacity (Ah)
- I = discharge current (A)
- k = Peukert exponent

**Measured k = 1.003 ± 0.02** (ideal = 1.00)

### State of Charge (Voltage Method)

For LiFePO₄ at rest (24h+):

| Voltage (12V system) | SOC |
|---------------------|-----|
| 13.60V | 100% |
| 13.40V | 99% |
| 13.30V | 90% |
| 13.20V | 70% |
| 13.10V | 40% |
| 13.00V | 30% |
| 12.80V | 20% |
| 12.00V | 10% |
| 10.00V | 0% |

### Self-Discharge Rate

```
Monthly_Loss_% = (I_parasitic × 24 × 30) / (C_Ah × 1000) × 100
```

**Measured:** 0.15%/month at 20-25mA parasitic load

### Thermal Voltage Coefficient

```
dV/dT = ΔV / ΔT
```

**Measured:** 0.21 mV/°F (lower than typical 0.3-0.5 mV/°F)

---

## References

1. Peukert, W. (1897). "Über die Abhängigkeit der Kapazität von der Entladestromstärke bei Bleiakkumulatoren"
2. LiFePO₄ Voltage-SOC curves: BatteryUniversity.com
3. Shelly Plus Uni specifications: Shelly Documentation
4. Statistical methods: NIST/SEMATECH e-Handbook of Statistical Methods

---

*Last updated: January 10, 2026*
