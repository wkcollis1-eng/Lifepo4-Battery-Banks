# Methodology

This document describes the analytical methods, estimators, and definitions used in this study.

---

## Definitions

### MA-60s (Moving Average, 60 Seconds)

A trailing, **time-based** 60-second rolling mean applied to high-frequency voltage data:

```python
df['MA60'] = df['voltage'].rolling('60s', min_periods=1).mean()
```

**Key distinction:** This is a time-window average, not a fixed-sample-count average. It adapts to variable sampling cadence.

### Mid-Voltage

The arithmetic mean of hourly minimum and maximum voltage:

```
Mid = (Min + Max) / 2
```

### Spread

The difference between hourly maximum and minimum voltage:

```
Spread = Max - Min
```

**Important caveat:** This is a single-channel bus measurement. It reflects measurement noise and ADC behavior, **not** per-cell or per-block voltage divergence. To claim cell-level divergence, per-unit sensing would be required.

### Effective Draw vs. System Draw

- **Effective draw:** Parasitic current inferred from voltage drift during stasis (constant-load model)
- **System draw:** Actual instantaneous current, which varies with telemetry bursts (Wi-Fi, polling cycles)

The effective draw (~13–20 mA) is lower than peak system draw because it averages over duty cycles.

---

## Drift Estimation

### Method: OLS on Daily Mean Mid-Voltage

1. Compute daily mean of hourly mid-voltage
2. Fit ordinary least squares regression: `V = a + b·t`
3. Report slope `b` in mV/day

### Window Dependence

Drift rates are **window- and estimator-dependent** on a non-linear relaxation curve. The voltage decay follows an exponential-like approach to equilibrium, not a linear decline.

| Window | Period | Drift Rate | R² | Interpretation |
|--------|--------|------------|-----|----------------|
| Full stasis | Nov 22 → Jan 31 | −0.665 mV/day | 0.876 | Long-term average |
| Last 30 days | Jan 2 → Jan 31 | −0.165 mV/day | 0.132 | Near-equilibrium |

The 75% rate reduction indicates the system is approaching a stable storage state.

### Why Multiple Slopes?

Depending on:
- Window start/end dates
- Whether you use daily means, MA-60s means, or raw samples
- OLS vs. robust regression

...you may compute drift rates anywhere from ~0.16 to ~0.30 mV/day for late January. **This is not a contradiction**—it's expected behavior for a flattening curve.

**Recommended reporting:** Always state the window and estimator explicitly.

---

## MA-60s Noise Reduction

### Method

1. Apply time-based 60-second rolling mean to high-frequency voltage
2. Compute standard deviation of raw and smoothed series
3. Report reduction: `(1 - σ_MA60 / σ_raw) × 100%`

### Results

| Scope | Raw σ | MA-60s σ | Reduction |
|-------|-------|----------|-----------|
| Global (328k samples) | 10.38 mV | 5.98 mV | 42.5% |
| Segment range | — | — | 42–50% |

**Report as a band (42–50%)** rather than a single number because reduction varies with:
- Sampling regularity (gaps reduce smoothing effectiveness)
- Short-term interference environment

---

## Temperature-Voltage Regression

### Two-Factor Model

To isolate temperature effects from monotonic drift:

```
V = a + b₁·t + b₂·T + ε
```

Where:
- `t` = days from start
- `T` = temperature (°F)
- `b₁` = residual drift rate
- `b₂` = temperature coefficient

### Results

| Coefficient | Value | SE | Interpretation |
|-------------|-------|-----|----------------|
| b₂ (temperature) | +1.01 mV/°F | 0.27 | System-level sensitivity |
| b₁ (residual drift) | −0.115 mV/day | 0.026 | After temperature control |

### Interpretation Caveats

This coefficient is **system-level**, not pure LiFePO₄ OCV temperature behavior. It includes:
- Pack electrochemistry
- ADC reference drift
- Wiring/contact resistance changes
- Enclosure thermal gradients

The temperature effect is **second-order** relative to monotonic drift for endurance inference, but matters for:
- Seasonal extrapolation
- Residual fitting quality
- Comparing measurements across different ambient conditions

---

## Architectural Immunity Assessment

### What We Can Claim

From bus-level voltage monitoring, we observe:
- No growing instability signatures
- Trendless anomalies (no systematic pattern)
- Stable detrended variance over 94+ days

### What We Cannot Claim (Without Additional Sensing)

- Per-cell SOC equality
- Per-block current sharing
- Individual cell degradation rates

The "architectural immunity" hypothesis is **supported but not proven** by this data. Definitive confirmation would require per-unit voltage or current sensing.

---

## References

1. Wang et al., *Batteries* 2023, "State of Charge Estimation of LiFePO₄ in Various Temperature Scenarios" — [DOI:10.3390/batteries9010043](https://doi.org/10.3390/batteries9010043)

2. Espressif Developer Portal, "Comparing ADC Performance of Espressif SoCs" — [Link](https://developer.espressif.com/blog/2025/08/adc-performance/)
