# Evidence Map

This document maps each key claim to its supporting data, analysis code, and output figure/table.

---

## How to Read This Map

| Column | Description |
|--------|-------------|
| **Claim** | The assertion made in the report/README |
| **Data** | Source file(s) in `data/` |
| **Code** | Function/section in `scripts/lifepo4_analysis.py` |
| **Output** | Figure or table that visualizes the result |
| **Report Section** | Location in technical report |

---

## Core Claims

### 1. Usable Capacity: 397 Ah (99.3%)

| Attribute | Reference |
|-----------|-----------|
| **Claim** | Bank delivered 397 Ah usable capacity (99.3% of 400 Ah rated) |
| **Data** | Original discharge test logs (Oct 2025) |
| **Code** | N/A (manual calculation from test) |
| **Output** | Discharge test report (v1.0) |
| **Report Section** | "Discharge Test Results" |

---

### 2. Full Stasis Drift: −0.665 mV/day

| Attribute | Reference |
|-----------|-----------|
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
```

---

### 3. Last 30-Day Drift: −0.165 mV/day (75% Rate Reduction)

| Attribute | Reference |
|-----------|-----------|
| **Claim** | Drift rate dropped to −0.165 mV/day in final 30 days |
| **Data** | `data/combined_output.csv` (Jan 2 → Jan 31 subset) |
| **Code** | `lifepo4_analysis.py` → "Last 30 Days" section |
| **Output** | `figures/fig5_drift_flattening.png` |
| **Report Section** | "Results — Storage Drift" (§3.2) |

**Rate reduction calculation:**
```python
reduction = (1 - abs(slope_30 / slope_full)) * 100
# = (1 - 0.165/0.665) * 100 = 75.1%
```

---

### 4. MA-60s Noise Reduction: 42–50%

| Attribute | Reference |
|-----------|-----------|
| **Claim** | Time-based 60s rolling mean reduces apparent noise by 42–50% |
| **Data** | High-frequency voltage files (via releases) |
| **Code** | `lifepo4_analysis.py` → "MA-60 SECONDS ANALYSIS" section |
| **Output** | `figures/fig2_ma60_comparison.png`, `figures/fig6_ma60_segments.png` |
| **Report Section** | "Results — MA-60-Seconds" (§5) |

**Computation:**
```python
hf_df['MA60'] = hf_df['voltage'].rolling('60s', min_periods=1).mean()
raw_std = hf_df['voltage'].std() * 1000  # 10.38 mV
ma60_std = hf_df['MA60'].std() * 1000     # 5.98 mV
reduction = (1 - ma60_std / raw_std) * 100  # 42.5%
```

---

### 5. Temperature Coefficient: +1.0 ± 0.3 mV/°F

| Attribute | Reference |
|-----------|-----------|
| **Claim** | System-level temperature sensitivity of +1.01 mV/°F |
| **Data** | `data/combined_output.csv`, `data/combined_temperature.csv` |
| **Code** | `lifepo4_analysis.py` → "TEMPERATURE-VOLTAGE RELATIONSHIP" section |
| **Output** | `figures/fig4_temperature_voltage.png` |
| **Report Section** | "Results — Temperature–Voltage Relationship" (§6) |

**Computation:**
```python
# Two-factor regression: V = a + b1*t + b2*T
# b2 = +1.01 mV/°F, SE = 0.27 mV/°F
```

---

### 6. Eco Mode Spread Shift: 28.75 → 35.42 mV

| Attribute | Reference |
|-----------|-----------|
| **Claim** | Mean spread increased after Eco Mode transition |
| **Data** | `data/combined_output.csv` (±48h around Dec 23 15:40) |
| **Code** | `lifepo4_analysis.py` → "ECO MODE" section |
| **Output** | `figures/fig3_spread_analysis.png` |
| **Report Section** | "Results — Eco Mode Step" (§4) |

---

### 7. Storage Endurance: ~7–10 Months to 80% SOC

| Attribute | Reference |
|-----------|-----------|
| **Claim** | Projected 7–10 months from 100% to 80% SOC |
| **Data** | Derived from drift rate + parasitic current model |
| **Code** | `lifepo4_analysis.py` → "SOC & STORAGE ENDURANCE" section |
| **Output** | `figures/fig7_soc_projection.png` |
| **Report Section** | "SOC & Storage Endurance" (§7) |

**Computation:**
```python
# Time to lose 100 Ah at various currents
# I = 13.3 mA → 313 days (10.3 months)
# I = 20 mA → 208 days (6.9 months)
```

---

### 8. No Cell Divergence (Architectural Immunity)

| Attribute | Reference |
|-----------|-----------|
| **Claim** | No evidence of divergence at bus potential |
| **Data** | `data/combined_output.csv` (detrended variance analysis) |
| **Code** | Visual inspection + residual analysis |
| **Output** | `figures/fig1_voltage_timeline.png` |
| **Report Section** | "Executive Summary — Architectural Immunity" |

**Evidence:**
- Detrended residual σ stable at ~5 mV
- No trending anomalies
- Spread increase correlates with measurement regime, not electrochemistry

**Caveat:** Bus-level only; per-cell sensing not available.

---

## Quick Reference Table

| Claim | Primary Figure | Data File | Code Section |
|-------|----------------|-----------|--------------|
| 397 Ah capacity | — | Discharge logs | Manual |
| −0.665 mV/day drift | fig1, fig5 | combined_output.csv | DRIFT ANALYSIS |
| 75% rate reduction | fig5 | combined_output.csv | DRIFT ANALYSIS |
| 42–50% MA-60s reduction | fig2, fig6 | High-freq (releases) | MA-60 SECONDS |
| +1.0 mV/°F temp coeff | fig4 | combined_output + temp | TEMPERATURE-VOLTAGE |
| Eco Mode spread shift | fig3 | combined_output.csv | ECO MODE |
| 7–10 mo to 80% SOC | fig7 | Derived | SOC & STORAGE |
| No divergence | fig1 | combined_output.csv | Residual analysis |
