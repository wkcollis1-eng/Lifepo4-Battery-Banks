# 📈 Figures Gallery

Visualization outputs from the analysis pipeline.

---

## Contents

- [Hero Figures](#hero-figures)
- [Complete Figure Index](#complete-figure-index)
- [Figure Descriptions](#figure-descriptions)
- [Regenerating Figures](#regenerating-figures)
- [Style Guide](#style-guide)

---

## Hero Figures

The three most important visualizations for understanding this study:

### 📊 Figure 1: Voltage Timeline

![Voltage Timeline](fig1_voltage_timeline.png)

**What it shows:** Complete 94+ day voltage monitoring record from Oct 2025 through Jan 2026, with OLS drift regression overlay.

**Key insight:** Monotonic decline approaching equilibrium; no divergence signatures.

---

### 📉 Figure 2: MA-60s Noise Reduction

![MA-60s Comparison](fig2_ma60_comparison.png)

**What it shows:** Before/after comparison of raw voltage vs. 60-second time-based rolling mean.

**Key insight:** 42–50% apparent noise reduction while preserving trend information.

---

### 📈 Figure 5: Drift Flattening

![Drift Flattening](fig5_drift_flattening.png)

**What it shows:** Comparison of drift rates between full stasis period and last 30 days.

**Key insight:** 75% rate reduction indicates approach to equilibrium storage state.

---

## Complete Figure Index

| Figure | File | Description | Report Section |
|:-------|:-----|:------------|:---------------|
| 1 | `fig1_voltage_timeline.png` | Full voltage timeline with drift overlay | §3 |
| 2 | `fig2_ma60_comparison.png` | Raw vs MA-60s filtered comparison | §5 |
| 3 | `fig3_spread_analysis.png` | Hourly spread showing Eco Mode effect | §4 |
| 4 | `fig4_temperature_voltage.png` | Temperature-voltage regression | §6 |
| 5 | `fig5_drift_flattening.png` | Full-period vs last-30d drift comparison | §3 |
| 6 | `fig6_ma60_segments.png` | MA-60s performance by time segment | §5 |
| 7 | `fig7_soc_projection.png` | SOC projection under parasitic draw model | §7 |

---

## Figure Descriptions

### Figure 3: Spread Analysis

![Spread Analysis](fig3_spread_analysis.png)

**What it shows:** Hourly voltage spread (Max − Min) over the monitoring period, with the Eco Mode transition marked.

**Key insight:** Spread increase on Dec 23 correlates with firmware change, not electrochemical divergence.

---

### Figure 4: Temperature-Voltage Relationship

![Temperature-Voltage](fig4_temperature_voltage.png)

**What it shows:** Two-factor regression isolating temperature effects from monotonic drift.

**Key insight:** System-level coefficient of +1.0 ± 0.3 mV/°F (includes measurement chain effects).

---

### Figure 6: MA-60s Segments

![MA-60s Segments](fig6_ma60_segments.png)

**What it shows:** Noise reduction performance across different time segments of the high-frequency data.

**Key insight:** Performance varies 42–50% depending on sampling regularity and interference.

---

### Figure 7: SOC Projection

![SOC Projection](fig7_soc_projection.png)

**What it shows:** Projected State of Charge decline under different parasitic draw assumptions.

**Key insight:** 7–10 months to 80% SOC at ~13–20 mA effective draw.

---

## Regenerating Figures

### Standard Resolution (Web)

```bash
# From repository root
python scripts/lifepo4_analysis.py
```

Figures are generated at **150 DPI** for web display.

### High Resolution (Print/Publication)

For print or publication quality, modify the script or use:

```python
import matplotlib.pyplot as plt

# Set higher DPI before saving
plt.savefig('figures/fig1_voltage_timeline.png', dpi=300, bbox_inches='tight')
```

### Dependencies

Ensure all requirements are installed:

```bash
pip install -r requirements.txt
```

Required packages for figure generation:
- `matplotlib` — Core plotting
- `seaborn` — Statistical visualizations
- `pandas` — Data manipulation
- `numpy` — Numerical operations

---

## Style Guide

### Current Style

| Property | Value |
|:---------|:------|
| Resolution | 150 DPI (web) |
| Format | PNG |
| Color palette | Matplotlib defaults |
| Font | System default |

### Recommended Improvements

For publication-ready figures, consider:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('colorblind')

# Figure size for publication (single column: 3.5", double: 7")
fig, ax = plt.subplots(figsize=(7, 4))

# Font sizes
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
})

# Save at publication DPI
plt.savefig('figure.png', dpi=300, bbox_inches='tight')
plt.savefig('figure.pdf', bbox_inches='tight')  # Vector format
```

### Color Accessibility

Current figures use default colors. For improved accessibility:

```python
# Colorblind-friendly palette
colors = ['#0077BB', '#EE7733', '#009988', '#CC3311', '#33BBEE']

# Or use seaborn's colorblind palette
sns.set_palette('colorblind')
```

---

## File Sizes

| Figure | Size | Dimensions |
|:-------|-----:|:-----------|
| fig1_voltage_timeline.png | 114 KB | 1200 × 600 |
| fig2_ma60_comparison.png | 215 KB | 1200 × 800 |
| fig3_spread_analysis.png | 85 KB | 1200 × 600 |
| fig4_temperature_voltage.png | 174 KB | 1200 × 800 |
| fig5_drift_flattening.png | 127 KB | 1200 × 600 |
| fig6_ma60_segments.png | 57 KB | 1200 × 400 |
| fig7_soc_projection.png | 132 KB | 1200 × 600 |

---

## See Also

- [Evidence Map](../docs/evidence_map.md) — Links figures to claims
- [Technical Report](../reports/LiFePO4_Report_2026-01-31.md) — Figures in context
- [Methodology](../docs/methodology.md) — How data was analyzed
