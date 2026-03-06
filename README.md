<div align="center">

# ⚡ LiFePO₄ Battery Bank Study

### Architectural Immunity & Long-Term Storage Analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18452542.svg)](https://doi.org/10.5281/zenodo.18452542)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-CODE)
[![Data: Open](https://img.shields.io/badge/Data-Open%20Access-green.svg)](data/)
[![Last Updated](https://img.shields.io/badge/Data%20Through-Mar%206%2C%202026-blue.svg)](reports/)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

*A DIY 12V 500Ah LiFePO₄ battery bank validated at 99% capacity with 94+ days of continuous voltage monitoring*

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

**📄 [Full Report](reports/LiFePO4_Report_2026-03-06.md)**<br>
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

A DIY **12V 500Ah LiFePO₄ battery bank** validated at 99% capacity with 94+ days of continuous voltage monitoring. This project demonstrates **architectural immunity**—the principle that parallel-connected mixed-brand cells achieve monolithic behavior through topology rather than cell matching.

> [!NOTE]
> **Architectural immunity** means the parallel bus connection forces all cells to the same voltage, eliminating the need for matched cells. This study provides empirical evidence supporting this principle.

**[📄 Read the Full Technical Report →](reports/LiFePO4_Report_2026-03-06.md)**

---

## 📈 Study Progress

| Phase | Status | Duration | Notes |
|:------|:------:|:--------:|:------|
| Discharge Testing | ✅ Complete | Oct 2025 | 397 Ah validated (99.3%) |
| Long-term Monitoring | ✅ Complete | 130+ days | Nov 2025 – Mar 2026 |
| Temperature Analysis | ✅ Complete | 62 days | +1.0 mV/°F coefficient |
| MA-60s Validation | ✅ Complete | 712k samples | 42–50% noise reduction |
| Charge Event Analysis | ✅ Complete | Feb 22, 2026 | 1.289 kWh, 81 Ah charged |
| Self-Discharge Analysis | ✅ Complete | 92 days | **~0% self-discharge confirmed** |
| Direct Current Measurement | 🔲 Planned | — | Validate 12.5 mA calculated |

---

## 📊 Key Findings at a Glance

| Metric | Value | Status | Details |
|:-------|------:|:------:|:--------|
| 🔋 **Usable Capacity** | 397 Ah (99.3%) | ✅ | [Discharge test](reports/) |
| ⚡ **Inverter Efficiency** | 90.3% @ 440W avg | ✅ | Peak 1880W |
| 🔌 **Internal Resistance** | 4.9 mΩ total | ✅ | System baseline |
| 📐 **Peukert Exponent** | k = 1.003 | ✅ | Near-ideal linearity |
| 📉 **Stasis Drift** | −0.575 mV/day | ✅ | Nov 22 – Feb 21, OLS on daily means |
| 🔋 **Self-Discharge** | ~0% | ✅ | Validated vs. published data; all loss from parasitic loads |
| ⚡ **Parasitic Draw** | 12.5 mA measured | ✅ | **New:** Drok ~10mA + Shelly ~2-6mA |
| 📊 **MA-60s Noise Reduction** | 42–50% | ✅ | Segment-dependent band |
| ⚖️ **BMS Balancing** | ~80-90 sec cycles | ✅ | Observed at 14.4V+ during charge |
| ⏱️ **Storage Endurance** | ~11+ months to 80% SOC | ✅ | At measured 12.5 mA draw |

> [!TIP]
> Drift rates are window- and estimator-dependent on a non-linear relaxation curve. We report both long-window (stasis-scale) and short-window (equilibrium-scale) slopes to quantify flattening. See [methodology](docs/methodology.md) for details.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks.git
cd Lifepo4-Battery-Banks

# Install Python dependencies
pip install -r requirements.txt

# Run the analysis pipeline
python scripts/lifepo4_analysis.py
```

**Expected output:**
- Drift analysis statistics printed to console
- Figures generated in `figures/` directory
- Summary metrics for all key claims

---

## 📂 Repository Structure

```
Lifepo4-Battery-Banks/
│
├── 📄 README.md                      ← You are here
├── 📋 CHANGELOG.md                   ← Version history
│
├── 📊 data/
│   ├── README.md                     ← Data dictionary
│   ├── combined_output.csv           ← Hourly voltage (Oct 29, 2025 – Mar 5, 2026)
│   ├── combined_temperature.csv      ← Hourly temperature (Jan 1 – Mar 6, 2026)
│   ├── combined_humidity.csv         ← Hourly humidity (Jan 1 – Mar 6, 2026)
│   └── high_freq_voltage/            ← High-frequency samples (~3s cadence)
│       └── voltage_data_YYYY-MM-DD_to_YYYY-MM-DD.csv  ← Weekly consolidated files
│
├── 📄 reports/
│   └── LiFePO4_Report_2026-03-06.md  ← Full technical report
│
├── 📈 figures/
│   ├── fig1_voltage_timeline.png     ← Primary visualization
│   ├── fig2_ma60_comparison.png      ← Noise reduction demo
│   └── ...                           ← Additional figures
│
├── 🐍 scripts/
│   └── lifepo4_analysis.py           ← Reproducible analysis pipeline
│
├── 📚 docs/
│   ├── methodology.md                ← Estimators, windowing, definitions
│   ├── replication.md                ← Hardware setup, calibration
│   ├── evidence_map.md               ← Claim → data → code → figure
│   ├── glossary.md                   ← Terms & abbreviations
│   └── faq.md                        ← Frequently asked questions
│
├── 📜 CITATION.cff                   ← Citation metadata
├── 📋 requirements.txt               ← Python dependencies
├── ⚖️ LICENSE                        ← Dual: CC BY 4.0 (data) + MIT (code)
└── ⚖️ LICENSE-CODE                   ← MIT license for scripts
```

---

<details>
<summary><strong>🔬 Core Claims (Technical Summary)</strong></summary>

### 1. Architectural Immunity

No evidence of divergence at the common bus potential, and no growing instability signatures consistent with imbalance (trendless anomalies; stable detrended variance). Spread inflation post-Eco Mode correlates with measurement-regime change, not electrochemical imbalance.

> **Caveat:** This study uses bus-level voltage only. Per-cell/block sensing would strengthen this claim.

### 2. Storage Viability

Drift is approaching equilibrium (75% rate reduction from full-period to last-30-day window). Projected **7–10 months to 80% SOC** at an effective draw of ~13–20 mA inferred from stasis behavior. System draw may be higher during telemetry bursts (Wi-Fi polling, etc.).

> **Highest-value next step:** Direct 24–72h bus-current measurement collapses SOC/endurance uncertainty in the flat-OCV region.

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
| **Effective draw** | Parasitic current inferred from voltage drift (vs. instantaneous system draw) |
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
| [📄 Technical Report](reports/LiFePO4_Report_2026-03-06.md) | Complete analysis with all results |
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

## 🤝 Contributing & Feedback

Peer review welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- 🐛 [Report issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) — Methodology questions, data errors
- 💡 [Start a discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions) — Ideas, replication attempts
- 📊 Submit your own replication data via Pull Request

---

## 💝 Support This Project

<a href="https://www.buymeacoffee.com/wkcollis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50"></a>

Your support funds continued monitoring, direct current measurement equipment, and documentation improvements.

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
