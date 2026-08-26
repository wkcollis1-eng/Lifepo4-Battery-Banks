# 📄 Reports

Technical reports and analysis documents for the LiFePO₄ battery monitoring study.

---

## Current Version

### LiFePO4_Report_2026-08-26.md

**[📄 Read the Full Report →](LiFePO4_Report_2026-08-26.md)**

| Property | Value |
|:---------|:------|
| Data through | August 26, 2026 |
| Published | August 26, 2026 |
| Published record | Oct 29, 2025 – Aug 26, 2026 (301 days) |
| Instrument | INA228 + 375 µΩ shunt (Shelly Plus Uni retired 2026-07-16) |
| Samples | 1,790,710 current @ 2 s, 42.2 days integrated, 99.93% coverage |

**Key findings:**
- ✅ **Quiescent drain measured, not inferred** — **7.4 ± 2.4 mA** over 41 quiescent
  days. With the Shelly and DROK meter retired and the inverter off, it is the
  INA228 monitor itself; the bank's own external load is nil.
- ✅ **Stasis confirmed, and the drift inside it is now resolvable** — −0.3031 mV/day
  over 7 days (se 0.0079, p = 2.2×10⁻⁷). Prior reports could only say
  "indistinguishable from zero," which was a statement about the Shelly.
- ⚠️ **Self-discharge + BMS standby bounded below 0.9 %/month (95%)**, not
  measured — the shunt sees only terminal current, so both terms are behind it.
  `P(> 2 %/month) = 0.02%`. Under the published LFP figure, and under this
  project's own commissioning estimate for 5 × BMS. Full→full cycle scheduled.
- ✅ **The bank returns to its own baseline after ten months** — 13.3005 V measured
  against a Nov 2025 baseline of 13.301 V restated on the same scale.
- ✅ **Apr 5 → Jul 14 gap closed** — 95 days of storage stasis at
  +0.0074 ± 0.0655 mV/day (p = 0.91).
- ⚠️ **The firmware coulomb ledger cannot see the drain** — silicon −5.8222 Ah,
  independent integration −5.8019 Ah, firmware −0.0149 Ah over the same ~32 days.
  SOC reads 99.996% when the truth is ≈98.2%. See §6.
- ✅ **The 2026-08-04 +2.9 mA step resolved to an instrument offset shift** — the
  bank was rewired that afternoon to eliminate stacked lugs, with no load added.
  At 375 µΩ the step is 1.08 µV, the same order as the chip's 0.9 µV offset.

---

### Previous: LiFePO4_Report_2026-03-31.md

**[📄 Read →](LiFePO4_Report_2026-03-31.md)** — the last Shelly-era report.

| Property | Value |
|:---------|:------|
| Data through | March 31, 2026 (hourly); April 2, 2026 (high-frequency) |
| Published | April 5, 2026 |
| Monitoring duration | 158 days (see notes on this figure below) |
| High-freq samples | 758,338 |

- ✅ Stasis confirmed — all four criteria pass at day 42 post-charge
- ✅ MA-60 std down 28.4% (9.38 mV → 6.72 mV)
- ⚠️ HF logging gap ~Mar 7–20, 2026

> [!NOTE]
> **Voltages in this and every earlier report are on the Shelly scale.** The INA228
> cross-calibration (2026-08-26 report §1.2) measured the Shelly reading
> **30.6 mV low** (n = 148 gated pairs). Add 30.6 mV before comparing any
> pre-July-2026 voltage with an INA228-era one.

---

## Version History

| Version | Date | Data Coverage | Key Changes |
|:--------|:-----|:--------------|:------------|
| **2026-08-26** | Aug 26, 2026 | Oct 29, 2025 – Aug 26, 2026 | INA228 era; direct parasitic measurement; instrument cross-calibration; coulomb-ledger deadband finding; Apr–Jul gap closed |
| 2026-03-31 | Apr 5, 2026 | Oct 29, 2025 – Mar 31/Apr 2, 2026 | Full stasis confirmed; 158-day study; HF gap Mar 7–20 noted |
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
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/blob/main/reports/LiFePO4_Report_2026-08-26.md}
}
```

---

## See Also

- [Evidence Map](../docs/evidence_map.md) — Claim-to-data traceability
- [Methodology](../docs/methodology.md) — Detailed methods
- [Data Dictionary](../data/README.md) — Dataset documentation
- [CHANGELOG](../CHANGELOG.md) — Full version history
