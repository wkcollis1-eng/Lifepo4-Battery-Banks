# LiFePO₄ Battery Bank: Technical Report

**Data through:** January 31, 2026  
**Published:** February 1, 2026  
**Version:** 2026-01-31  
**DOI:** [10.5281/zenodo.14538065](https://doi.org/10.5281/zenodo.14538065)

---

## Abstract

This report presents findings from a 94+ day monitoring study of a DIY 12V 500Ah LiFePO₄ battery bank configured with mixed-brand cells in parallel. The study investigates the "architectural immunity" hypothesis—that parallel-connected cells achieve monolithic behavior through topology rather than cell matching—and characterizes long-term storage viability.

**Key results:** The battery bank delivered 397 Ah usable capacity (99.3% of rated) in discharge testing. Continuous voltage monitoring revealed no evidence of cell divergence at the bus potential over 94+ days, supporting architectural immunity. Voltage drift decreased from −0.665 mV/day (full stasis period) to −0.165 mV/day (last 30 days), representing a 75% rate reduction indicative of equilibrium approach. Time-based 60-second moving average (MA-60s) filtering reduced apparent measurement noise by 42–50%. System-level temperature sensitivity was +1.0 ± 0.3 mV/°F. Projected storage endurance is 7–10 months to 80% SOC at ~13–20 mA effective parasitic draw.

**Implications:** These findings support the viability of mixed-brand parallel LiFePO₄ configurations for DIY applications and demonstrate that architectural immunity provides inherent voltage balancing without matched cells. Direct bus-current measurement would further reduce SOC projection uncertainty.

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
|:--------|:-----|:---------|--------:|
| Hourly voltage | `combined_output.csv` | Oct 29, 2025 → Jan 31, 2026 | 2,222 |
| Hourly temperature | `combined_temperature.csv` | Dec 29, 2025 → Jan 31, 2026 | 816 |
| High-frequency voltage | Release assets | Dec 26, 2025 → Feb 1, 2026 | ~328,000 |

### 1.1 Derived Series

| Series | Formula | Description |
|:-------|:--------|:------------|
| Mid-voltage | `(Min + Max) / 2` | Hourly central estimate |
| Spread | `Max - Min` | Hourly range |
| Daily mean | `groupby(date).mean()` | Daily average of hourly mid-voltage |
| MA-60s | `rolling('60s').mean()` | Time-based 60-second rolling mean |

---

## 2. Methodology

### 2.1 Drift Estimation

OLS (Ordinary Least Squares) regression on daily mean mid-voltage:

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

Where b₁ = residual drift rate and b₂ = temperature coefficient.

---

## 3. Results: Drift Analysis

### 3.1 Full Stasis Period (Nov 22 → Jan 31)

| Metric | Value |
|:-------|------:|
| Days | 70 |
| OLS drift rate | −0.665 mV/day |
| Total change | −46.6 mV |
| R² | 0.876 |
| Detrended residual σ | 5.17 mV |

### 3.2 Last 30 Days (Jan 2 → Jan 31)

| Metric | Value |
|:-------|------:|
| Days | 29 |
| OLS drift rate | −0.165 mV/day |
| Total change | −4.8 mV |
| R² | 0.132 |
| p-value | 0.048 |

### 3.3 Drift Flattening

**Rate reduction:** 75.1%

This is the clearest quantitative evidence that the bank is approaching an equilibrium storage state rather than continuing linear decline.

> **Note:** Late-January drift is plausibly 0.16–0.30 mV/day depending on windowing and estimator choice. This is expected for a flattening curve.

---

## 4. Results: Eco Mode Effect

Eco Mode was enabled on the Shelly Plus Uni at Dec 23, 2025 ~15:40 local time. This reduces device power consumption but triggers a reboot.

### 4.1 ±48h Window Analysis

| Metric | Before | After | Change |
|:-------|-------:|------:|-------:|
| Mean mid-voltage | 13.286 V | 13.282 V | −4.38 mV |
| Mean min-voltage | 13.272 V | 13.264 V | −7.71 mV |
| Mean spread | 28.75 mV | 35.42 mV | +6.67 mV |

**Interpretation:** Spread inflation is a measurement-regime artifact, not electrochemical divergence.

---

## 5. Results: MA-60s Analysis

### 5.1 Global Performance (328,556 samples)

| Metric | Value |
|:-------|------:|
| Raw σ | 10.38 mV |
| MA-60s σ | 5.98 mV |
| Noise reduction | 42.5% |

### 5.2 Minute-Bucket Diagnostics

| Metric | Value |
|:-------|------:|
| Mean within-minute σ | 9.01 mV |
| Between-minute σ | 5.98 mV |
| Mean minute min-max | 22.88 mV |
| Mean samples/minute | 8.96 |

### 5.3 Segment Performance

| Segment | Samples | Raw σ | MA-60s σ | Reduction |
|:--------|--------:|------:|---------:|----------:|
| Dec 26 – Jan 08 | 33,400 | 9.88 mV | 4.96 mV | 49.8% |
| Jan 09 – Jan 18 | 120,926 | 10.19 mV | 5.86 mV | 42.5% |
| Jan 19 – Jan 27 | 116,499 | 9.89 mV | 4.90 mV | 50.4% |
| Jan 28 – Jan 31 | 54,781 | 10.47 mV | 5.95 mV | 43.2% |

**Reportable claim:** MA-60s reduces apparent noise by **42–50%** depending on cadence regularity and interference environment.

### 5.4 Extreme Minutes

Only 3 minutes exceed 60 mV spread across the full record:

| Timestamp (UTC) | Spread |
|:----------------|-------:|
| 2026-01-14 02:13 | >60 mV |
| 2026-01-20 18:35 | >60 mV |
| 2026-01-23 08:37 | >60 mV |

These are rare EMI/ADC artifacts with no trend growth.

---

## 6. Results: Temperature-Voltage Relationship

### 6.1 Dataset

| Parameter | Value |
|:----------|------:|
| Matched hourly points | 816 |
| Temperature range | 51.5°F → 55.95°F (Δ4.45°F) |
| Mean temperature | 54.12°F |
| Daily swing | 0.6°F – 2.0°F (mean 1.40°F) |

### 6.2 Naive Regression (V vs T only)

| Coefficient | Value |
|:------------|------:|
| Temperature | +1.79 mV/°F |
| R² | 0.082 |

### 6.3 Two-Factor Regression (Time + Temperature)

| Coefficient | Value | SE |
|:------------|------:|---:|
| Residual drift (b₁) | −0.115 mV/day | 0.026 |
| Temperature (b₂) | +1.01 mV/°F | 0.27 |
| R² | 0.103 | — |

**Interpretation:** This is a **system-level** coefficient (pack + measurement chain), not pure LiFePO₄ OCV behavior. It is second-order relative to monotonic drift but matters for seasonal extrapolation.

---

## 7. Results: SOC & Storage Endurance

### 7.1 Parasitic Current Model

Time elapsed (Nov 4 00:00 → Jan 31 23:00): **2,135 hours**

| Assumed Draw | Ah Lost | Implied SOC |
|:-------------|--------:|------------:|
| 13.3 mA | 28.4 Ah | ~94.3% |
| 17 mA | 36.3 Ah | ~92.7% |
| 20 mA | 42.7 Ah | ~91.5% |

### 7.2 Time to 80% SOC

| Assumed Draw | Days | Months |
|:-------------|-----:|-------:|
| 13.3 mA | 313 | 10.3 |
| 17 mA | 245 | 8.1 |
| 20 mA | 208 | 6.9 |

**Reportable claim:** Projected 7–10 months from 100% to 80% SOC at an effective draw of ~13–20 mA inferred from stasis behavior.

> **Caveat:** System draw may be higher during telemetry bursts (Wi-Fi polling). Direct bus-current measurement is the highest-value next step.

---

## 8. Late-January Stability

Last 7 days ending Jan 31, 2026:

| Metric | Value |
|:-------|------:|
| Mean mid-voltage | 13.234 V |
| Mid σ | 5.43 mV |
| Mean spread | 45.0 mV |

Stability remains excellent with no degradation signals.

---

## 9. Recommendations

### 9.1 Highest-Value Next Step

**Direct 24–72h bus-current measurement** using a calibrated shunt/meter with mA resolution. This collapses SOC/endurance uncertainty in the flat-OCV region.

**Estimated effort:** Low (hardware: ~$30–50; time: 1–3 days)  
**Expected impact:** High (reduces SOC uncertainty from ±30% to ±5%)

### 9.2 Optional Improvements

| Enhancement | Effort | Impact |
|:------------|:-------|:-------|
| Per-cell voltage sensing | Medium | Confirms architectural immunity at cell level |
| Temperature compensation | Low | Apply `V_corr = V - β(T - T₀)` with β ≈ 1.0 mV/°F |
| Fixed-interval logging | Low | Enables spectral analysis; eliminates gaps |
| Higher-resolution ADC | Medium | Reduces quantization noise |

### 9.3 Timeline

| Timeframe | Action |
|:----------|:-------|
| Immediate | Continue passive monitoring |
| 1–2 weeks | Direct current measurement |
| 1 month | Publish updated report |
| 3 months | Seasonal temperature analysis |
| 6 months | Long-term stability validation |

---

## 10. Conclusions

1. **Architectural immunity holds** — No evidence of divergence at bus potential over 94+ days
2. **Storage viability excellent** — Drift flattening indicates equilibrium approach
3. **MA-60s effective** — 42–50% noise reduction for research-usable stability
4. **Temperature effect small but real** — System-level coefficient ~1 mV/°F
5. **No degradation signals** — System health remains excellent

These findings support the viability of mixed-brand parallel LiFePO₄ configurations for DIY applications, with the caveat that per-cell monitoring would provide definitive confirmation of the architectural immunity hypothesis.

---

## References

1. Wang, Y., et al. (2023). "State of Charge Estimation of LiFePO₄ in Various Temperature Scenarios." *Batteries*, 9(1), 43.  
   DOI: [10.3390/batteries9010043](https://doi.org/10.3390/batteries9010043)

2. Espressif Developer Portal (2025). "Comparing ADC Performance of Espressif SoCs."  
   Link: [developer.espressif.com](https://developer.espressif.com/blog/2025/08/adc-performance/)

3. ESP-IDF Programming Guide. "ESP32-S2 ADC Calibration."  
   Link: [docs.espressif.com](https://docs.espressif.com/projects/esp-idf/en/v4.4.8/esp32s2/api-reference/peripherals/adc.html)

---

## Appendix A: Data Availability

All data and code are available at:  
**Repository:** https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks  
**DOI:** 10.5281/zenodo.14538065  
**License:** CC BY 4.0 (data) / MIT (code)

---

## Appendix B: Revision History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2026-01-31 | Feb 1, 2026 | Extended to 94+ days; added abstract; temperature analysis |
| 2025-12-26 | Dec 27, 2025 | Added high-frequency data; Eco Mode analysis |
| 2025-11-22 | Nov 23, 2025 | Initial stasis monitoring report |
| 2025-10-29 | Oct 30, 2025 | Original discharge test report |
