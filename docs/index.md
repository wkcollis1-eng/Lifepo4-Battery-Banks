---
layout: default
title: LiFePO₄ Battery Bank Study
description: Architectural Immunity & Long-Term Storage Analysis
---

# ⚡ LiFePO₄ Battery Bank Study

**Architectural Immunity & Long-Term Storage Analysis**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18452542.svg)](https://doi.org/10.5281/zenodo.18452542)
[![Data: Open](https://img.shields.io/badge/Data-Open%20Access-green.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/tree/main/data)
[![Last Updated](https://img.shields.io/badge/Data%20Through-Aug%2026%2C%202026-blue.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases)
[![Instrument](https://img.shields.io/badge/Instrument-INA228%20%2B%20375%20%C2%B5%CE%A9%20shunt-6f42c1.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/tree/main/INA228%20Monitor)

---

## Overview

A DIY **12V 500Ah LiFePO₄ battery bank**, validated at **397 Ah** (99.3% of nameplate) by discharge test, under continuous monitoring since October 2025 — **301 days** across two instruments (Oct 29, 2025 – Aug 26, 2026).

This project demonstrates **architectural immunity**—the principle that parallel-connected mixed-brand cells achieve monolithic behavior through topology rather than cell matching.

Since July 2026 the bank has been instrumented by a purpose-built **INA228 monitor** on a 375 µΩ shunt, sampling voltage *and current* every 2 seconds. That closed the study's longest-standing open question: the quiescent drain, inferred for a year from voltage drift, is now **measured at 7.4 mA** — and with the Shelly and DROK meter retired and the inverter off, that current turns out to be the monitor itself.

**[📊 View Full Repository →](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks)**

---

## Key Findings

| Metric | Value | Notes |
|:-------|------:|:------|
| 🔋 **Usable Capacity** | 397 Ah (99.3%) | Discharge test validated, Oct 2025 |
| ⚡ **Quiescent Drain** | **7.4 ± 2.4 mA measured** | It is the monitor itself; the bank's own external load is nil |
| ⏱️ **Storage Endurance** | **≈15 months** | To 80% SOC on the validated 397 Ah; band 11–22 |
| 📉 **Stasis Drift** | **−0.303 mV/day** | 7-day OLS, se 0.008, p = 2.2×10⁻⁷ |
| 🔋 **Self-discharge + BMS** | **< 0.9 %/month (95%)** | A bound, not a measurement; full→full cycle scheduled |
| 📊 **Voltage Noise Floor** | **0.131 mV** | Within-day sd, below the 195.3 µV bus LSB |
| 🌡️ **Temperature Coefficient** | +1.0 mV/°F | System-level |
| ⚠️ **SOC ledger blind spot** | 1.46 %SOC / 32 d | ±50 mA firmware deadband hides the 7.4 mA drain |
| 🔌 **Real outage survived** | **11.08 h** | 2026-07-04, 340 mV clear of the first alarm |
| ⚠️ **Coincident peak** | **3328 W vs 1500 W inverter** | Fridge inrush 22× + coffee maker, 34 of 45 days |

> **Two instruments, one scale.** The Shelly Plus Uni was retired 2026-07-16 and reads
> **30.6 mV low** against the INA228 (n = 148 gated pairs). Add 30.6 mV to any
> pre-July-2026 voltage in this study before comparing it with a later one.

---

## Study Progress

| Phase | Status | Duration |
|:------|:------:|:---------|
| Discharge Testing | ✅ Complete | Oct 2025 |
| Long-term Monitoring | ✅ Complete | 130+ days (Nov 2025 – Mar 2026) |
| Temperature Analysis | ✅ Complete | 62 days |
| MA-60s Validation | ✅ Complete | 712k samples |
| Charge Event Analysis | ✅ Complete | Feb 22, 2026 |
| Self-Discharge Analysis | ✅ Complete | ~0% confirmed |
| Storage Stasis | ✅ Complete | 95 days (Apr – Jul 2026) |
| INA228 Commissioning | ✅ Complete | Jul 13–16, 2026 |
| **Direct Current Measurement** | ✅ **Complete** | **41 days — 7.4 mA** |
| Cycle-2 Coulombic Efficiency | 🔲 Blocked | Needs a second full charge |
| True self-discharge | 🔲 Scheduled | Discharge <80% SOC → charge → reconcile |
| Winter INA228 window | 🔲 Planned | Limits are stated at 68–70 °F |

---

## Quick Links

| Resource | Description |
|:---------|:------------|
| [📄 Full Technical Report](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/reports/LiFePO4_Report_2026-08-26.md) | Complete analysis with all results |
| [⚡ Commissioning Report](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/INA228%20Monitor/Battery-Bank-Monitor-Commissioning-Report.md) | How the INA228 monitor was built and qualified |
| [🔬 Methodology](methodology.md) | Statistical methods and definitions |
| [🔁 Replication Guide](replication.md) | Hardware setup and calibration |
| [🗺️ Evidence Map](evidence_map.md) | Claim → data → code traceability |
| [📖 Glossary](glossary.md) | Terms and abbreviations |
| [❓ FAQ](faq.md) | Frequently asked questions |
| [📊 Data](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/tree/main/data) | Raw datasets |

---

## Expected Results for Replication

If you replicate this study, you should observe:

| Metric | Expected Range | Notes |
|:-------|:---------------|:------|
| **Capacity** | >95% of rated | Via controlled discharge test |
| **Drift rate** | −0.5 to −1.0 mV/day | Early stasis; flattens over time |
| **Hourly spread** | <50 mV typical | Bus-level max−min measurement (not cell-to-cell) |
| **MA-60s reduction** | 40–55% | Depends on sampling regularity |

> **Important:** "Spread" in this study refers to the difference between hourly maximum and minimum voltage readings from a **single bus-level sensor**—it is **not** a measure of voltage difference between individual cells. Per-cell sensing would be required to measure cell-to-cell variation.

---

## Core Claims

### 1. Architectural Immunity

No evidence of divergence at the common bus potential over 130+ days. Spread inflation post-Eco Mode correlates with measurement-regime change, not electrochemical imbalance.

### 2. Storage Viability — measured, not inferred

The bus draws **7.4 ± 2.4 mA** in storage: a time-weighted mean over 41 quiescent days and 1.79 M samples on a 375 µΩ shunt. That is **≈15 months to 80% SOC** on the validated 397 Ah, and ≈59 months to the 20% operator floor — figures that describe how long the *instrument* can watch the bank, since the instrument is the entire load.

**Self-discharge remains ~0%** — all capacity loss is parasitic load. Two independent paths now agree on the rate to within 11%: the voltage path (−0.303 mV/day ÷ 6.0 mV per %SOC = −1.54 %SOC/month) and the coulomb path (−7.188 Ah ÷ 397 Ah = −1.38 %SOC/month).

> Earlier versions of this page projected 11+ months at 12.5 mA, and a direct bus-current measurement was the study's stated next step. That measurement is done. The old figure also applied its draw to the 500 Ah nameplate rather than the 397 Ah the discharge test validated; both corrections are folded into the numbers above.

### 2b. Instrument self-awareness

The firmware's coulomb ledger applies a ±0.05 A deadband — 6.7× larger than the drain above — so it books 0.26% of the charge the same chip actually moves during storage, and SOC drifts optimistic at ~1.4 %SOC/month. This is published rather than quietly patched because a noise-rejection deadband is a *standard* coulomb-counter design: any replication of this build will share the blind spot unless it is looked for.

### 3. Temperature Sensitivity

System-level coefficient of **+1.0 ± 0.3 mV/°F** (pack + measurement chain combined).

---

## Safety Warning

⚠️ **Lithium batteries carry inherent risks.** This 500Ah bank can deliver thousands of amps in a short circuit.

- ✅ Always use **Class T fuses** at terminals
- ✅ Never charge below **0°C (32°F)**
- ✅ **Always use a BMS** — architectural immunity does not replace cell protection
- ✅ Keep a **Class D fire extinguisher** accessible

---

## Citation

```bibtex
@misc{collis2026lifepo4,
  author       = {Collis, William K.},
  title        = {LiFePO4 Battery Bank: Architectural Immunity \& Long-Term Storage Study},
  year         = {2026},
  doi          = {10.5281/zenodo.18452542},
  url          = {https://doi.org/10.5281/zenodo.18452542},
  note         = {GitHub repository: https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks}
}
```

---

## Support

<a href="https://www.buymeacoffee.com/wkcollis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

*Last updated: March 6, 2026 • Data through March 6, 2026*

*Made with ⚡ in Connecticut*
