# Contributing to LiFePO₄ Battery Bank Study

Thank you for your interest in contributing! This project aims to build an open, reproducible dataset for DIY battery builders and researchers.

## Ways to Contribute

### 📊 Submit Your Own Data

The most valuable contribution is **replication data** from your own battery bank:

1. **Fork this repository**
2. **Collect your data** following the [Replication Protocol](README.md#replication-protocol)
3. **Format your data** to match our CSV structure
4. **Submit a Pull Request** with:
   - Your CSV data file(s)
   - A brief description of your system configuration
   - Duration of monitoring
   - Any notable observations

**Data format requirements:**
- CSV with headers: `Timestamp,Voltage_Min,Voltage_Max`
- Timestamps in ISO 8601 format
- Voltage values in decimal volts (e.g., 13.271)

### 🐛 Report Issues

Found an error in calculations, data, or documentation?

1. Check [existing issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues) first
2. Use the appropriate [issue template](.github/ISSUE_TEMPLATE/)
3. Provide as much detail as possible

### 💡 Suggest Improvements

Have ideas for the project?

- **Analysis improvements**: Better statistical methods, visualizations
- **Documentation**: Clearer explanations, additional examples
- **Methodology**: Enhanced protocols, additional metrics

Use [GitHub Discussions](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions) for open-ended ideas.

### 🔧 Improve the Code

Contributions to analysis scripts are welcome:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests if applicable
5. Submit a Pull Request

**Code style:**
- Python 3.8+ compatible
- Use descriptive variable names
- Include docstrings for functions
- Comment complex logic

## Pull Request Process

1. **Describe your changes** clearly in the PR description
2. **Link related issues** if applicable
3. **Update documentation** if you changed functionality
4. **Wait for review** - I'll respond within a few days

## Data Submission Guidelines

When submitting replication data:

### Required Information

| Field | Description |
|-------|-------------|
| System Config | Cell count, brands, capacity |
| Topology | Parallel, series-parallel, etc. |
| Monitoring Duration | Total days of data |
| Sensor Used | Make/model, resolution |
| Location | General region (for climate context) |

### Optional but Helpful

- Temperature data
- Load profiles
- Discharge test results
- Photos of your setup

### Privacy

- Do not include personal identifying information
- Geographic data should be region-level only (e.g., "New England, USA")

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Questions?

- **Technical questions**: Open a [Discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions)
- **Bug reports**: Use [Issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues)
- **Direct contact**: See [README.md](README.md#license--contact)

---

Thank you for helping improve battery knowledge for the DIY community!
