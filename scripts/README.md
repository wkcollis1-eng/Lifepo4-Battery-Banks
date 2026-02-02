# Scripts

Analysis code for the LiFePO₄ battery monitoring study.

## Files

| File | Description |
|------|-------------|
| `lifepo4_analysis.py` | Main analysis pipeline (drift, MA-60s, temperature, SOC) |

## Usage

```bash
# From repository root
pip install -r requirements.txt
python scripts/lifepo4_analysis.py
```

## Output

The script prints analysis results to stdout and generates figures in `figures/`.

## Dependencies

See `requirements.txt` in repository root:
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- statsmodels

## Modifying for Your Data

1. Update file paths in the "LOAD DATA" section
2. Adjust date parsing if your format differs
3. Modify stasis_start/stasis_end dates for your timeline

## License

MIT License — see `/LICENSE-CODE`
