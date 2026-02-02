# Figures

Visualization outputs from the analysis pipeline.

## Hero Figures

| File | Description |
|------|-------------|
| `fig1_voltage_timeline.png` | Full voltage timeline with drift overlay |
| `fig2_ma60_comparison.png` | MA-60s noise reduction before/after |
| `fig5_drift_flattening.png` | Drift rate window comparison |

## All Figures

| File | Description | Report Section |
|------|-------------|----------------|
| `fig1_voltage_timeline.png` | Oct 2025 → Jan 2026 voltage with drift lines | §3 |
| `fig2_ma60_comparison.png` | Raw vs MA-60s filtered comparison | §5 |
| `fig3_spread_analysis.png` | Hourly spread showing Eco Mode effect | §4 |
| `fig4_temperature_voltage.png` | Temperature-voltage regression | §6 |
| `fig5_drift_flattening.png` | Full-period vs last-30d drift | §3 |
| `fig6_ma60_segments.png` | MA-60s performance by time segment | §5 |
| `fig7_soc_projection.png` | SOC projection under parasitic draw model | §7 |

## Regenerating Figures

```bash
python scripts/lifepo4_analysis.py
python scripts/generate_figures.py  # if separate
```

Figures are generated at 150 DPI for web display. For print/publication, regenerate at 300 DPI.
