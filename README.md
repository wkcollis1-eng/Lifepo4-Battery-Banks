<div align="center">

# ⚡ LiFePO₄ Battery Bank Study

### Architectural Immunity & Long-Term Storage Analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18452542.svg)](https://doi.org/10.5281/zenodo.18452542)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-CODE)
[![Data: Open](https://img.shields.io/badge/Data-Open%20Access-green.svg)](data/)
[![Last Updated](https://img.shields.io/badge/Data%20Through-Aug%2026%2C%202026-blue.svg)](reports/)
[![Instrument](https://img.shields.io/badge/Instrument-INA228%20%2B%20375%20%C2%B5%CE%A9%20shunt-6f42c1.svg)](INA228%20Monitor/)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![CI - LiFePO4 Battery Bank](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/actions/workflows/ci.yml/badge.svg)](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/actions/workflows/ci.yml)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-EA4AAA.svg?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/wkcollis1-eng)

*A DIY 12V 500Ah LiFePO₄ battery bank validated at 99% capacity, with 301 days of continuous monitoring
across two instruments — and a quiescent drain now measured, not inferred, at 7.4 mA*

</div>

---

## 📍 Quick Navigation

<table>
<tr>
<td width="25%" align="center">

**📊 [Data](data/)**<br>
Raw datasets & dictionary

</td>
<td width="25%" align="center">

**📄 [Full Report](reports/LiFePO4_Report_2026-08-26.md)**<br>
Complete technical analysis

</td>
<td width="25%" align="center">

**🔬 [Methodology](docs/methodology.md)**<br>
Methods & definitions

</td>
<td width="25%" align="center">

**🔁 [Replicate](docs/replication.md)**<br>
Build your own setup

</td>
</tr>
</table>

---

## 📋 What This Is

A DIY **12V 500Ah LiFePO₄ battery bank**, validated at **397 Ah** (99.3% of nameplate) by discharge test, under continuous monitoring since October 2025 — 301 days across two instruments. It demonstrates **architectural immunity**: the principle that parallel-connected mixed-brand cells achieve monolithic behavior through topology rather than cell matching.

Since July 2026 the bank has been instrumented by a purpose-built **INA228 monitor** on a 375 µΩ shunt, sampling voltage *and current* every 2 seconds. That closed the study's longest-standing open question: the quiescent drain, estimated for a year from voltage drift, is now **measured at 7.4 mA** — and with the Shelly and DROK meter retired and the inverter off, that current turns out to be the monitor itself.

> [!NOTE]
> **Architectural immunity** means the parallel bus connection forces all cells to the same voltage, eliminating the need for matched cells. This study provides empirical evidence supporting this principle.

**[📄 Read the Full Technical Report →](reports/LiFePO4_Report_2026-08-26.md)**

---

## 📈 Study Progress

| Phase | Status | Duration | Notes |
|:------|:------:|:--------:|:------|
| Discharge Testing | ✅ Complete | Oct 2025 | 397 Ah validated (99.3%) |
| Long-term Monitoring | ✅ Complete | 130+ days | Nov 2025 – Mar 2026 |
| Temperature Analysis | ✅ Complete | 62 days | +1.0 mV/°F coefficient |
| MA-60s Validation | ✅ Complete | 712k samples | 42–50% noise reduction |
| Charge Event Analysis | ✅ Complete | Feb 22, 2026 | 1.289 kWh, 81 Ah charged |
| Self-Discharge Analysis (Shelly era) | ⚠️ Superseded | 92 days | "~0%" was inherited from a 10 mV instrument; not re-established on the INA228 |
| Storage Stasis | ✅ Complete | 95 days | Apr–Jul 2026; drift +0.007 ± 0.066 mV/day (p = 0.91) |
| **Real outage** | ✅ Documented | 11.08 h | 2026-07-04; bank fine, **inverter failed** |
| **INA228 Commissioning** | ✅ Complete | Jul 13–16, 2026 | 8 defects found and closed; all acceptance criteria met |
| **Direct Current Measurement** | ✅ **Complete** | **41 days** | **7.4 mA measured — was the study's #1 open item** |
| **Charge/Discharge at 2 s** | ✅ Complete | Jul 2026 | 115.4 Ah charge, 110.7 Ah campaign, 130 A peak |
| Cycle-2 Coulombic Efficiency | 🔲 Blocked | — | Needs a second full charge; only one anchor has ever fired |
| **True self-discharge** | 🔲 Scheduled | — | Discharge <80% SOC → charge → reconcile. **Blocked on the §6 deadband fix first** |
| Winter INA228 window | 🔲 Planned | — | Every limit is currently stated at 68–70 °F |

---

## 📊 Key Findings at a Glance

| Metric | Value | Status | Details |
|:-------|------:|:------:|:--------|
| 🔋 **Usable Capacity** | 397 Ah (99.3%) | ✅ | [Discharge test](reports/) |
| ⚡ **Quiescent Drain** | **7.4 ± 2.4 mA measured** | ✅ | **New:** 41 d, 1.79 M samples. It is the monitor — the bank's own external load is nil |
| ⏱️ **Storage Endurance** | **≈15 months to 80% SOC** | ✅ | On 397 Ah at the measured drain; band 11–22 months |
| 📉 **Stasis Drift** | **−0.303 mV/day** | ✅ | 7-day OLS, se 0.008, p = 2.2×10⁻⁷ — now resolvable |
| 🔋 **Self-discharge + BMS** | **< 0.9 %/month (95%)** | ⚠️ | A *bound*, not a measurement — shunt sees only terminal current. Full→full cycle scheduled |
| 🔌 **Internal Resistance** | 3.73 mΩ (2-min DC-IR) | ✅ | Aging baseline, 69 °F, ~80% SOC |
| ⚡ **Inverter Efficiency** | 87–94% (provisional) | ⚠️ | Window-alignment limited; definitive run outstanding |
| 🔌 **Charger AC→DC** | 95.7% ± 2.5% | ✅ | LiTime 80 A, Kill-A-Watt ledger |
| 🔁 **Round-trip energy** | ~94.8% | ✅ | Voltaic 95.8% × CE |
| 📐 **Peukert Exponent** | k = 1.003 | ✅ | Near-ideal linearity |
| 📊 **Voltage Noise Floor** | **0.131 mV within-day sd** | ✅ | Below the INA228's own 195.3 µV bus LSB |
| ⚖️ **BMS Balancing** | ~80–90 s cycles | ✅ | 183 mV pk-pk above 14.4 V, now countable |
| 🌡️ **Temperature Sensitivity** | +1.0 ± 0.3 mV/°F | ✅ | System-level (pack + measurement chain) |
| ⚠️ **SOC ledger blind spot** | 1.46 %SOC unbooked / 32 d | ⚠️ | ±50 mA firmware deadband hides the 7.4 mA drain — [see §6](reports/LiFePO4_Report_2026-08-26.md) |
| 🔌 **Real outage survived** | **11.08 h**, 340 mV margin | ✅ | 2026-07-04; bank never approached an alarm |
| ⚠️ **Coincident peak vs inverter** | **3328 W vs 1500 W** | ⚠️ | Fridge inrush 22× + coffee maker; on 34 of 45 days |

> [!IMPORTANT]
> **Two instruments, one scale.** The Shelly Plus Uni was retired 2026-07-16 and
> reads **30.6 mV low** against the INA228 (n = 148 gated pairs, 95% CI ±1.3 mV;
> usable uncertainty ±3 mV). **Add 30.6 mV to any pre-July-2026 voltage in this
> repository before comparing it with a later one.**

> [!TIP]
> Drift rates are window- and estimator-dependent on a non-linear relaxation curve.
> We report both long-window (stasis-scale) and short-window (equilibrium-scale)
> slopes to quantify flattening. See [methodology](docs/methodology.md) for details.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks.git
cd Lifepo4-Battery-Banks

# Install Python dependencies
pip install -r requirements.txt

# Reproduce the current (INA228-era) report — no host access needed
python scripts/ina228_analysis.py

# Reproduce the earlier Shelly-era analysis
python scripts/lifepo4_analysis.py
```

**Expected output:**
- Every figure and headline number in the [2026-08-26 report](reports/LiFePO4_Report_2026-08-26.md),
  printed to console and written to `figures/`
- Drift, relaxation, parasitic-drain, coulomb-ledger and cross-calibration statistics
- All of it computed from the CSVs in `data/` — nothing is fetched at runtime

---

## 📂 Repository Structure

```
Lifepo4-Battery-Banks/
│
├── 📄 README.md                        ← You are here
├── 📋 CHANGELOG.md                     ← Version history
│
├── ⚡ INA228 Monitor/                   ← The current instrument
│   ├── Battery-Bank-Monitor-Commissioning-Report.md
│   ├── battery-bank-monitor-wiring-summary-v1_10.md
│   └── battery-bank-monitor.yaml       ← ESPHome firmware
│
├── 📊 data/
│   ├── README.md                       ← Data dictionary (read this first)
│   ├── ina228/                         ← INA228 era, Jul 2026 onward
│   │   ├── ina228_hourly_*.csv         ← Hourly V/I/P, Ah, Wh, temps
│   │   ├── ina228_daily_*.csv          ← Daily, same columns
│   │   ├── stasis_ma60_*.csv.gz        ← 1-min MA-60s voltage means
│   │   ├── coulomb_ledger_hourly.csv   ← Hardware vs software vs independent
│   │   ├── shelly_ina228_crosscheck.csv ← The two-instrument offset
│   │   └── events/                     ← Full 2 s resolution, charge & discharge
│   ├── combined_output.csv             ← Shelly hourly voltage (Oct 2025 – Mar 2026)
│   ├── shelly_daily_min_*.csv          ← Shelly daily minima (Apr – Jul 2026)
│   ├── combined_temperature.csv        ← Hourly temperature
│   ├── combined_humidity.csv           ← Hourly humidity
│   ├── monthly_metrics.csv             ← One row per month, both eras
│   └── high_freq_voltage/              ← Shelly HF samples, weekly files
│
├── 📄 reports/
│   ├── LiFePO4_Report_2026-08-26.md    ← Current report (INA228 era)
│   └── LiFePO4_Report_2026-03-31.md    ← Last Shelly-era report
│
├── 📈 figures/
│   ├── fig_ina228_*.png                ← Current-era figures
│   └── fig1_voltage_timeline.png …     ← Shelly-era figures
│
├── 🐍 scripts/
│   ├── ina228_analysis.py              ← Reproduces the current report
│   ├── ina228_export.py                ← Rebuilds data/ina228/ from InfluxDB
│   ├── update_monthly_metrics.py       ← Rebuilds monthly_metrics.csv
│   └── lifepo4_analysis.py             ← Shelly-era pipeline
│
├── 📚 docs/
│   ├── methodology.md                  ← Estimators, windowing, definitions
│   ├── replication.md                  ← Hardware setup, calibration
│   ├── evidence_map.md                 ← Claim → data → code → figure
│   ├── glossary.md                     ← Terms & abbreviations
│   └── faq.md                          ← Frequently asked questions
│
├── 📜 CITATION.cff                     ← Citation metadata
├── 📋 requirements.txt                 ← Python dependencies
├── ⚖️ LICENSE                          ← Dual: CC BY 4.0 (data) + MIT (code)
└── ⚖️ LICENSE-CODE                     ← MIT license for scripts
```

---

<details>
<summary><strong>🔬 Core Claims (Technical Summary)</strong></summary>

### 1. Architectural Immunity

No evidence of divergence at the common bus potential, and no growing instability signatures consistent with imbalance (trendless anomalies; stable detrended variance). Spread inflation post-Eco Mode correlates with measurement-regime change, not electrochemical imbalance.

> **Caveat:** This study uses bus-level voltage only. Per-cell/block sensing would strengthen this claim.

### 2. Storage Viability — measured, and the load turns out to be the instrument

The bank draws **7.4 ± 2.4 mA** in storage: a time-weighted mean over 41 quiescent
days and 1.79 M samples at 99.93% coverage, on a 375 µΩ shunt read by a 20-bit
front end. That is **≈15 months to 80% SOC** and **≈59 months to the 20% operator
floor** on the validated 397 Ah.

**What is drawing it:** the Shelly and the DROK panel meter are both retired and
the inverter is off, so the INA228 monitor — powered from the busbars, its return
running through the shunt — is the only load on the bus. 7.4 mA at 13.35 V is
**99 mW**, which is what a Wi-Fi-associated XIAO ESP32-C3 behind an 87% buck
converter should draw. **The bank's own external parasitic load is effectively
nil**, and the endurance figures above describe how long the instrument can watch
the bank rather than a property of the bank.

The ±2.4 mA is not statistical — the 41-day mean is tight. It is this INA228's
commissioning-measured 0.9 µV shunt offset, which averaging cannot reduce and
which a clamp-meter calibration would.

> **Superseded:** earlier versions projected 7–10 months to 80% SOC at "~13–20 mA
> inferred from stasis behaviour," and listed direct bus-current measurement as the
> highest-value next step. **That measurement is done.** The inferred band was
> 42–63% high. The inference was not unreasonable on a 10 mV instrument — it was
> simply untestable until there was a current sensor on the bank.

### 2c. Self-discharge is NOT what this measures

The shunt sees charge crossing the terminals. Self-discharge — and the five
internal BMS boards' standby draw — happen behind them and do not cross it.
**No figure in this study is a *measurement* of true self-discharge**; the "~0%"
carried in earlier releases is inherited from the Shelly-era study, on an
instrument that could not resolve 0.3 mV/day.

What this release does add is a **bound**. Differencing the voltage path (total
SOC decline) against the coulomb path (terminal current) over the one clean
window, with all four uncertainties propagated, puts the combined internal term
**below 0.9 %SOC/month at 95% confidence**, `P(> 2 %/month) = 0.02%`. That is
under the 2–3 %/month commonly quoted for LiFePO₄ — plausibly, because datasheet
figures are conservative and often taken at higher temperature, because most of
the quoted figure is first-month settling, and because it replicates this
study's own earlier result by a second method.

It remains a ceiling and not a measurement: the median comes out *negative*,
which self-discharge cannot be, and the shunt offset alone is ~90% of the error
budget.

The measurement is scheduled: reach stasis (done), discharge below 80% SOC, then
charge, and reconcile the full→full cycle. **Its prerequisite is the deadband fix
in §2b** — run it first, or the monitor's own 0.177 Ah/day is booked as
self-discharge, an artefact of ≈1.3 %/month that lands inside the published LFP
range and reads as a confirmation.

### 2b. Instrument Self-Awareness

The firmware's coulomb ledger applies a ±0.05 A deadband before integrating — 6.7×
larger than the drain above. Over 31.96 continuous days the INA228's own hardware
CHARGE register accumulated −5.8222 Ah and an independent integration of the
published series returned −5.8019 Ah (0.35% apart), while the firmware's ledger
recorded **−0.0149 Ah**. SOC therefore reads 99.996% when the coulomb truth is
≈98.2%, drifting ≈1.4 %SOC per month of storage.

This is published rather than quietly fixed because it is the more useful finding:
a coulomb counter with a noise-rejection deadband is a *standard* design, and any
replication of this build on any BMS will have the same blind spot in storage
unless it is looked for. See [§6 of the current report](reports/LiFePO4_Report_2026-08-26.md)
for the three-way ledger and the proposed remedies.

### 3. Temperature Sensitivity

System-level coefficient of **+1.0 ± 0.3 mV/°F** (pack + measurement chain combined). This is second-order relative to monotonic drift for endurance inference, but matters for seasonal extrapolation and residual fitting.

</details>

---

<details>
<summary><strong>📐 Definitions</strong></summary>

| Term | Definition |
|:-----|:-----------|
| **MA-60s** | Trailing, time-based 60-second rolling mean (`rolling('60s').mean()`) |
| **Spread** | Hourly (Max − Min) from a single bus measurement (not per-cell) |
| **Effective draw** | Parasitic current inferred from voltage drift. **Superseded from Jul 2026** by the directly measured quiescent drain |
| **Quiescent drain** | Time-weighted mean bank current with no charger and no deliberate load, measured on the shunt |
| **Coulomb ledger** | The running Ah account that anchors SOC. Three exist here: firmware, INA228 silicon, and independent re-integration |
| **OLS** | Ordinary Least Squares — standard linear regression method |
| **SOC** | State of Charge — remaining battery capacity as percentage |

For complete terminology, see the [Glossary](docs/glossary.md).

</details>

---

## ⚠️ Safety Warning

> [!CAUTION]
> **Lithium batteries carry inherent risks.** This 500Ah bank can deliver thousands of amps in a short circuit.

- ✅ Always use **Class T fuses** at terminals
- ✅ Never charge below **0°C (32°F)**
- ✅ **Always use a BMS** — architectural immunity does not replace cell protection
- ✅ Keep a **Class D fire extinguisher** accessible

**Disclaimer:** Information provided for educational purposes only. Build at your own risk.

---

## 📚 Documentation

| Document | Description |
|:---------|:------------|
| [📄 Technical Report](reports/LiFePO4_Report_2026-08-26.md) | Complete analysis with all results |
| [⚡ Commissioning Report](INA228%20Monitor/Battery-Bank-Monitor-Commissioning-Report.md) | Build, defects, acceptance tests for the INA228 monitor |
| [🔬 Methodology](docs/methodology.md) | Statistical methods and definitions |
| [🔁 Replication Guide](docs/replication.md) | Hardware setup and calibration |
| [🗺️ Evidence Map](docs/evidence_map.md) | Claim → data → code → figure traceability |
| [📖 Glossary](docs/glossary.md) | Terms and abbreviations |
| [❓ FAQ](docs/faq.md) | Frequently asked questions |
| [📊 Data Dictionary](data/README.md) | Dataset documentation |

---

## 📜 License

| Content Type | License | SPDX |
|:-------------|:--------|:-----|
| Data & Reports | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | CC-BY-4.0 |
| Code & Scripts | [MIT](LICENSE-CODE) | MIT |

---

## 📝 Citation

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

See [CITATION.cff](CITATION.cff) for machine-readable metadata.

---

## 🔗 Related Projects

- **[DIY LiFePO₄ UPS](https://github.com/wkcollis1-eng/DIY-LiFePO4-UPS)** — 12V UPS for Home Assistant and network equipment using similar monitoring approach
- **[Home Assistant Config](https://github.com/wkcollis1-eng/home-assistant-config)** — Production HA configuration with statistical process control for HVAC monitoring
- **[HVAC Performance Baseline](https://github.com/wkcollis1-eng/Residential-HVAC-Performance-Baseline-)** — 50-month residential energy study with similar data-driven methodology

---

## 🤝 Contributing & Feedback

Peer review welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- 🐛 [Report issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) — Methodology questions, data errors
- 💡 [Start a discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions) — Ideas, replication attempts
- 📊 Submit your own replication data via Pull Request

---

## 💝 Support This Project

<a href="https://www.buymeacoffee.com/wkcollis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50"></a>
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/wkcollis1-eng)

Your support funds continued monitoring, direct current measurement equipment, and documentation improvements. One-time or monthly sponsorship both help.

---

## 🙏 Acknowledgments

- **[Home Assistant Community](https://www.home-assistant.io/)** — Monitoring infrastructure and integration support
- **[Shelly](https://www.shelly.com/)** — Plus Uni voltage monitoring hardware
- **[Will Prowse / DIY Solar Power](https://www.youtube.com/@WillProwse)** — Educational inspiration and community building
- **[Zenodo](https://zenodo.org/)** — DOI registration and data archiving
- **DIY Solar Community** — Peer feedback and methodology review

---

<div align="center">

*Made with ⚡ in Connecticut*

</div>
