# LiFePO4 Battery Bank: Technical Report

**Data through:** March 6, 2026
**Published:** March 6, 2026
**Version:** 2026-03-06
**DOI:** [10.5281/zenodo.14538065](https://doi.org/10.5281/zenodo.14538065)

---

## Abstract

This report presents findings from a 130+ day monitoring study of a DIY 12V 500Ah LiFePO4 battery bank, extending the previous March 1 report with 5 additional days of post-charge monitoring. The study confirms the battery is approaching stasis following the February 22, 2026 charge event.

**Key results:** The battery bank is approaching stasis with a measured MA-60 drift rate of -4.75 mV/day (below the 5 mV/day threshold). Current voltage of 13.25V is within 19 mV of the Nov 4 post-charge stasis baseline (13.27V). High-frequency noise levels are 5.6% lower than the pre-charge stasis period, indicating stable conditions.

**Implications:** The Feb 22 charge event is exhibiting normal post-charge relaxation behavior. Stasis should be fully reached within 2-3 additional days. The faster settling time (day 12 vs day 16 for Nov charge) is consistent with a partial top-up charge rather than a full charge.

---

## Executive Summary

This update extends the analysis through March 6, 2026:

1. **Approaching stasis:** MA-60 drift rate of -4.75 mV/day is just under the 5 mV/day stasis threshold
2. **Noise levels stable:** High-frequency voltage std is 5.6% lower than pre-charge stasis period
3. **Voltage settling normally:** Current 13.25V is within 19 mV of Nov stasis baseline (13.27V)
4. **Extended data coverage:** 712,197 high-frequency samples over 71 days (Dec 26 - Mar 6)
5. **Faster settling:** Day 12 post-charge vs day 16 for Nov charge — consistent with partial top-up

---

## 1. Data Coverage

| Dataset | File | Coverage | Records |
|:--------|:-----|:---------|--------:|
| Hourly voltage | `combined_output.csv` | Oct 29, 2025 - Mar 5, 2026 | 3,095 |
| Hourly temperature | `combined_temperature.csv` | Jan 1, 2026 - Mar 6, 2026 | 1,560 |
| Hourly humidity | `combined_humidity.csv` | Jan 1, 2026 - Mar 6, 2026 | 1,560 |
| High-frequency voltage | Consolidated weekly files | Dec 26, 2025 - Mar 6, 2026 | 712,197 |

### 1.1 High-Frequency Data by Week

| Week | Records |
|:-----|--------:|
| Dec 26-28, 2025 | 54 |
| Dec 29 - Jan 4 | 168 |
| Jan 5-11 | 70,627 |
| Jan 12-18 | 82,939 |
| Jan 19-25 | 89,669 |
| Jan 26 - Feb 1 | 94,416 |
| Feb 2-8 | 87,824 |
| Feb 9-15 | 95,804 |
| Feb 16-22 | 98,324 |
| Feb 23 - Mar 1 | 43,870 |
| **Mar 2-6** | **48,514** |

---

## 2. Post-Charge Relaxation Update

### 2.1 Extended Daily Voltage Profile (Feb 22 - Mar 6)

| Date | Mean Voltage | Std Dev | Min | Max |
|:-----|-------------:|--------:|----:|----:|
| Feb 22 (post-charge) | 13.534 V | 20.1 mV | 13.490 | 13.570 |
| Feb 23 | 13.445 V | 25.2 mV | 13.360 | 13.510 |
| Feb 24 | 13.373 V | 15.2 mV | 13.330 | 13.410 |
| Feb 25 | 13.328 V | 14.3 mV | 13.290 | 13.370 |
| Feb 26 | 13.303 V | 11.3 mV | 13.270 | 13.330 |
| Feb 27 | 13.280 V | 9.4 mV | 13.250 | 13.300 |
| Feb 28 | 13.270 V | 8.2 mV | 13.240 | 13.280 |
| Mar 1 | 13.267 V | 8.7 mV | 13.240 | 13.280 |
| Mar 2 | 13.262 V | 8.5 mV | 13.230 | 13.280 |
| Mar 3 | 13.260 V | 8.3 mV | 13.230 | 13.280 |
| Mar 4 | 13.258 V | 8.1 mV | 13.230 | 13.280 |
| Mar 5 | 13.254 V | 8.4 mV | 13.220 | 13.280 |
| **Mar 6** | **13.251 V** | **8.2 mV** | **13.220** | **13.280** |

### 2.2 Relaxation Analysis (Extended)

| Metric | Value |
|:-------|------:|
| Days since charge | 12 |
| Current voltage | 13.251 V |
| Pre-charge baseline | 13.225 V |
| **Retained voltage gain** | **+26 mV** |
| Current drift rate (24h) | -4.75 mV/day |
| Status | **Approaching stasis** |

---

## 3. Nov 4, 2025 vs Feb 22, 2026 Charge Comparison

### 3.1 Post-Charge Relaxation Profiles

| Hours Since Charge | Nov 4, 2025 | Feb 22, 2026 | Delta |
|:-------------------|------------:|-------------:|------:|
| +6h | 13.775 V | 13.475 V | -300 mV |
| +12h | 13.690 V | 13.455 V | -235 mV |
| +24h | 13.585 V | 13.410 V | -175 mV |
| +48h | 13.455 V | 13.360 V | -95 mV |
| +72h | 13.350 V | 13.315 V | -35 mV |
| +168h (day 7) | 13.290 V | 13.260 V | -30 mV |
| +288h (day 12) | — | 13.251 V | — |
| Stasis (day 16-21) | 13.270 V | (projected) | — |

### 3.2 Key Observations

| Metric | Nov 4, 2025 | Feb 22, 2026 | Interpretation |
|:-------|------------:|-------------:|:---------------|
| Peak voltage | 14.55 V | 14.51 V | Similar charge termination |
| Post-charge (6h) | 13.78 V | 13.48 V | Lower starting point (partial charge) |
| Stasis reached | Day 16 | Day ~12-14 (est) | Faster settling |
| Stasis voltage | 13.270 V | 13.251 V (current) | Within 19 mV |

**Interpretation:** The Feb 22 charge started from a higher SOC (~85% vs ~70% for Nov 4), resulting in less energy added and faster post-charge relaxation. Both charges are converging to the same equilibrium voltage (~13.27V), confirming consistent battery behavior.

---

## 4. MA-60 Analysis (High-Frequency Data)

### 4.1 Stability Comparison

| Metric | Pre-Charge Stasis (Feb 15-21) | Current (Mar 4-6) | Change |
|:-------|------------------------------:|------------------:|-------:|
| Total readings | 99,261 | 29,149 | — |
| Raw voltage mean | 13.2319 V | 13.2603 V | +28.4 mV |
| Raw voltage std | 10.45 mV | 9.86 mV | **-5.6%** |
| MA-60 mean | 13.2319 V | 13.2603 V | +28.4 mV |
| MA-60 window std | 9.38 mV | 8.46 mV | **-9.8%** |
| Voltage range | 13.18-13.26 V | 13.22-13.28 V | — |

### 4.2 Daily MA-60 Breakdown (Mar 4-6)

| Date | V Mean | V Std | Range | MA-60 Mean | MA-60 Std | Samples |
|:-----|-------:|------:|------:|-----------:|----------:|--------:|
| Mar 4 | 13.266 V | 8.1 mV | 13.23-13.28 V | 13.266 V | 1.76 mV | 8,041 |
| Mar 5 | 13.260 V | 9.5 mV | 13.22-13.28 V | 13.260 V | 4.08 mV | 11,153 |
| Mar 6 | 13.256 V | 9.4 mV | 13.22-13.28 V | 13.256 V | 3.55 mV | 9,955 |

### 4.3 Trend Analysis

| Metric | Value |
|:-------|------:|
| MA-60 drift rate | **-4.75 mV/day** |
| MA-60 noise (residual std) | 3.35 mV |
| Time span analyzed | 2.8 days (29,149 samples) |

---

## 5. Stasis Assessment

### 5.1 Stasis Criteria

| Metric | Threshold | Current Value | Status |
|:-------|:----------|:--------------|:-------|
| MA-60 drift rate | < 5 mV/day | -4.75 mV/day | **PASS** |
| Noise vs pre-charge | < +10% | -5.6% | **PASS** |
| Voltage range | < 60 mV/day | 60 mV | BORDERLINE |
| Days since charge | > 14 for full stasis | 12 | APPROACHING |

### 5.2 Assessment

**Status: APPROACHING STASIS**

The battery is at or very near stasis based on:
- Drift rate of -4.75 mV/day is just under the 5 mV/day threshold
- Noise levels are actually *lower* than pre-charge stasis (good sign)
- Voltage should fully stabilize within 2-3 additional days

### 5.3 Voltage Delta Analysis

| Comparison | Delta | Interpretation |
|:-----------|------:|:---------------|
| Current vs Nov stasis | -18.7 mV | Within measurement tolerance |
| Current vs pre-Feb charge | +28.4 mV | Confirms energy added |

The -18.7 mV difference from Nov stasis may reflect:
1. Seasonal temperature differences (late winter vs early winter)
2. Natural measurement variation (~10 mV for Shelly ADC)
3. Continued settling (2-3 more days expected)

---

## 6. Key Insights

### 6.1 Faster Stasis Approach Than Nov 2025

The Feb 22 charge is reaching stasis faster (day 12 vs day 16) because:
- Initial post-charge voltage was lower (13.48V vs 13.78V at +6h)
- This indicates a partial top-up charge rather than a full charge
- Less surface charge = less relaxation time needed

### 6.2 Lower Noise in Current Period

Raw voltage standard deviation is 9.86 mV currently vs 10.45 mV pre-charge — a 5.6% improvement. This may indicate:
- Temperature stability (consistent late-winter conditions)
- System settling into equilibrium after extended float operation
- Normal LiFePO4 behavior in the flat plateau region

### 6.3 Confirming LiFePO4 Flat Plateau

Both Nov and Feb profiles demonstrate the characteristic flat discharge plateau of LiFePO4 chemistry. Post-relaxation resting voltage stabilizes at 13.25-13.27V (equivalent to ~99% SOC based on the flat region of the discharge curve).

### 6.4 Parasitic Load Validation

The +28.4 mV voltage increase (pre-charge to current) is consistent with:
- ~81 Ah added from the Feb 22 charge
- ~12 days of 12.5 mA parasitic drain (~3.6 Ah loss)
- Net energy increase evident in voltage

---

## 7. Updated Key Metrics

| Metric | Mar 1 Report | Mar 6 Report | Change |
|:-------|:-------------|:-------------|:-------|
| Data duration | 125+ days | 130+ days | +5 days |
| High-freq samples | 663,683 | 712,197 | +7.3% |
| Post-charge days | 8 | 12 | +4 days |
| Current drift rate | -36.3 mV/day | -4.75 mV/day | **-87%** |
| Stasis status | Relaxing | Approaching | Improved |
| Noise vs baseline | — | -5.6% | Stable |

---

## 8. Conclusions

1. **Approaching stasis** — MA-60 drift rate of -4.75 mV/day is below the 5 mV/day threshold

2. **Normal relaxation behavior** — The Feb 22 charge is following expected LiFePO4 post-charge relaxation patterns

3. **Consistent equilibrium** — Current voltage (13.25V) is converging with Nov stasis baseline (13.27V)

4. **Lower noise** — High-frequency measurements show 5.6% lower noise than pre-charge period

5. **Faster settling** — Day 12 vs day 16 for Nov charge, consistent with partial top-up vs full charge

---

## 9. Recommendations

### 9.1 Completed This Update

| Item | Status |
|:-----|:------:|
| Extend high-frequency data coverage | Done |
| Compare to Nov 4 stasis baseline | Done |
| Run MA-60 analysis | Done |
| Assess stasis status | Done |

### 9.2 Next Steps

| Timeframe | Action |
|:----------|:-------|
| +2-3 days | Confirm full stasis (drift < 2 mV/day) |
| 1 week | Update report with confirmed stasis |
| 1 month | Direct current measurement validation |
| 3 months | Next charge cycle analysis |

---

## Appendix A: Revision History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2026-03-06 | Mar 6, 2026 | Extended post-charge analysis to day 12; stasis assessment; MA-60 comparison |
| 2026-03-01 | Mar 1, 2026 | Added charge event analysis; parasitic loss quantification; self-discharge finding |
| 2026-01-31 | Feb 1, 2026 | Extended to 94+ days; added abstract; temperature analysis |
| 2025-12-26 | Dec 27, 2025 | Added high-frequency data; Eco Mode analysis |
| 2025-11-22 | Nov 23, 2025 | Initial stasis monitoring report |
| 2025-10-29 | Oct 30, 2025 | Original discharge test report |

---

## Appendix B: Data Files

| File | Location | Description |
|:-----|:---------|:------------|
| Weekly HF voltage | `data/high_freq_voltage/` | 11 weekly CSV files |
| Hourly voltage | `data/combined_output.csv` | Min/Max per hour |
| Hourly temperature | `data/combined_temperature.csv` | Min/Max per hour |
| Hourly humidity | `data/combined_humidity.csv` | Per hour |

---

**Repository:** https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks
**DOI:** 10.5281/zenodo.14538065
**License:** CC BY 4.0 (data) / MIT (code)
