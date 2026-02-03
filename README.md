# LiFePO₄ Battery Bank: Architectural Immunity & Long-Term Storage Study

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18452542.svg)](https://doi.org/10.5281/zenodo.18452542)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-CODE)
[![Data: Open](https://img.shields.io/badge/Data-Open%20Access-green.svg)](data/)
[![Last Updated](https://img.shields.io/badge/Data%20Through-Jan%2031%2C%202026-blue.svg)](reports/)

<a href="https://www.buymeacoffee.com/wkcollis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

## What This Is

A DIY **12V 500Ah LiFePO₄ battery bank** validated at 99% capacity with 94+ days of continuous voltage monitoring. This project demonstrates **architectural immunity**—the principle that parallel-connected mixed-brand cells achieve monolithic behavior through topology rather than cell matching.

**[📄 Read the Full Technical Report →](reports/LiFePO4_Report_2026-01-31.md)**

---

## Key Findings at a Glance

| Metric | Value | Details |
|--------|-------|---------|
| **Usable Capacity** | 397 Ah (99.3%) | [Discharge test](reports/) |
| **Inverter Efficiency** | 90.3% @ 440W avg | Peak 1880W |
| **Internal Resistance** | 4.9 mΩ total | System baseline |
| **Peukert Exponent** | k = 1.003 | Near-ideal linearity |
| **Stasis Drift** | −0.67 mV/day | Nov 22 → Jan 31, OLS on daily means |
| **Late-Jan Drift** | 0.16–0.30 mV/day | Window-dependent; see [methodology](docs/methodology.md) |
| **MA-60s Noise Reduction** | 42–50% | Segment-dependent band |
| **Storage Endurance** | ~7–10 mo to 80% SOC | At ~13–20 mA effective draw |

> **Note on drift rates:** Values are window- and estimator-dependent on a non-linear relaxation curve. We report both long-window (stasis-scale) and short-window (equilibrium-scale) slopes to quantify flattening. See [methodology](docs/methodology.md).

---

## Quick Start

```bash
# Clone
git clone https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks.git
cd Lifepo4-Battery-Banks

# Install dependencies
pip install -r requirements.txt

# Run analysis
python scripts/lifepo4_analysis.py
```

---

## Repository Map

```
├── README.md                     # You are here
├── data/
│   ├── README.md                 # Data dictionary (columns, units, cadence)
│   ├── combined_output.csv       # Hourly voltage, Oct 29 2025 → Jan 31 2026
│   ├── combined_temperature.csv  # Hourly temperature, Dec 29 2025 → Jan 31 2026
│   └── high_freq/                # ~3s cadence samples (release assets)
├── reports/
│   └── LiFePO4_Report_2026-01-31.md  # Full technical report
├── figures/
│   ├── fig1_voltage_timeline.png
│   ├── fig2_ma60_comparison.png
│   └── ...
├── scripts/
│   └── lifepo4_analysis.py       # Reproducible analysis pipeline
├── docs/
│   ├── methodology.md            # Estimators, windowing, definitions
│   ├── replication.md            # Hardware setup, calibration notes
│   └── evidence_map.md           # Claim → data → code → figure
├── CITATION.cff                  # Citation metadata
├── requirements.txt              # Python dependencies
└── LICENSE                       # Dual: CC BY 4.0 (data) + MIT (code)
```

---

## Core Claims (Summary)

### 1. Architectural Immunity
No evidence of divergence at the common bus potential, and no growing instability signatures consistent with imbalance (trendless anomalies; stable detrended variance). Spread inflation post-Eco Mode correlates with measurement-regime change, not electrochemical imbalance.

> **Caveat:** This study uses bus-level voltage only. Per-cell/block sensing would strengthen this claim.

### 2. Storage Viability
Drift is approaching equilibrium (75% rate reduction from full-period to last-30-day window). Projected **7–10 months to 80% SOC** at an effective draw of ~13–20 mA inferred from stasis behavior. System draw may be higher during telemetry bursts (Wi-Fi polling, etc.).

> **Highest-value next step:** Direct 24–72h bus-current measurement collapses SOC/endurance uncertainty in the flat-OCV region.

### 3. Temperature Sensitivity
System-level coefficient of **+1.0 ± 0.3 mV/°F** (pack + measurement chain combined). This is second-order relative to monotonic drift for endurance inference, but matters for seasonal extrapolation and residual fitting.

---

## Definitions

- **MA-60s** = Trailing, time-based 60-second rolling mean (`rolling('60s').mean()`)
- **Spread** = Hourly (Max − Min) from a single bus measurement (not per-cell)
- **Effective draw** = Parasitic current inferred from voltage drift (vs. instantaneous system draw)

---

## ⚠️ Safety Warning

**Lithium batteries carry inherent risks.** This 500Ah bank can deliver thousands of amps in a short circuit.

- Always use **Class T fuses** at terminals
- Never charge below **0°C (32°F)**
- **Always use a BMS** — architectural immunity does not replace cell protection
- Keep a **Class D fire extinguisher** accessible

**Disclaimer:** Information provided for educational purposes only. Build at your own risk.

---

## License

| Content | License |
|---------|---------|
| Data & Reports | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Code & Scripts | [MIT](LICENSE-CODE) |

---

## Citation

```bibtex
@misc{collis2026lifepo4,
  author       = {Collis, William K.},
  title        = {{LiFePO₄ Battery Bank: Architectural Immunity \& Long-Term Storage Study}},
  year         = {2026},
  publisher    = {GitHub},
  doi          = {10.5281/zenodo.14538065},
  url          = {https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable metadata.

---

## Contributing & Feedback

Peer review welcome! Please [open an Issue](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) for:
- Methodology questions or critiques
- Data quality observations
- Replication attempts
- Feature requests

---

## Support This Project

<a href="https://www.buymeacoffee.com/wkcollis1" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50"></a>

Your support funds continued monitoring, direct current measurement equipment, and documentation.

---

## Acknowledgments

- **Home Assistant Community** — Monitoring infrastructure
- **Shelly** — Plus Uni voltage hardware
- **Will Prowse / DIY Solar Power** — Educational inspiration
