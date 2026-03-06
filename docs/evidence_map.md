# 🗺️ Evidence Map

This document maps each key claim to its supporting data, analysis code, and output figure/table.

---

## Contents

- [How to Read This Map](#how-to-read-this-map)
- [Quick Reference Table](#quick-reference-table)
- [Core Claims](#core-claims)
  - [1. Usable Capacity: 397 Ah (99.3%)](#1-usable-capacity-397-ah-993)
  - [2. Full Stasis Drift: −0.665 mV/day](#2-full-stasis-drift-0665-mvday)
  - [3. Last 30-Day Drift: −0.165 mV/day](#3-last-30-day-drift-0165-mvday)
  - [4. MA-60s Noise Reduction: 42–50%](#4-ma-60s-noise-reduction-4250)
  - [5. Temperature Coefficient: +1.0 ± 0.3 mV/°F](#5-temperature-coefficient-10--03-mvf)
  - [6. Eco Mode Spread Shift](#6-eco-mode-spread-shift)
  - [7. Storage Endurance: 7–10 Months](#7-storage-endurance-710-months)
  - [8. Architectural Immunity](#8-architectural-immunity-no-cell-divergence)

---

## How to Read This Map

Each claim entry contains:

| Column | Description |
|:-------|:------------|
| **Claim** | The assertion made in the report/README |
| **Data** | Source file(s) in `data/` |
| **Code** | Function/section in `scripts/lifepo4_analysis.py` |
| **Output** | Figure or table that visualizes the result |
| **Report Section** | Location in technical report |

> [!TIP]
> Use this map to verify any claim by tracing it back to source data and reproducible code.

---

## Quick Reference Table

| # | Claim | Primary Figure | Data File | Code Section |
|:-:|:------|:---------------|:----------|:-------------|
| 1 | 397 Ah capacity | — | Discharge logs | Manual |
| 2 | −0.665 mV/day drift | fig1, fig5 | combined_output.csv | DRIFT ANALYSIS |
| 3 | 75% rate reduction | fig5 | combined_output.csv | DRIFT ANALYSIS |
| 4 | 42–50% MA-60s reduction | fig2, fig6 | High-freq (releases) | MA-60 SECONDS |
| 5 | +1.0 mV/°F temp coeff | fig4 | combined_output + temp | TEMPERATURE-VOLTAGE |
| 6 | Eco Mode spread shift | fig3 | combined_output.csv | ECO MODE |
| 7 | 7–10 mo to 80% SOC | fig7 | Derived | SOC & STORAGE |
| 8 | No divergence | fig1 | combined_output.csv | Residual analysis |

---

## Core Claims

### 1. Usable Capacity: 397 Ah (99.3%)

<a id="claim-1"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Bank delivered 397 Ah usable capacity (99.3% of 400 Ah rated) |
| **Data** | Original discharge test logs (Oct 2025) |
| **Code** | N/A (manual calculation from test) |
| **Output** | Discharge test report (v1.0) |
| **Report Section** | "Discharge Test Results" |

**Test conditions:**
- Constant current discharge at ~40A average
- Cutoff voltage: 10.0V (2.5V/cell)
- Ambient temperature: ~65°F

---

### 2. Full Stasis Drift: −0.665 mV/day

<a id="claim-2"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | OLS drift rate of −0.665 mV/day over Nov 22 → Jan 31 |
| **Data** | `data/combined_output.csv` |
| **Code** | `lifepo4_analysis.py` → "DRIFT ANALYSIS" section |
| **Output** | `figures/fig1_voltage_timeline.png`, `figures/fig5_drift_flattening.png` |
| **Report Section** | "Results — Storage Drift & Equilibrium Approach" (§3) |

**Computation:**

```python
# Daily mean mid-voltage
daily_mid = hourly_df.groupby('date')['Mid'].mean()

# OLS regression
slope, intercept, r, p, se = stats.linregress(days, daily_mid)
# slope = -0.000665 V/day = -0.665 mV/day
# R² = 0.876
```

**Verification:**
- 70 data points (daily means)
- R² = 0.876 indicates strong linear fit
- p < 0.001 (highly significant)

---

### 3. Last 30-Day Drift: −0.165 mV/day

<a id="claim-3"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Drift rate dropped to −0.165 mV/day in final 30 days (75% reduction) |
| **Data** | `data/combined_output.csv` (Jan 2 → Jan 31 subset) |
| **Code** | `lifepo4_analysis.py` → "Last 30 Days" section |
| **Output** | `figures/fig5_drift_flattening.png` |
| **Report Section** | "Results — Storage Drift" (§3.2) |

**Rate reduction calculation:**

```python
reduction = (1 - abs(slope_30 / slope_full)) * 100
# = (1 - 0.165/0.665) * 100 = 75.1%
```

**Interpretation:**
The 75% rate reduction is the clearest evidence that the system is approaching equilibrium rather than continuing linear decline.

---

### 4. MA-60s Noise Reduction: 42–50%

<a id="claim-4"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Time-based 60s rolling mean reduces apparent noise by 42–50% |
| **Data** | High-frequency voltage files (via releases) |
| **Code** | `lifepo4_analysis.py` → "MA-60 SECONDS ANALYSIS" section |
| **Output** | `figures/fig2_ma60_comparison.png`, `figures/fig6_ma60_segments.png` |
| **Report Section** | "Results — MA-60-Seconds" (§5) |

**Computation:**

```python
hf_df['MA60'] = hf_df['voltage'].rolling('60s', min_periods=1).mean()

raw_std = hf_df['voltage'].std() * 1000    # 10.38 mV
ma60_std = hf_df['MA60'].std() * 1000      # 5.98 mV
reduction = (1 - ma60_std / raw_std) * 100 # 42.5%
```

**Segment-level results:**

| Segment | Samples | Raw σ | MA-60s σ | Reduction |
|:--------|--------:|------:|---------:|----------:|
| Dec 26 – Jan 08 | 33,400 | 9.88 mV | 4.96 mV | 49.8% |
| Jan 09 – Jan 18 | 120,926 | 10.19 mV | 5.86 mV | 42.5% |
| Jan 19 – Jan 27 | 116,499 | 9.89 mV | 4.90 mV | 50.4% |
| Jan 28 – Jan 31 | 54,781 | 10.47 mV | 5.95 mV | 43.2% |

---

### 5. Temperature Coefficient: +1.0 ± 0.3 mV/°F

<a id="claim-5"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | System-level temperature sensitivity of +1.01 mV/°F |
| **Data** | `data/combined_output.csv`, `data/combined_temperature.csv` |
| **Code** | `lifepo4_analysis.py` → "TEMPERATURE-VOLTAGE RELATIONSHIP" section |
| **Output** | `figures/fig4_temperature_voltage.png` |
| **Report Section** | "Results — Temperature–Voltage Relationship" (§6) |

**Computation:**

```python
import statsmodels.api as sm

# Two-factor regression: V = a + b1*t + b2*T
X = merged_df[['days', 'temperature']]
X = sm.add_constant(X)
model = sm.OLS(merged_df['mid_voltage'], X).fit()

# b2 = +1.01 mV/°F, SE = 0.27 mV/°F
```

**Caveat:** This is a system-level coefficient, not pure LiFePO₄ electrochemistry.

---

### 6. Eco Mode Spread Shift

<a id="claim-6"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Mean spread increased from 28.75 to 35.42 mV after Eco Mode transition |
| **Data** | `data/combined_output.csv` (±48h around Dec 23 15:40) |
| **Code** | `lifepo4_analysis.py` → "ECO MODE" section |
| **Output** | `figures/fig3_spread_analysis.png` |
| **Report Section** | "Results — Eco Mode Step" (§4) |

**±48h Window Analysis:**

| Metric | Before | After | Change |
|:-------|-------:|------:|-------:|
| Mean mid-voltage | — | — | −4.38 mV |
| Mean min-voltage | — | — | −7.71 mV |
| Mean spread | 28.75 mV | 35.42 mV | +6.67 mV |

**Interpretation:**
The spread increase is a measurement-regime artifact (firmware behavior change), not electrochemical divergence.

---

### 7. Storage Endurance: 7–10 Months

<a id="claim-7"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Projected 7–10 months from 100% to 80% SOC |
| **Data** | Derived from drift rate + parasitic current model |
| **Code** | `lifepo4_analysis.py` → "SOC & STORAGE ENDURANCE" section |
| **Output** | `figures/fig7_soc_projection.png` |
| **Report Section** | "SOC & Storage Endurance" (§7) |

**Computation:**

```python
# Time to lose 100 Ah (20% of 500Ah) at various currents
capacity_ah = 500
target_loss_ah = 100  # 20% of capacity

# Time = Ah / Current
# I = 13.3 mA → 100 Ah / 0.0133 A = 7519 hours = 313 days (10.3 months)
# I = 17 mA   → 100 Ah / 0.017 A  = 5882 hours = 245 days (8.1 months)
# I = 20 mA   → 100 Ah / 0.020 A  = 5000 hours = 208 days (6.9 months)
```

**Range justification:**
The 13–20 mA effective draw range is inferred from voltage drift behavior. Direct current measurement would narrow this uncertainty.

---

### 8. Architectural Immunity (No Cell Divergence)

<a id="claim-8"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | No evidence of divergence at bus potential over 94+ days |
| **Data** | `data/combined_output.csv` (detrended variance analysis) |
| **Code** | Visual inspection + residual analysis |
| **Output** | `figures/fig1_voltage_timeline.png` |
| **Report Section** | "Executive Summary — Architectural Immunity" |

**Evidence supporting the claim:**

| Observation | Status | Implication |
|:------------|:------:|:------------|
| Detrended residual σ stable at ~5 mV | ✅ | No growing instability |
| No trending anomalies | ✅ | Trendless variation |
| Spread increase = measurement regime | ✅ | Not electrochemical |

**Critical caveat:**
This is bus-level voltage only. Per-cell sensing would strengthen (or challenge) this claim.

```python
# Residual analysis
residuals = daily_mid - (intercept + slope * days)
residual_std = residuals.std() * 1000  # ~5.17 mV

# Check for trend in residuals
resid_slope, _, _, resid_p, _ = stats.linregress(days, residuals)
# resid_p > 0.05 → no significant trend in residuals
```

---

## Traceability Matrix

For quick verification of any claim:

```
Claim → Data File → Code Section → Figure → Report Section
```

| Claim | Data Path | Code | Figure | Report |
|:------|:----------|:-----|:-------|:-------|
| Capacity | discharge_logs | Manual | — | §1 |
| Stasis drift | combined_output.csv | DRIFT | fig1, fig5 | §3 |
| Rate reduction | combined_output.csv | DRIFT | fig5 | §3.2 |
| MA-60s | high_freq/*.csv | MA-60 | fig2, fig6 | §5 |
| Temperature | combined_*.csv | TEMP | fig4 | §6 |
| Eco Mode | combined_output.csv | ECO | fig3 | §4 |
| Endurance | derived | SOC | fig7 | §7 |
| No divergence | combined_output.csv | Residual | fig1 | Summary |

---

## See Also

- [Methodology](methodology.md) — Detailed analytical methods
- [Data Dictionary](../data/README.md) — Dataset documentation
- [Technical Report](../reports/LiFePO4_Report_2026-03-06.md) — Full analysis
