# LiFePO₄ Battery Bank: Architectural Immunity Study

[![DOI](https://zenodo.org/badge/1110266162.svg)](https://doi.org/10.5281/zenodo.18232628)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Data: Available](https://img.shields.io/badge/Data-Available-green.svg)](Data/)
[![Status: Active](https://img.shields.io/badge/Status-Active%20Research-blue.svg)](#update-history)

> **TL;DR:** A 73-day study proving mixed-brand LiFePO₄ cells achieve monolithic behavior in parallel topology. Full data, analysis scripts, and replication protocol included.

---

## ⚠️ Safety Warning

> **IMPORTANT:** LiFePO₄ batteries store significant energy and require proper safety precautions.
> 
> - Always wear safety glasses when working with batteries
> - Use insulated tools to prevent short circuits
> - Never exceed BMS current ratings
> - Ensure adequate ventilation during charging
> - This documentation is for educational purposes only
> 
> **The author assumes no liability for damages resulting from replication attempts. Build at your own risk.**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Why This Matters](#why-this-matters)
3. [Key Findings](#key-findings)
4. [Quick Start](#quick-start)
5. [System Configuration](#system-configuration)
6. [Repository Contents](#repository-contents)
7. [How to Use the Data](#how-to-use-the-data)
8. [Methodology](#methodology)
9. [Results Summary](#results-summary)
10. [Replication Protocol](#replication-protocol)
11. [Contributing](#contributing)
12. [Citation](#citation)
13. [Update History](#update-history)
14. [License & Contact](#license--contact)

---

## Executive Summary

This repository documents a **73-day continuous monitoring study** of a DIY 12V 500Ah LiFePO₄ battery bank using mixed-brand cells (3× LIPULS + 2× Cyclenbatt) in a 1S5P parallel configuration.

**The central hypothesis:** In a purely parallel topology with low bus-bar resistance, the architecture itself forces cells to behave as a monolithic unit—a property we call **"Architectural Immunity."**

### Performance Highlights

| Metric | Value | Significance |
|--------|-------|--------------|
| **Usable Capacity** | 397Ah (99.3% of rated) | Exceeds manufacturer claims |
| **System Efficiency** | 90.3% | Excellent for inverter systems |
| **Peak Load** | 1,880W AC (160A DC) | No BMS trip events |
| **Peukert Exponent** | k = 1.003 ± 0.02 | Near-ideal linearity |
| **Voltage Stability** | σ = 0.0050V (60s MA) | Exceptional consistency |
| **Parasitic Load** | 20-25 mA | 1.8-2.3 year standby |

---

## Why This Matters

**The Problem:** DIY battery builders are universally told "never mix battery brands." This advice is based on series configurations where cell mismatch causes dangerous imbalances. But is it true for parallel banks?

**The Gap:** No rigorous, long-term data existed for mixed-brand parallel LiFePO₄ configurations. Forum posts and YouTube videos lack statistical rigor, raw data, or reproducible protocols.

**This Study Fills That Gap By Providing:**
- ✅ 73+ days of continuous voltage monitoring
- ✅ Raw CSV data for independent verification
- ✅ Statistical analysis with confidence intervals
- ✅ Complete replication protocol
- ✅ Open-source analysis scripts

### Comparison to Existing Resources

| Source | Duration | Mixed Brands | Raw Data | Statistics | Protocol |
|--------|----------|--------------|----------|------------|----------|
| **This Study** | 73+ days | ✅ Yes | ✅ CSV | ✅ p<0.001 | ✅ Complete |
| Manufacturer Specs | — | ❌ No | ❌ No | ❌ No | ❌ No |
| Forum Posts | Hours-days | Varies | ❌ No | ❌ No | ❌ No |
| Academic Papers | Varies | ❌ Usually No | ⚠️ Sometimes | ✅ Yes | ⚠️ Limited |

---

## Key Findings

### V8.3 Update (January 8, 2026)

**Verified Claims:**
- ✅ 100% SOC resting voltage: 13.27-13.28V at 60-65°F
- ✅ Dec 19 voltage anomaly: Confirmed EMI/Wi-Fi artifact (not battery issue)
- ✅ Eco Mode effect: -5.8mV baseline shift (as expected)
- ✅ Parasitic load calculations: Verified correct

**New Insights:**
- 📉 Winter drift corrected: 40mV over 46 days (0.87mV/day)—45% of originally reported value
- 🌡️ Thermal coefficient: 0.21mV/°F (lower than expected; drift primarily instrumentation artifact)
- 📊 60-second MA analysis: 9.06mV ADC noise floor, 5.02mV true system stability
- ✅ No cell divergence: Spread increase is Eco Mode instrumentation artifact, not cell imbalance

---

## Quick Start

### For DIY Builders
1. Download the [V8.3 Report (PDF)](Reports/Battery_Analysis_V8.3_Deep_Dive_Report.pdf)
2. Compare your system to the [System Configuration](#system-configuration)
3. Benchmark against the [Performance Highlights](#performance-highlights)

### For Researchers
1. Clone this repository: `git clone https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks.git`
2. Review the [Methodology](docs/METHODS.md)
3. Run the analysis: `python Scripts/battery_analysis.py`
4. Explore raw data in `Data/combined_output.csv`

### For Contributors
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check open [Issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues)
3. Join the [Discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions)

---

## System Configuration

| Component | Specification |
|-----------|--------------|
| **Configuration** | 1S5P (5 × 12V 100Ah in parallel) |
| **Total Capacity** | 500Ah Nominal / 400Ah Usable |
| **Chemistry** | Lithium Iron Phosphate (LiFePO₄) |
| **Cell Mix** | 3× LIPULS + 2× Cyclenbatt |
| **BMS** | Distributed (5 × 100A units per cell) |
| **Interconnects** | 2 AWG pure copper, star topology |
| **Bus Bar Resistance** | <1 mΩ per connection |
| **Inverter** | Giandel 1500W Pure Sine |
| **Monitoring** | Shelly Plus Uni (ESP32 Wi-Fi sensor) |

### Topology Diagram

```
                    ┌─────────────────┐
                    │   LOAD / INV    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
         │ LIPULS  │    │ LIPULS  │    │ LIPULS  │
         │  100Ah  │    │  100Ah  │    │  100Ah  │
         └────┬────┘    └────┬────┘    └────┬────┘
              │              │              │
         ┌────┴────┐    ┌────┴────┐
         │CYCLENBAT│    │CYCLENBAT│
         │  100Ah  │    │  100Ah  │
         └────┬────┘    └────┬────┘
              │              │
              └──────────────┴──────────────┘
                             │
                    ┌────────┴────────┐
                    │   COMMON BUS    │
                    │   (2 AWG Cu)    │
                    └─────────────────┘
```

---

## Repository Contents

```
Lifepo4-Battery-Banks/
├── README.md                          # This file
├── CONTRIBUTING.md                    # Contribution guidelines
├── CODE_OF_CONDUCT.md                 # Community standards
│
├── Reports/
│   └── Battery_Analysis_V8.3_Deep_Dive_Report.pdf
│
├── Data/
│   ├── combined_output.csv            # Hourly min/max voltage (73 days)
│   ├── Combined_Temperature_Data.csv  # Basement temperature logs
│   └── Combined_Humidity_Data.csv     # Environmental humidity
│
├── Charts/
│   ├── fig1_voltage_timeline.png      # Full monitoring history
│   ├── fig2_spread_analysis.png       # Cell balance indicator
│   ├── fig3_high_freq_analysis.png    # 60-second moving average
│   ├── fig4_temp_correlation.png      # Temperature vs voltage
│   ├── fig5_drift_analysis.png        # Long-term drift rate
│   └── fig6_anomaly_analysis.png      # Anomaly detection
│
├── Scripts/
│   ├── battery_analysis.py            # Main analysis script
│   ├── visualizations.py              # Chart generation
│   └── spread_investigation.py        # Cell divergence study
│
├── docs/
│   └── METHODS.md                     # Detailed methodology
│
└── .github/
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        ├── data_request.md
        └── feature_request.md
```

---

## How to Use the Data

### Data Format

**combined_output.csv** (primary dataset):
```csv
Timestamp,Voltage_Min,Voltage_Max
2025-10-26 00:00:00,13.271,13.282
2025-10-26 01:00:00,13.270,13.281
...
```

- **Timestamp**: ISO 8601 format, hourly samples
- **Voltage_Min**: Minimum voltage reading in the hour (V)
- **Voltage_Max**: Maximum voltage reading in the hour (V)

### Quick Analysis (Python)

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('Data/combined_output.csv', parse_dates=['Timestamp'])
df['Voltage_Avg'] = (df['Voltage_Min'] + df['Voltage_Max']) / 2
df['Spread'] = df['Voltage_Max'] - df['Voltage_Min']

# Plot voltage timeline
plt.figure(figsize=(12, 6))
plt.plot(df['Timestamp'], df['Voltage_Avg'])
plt.xlabel('Date')
plt.ylabel('Voltage (V)')
plt.title('Battery Bank Voltage Over Time')
plt.savefig('voltage_plot.png')
```

### Statistical Validation

```python
# Verify key claims
print(f"Mean Voltage: {df['Voltage_Avg'].mean():.4f} V")
print(f"Std Dev: {df['Voltage_Avg'].std():.4f} V")
print(f"Mean Spread: {df['Spread'].mean()*1000:.2f} mV")
```

---

## Methodology

For complete methodology including measurement protocols, calibration procedures, and uncertainty analysis, see **[docs/METHODS.md](docs/METHODS.md)**.

### Summary

1. **Voltage Monitoring**: Shelly Plus Uni ESP32 sensor, 60-second sampling, hourly aggregation
2. **Temperature Logging**: Concurrent basement temperature for thermal correlation
3. **Isolation Tests**: Inverter disconnected to measure true parasitic load
4. **Discharge Tests**: Full capacity verification under controlled load
5. **Statistical Analysis**: Python-based analysis with uncertainty quantification

### Key Equations

**Peukert's Law:**
```
t = C / I^k
```
Where: t = discharge time, C = capacity, I = current, k = Peukert exponent

**Measured:** k = 1.003 ± 0.02 (ideal = 1.00)

**Self-Discharge Rate:**
```
Monthly loss = (Parasitic_mA × 24 × 30) / (Capacity_Ah × 1000) × 100%
```
**Measured:** 0.15%/month at 20-25mA parasitic

---

## Results Summary

### Voltage Stability

![Voltage Timeline](Charts/fig1_voltage_timeline.png)

The 73-day voltage record shows exceptional stability with no drift beyond instrumentation artifacts.

### Cell Balance

![Spread Analysis](Charts/fig2_spread_analysis.png)

Max-Min spread remains under 15mV throughout the study, confirming architectural immunity.

### Temperature Correlation

![Temperature Correlation](Charts/fig4_temp_correlation.png)

Thermal coefficient of 0.21mV/°F—lower than typical LiFePO₄ specs, indicating stable chemistry.

---

## Replication Protocol

### Requirements

- 3+ parallel LiFePO₄ cells (any brand mix)
- Low-resistance bus bar (2 AWG or better)
- Voltage monitoring (±1mV resolution recommended)
- Temperature logging (optional but recommended)

### Steps

1. **Configure Bank**: Wire cells in parallel with equal-length cables, star topology
2. **Establish Baseline**: Charge to 100% SOC, record resting voltage after 24h
3. **Enable Monitoring**: Log voltage at minimum 1-hour intervals
4. **Collect Data**: Minimum 30 days recommended (90+ days for seasonal effects)
5. **Analyze**: Calculate spread, drift rate, and correlation with temperature
6. **Validate**: Compare to expected metrics:
   - Spread: <20mV
   - Drift: <1mV/day
   - Peukert k: <1.05

### Expected Results

If your parallel bank exhibits "architectural immunity":
- All cells converge to within 10-20mV regardless of brand
- No progressive divergence over time
- Voltage responds uniformly to load

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 📊 **Submit Your Data**: Replicate the study with your own battery bank
- 🐛 **Report Issues**: Found an error in calculations? [Open an issue](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues)
- 💡 **Suggest Improvements**: Have ideas? [Start a discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions)
- 🔧 **Improve Analysis**: Submit PRs with enhanced scripts or visualizations

---

## Citation

If you use this work in your project or research, please cite:

### BibTeX
```bibtex
@techreport{collis2026architectural,
  title={Architectural Immunity in Heterogeneous LiFePO₄ Parallel Arrays: 
         A 73-Day Monitoring Study},
  author={Collis, Bill},
  year={2026},
  month={January},
  institution={Independent Research},
  url={https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks}
}
```

### APA
Collis, B. (2026). *Architectural immunity in heterogeneous LiFePO₄ parallel arrays: A 73-day monitoring study* [Technical report]. GitHub. https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks

### IEEE
B. Collis, "Architectural Immunity in Heterogeneous LiFePO₄ Parallel Arrays," Independent Research, East Hampton, CT, Tech. Rep., Jan. 2026. [Online]. Available: https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks

---

## Update History

| Version | Date | Description |
|---------|------|-------------|
| **V8.3** | Jan 8, 2026 | Deep dive analysis, 60s MA analysis, extended to 73 days |
| V8.2 | Dec 24, 2025 | Master consolidation of V6.0, V7.1, V8.0 |
| V7.1 | Dec 23, 2025 | Anomaly investigation, Eco Mode analysis |
| V6.0 | Dec 9, 2025 | Discharge test data documentation |
| V5.0 | Dec 4, 2025 | Initial public release |

---

## License & Contact

### License

This project is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this work with appropriate credit.

### Contact

**Author:** Bill Collis  
**Location:** East Hampton, Connecticut, USA  
**Repository:** [github.com/wkcollis1-eng/Lifepo4-Battery-Banks](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks)

---

*Last updated: January 10, 2026*
