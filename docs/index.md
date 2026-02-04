---
layout: default
title: LiFePO₄ Battery Bank Study
description: Architectural Immunity & Long-Term Storage Analysis
---

# ⚡ LiFePO₄ Battery Bank Study

**Architectural Immunity & Long-Term Storage Analysis**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18452542.svg)](https://doi.org/10.5281/zenodo.18452542)
[![Data: Open](https://img.shields.io/badge/Data-Open%20Access-green.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/tree/main/data)
[![Last Updated](https://img.shields.io/badge/Data%20Through-Jan%2031%2C%202026-blue.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases)

---

## Overview

A DIY **12V 500Ah LiFePO₄ battery bank** validated at **99% capacity** with **94+ days** of continuous voltage monitoring (Oct 29, 2025 – Jan 31, 2026).

This project demonstrates **architectural immunity**—the principle that parallel-connected mixed-brand cells achieve monolithic behavior through topology rather than cell matching.

**[📊 View Full Repository →](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks)**

---

## Key Findings

| Metric | Value | Notes |
|:-------|------:|:------|
| 🔋 **Usable Capacity** | 397 Ah (99.3%) | Discharge test validated |
| 📉 **Stasis Drift** | −0.67 mV/day | Full 70-day stasis period |
| 📈 **Late Drift** | −0.17 mV/day | Last 30 days (75% reduction) |
| 📊 **MA-60s Noise Reduction** | 42–50% | Segment-dependent |
| 🌡️ **Temperature Coefficient** | +1.0 mV/°F | System-level |
| ⏱️ **Storage Endurance** | 7–10 months | To 80% SOC at ~13–20 mA |

---

## Study Progress

| Phase | Status | Duration |
|:------|:------:|:---------|
| Discharge Testing | ✅ Complete | Oct 2025 |
| Long-term Monitoring | ✅ Complete | 94+ days (Nov 2025 – Jan 2026) |
| Temperature Analysis | ✅ Complete | 34 days |
| MA-60s Validation | ✅ Complete | 328k samples |
| Direct Current Measurement | 🔲 Planned | Next step |

---

## Quick Links

| Resource | Description |
|:---------|:------------|
| [📄 Full Technical Report](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/reports/LiFePO4_Report_2026-01-31.md) | Complete analysis with all results |
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

No evidence of divergence at the common bus potential over 94+ days. Spread inflation post-Eco Mode correlates with measurement-regime change, not electrochemical imbalance.

### 2. Storage Viability

Drift is approaching equilibrium (75% rate reduction from full-period to last-30-day window). Projected **7–10 months to 80% SOC** at an effective draw of ~13–20 mA.

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
  title        = {{LiFePO₄ Battery Bank: Architectural Immunity & Long-Term Storage Study}},
  year         = {2026},
  publisher    = {GitHub},
  doi          = {10.5281/zenodo.14538065},
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks}
}
```

---

## Support

<a href="https://www.buymeacoffee.com/wkcollis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

*Last updated: February 4, 2026 • Data through January 31, 2026*

*Made with ⚡ in Connecticut*
