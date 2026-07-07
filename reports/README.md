# 📄 Reports

Technical reports and analysis documents for the LiFePO₄ battery monitoring study.

---

## Current Version

### LiFePO4_Report_2026-03-31.md

**[📄 Read the Full Report →](LiFePO4_Report_2026-03-31.md)**

| Property | Value |
|:---------|:------|
| Data through | March 31, 2026 (hourly); April 2, 2026 (high-frequency) |
| Published | April 5, 2026 |
| Monitoring duration | 158 days (see notes on this figure below) |
| High-freq samples | 758,338 |

**Key findings:**
- ✅ **Stasis confirmed** — all four stasis criteria pass (drift +3.02 mV/day, noise −28.4% vs. pre-charge baseline, voltage range 50 mV, day 42 post-charge)
- ✅ **Near-zero long-term drift** — 5-day MA-60 rate of −0.19 mV/day, indistinguishable from zero
- ✅ **Best noise performance recorded** — MA-60 std down 28.4% (9.38 mV → 6.72 mV)
- ✅ Resting voltage 13.247–13.251 V, within 19–23 mV of the Nov 4, 2025 stasis baseline
- ⚠️ HF logging gap ~Mar 7–20, 2026 — only hourly averages available for that window

---

## Version History

| Version | Date | Data Coverage | Key Changes |
|:--------|:-----|:--------------|:------------|
| **2026-03-31** | Apr 5, 2026 | Oct 29, 2025 – Mar 31/Apr 2, 2026 | Full stasis confirmed; 158-day study; HF gap Mar 7–20 noted |
| 2026-03-06 | Mar 6, 2026 | Oct 29, 2025 – Mar 6, 2026 | Approaching stasis; 130+ day monitoring; drift −4.75 mV/day |
| 2026-03-01 | Mar 1, 2026 | Oct 29, 2025 – Mar 1, 2026 | Self-discharge analysis; BMS balancing; charge event; 125+ days |
| 2026-01-31 | Feb 1, 2026 | Oct 29, 2025 – Jan 31, 2026 | Extended to 94+ days; drift flattening; temperature analysis |
| 2025-12-26 | Dec 27, 2025 | Oct 29, 2025 – Dec 26, 2025 | Added high-frequency data; Eco Mode analysis |
| 2025-11-22 | Nov 23, 2025 | Oct 29, 2025 – Nov 22, 2025 | Initial stasis monitoring |
| 2025-10-29 | Oct 30, 2025 | Discharge test only | Original discharge test report |

---

## Versioning Convention

This project uses **date-based versioning** (`YYYY-MM-DD`) based on the data cutoff date.

| Component | Format | Example |
|:----------|:-------|:--------|
| Version | YYYY-MM-DD | 2026-03-01 |
| File name | `LiFePO4_Report_YYYY-MM-DD.md` | `LiFePO4_Report_2026-03-01.md` |

### Previous Notation

Earlier versions used sequential notation (v1.0, v2.1, v8.4, etc.). This has been consolidated into the date-based timeline for clarity and traceability.

---

## Report Structure

The technical report (2026-03-01) follows this structure:

| Section | Content |
|:--------|:--------|
| Executive Summary | Key findings overview |
| §1 Data Coverage | Datasets and derived series |
| §2 Charge Event | February 22, 2026 charge analysis |
| §3 BMS Balancing | Balance cycle observations |
| §4 Post-Charge Relaxation | Surface charge dissipation |
| §5 Self-Discharge & Parasitic | Parasitic load quantification |
| §6 Drift Analysis | Voltage decline and equilibrium |
| §7 Storage Endurance | SOC projections |
| §8 MA-60s Analysis | Noise reduction |
| §9 Temperature-Voltage | Thermal sensitivity |
| §10 Updated Key Metrics | Summary table |
| §11 Conclusions | Summary |
| §12 Recommendations | Next steps |

---

## Citing Reports

When citing a specific report version:

```bibtex
@techreport{collis2026lifepo4report,
  author       = {Collis, William K.},
  title        = {{LiFePO₄ Battery Bank: Technical Report}},
  year         = {2026},
  month        = {March},
  version      = {2026-03-01},
  institution  = {Independent Research},
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/reports/LiFePO4_Report_2026-03-01.md}
}
```

---

## See Also

- [Evidence Map](../docs/evidence_map.md) — Claim-to-data traceability
- [Methodology](../docs/methodology.md) — Detailed methods
- [Data Dictionary](../data/README.md) — Dataset documentation
- [CHANGELOG](../CHANGELOG.md) — Full version history
