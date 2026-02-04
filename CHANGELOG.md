# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses date-based versioning (`YYYY-MM-DD`) based on data cutoff dates.

---

## [2026-01-31] — 2026-02-01

### Added
- Extended monitoring data through January 31, 2026 (94+ days total)
- Temperature correlation analysis (Dec 29, 2025 – Jan 31, 2026)
- High-frequency voltage data (~328,000 samples at ~3s cadence)
- MA-60s segment analysis with per-segment noise reduction metrics
- Two-factor regression model (time + temperature)
- SOC projection model with parasitic current estimates
- Comprehensive documentation suite:
  - `docs/glossary.md` — Terms and abbreviations
  - `docs/faq.md` — Frequently asked questions
  - `CHANGELOG.md` — This file
  - `SECURITY.md` — Security policy

### Changed
- Updated drift calculations to reflect equilibrium approach (75% rate reduction)
- Recomputed MA-60s noise reduction with segment analysis (42–50% band)
- Enhanced README with visual navigation, icons, and collapsible sections
- Improved all documentation with consistent formatting and terminology
- Standardized on "MA-60s" terminology throughout

### Fixed
- Clarified window-dependent drift rate reporting in methodology
- Completed Acknowledgments section in README
- Fixed terminology inconsistencies across documentation

---

## [2025-12-26] — 2025-12-27

### Added
- High-frequency voltage monitoring (~3s cadence)
- Eco Mode transition analysis (Dec 23, 2025)
- Initial MA-60s noise reduction calculations
- Temperature sensor integration

### Changed
- Enabled Eco Mode on Shelly Plus Uni (Dec 23, 2025 ~15:40 local)
- Updated spread analysis to account for measurement regime change

### Noted
- Spread increase post-Eco Mode correlates with measurement regime, not electrochemistry

---

## [2025-11-22] — 2025-11-23

### Added
- Stasis monitoring phase initiated
- Daily mean voltage tracking
- Initial drift rate calculations

### Changed
- Transitioned from active testing to passive monitoring
- Battery bank placed in storage configuration

---

## [2025-11-04] — 2025-11-05

### Added
- Continuous hourly voltage monitoring via Home Assistant
- Shelly Plus Uni voltmeter integration
- Data export pipeline (CSV format)

---

## [2025-10-29] — 2025-10-30

### Added
- Initial repository creation
- Discharge test results (397 Ah / 99.3% capacity)
- Original technical report (v1.0)
- Basic documentation structure

### Established
- Dual licensing model (CC BY 4.0 for data, MIT for code)
- Citation metadata (CITATION.cff)
- Contributing guidelines

---

## Version History Notes

### Previous Versioning

Earlier versions used sequential notation (v1.0, v2.1, v8.4, etc.) which has been consolidated into the date-based timeline above for clarity.

### Data Availability

| Version | Data Coverage | High-Freq Data |
|:--------|:--------------|:---------------|
| 2026-01-31 | Oct 29, 2025 – Jan 31, 2026 | Dec 26, 2025 – Feb 1, 2026 |
| 2025-12-26 | Oct 29, 2025 – Dec 26, 2025 | Initial collection |
| 2025-11-22 | Oct 29, 2025 – Nov 22, 2025 | Not available |
| 2025-10-29 | Discharge test only | Not available |

---

## How to Cite Specific Versions

When citing a specific version of this dataset, include the version date:

```bibtex
@misc{collis2026lifepo4,
  author       = {Collis, William K.},
  title        = {{LiFePO₄ Battery Bank: Architectural Immunity \& Long-Term Storage Study}},
  year         = {2026},
  version      = {2026-01-31},
  publisher    = {GitHub},
  doi          = {10.5281/zenodo.14538065},
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks}
}
```
