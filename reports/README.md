# 📄 Reports

Technical reports and analysis documents for the LiFePO₄ battery monitoring study.

---

## Current Version

### LiFePO4_Report_2026-01-31.md

**[📄 Read the Full Report →](LiFePO4_Report_2026-01-31.md)**

| Property | Value |
|:---------|:------|
| Data through | January 31, 2026 |
| Published | February 1, 2026 |
| Monitoring duration | 94+ days |
| High-freq samples | ~328,000 |

**Key findings:**
- ✅ Architectural immunity confirmed (no divergence)
- ✅ 75% drift rate reduction (approaching equilibrium)
- ✅ 42–50% MA-60s noise reduction
- ✅ +1.0 mV/°F temperature coefficient
- ✅ 7–10 months projected to 80% SOC

---

## Version History

| Version | Date | Data Coverage | Key Changes |
|:--------|:-----|:--------------|:------------|
| **2026-01-31** | Feb 1, 2026 | Oct 29, 2025 – Jan 31, 2026 | Extended to 94+ days; drift flattening; temperature analysis |
| 2025-12-26 | Dec 27, 2025 | Oct 29, 2025 – Dec 26, 2025 | Added high-frequency data; Eco Mode analysis |
| 2025-11-22 | Nov 23, 2025 | Oct 29, 2025 – Nov 22, 2025 | Initial stasis monitoring |
| 2025-10-29 | Oct 30, 2025 | Discharge test only | Original discharge test report |

---

## Versioning Convention

This project uses **date-based versioning** (`YYYY-MM-DD`) based on the data cutoff date.

| Component | Format | Example |
|:----------|:-------|:--------|
| Version | YYYY-MM-DD | 2026-01-31 |
| File name | `LiFePO4_Report_YYYY-MM-DD.md` | `LiFePO4_Report_2026-01-31.md` |

### Previous Notation

Earlier versions used sequential notation (v1.0, v2.1, v8.4, etc.). This has been consolidated into the date-based timeline for clarity and traceability.

---

## Report Structure

The technical report follows this structure:

| Section | Content |
|:--------|:--------|
| Executive Summary | Key findings overview |
| §1 Data Coverage | Datasets and derived series |
| §2 Methodology | Analytical methods |
| §3 Drift Analysis | Voltage decline and equilibrium approach |
| §4 Eco Mode Effect | Measurement regime change |
| §5 MA-60s Analysis | Noise reduction |
| §6 Temperature-Voltage | Thermal sensitivity |
| §7 SOC & Endurance | Storage projections |
| §8 Late-January Stability | Recent metrics |
| §9 Recommendations | Next steps |
| §10 Conclusions | Summary |
| References | Citations |

---

## Citing Reports

When citing a specific report version:

```bibtex
@techreport{collis2026lifepo4report,
  author       = {Collis, William K.},
  title        = {{LiFePO₄ Battery Bank: Technical Report}},
  year         = {2026},
  month        = {February},
  version      = {2026-01-31},
  institution  = {Independent Research},
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/reports/LiFePO4_Report_2026-01-31.md}
}
```

---

## See Also

- [Evidence Map](../docs/evidence_map.md) — Claim-to-data traceability
- [Methodology](../docs/methodology.md) — Detailed methods
- [Data Dictionary](../data/README.md) — Dataset documentation
- [CHANGELOG](../CHANGELOG.md) — Full version history
