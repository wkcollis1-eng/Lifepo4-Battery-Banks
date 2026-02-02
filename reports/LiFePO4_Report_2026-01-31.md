# LiFePO₄ Battery Bank: Technical Report

**Data through:** January 31, 2026  
**Published:** February 1, 2026  
**Version:** 2026-01-31  

---

## Executive Summary

This report extends the analysis of a DIY 12V 500Ah LiFePO₄ battery bank with 94+ days of continuous voltage monitoring. Key findings:

1. **Architectural immunity confirmed:** No evidence of cell divergence at bus potential; spread inflation correlates with measurement-regime changes, not electrochemical imbalance.

2. **Drift approaching equilibrium:** Rate reduced from −0.665 mV/day (full stasis) to −0.165 mV/day (last 30 days) — a 75% reduction indicating system stabilization.

3. **MA-60s effective:** Time-based 60-second rolling mean reduces apparent noise by 42–50% depending on segment.

4. **Temperature effect detectable:** System-level coefficient of +1.0 ± 0.3 mV/°F (includes measurement chain effects).

5. **Storage viability excellent:** Projected 7–10 months to 80% SOC at ~13–20 mA effective parasitic draw.

---

## 1. Data Coverage

| Dataset | File | Coverage | Records |
|---------|------|----------|---------|
| Hourly voltage | `combined_output.csv` | Oct 29, 2025 → Jan 31, 2026 | 2,222 |
| Hourly temperature | `combined_temperature.csv` | Dec 29, 2025 → Jan 31, 2026 | 816 |
| High-frequency voltage | Release assets | Dec 26, 2025 → Feb 1, 2026 | ~328,000 |

### Derived Series

- **Mid-voltage:** `(Min + Max) / 2`
- **Spread:** `Max - Min`
- **Daily mean:** Average of hourly mid-voltage per day
- **MA-60s:** Time-based trailing 60-second rolling mean

---

## 2. Methodology

### 2.1 Drift Estimation

OLS regression on daily mean mid-voltage:

```
V_d = a + b·t_d + ε_d
```

Where `t_d` is days from interval start. Slope `b` reported in mV/day.

**Window dependence:** Drift rates vary with window selection on a non-linear relaxation curve. We report both long-window (stasis-scale) and short-window (equilibrium-scale) values.

### 2.2 MA-60s

Time-based trailing mean:

```python
MA_60s(t) = voltage.rolling('60s', min_periods=1).mean()
```

This adapts to variable sampling cadence (not a fixed sample count).

### 2.3 Temperature Model

Two-factor regression isolating temperature from monotonic drift:

```
V = a + b₁·t + b₂·T + ε
```

---

## 3. Results: Drift Analysis

### 3.1 Full Stasis Period (Nov 22 → Jan 31)

| Metric | Value |
|--------|-------|
| Days | 70 |
| OLS drift rate | −0.665 mV/day |
| Total change | −46.6 mV |
| R² | 0.876 |
| Detrended residual σ | 5.17 mV |

### 3.2 Last 30 Days (Jan 2 → Jan 31)

| Metric | Value |
|--------|-------|
| Days | 29 |
| OLS drift rate | −0.165 mV/day |
| Total change | −4.8 mV |
| R² | 0.132 |
| p-value | 0.048 |

### 3.3 Drift Flattening

**Rate reduction:** 75.1%

This is the clearest quantitative evidence that the bank is approaching an equilibrium storage state rather than continuing linear decline.

**Note:** Late-January drift is plausibly 0.16–0.30 mV/day depending on windowing and estimator choice. This is expected for a flattening curve.

---

## 4. Results: Eco Mode Effect

Eco Mode was enabled on the Shelly Plus Uni at Dec 23, 2025 ~15:40 local time. This reduces device power consumption but triggers a reboot.

### ±48h Window Analysis

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Mean mid-voltage | — | — | −4.38 mV |
| Mean min-voltage | — | — | −7.71 mV |
| Mean spread | 28.75 mV | 35.42 mV | +6.67 mV |

**Interpretation:** Spread inflation is a measurement-regime artifact, not electrochemical divergence.

---

## 5. Results: MA-60s Analysis

### 5.1 Global Performance (328,556 samples)

| Metric | Value |
|--------|-------|
| Raw σ | 10.38 mV |
| MA-60s σ | 5.98 mV |
| Noise reduction | 42.5% |

### 5.2 Minute-Bucket Diagnostics

| Metric | Value |
|--------|-------|
| Mean within-minute σ | 9.01 mV |
| Between-minute σ | 5.98 mV |
| Mean minute min-max | 22.88 mV |
| Mean samples/minute | 8.96 |

### 5.3 Segment Performance

| Segment | Samples | Raw σ | MA-60s σ | Reduction |
|---------|---------|-------|----------|-----------|
| Dec 26 – Jan 08 | 33,400 | 9.88 mV | 4.96 mV | 49.8% |
| Jan 09 – Jan 18 | 120,926 | 10.19 mV | 5.86 mV | 42.5% |
| Jan 19 – Jan 27 | 116,499 | 9.89 mV | 4.90 mV | 50.4% |
| Jan 28 – Jan 31 | 54,781 | 10.47 mV | 5.95 mV | 43.2% |

**Reportable claim:** MA-60s reduces apparent noise by **42–50%** depending on cadence regularity and interference environment.

### 5.4 Extreme Minutes

Only 3 minutes exceed 60 mV spread across the full record:
- 2026-01-14 02:13 UTC
- 2026-01-20 18:35 UTC
- 2026-01-23 08:37 UTC

These are rare EMI/ADC artifacts with no trend growth.

---

## 6. Results: Temperature-Voltage Relationship

### 6.1 Dataset

- Matched hourly points: 816
- Temperature range: 51.5°F → 55.95°F (Δ4.45°F)
- Mean temperature: 54.12°F
- Daily swing: 0.6°F – 2.0°F (mean 1.40°F)

### 6.2 Naive Regression (V vs T only)

| Coefficient | Value |
|-------------|-------|
| Temperature | +1.79 mV/°F |
| R² | 0.082 |

### 6.3 Two-Factor Regression (Time + Temperature)

| Coefficient | Value | SE |
|-------------|-------|-----|
| Residual drift (b₁) | −0.115 mV/day | 0.026 |
| Temperature (b₂) | +1.01 mV/°F | 0.27 |
| R² | 0.103 | — |

**Interpretation:** This is a **system-level** coefficient (pack + measurement chain), not pure LiFePO₄ OCV behavior. It is second-order relative to monotonic drift but matters for seasonal extrapolation.

---

## 7. Results: SOC & Storage Endurance

### 7.1 Parasitic Current Model

Time elapsed (Nov 4 00:00 → Jan 31 23:00): **2,135 hours**

| Assumed Draw | Ah Lost | Implied SOC |
|--------------|---------|-------------|
| 13.3 mA | 28.4 Ah | ~94.3% |
| 17 mA | 36.3 Ah | ~92.7% |
| 20 mA | 42.7 Ah | ~91.5% |

### 7.2 Time to 80% SOC

| Assumed Draw | Days | Months |
|--------------|------|--------|
| 13.3 mA | 313 | 10.3 |
| 17 mA | 245 | 8.1 |
| 20 mA | 208 | 6.9 |

**Reportable claim:** Projected 7–10 months from 100% to 80% SOC at an effective draw of ~13–20 mA inferred from stasis behavior.

**Caveat:** System draw may be higher during telemetry bursts (Wi-Fi polling). Direct bus-current measurement is the highest-value next step.

---

## 8. Late-January Stability

Last 7 days ending Jan 31, 2026:

| Metric | Value |
|--------|-------|
| Mean mid-voltage | 13.234 V |
| Mid σ | 5.43 mV |
| Mean spread | 45.0 mV |

Stability remains excellent with no degradation signals.

---

## 9. Recommendations

### 9.1 Highest-Value Next Step

**Direct 24–72h bus-current measurement** using a calibrated shunt/meter with mA resolution. This collapses SOC/endurance uncertainty in the flat-OCV region.

### 9.2 Optional Improvements

1. **Per-cell voltage sensing** — Would confirm architectural immunity at cell level
2. **Temperature compensation** — Apply `V_corr = V - β(T - T₀)` with β ≈ 1.0 mV/°F
3. **Fixed-interval logging** — Enables spectral analysis; eliminates gaps

---

## 10. Conclusions

1. **Architectural immunity holds** — No evidence of divergence at bus potential over 94+ days
2. **Storage viability excellent** — Drift flattening indicates equilibrium approach
3. **MA-60s effective** — 42–50% noise reduction for research-usable stability
4. **Temperature effect small but real** — System-level coefficient ~1 mV/°F
5. **No degradation signals** — System health remains excellent

---

## References

1. Wang et al., *Batteries* 2023, "State of Charge Estimation of LiFePO₄ in Various Temperature Scenarios" — [DOI:10.3390/batteries9010043](https://doi.org/10.3390/batteries9010043)

2. Espressif Developer Portal (2025), "Comparing ADC Performance of Espressif SoCs" — [Link](https://developer.espressif.com/blog/2025/08/adc-performance/)

3. ESP-IDF Programming Guide, "ESP32-S2 ADC Calibration" — [Link](https://docs.espressif.com/projects/esp-idf/en/v4.4.8/esp32s2/api-reference/peripherals/adc.html)
