# Lifepo4-Battery-Banks
# LiFePO4 Battery Bank Master Report

## Overview
This repository documents the performance, monitoring, and long-term analysis of a DIY 12V 500Ah LiFePO₄ battery bank.  
It includes detailed discharge test reports, continuous voltage monitoring logs, and engineering analysis of efficiency, internal resistance, and reliability.  

The goal is to provide a reproducible, transparent reference for DIY builders and researchers, demonstrating **architectural immunity** in parallel battery configurations.

---

## Contents
- **Reports/** – Publication-ready PDF reports (v1.0 → v5.0 and future updates)
- **Data/** – Raw CSV voltage logs from Shelly Plus Uni monitoring
- **Appendices/** – Formula references, equipment specifications, and test conditions
- **README.md** – Project overview and update workflow

---

## Key Findings
- Delivered **397Ah usable capacity** (99.3% of rated 400Ah usable)  
- Achieved **90.3% inverter efficiency**  
- System internal resistance baseline: **4.9 mΩ total**  
- Peukert exponent: **k = 1.003 (near-perfect linearity)**  
- Self-discharge rate: **≤0.25% per month**  
- Parallel configuration provides **architectural immunity** against single-point failures

---

## Update Workflow
This repository is a **living master record**. Updates follow this protocol:

1. **Daily Voltage Logs**  
   - Export CSV from Shelly Plus Uni  
   - Append to `/Data/combined_output.csv`  
   - Summarize in the next report update

2. **Discharge/Recharge Tests**  
   - Conduct full discharge to ~20% SOC annually  
   - Record internal resistance at end of test  
   - Append results to the next report version

3. **Report Updates**  
   - Publish updated PDF in `/Reports/`  
   - Tag release with version number and date  
   - Update version history in Appendix E

---

## How to Use
- **DIY Builders**: Benchmark your own systems against the documented performance metrics.  
- **Researchers**: Reference the reproducible methodology and long-term monitoring data.  
- **Community**: Fork, comment, or contribute improvements to analysis and documentation.

---

## License
This project is shared openly for educational and technical reference.  
Please credit the author (Bill Collis) when reusing or adapting content.

---

## Contact
Location: East Hampton, Connecticut, US  
Author: Bill Collis  
Repository: [LiFePO4 Battery Banks](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/releases)

