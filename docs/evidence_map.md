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
- [INA228-Era Claims (2026-07 onward)](#ina228-era-claims-2026-07-onward)
  - [9. Quiescent Drain: 7.4 mA, and it is the monitor](#9-quiescent-drain-74-ma-and-it-is-the-monitor)
  - [10. Stasis Drift: -0.3031 mV/day](#10-stasis-drift--03031-mvday)
  - [10b. 95-Day Storage Stasis](#10b-95-day-storage-stasis)
  - [11. Shelly Reads 30.6 mV Low](#11-shelly-reads-306-mv-low)
  - [12. Coulomb Ledger Deadband Blind Spot](#12-coulomb-ledger-deadband-blind-spot)
  - [13. Post-Charge Relaxation](#13-post-charge-relaxation)
  - [14. True self-discharge is NOT measured](#14-true-self-discharge-is-not-measured)

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

> [!WARNING]
> **SUPERSEDED 2026-08-26 by [claim 9](#9-quiescent-drain-749-ma-measured).** The
> direct measurement was made, and the drain is **7.4 mA** — so the inferred
> 13–20 mA band was 42–63% high. Two separate errors compound in the computation
> above, and both are worth naming because both are easy to repeat:
> 1. It uses the **500 Ah nameplate**, not the 397 Ah the discharge test
>    validated — a 26% overstatement of the Ah available above 80% SOC.
> 2. The current itself came from a drift model, not from a shunt.
>
> Corrected on both counts, endurance to 80% SOC is **≈15 months**, not 7–10 —
> and per [claim 9](#9-quiescent-drain-74-ma-and-it-is-the-monitor) it is the
> endurance of the *monitor*, which is the entire load.
> This entry is kept rather than edited so the supersession stays auditable.

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


## INA228-Era Claims (2026-07 onward)

Every claim below is reproduced by `python scripts/ina228_analysis.py` from files
that ship in this repository. No host access is needed.

---

### 9. Quiescent Drain: 7.4 mA, and it is the monitor

<a id="claim-9"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | The bus draws 7.4 ± 2.4 mA time-weighted with no charger and no deliberate load, and that current is the INA228 monitor itself |
| **Data** | `data/ina228/ina228_daily_2026-07-13_2026-08-26.csv` |
| **Code** | `ina228_analysis.py` -> `fig_parasitic()` and the PARASITIC DRAIN block of `main()` |
| **Output** | `figures/fig_ina228_parasitic.png` |
| **Report Section** | 2026-08-26 report §7 |

**Computation:**

```python
d = daily[(daily.index > ANCHOR) & (daily["coverage_s"] > 80000)]
ah   = d["ah_net"].sum()            # -7.1877 Ah
secs = d["coverage_s"].sum()        # 39.97 days actually integrated
mA   = ah * 3600 / secs * 1000      # -7.4 mA, TIME-weighted, not sample-weighted
```

**Evidence quality:** [M] measured. n = 1.79 M current samples at 2 s over 41
days, 99.93% integrated coverage. Regime means 5.90 / 8.78 / 7.36 mA.

**Attribution — [M], from the operator 2026-08-26, not from the data:** the
Shelly Plus Uni and the DROK panel meter are **retired**, the Giandel inverter is
**connected but off**, and the INA228 monitor is **powered from the busbars**. In
the low-side topology the monitor's return runs through the shunt, so **the
measured current is the monitor itself** — 7.4 mA at 13.35 V = 99 mW, against
~7.1 mA predicted for a Wi-Fi-associated XIAO ESP32-C3 behind an 87% buck [D].
**The bank's own external parasitic load is effectively nil.**

This also corrects a firmware figure from [I] to [M]: the `battery-bank-monitor.yaml`
header assumes "Monitor ~100 mA" in its survival-sleep note. Measured, it is
**14× lower**.

> **The inference this replaced was backwards, recorded per R13.** From
> "commissioning says ~100 mA" and "the total is 7.4 mA" it followed that the
> monitor must sit *upstream* of the shunt. Valid logic, bad premise — the
> ~100 mA was an [I] never measured. One question to the operator replaced a
> claim about wiring that nobody had looked at.

**Limits:** the ±2.4 mA is not statistical. The 41-day mean is tight; its
accuracy is bounded by this chip's commissioning-measured 0.9 µV ≡ 2.4 mA shunt
offset, which averaging cannot reduce. **Quote two significant figures, not
three.** Also: one season (pack 68.0–70.5 °F), one SOC (~100%), one load set —
and the load set is a property of the installation, not the bank.

**Not self-discharge.** The shunt measures charge crossing the terminals only;
see [claim 14](#14-true-self-discharge-is-not-measured).

---

### 10. Stasis Drift: -0.3031 mV/day

<a id="claim-10"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Bank voltage declines at 0.3031 mV/day in deep stasis — a real, resolvable rate, not zero |
| **Data** | `data/ina228/ina228_daily_*.csv`, `data/ina228/stasis_ma60_*.csv` |
| **Code** | `ina228_analysis.py` -> MA-60s drift block of `main()` |
| **Output** | `figures/fig_ina228_noise_floor.png` |
| **Report Section** | 2026-08-26 report §5.2 |

**Computation:**

```python
y = d["v_mean"].iloc[-7:].to_numpy() * 1000
r = stats.linregress(np.arange(7), y)
# slope -0.3031 mV/day, se 0.0079, r2 0.997, p 2.2e-07  ->  38 sigma from zero
```

**Evidence quality:** [M] measured. The 5-day and 7-day windows agree to
0.001 mV/day; the 14- and 30-day windows are steeper (-0.358, -0.552) because
they still contain the tail of post-charge relaxation.

**Why earlier reports said zero:** they were right about their instrument. A
10 mV-quantised sensor cannot resolve 0.3 mV/day, so "indistinguishable from
zero" was a statement about the Shelly. [Claim 10b](#10b-95-day-storage-stasis)
is that detection floor measured directly.

**Cross-check [D]:** -0.3031 mV/day / 6.0 mV per %SOC = -1.54 %SOC/month, against
-1.38 %SOC/month from the independent coulomb path. The two are consistent, but
their *difference* does not bound self-discharge — both uncertainties exceed the
gap. See [claim 14](#14-true-self-discharge-is-not-measured).

---

### 10b. 95-Day Storage Stasis

<a id="claim-10b"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Apr 1 – Jul 4 2026: drift +0.0074 ± 0.0655 mV/day, p = 0.91, n = 95 days |
| **Data** | `data/shelly_daily_min_2026-04-01_2026-07-16.csv` |
| **Code** | `ina228_analysis.py` -> STORAGE STASIS block of `main()` |
| **Output** | `figures/fig_ina228_ten_month_timeline.png` |
| **Report Section** | 2026-08-26 report §5.4 |

**Evidence quality:** [M] measured, but **at the instrument's detection floor.**
The standard error of 0.066 mV/day is itself larger than the 0.303 mV/day the
INA228 resolves, so the correct reading is "below the Shelly's detection limit,"
not "zero." This entry's main job is closing the Apr 5 -> Jul 14 gap in the
published record.

---

### 11. Shelly Reads 30.6 mV Low

<a id="claim-11"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | The Shelly Plus Uni reads 30.6 mV below the INA228 on a quiet bank |
| **Data** | `data/ina228/shelly_ina228_crosscheck.csv` |
| **Code** | `ina228_analysis.py` -> `crosscheck()` |
| **Output** | `figures/fig_shelly_ina228_offset.png` |
| **Report Section** | 2026-08-26 report §1.2 |

**Computation:**

```python
quiet = m[(m["current_A"].abs() < 0.5) & (m["dvdt_mV_per_min"].abs() < 1)]
quiet["d_mV"].mean()   # -30.64 mV, sd 7.84, n = 148, 95% CI [-31.91, -29.37]
```

**Evidence quality:** [M] measured, n = 148 gated pairs.

**Limits — and why the CI is not the uncertainty:** the loaded subset gives
-25.51 mV and the ungated set -26.95 mV. The estimators disagree by up to 5.1 mV,
so the **usable uncertainty when restating a Shelly-era figure is ±3 mV**, not
the ±1.3 mV the CI suggests. The overlap is two days at one temperature and one
SOC, and it can never be extended — the Shelly is retired. **This is the single
most important number for comparing across the two eras**, and it is why
`monthly_metrics.csv` now carries an `instrument` column.

---

### 12. Coulomb Ledger Deadband Blind Spot

<a id="claim-12"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | The firmware's coulomb ledger books 0.26% of the charge the INA228 actually moved during storage |
| **Data** | `data/ina228/coulomb_ledger_hourly.csv` |
| **Code** | `ina228_analysis.py` -> `fig_coulomb_ledger()` |
| **Output** | `figures/fig_ina228_coulomb_ledger.png` |
| **Report Section** | 2026-08-26 report §6 |

**Three accountants, one current, 31.96 continuous days (no reboot):**

| Accountant | Net charge | Equivalent |
|:-----------|-----------:|-----------:|
| INA228 CHARGE register (silicon, 1.58 s) | -5.8222 Ah | -7.582 mA |
| Independent left-rectangle integration | -5.8019 Ah | -7.555 mA |
| Firmware ledger (±0.05 A deadband) | **-0.0149 Ah** | -0.019 mA |

**Root cause:** `discharge_current` returns `0.0f` whenever
`i > discharge_threshold_a`, and `discharge_threshold_a` is -0.05 A. The measured
drain is 7.5 mA, so the deadband is 6.7x larger than the current it excludes.

**Evidence quality:** [M] measured, three independent paths. The first two agree
to 0.35% — the integration-method error the design intended to bound. The third's
divergence is the deadband.

**Consequence [D]:** SOC reads 99.996% when the coulomb truth is ~98.2%, and the
error is one-directional and unbounded during storage, at ~1.4 %SOC/month.

**Note on the detector:** the firmware's `Cycle Integration Delta (SW-HW)` sensor
exists to catch exactly this, but returns NaN until a full-charge anchor seeds its
snapshot. The hardware accumulators it reads were added *after* the only anchor
this system has recorded, so it has never published a value and has no InfluxDB
series at all. A check that has never run is not a check.

---

### 13. Post-Charge Relaxation

<a id="claim-13"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | Post-charge OCV relaxation is two-exponential (tau1 2.16 h, tau2 3.12 d); 99% complete at ~14 days |
| **Data** | `data/ina228/stasis_ma60_2026-07-16_2026-08-26.csv.gz` |
| **Code** | `ina228_analysis.py` -> `fig_relaxation()` |
| **Output** | `figures/fig_ina228_relaxation.png` |
| **Report Section** | 2026-08-26 report §5.1 |

**Computation:**

```python
def two_exp(t, vinf, a1, t1, a2, t2):
    return vinf + a1 * np.exp(-t / t1) + a2 * np.exp(-t / t2)
# V_inf 13.3042 V; A1 +0.1699 V, tau1 2.16 h; A2 +0.6105 V, tau2 3.12 d
# residual sd 5.58 mV over n = 55,691 minute means
```

**Evidence quality:** [M] measured, n = 55,691.

**Limits:** one temperature band (68.0–70.5 °F), one SOC (~100%), one charge
profile. **Do not confuse this with post-*load* relaxation**, reported at
tau63 ~ 7.1 min in the commissioning report. Surface-charge decay after a CV
charge and polarisation decay after a current step are different processes, and
their time constants differ by three orders of magnitude. The ~30-minute industry
rest rule applies to the second, not the first.

**Falsifying observation:** the fit residual grows back to ~4 mV by day 41, when
both exponentials are fully decayed. That is the slow linear term the model does
not contain — i.e. [claim 10](#10-stasis-drift--03031-mvday). A fit that absorbed
it into a third exponential would be over-fitting a real physical process.

---


### 14. True self-discharge is NOT measured

<a id="claim-14"></a>

| Attribute | Reference |
|:----------|:----------|
| **Claim** | No figure in this study measures true self-discharge |
| **Data** | — (this is a negative claim about what the instrument can see) |
| **Code** | — |
| **Output** | — |
| **Report Section** | 2026-08-26 report §7.7 |

**Why the shunt cannot see it.** The DROK shunt sits in the negative cable
between battery− and the negative busbar. It measures charge **crossing the
terminals**. Self-discharge is internal to the cells and never crosses it. A
perfect shunt measurement of 0.000 mA would still be consistent with any
self-discharge rate whatsoever.

**Two earlier claims withdrawn 2026-08-26:**

1. *"Two independent loss paths agree to 11%, bounding self-discharge."* The
   difference between the voltage path (total SOC decline) and the coulomb path
   (terminal current) is the self-discharge candidate — but both uncertainties
   exceed the gap. The voltage path is contaminated by the relaxation tail
   (τ₂ ≈ 3.3 d, window starts day 13), and the 6.0 mV/%SOC plateau slope is
   extrapolated from 76–81% SOC to ~98%.
2. *"Self-discharge ~0%."* Inherited from the Shelly-era 92-day study, on an
   instrument that could not resolve 0.3 mV/day. Nothing in the INA228 record
   confirms or refutes it.

**The measurement that would establish it**, scheduled by the operator: reach
stasis (done) → discharge below 80% SOC → charge to a full anchor → reconcile
the full→full cycle via the firmware's V1.10 logger,

    U = recon_coul_eff × Ah_in − Ah_out

**Prerequisite — [claim 12](#12-coulomb-ledger-deadband-blind-spot) must be fixed
first.** With the ±0.05 A deadband in place, `Ah_out` misses the monitor's
0.177 Ah/day entirely, so `U` absorbs it and reports it as self-discharge. Over a
60-day storage leg that is 10.6 Ah = 2.7% of 397 Ah ≡ ≈1.3 %/month — inside the
published LFP range, and therefore an artefact that would read as a confirmation.

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
| Endurance | derived | SOC | fig7 | §7 (superseded) |
| No divergence | combined_output.csv | Residual | fig1 | Summary |

**INA228 era** — all reproduced by `scripts/ina228_analysis.py`:

| Claim | Data Path | Code | Figure | Report |
|:------|:----------|:-----|:-------|:-------|
| Quiescent drain 7.4 mA (= the monitor) | ina228/ina228_daily_*.csv | `fig_parasitic` | fig_ina228_parasitic | §7 |
| Self-discharge NOT measured | — | — | — | §7.7 |
| Stasis drift -0.303 mV/day | ina228/ina228_daily_*.csv | MA-60s block | fig_ina228_noise_floor | §5.2 |
| 95-day storage stasis | shelly_daily_min_*.csv | STORAGE block | fig_ina228_ten_month_timeline | §5.4 |
| Shelly -30.6 mV | ina228/shelly_ina228_crosscheck.csv | `crosscheck` | fig_shelly_ina228_offset | §1.2 |
| Ledger blind spot | ina228/coulomb_ledger_hourly.csv | `fig_coulomb_ledger` | fig_ina228_coulomb_ledger | §6 |
| Relaxation tau1/tau2 | ina228/stasis_ma60_*.csv | `fig_relaxation` | fig_ina228_relaxation | §5.1 |
| Charge 115.4 Ah | ina228/events/charge_*.csv | `fig_charge` | fig_ina228_charge_profile | §3 |
| Discharge campaign | ina228/events/discharge_*.csv | `fig_discharge` | fig_ina228_discharge_legs | §4 |

---

## See Also

- [Methodology](methodology.md) — Detailed analytical methods
- [Data Dictionary](../data/README.md) — Dataset documentation
- [Technical Report](../reports/LiFePO4_Report_2026-08-26.md) — Current analysis (INA228 era)
- [Previous Report](../reports/LiFePO4_Report_2026-03-31.md) — Last Shelly-era analysis
- [Commissioning Report](../INA228%20Monitor/Battery-Bank-Monitor-Commissioning-Report.md) — How the current instrument was qualified
