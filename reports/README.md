# 📄 Reports

Technical reports and analysis documents for the LiFePO₄ battery monitoring study.

---

## Current Version

### LiFePO4_Report_2026-03-01.md

**[📄 Read the Full Report →](LiFePO4_Report_2026-03-01.md)**

| Property | Value |
|:---------|:------|
| Data through | March 1, 2026 |
| Published | March 1, 2026 |
| Monitoring duration | 125+ days |
| High-freq samples | 663,683 |

**Key findings:**
- ✅ **Self-discharge: ~0%** — All loss from parasitic loads (validated vs. published data)
- ✅ **BMS balancing observed** — ~80-90 sec cycles captured at 14.4V+
- ✅ Parasitic draw measured: 12.5 mA (Drok ~10mA + Shelly ~2-6mA)
- ✅ Charge event analyzed: Feb 22, 2026 (1.289 kWh, ~81 Ah)
- ✅ 11+ months projected to 80% SOC
- ✅ Architectural immunity maintained through charge/discharge cycle

---

## Version History

| Version | Date | Data Coverage | Key Changes |
|:--------|:-----|:--------------|:------------|
| **2026-03-01** | Mar 1, 2026 | Oct 29, 2025 – Mar 1, 2026 | Self-discharge analysis; BMS balancing; charge event; 125+ days |
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
