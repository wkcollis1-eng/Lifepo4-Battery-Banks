# 🤝 Contributing to LiFePO₄ Battery Bank Study

Thank you for your interest in contributing! This project aims to build an open, reproducible dataset for DIY battery builders and researchers.

---

## Contents

- [Ways to Contribute](#ways-to-contribute)
- [Submitting Your Data](#submitting-your-data)
- [Reporting Issues](#reporting-issues)
- [Suggesting Improvements](#suggesting-improvements)
- [Code Contributions](#code-contributions)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

---

## Ways to Contribute

| Contribution Type | Description | How |
|:------------------|:------------|:----|
| 📊 **Data** | Share replication data from your own system | Pull Request |
| 🐛 **Bug Reports** | Report errors in calculations, data, or docs | Issue |
| 💡 **Ideas** | Suggest improvements or new analyses | Discussion |
| 🔧 **Code** | Improve analysis scripts | Pull Request |
| 📝 **Documentation** | Improve clarity or add examples | Pull Request |
| 🔬 **Peer Review** | Critique methodology or results | Issue or Discussion |

---

## Submitting Your Data

The most valuable contribution is **replication data** from your own battery bank.

### Step 1: Collect Your Data

Follow the [Replication Protocol](docs/replication.md) to collect data compatible with this study.

### Step 2: Format Your Data

Match our CSV structure:

**Hourly voltage data:**
```csv
Date,Time,Min,Max
29/10/2025,00:00,13.271,13.301
29/10/2025,01:00,13.268,13.298
```

**High-frequency data:**
```csv
entity_id,state,last_changed
sensor.battery_voltage,13.285,2025-12-26T00:00:03Z
sensor.battery_voltage,13.282,2025-12-26T00:00:06Z
```

### Step 3: Document Your System

Create a brief description including:

| Field | Required | Description |
|:------|:--------:|:------------|
| System Config | ✅ | Cell count, brands, capacity |
| Topology | ✅ | Parallel, series-parallel, etc. |
| Monitoring Duration | ✅ | Total days of data |
| Sensor Used | ✅ | Make/model, resolution |
| Location | ✅ | General region (e.g., "New England, USA") |
| Temperature Data | ⭕ | If available |
| Discharge Test Results | ⭕ | If performed |
| Photos | ⭕ | Of your setup (optional) |

### Step 4: Submit via Pull Request

1. Fork this repository
2. Create a branch: `git checkout -b data/your-username`
3. Add your files to `data/contributed/your-username/`
4. Include a `README.md` describing your system
5. Submit a Pull Request

### Privacy Guidelines

- ❌ Do not include personal identifying information
- ✅ Use region-level geographic data only (e.g., "Pacific Northwest, USA")
- ✅ Anonymize any identifiable timestamps if concerned

---

## Reporting Issues

### Found an Error?

1. Check [existing issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) first
2. Use the appropriate [issue template](.github/ISSUE_TEMPLATE/)
3. Provide as much detail as possible

### Issue Types

| Template | Use For |
|:---------|:--------|
| 🐛 Bug Report | Errors in calculations, data, or documentation |
| 📊 Data Request | Request additional data or clarification |
| 💡 Feature Request | Suggest improvements or new analyses |
| 🔬 Methodology Question | Questions about analytical methods |

---

## Suggesting Improvements

Have ideas for the project? We welcome suggestions for:

- **Analysis improvements** — Better statistical methods, visualizations
- **Documentation** — Clearer explanations, additional examples
- **Methodology** — Enhanced protocols, additional metrics
- **Repository structure** — Better organization, navigation

Use [GitHub Discussions](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions) for open-ended ideas.

---

## Code Contributions

Contributions to analysis scripts are welcome!

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Lifepo4-Battery-Banks.git
cd Lifepo4-Battery-Banks

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

### Code Style

| Aspect | Standard |
|:-------|:---------|
| Python version | 3.8+ compatible |
| Style guide | PEP 8 |
| Formatting | Black (optional but encouraged) |
| Type hints | Encouraged for public functions |
| Docstrings | NumPy style |

### Example

```python
def compute_drift_rate(
    daily_means: pd.Series, 
    start_date: str, 
    end_date: str
) -> dict:
    """
    Compute OLS drift rate for a given time window.
    
    Parameters
    ----------
    daily_means : pd.Series
        Daily mean voltage values with datetime index.
    start_date : str
        Window start date (YYYY-MM-DD format).
    end_date : str
        Window end date (YYYY-MM-DD format).
    
    Returns
    -------
    dict
        Contains 'slope_mv_day', 'r_squared', 'p_value', 'std_error'.
    
    Examples
    --------
    >>> result = compute_drift_rate(daily_means, '2025-11-22', '2026-01-31')
    >>> print(f"Drift: {result['slope_mv_day']:.3f} mV/day")
    """
    ...
```

---

## Pull Request Process

### Before Submitting

- [ ] Run the analysis script to verify no regressions
- [ ] Update documentation if you changed functionality
- [ ] Add yourself to contributors (optional)
- [ ] Write a clear PR description

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Data contribution

## Related Issues
Fixes #123

## Testing
- [ ] Ran `lifepo4_analysis.py` successfully
- [ ] Verified output figures
- [ ] Checked documentation renders correctly

## Notes
Any additional context.
```

### Review Process

1. Submit your PR with a clear description
2. Automated checks will run (linting, link checking)
3. Maintainer will review within a few days
4. Address any feedback
5. PR merged upon approval

---

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

**Summary:**
- 🤝 Be respectful and inclusive
- 💬 Use welcoming language
- 🎯 Focus on what's best for the community
- 📖 Share knowledge openly

---

## Questions?

| Topic | Where to Ask |
|:------|:-------------|
| Technical questions | [Discussions](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions) |
| Bug reports | [Issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) |
| Methodology questions | [Methodology Issue Template](.github/ISSUE_TEMPLATE/methodology_question.md) |

---

## Thank You! 🙏

Your contributions help improve battery knowledge for the entire DIY community!
