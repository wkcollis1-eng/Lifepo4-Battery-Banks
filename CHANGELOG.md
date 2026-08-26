# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses date-based versioning (`YYYY-MM-DD`) based on data cutoff dates.

---

## [2026-08-26] — 2026-08-26

First report of the INA228 instrumentation era. The Shelly Plus Uni was retired
2026-07-16; the bank has been on a purpose-built INA228 monitor (375 µΩ shunt,
2 s cadence, voltage **and** current) since 2026-07-14.

### Added
- `reports/LiFePO4_Report_2026-08-26.md` — INA228-era technical report
- `data/ina228/` — the new published data tier, rebuilt from InfluxDB rather than
  the HA recorder (infinite retention vs a 14-day purge):
  - `ina228_hourly_*.csv` (1,052 rows) and `ina228_daily_*.csv` (44 rows) — V/I/P
    aggregates, net Ah/Wh, pack and die temperature, integration coverage
  - `stasis_ma60_*.csv` (55,691 rows) — 1-minute MA-60s voltage means
  - `coulomb_ledger_hourly.csv` (968 rows) — hardware vs software vs independent
  - `shelly_ina228_crosscheck.csv` (817 rows) — the paired two-instrument overlap
  - `events/*.csv` (32,486 rows) — **full 2 s resolution** for the charge and the
    three discharge legs
- `data/shelly_daily_min_2026-04-01_2026-07-16.csv` (107 rows) — **closes the
  Apr 5 → Jul 14 gap**; the published record is now continuous Oct 29 2025 →
  Aug 26 2026
- `data/high_freq_voltage/voltage_data_2026-06-17_to_2026-07-16.csv` (8,343 rows)
  — the final Shelly HF file, which supplies the cross-calibration overlap
- `scripts/ina228_export.py` — rebuilds every `data/ina228/` file from InfluxDB
  over any window; read-only credentials, `SELECT` only
- `scripts/ina228_analysis.py` — reproduces every figure and headline number in
  the new report **from repository files alone**, with no host access
- `scripts/update_monthly_metrics.py` — rebuilds `monthly_metrics.csv` across
  both instrument eras
- Seven figures: `fig_ina228_relaxation`, `_noise_floor`, `_parasitic`,
  `_coulomb_ledger`, `_charge_profile`, `_discharge_legs`, `_ten_month_timeline`,
  plus `fig_shelly_ina228_offset`

### Changed
- `data/monthly_metrics.csv` — new **`instrument`** column (`shelly` /
  `shelly->ina228` / `ina228`); the two instruments do not share a scale, so the
  era belongs with the row rather than in a reader's head. March 2026 recomputed
  over the full month (the prior row covered Mar 2–6 only); April–August added
- `README.md`, `data/README.md`, `reports/README.md`, `scripts/README.md` — two-era
  structure, the cross-calibration warning, and the new files
- Storage-viability claim rewritten: **7.49 mA measured** replaces "~13–20 mA
  inferred from stasis behaviour," and endurance is restated on the validated
  397 Ah rather than the 500 Ah nameplate

### Key Findings
- **Parasitic drain measured, not inferred: 7.49 mA** over 41 quiescent days
  (−7.188 Ah, 1.811% of 397 Ah, 1.38 %/month), 1.79 M samples at 99.93% coverage.
  The study's stated highest-value next step is complete. The prior inferred band
  was 42–63% high
- **Stasis drift is now resolvable at −0.3031 mV/day** (7-day OLS, se 0.0079,
  p = 2.2×10⁻⁷). Prior reports' "indistinguishable from zero" was a statement
  about the Shelly's 10 mV quantisation, not about the bank
- **Two independent loss paths agree to 11%** — voltage −1.54 %SOC/month via the
  OCV plateau slope, coulomb −1.38 %SOC/month
- **The bank returns to its own baseline after ten months and a full cycle** —
  13.3005 V measured, against a Nov 2025 baseline of 13.301 V restated on the
  INA228 scale
- **Post-charge relaxation resolved:** τ₁ = 2.16 h, τ₂ = 3.12 d, asymptote
  13.3042 V (n = 55,691 minute means, residual sd 5.6 mV). 99% relaxation at
  ≈14 days — a different process from the ≈30 min post-*load* rest rule
- **Noise floor fell 2.7 decades** — within-day voltage sd 60.25 mV → 0.131 mV
- **95-day storage stasis (Apr 1 – Jul 4) at +0.0074 ± 0.0655 mV/day, p = 0.91**
- **The quiescent drain is the monitor itself.** Operator confirmed 2026-08-26:
  Shelly retired, DROK panel meter retired, inverter connected but off, INA228
  monitor powered from the busbars — so in the low-side topology its return runs
  through the shunt and its own consumption is inside the measurement. 7.4 mA at
  13.35 V is 99 mW, against ~7.1 mA predicted for a Wi-Fi-associated XIAO
  ESP32-C3 behind an 87% buck. **The bank's own external parasitic load is
  effectively nil**, and the firmware header's "Monitor ~100 mA" is 14× high
- **The 2026-08-04 +2.9 mA step is an instrument offset shift, not a load.** The
  operator rewired the bank that afternoon to eliminate stacked lugs, with
  nothing added or removed. No load on the bus could consume 50% more — the
  monitor is the only one, it did not reboot, the firmware did not change — while
  joints in the shunt's own current path were unbolted and re-landed. At 375 µΩ
  the step is 1.08 µV, the same order as the chip's 0.9 µV commissioning offset.
  Two analyses that looked decisive and were not are recorded in report §7.4: the
  data-feed "blip" is indistinguishable from the 82 routine Wi-Fi dropouts in the
  window, and the voltage record cannot separate a load step from an offset step
  at day 19 post-charge because the relaxation tail dominates there

### Fixed
- Endurance figures were mixing capacity bases across reports: the README's
  "~11+ months to 80% SOC" applied the old 12.5 mA draw to the **500 Ah
  nameplate**, while the discharge test validated **397 Ah**. All endurance
  figures now use 397 Ah, and both draws are stated on that one basis
- `monthly_metrics.csv` March 2026 row described the month but covered five days
  of it

### Known Issues
- **The firmware coulomb ledger cannot see the quiescent drain.** Over the same
  32 continuous days: INA228 hardware CHARGE register −5.8222 Ah, independent
  integration −5.8019 Ah (0.35% apart), firmware ledger **−0.0149 Ah**. The
  ±0.05 A integration deadband is 6.7× larger than the 7.5 mA it excludes, so SOC
  reads 99.996% when the coulomb truth is ≈98.2% and drifts ≈1.4 %SOC per month
  of storage. Remedies proposed in report §6.5; **no firmware change made here**
- **The detector for this has never run.** `Cycle Integration Delta (SW−HW)`
  returns NaN until a full-charge anchor seeds its snapshot, and the hardware
  accumulators it reads were added after the only anchor this system has
  recorded. It has no InfluxDB series at all
- **Self-discharge + BMS standby is now bounded below 0.9 %SOC/month at 95%**
  (`P(> 2 %/month) = 0.02%`), by differencing the voltage and coulomb paths over
  the clean late window with all four uncertainties propagated. It is a ceiling,
  not a measurement: the median is negative, which is physically impossible, and
  the shunt offset is ~90% of the error budget. The bound sits under the 2-3
  %/month usually quoted for LiFePO4 and under this project's own commissioning
  estimate of 5 x BMS standby (4.9-9.8 mA = 0.9-1.8 %/month) - a tension the
  scheduled cycle resolves. Reproduce with `scripts/ina228_analysis.py`
- **True self-discharge is still unmeasured**, and the deadband above is in its
  way. The shunt sees only charge crossing the terminals; self-discharge is
  internal to the cells. The scheduled measurement — discharge below 80% SOC,
  then charge, then reconcile the full→full cycle — will misattribute the
  monitor's 0.177 Ah/day to the cells unless the ledger is fixed first: over a
  60-day storage leg that is 10.6 Ah = 2.7% of 397 Ah ≡ ≈1.3 %/month, inside the
  published LFP range and therefore an artefact that would read as a
  confirmation. Two earlier claims are withdrawn — "two loss paths agree to 11%,
  bounding self-discharge" (both uncertainties exceed the gap) and
  "self-discharge ~0%" (inherited from the Shelly era, never re-established)
- **Cycle-2 coulombic efficiency still unavailable.** One anchor has ever fired;
  `last_coulombic_efficiency` has read the commissioning floor 95.78% and
  `cv_absorption_time` 16.82 min, unchanged for 41 days. Needs a second full charge
- **Three firmware copies have diverged.** The device runs ≥V1.23 (it publishes
  `HW Net Charge (INA228)`); the repository YAML holds V1.20–V1.24 code under a
  V1.19 header; `H:/esphome/ina228-bringup.yaml` holds no V1.20+ code at all

---

## [2026-03-16] — 2026-03-16

### Added
- `CLAUDE.md` — machine-optimized Claude Code instruction file for all sessions; covers task-type routing, data format rules, validated baselines, known artifacts, halt conditions, monthly update procedure, report/README triggers, and current study state
- `data/monthly_metrics.csv` — new monthly summary dataset (one row per month, Oct 2025–Mar 2026); enables V-BATT range checks against trailing 3-month averages without re-parsing raw CSVs each session

### Changed
- `scripts/lifepo4_analysis.py` — refactored for maintainability:
  - Added `CONFIGURATION` block with named constants (`STASIS_START`, `STASIS_END`, `CHARGE_EVENT_DATE`, `ECO_MODE_DATETIME`, file paths) at top of script; CLAUDE comments mark which values to update each month
  - Replaced hardcoded `/mnt/user-data/uploads/` file paths with repo-relative `os.path` references
  - HF data loading now uses `glob.glob(HF_DIR + '/*.csv')` to auto-discover all weekly files; no manual file list needed when new weekly files are added
  - All hardcoded `pd.Timestamp('YYYY-MM-DD')` dates in script body replaced with config constant references
  - MA-60 segment boundaries auto-computed from stasis window; no hardcoded date list to maintain
  - Script title line now prints actual data end date dynamically from CSV
- `scripts/update_voltage_chart.py` — replaced three hardcoded Windows paths (`C:/Users/wkcol/...`) with repo-relative `os.path` references; script now runs correctly from any machine via `python scripts/update_voltage_chart.py` from repo root; added CLAUDE comment block listing HTML strings to update each month
- `data/README.md` — added `monthly_metrics.csv` to files overview table; added full schema section with column definitions and monthly update procedure

### Notes
- No data added in this release; all changes are infrastructure/tooling
- `monthly_metrics.csv` values computed from existing raw data — no new measurements

---

## [2026-03-06] — 2026-03-06

### Added
- Extended monitoring data through March 6, 2026 (130+ days total)
- High-frequency voltage data: Mar 2-6 (48,514 samples, 712k total)
- New report: `LiFePO4_Report_2026-03-06.md` with stasis assessment
- MA-60 trend analysis comparing current state to Nov 4 post-charge baseline

### Changed
- Updated data coverage in README and data/README.md
- Report links now point to latest March 6 report

### Key Findings
- **Approaching stasis:** MA-60 drift rate of -4.75 mV/day (below 5 mV/day threshold)
- **Voltage stabilizing:** Current 13.25V within 19 mV of Nov stasis baseline (13.27V)
- **Lower noise:** High-frequency std 5.6% lower than pre-charge stasis period
- **Faster settling:** Day 12 post-charge vs day 16 for Nov charge (partial top-up effect)

---

## [2026-03-01] — 2026-03-01

### Added
- Extended monitoring data through March 1, 2026 (125+ days total)
- February 22, 2026 charge event analysis (1.289 kWh AC, 81 Ah estimated)
- Post-charge relaxation tracking (Feb 22 - Mar 1)
- Self-discharge quantification (effectively 0%)
- Self-discharge validation against published literature (Section 5.5)
- **BMS balancing activity analysis** — ~80-90 sec balance cycles observed at 14.4V+ (Section 3)
- BMS balancing visualization figures (`fig_bms_balancing.png`, `fig_bms_balancing_detail.png`)
- Parasitic load calculation (12.5 mA measured vs 18-27 mA expected)
- High-frequency data extended to 663,683 samples
- Humidity data integration (1,488 hourly records)
- New report: `LiFePO4_Report_2026-03-01.md`

### Changed
- Updated storage endurance projection: 11+ months to 80% SOC (was 7-10 months)
- Revised parasitic load estimates based on measured data
- Shelly Plus Uni Eco Mode confirmed at ~2-6 mA (vs 8-12 mA spec)

### Key Findings
- **Self-discharge: ~0%** — All capacity loss attributable to monitoring equipment (validated vs. published data)
- **BMS balancing observed:** High-frequency data captured ~80-90 sec balance cycles during absorption phase
- **Charge event captured:** 309 mV voltage rise, typical relaxation curve
- **Architectural immunity maintained** through charge/discharge cycle

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
| 2026-03-06 | Oct 29, 2025 – Mar 6, 2026 | Dec 26, 2025 – Mar 6, 2026 (712,197 samples) |
| 2026-03-01 | Oct 29, 2025 – Mar 1, 2026 | Dec 26, 2025 – Mar 1, 2026 (663,683 samples) |
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
