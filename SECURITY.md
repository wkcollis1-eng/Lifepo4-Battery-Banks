# Security Policy

## Scope

This repository contains research data, analysis scripts, and documentation. It does not contain:
- Authentication systems
- User credentials
- Personal identifying information
- Executable binaries

## Data Integrity

### Verification

All data releases include SHA-256 checksums. Verify downloaded files:

```bash
# Download checksums file from release
sha256sum -c checksums.txt
```

### Known Data Sources

| Data Type | Source | Verification |
|:----------|:-------|:-------------|
| Voltage data | Shelly Plus Uni via Home Assistant | Sensor serial logged |
| Temperature data | Co-located sensor via Home Assistant | Same system |
| Derived data | Python scripts in `scripts/` | Reproducible |

## Reporting Issues

### Data Integrity Concerns

If you discover potential data integrity issues (corrupted files, inconsistent values, unexplained anomalies):

1. **Check the [Evidence Map](docs/evidence_map.md)** — Verify the claim-to-data linkage
2. **Attempt reproduction** — Run the analysis scripts on provided data
3. **Open an Issue** — Use the Bug Report template with details

### Security Vulnerabilities

If you discover security vulnerabilities in the analysis scripts:

1. **Do not** open a public issue for exploitable vulnerabilities
2. **Contact the maintainer** via GitHub private messaging
3. **Allow reasonable time** (30 days) for response before public disclosure

### What Constitutes a Vulnerability

For this research repository, relevant security concerns include:
- Script vulnerabilities that could execute arbitrary code
- Data injection risks in analysis pipelines
- Dependency vulnerabilities in `requirements.txt`

### What Is NOT a Security Issue

- Data quality questions (use Issues)
- Methodology disagreements (use Discussions)
- Feature requests (use Issues)

## Dependencies

This project uses common Python data science libraries. Known vulnerabilities in dependencies should be reported via Issues referencing the specific CVE.

Current dependencies (`requirements.txt`):
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- statsmodels

Check for known vulnerabilities:

```bash
pip install safety
safety check -r requirements.txt
```

## Supported Versions

| Version | Supported |
|:--------|:----------|
| 2026-03-01 (current) | ✅ Yes |
| 2026-01-31 | ⚠️ Limited (data updates only) |
| Earlier | ❌ No |

## Responsible Disclosure

We appreciate responsible disclosure of any issues. Contributors who report valid security concerns will be acknowledged (with permission) in the repository.

## Contact

- **GitHub Issues:** For non-sensitive reports
- **GitHub Discussions:** For questions
- **Direct contact:** Via GitHub profile for sensitive security matters
