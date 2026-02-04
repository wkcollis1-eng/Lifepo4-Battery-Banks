# 📖 Glossary

Terms, abbreviations, and definitions used throughout this study.

---

## Contents

- [Battery & Electrochemistry](#battery--electrochemistry)
- [Statistics & Analysis](#statistics--analysis)
- [Hardware & Sensors](#hardware--sensors)
- [Data & Measurement](#data--measurement)
- [Units & Conversions](#units--conversions)

---

## Battery & Electrochemistry

| Term | Definition |
|:-----|:-----------|
| **LiFePO₄** | Lithium Iron Phosphate — a lithium-ion battery chemistry known for safety, longevity, and thermal stability. Also written as LFP. |
| **4S Configuration** | Four cells connected in Series, producing ~12.8V nominal (3.2V × 4). |
| **Parallel Configuration** | Multiple cells or blocks connected positive-to-positive and negative-to-negative, increasing capacity while maintaining voltage. |
| **BMS** | Battery Management System — circuitry that monitors cell voltages, temperatures, and current, providing protection against overcharge, overdischarge, and overcurrent. |
| **SOC** | State of Charge — the remaining capacity of a battery expressed as a percentage of its full capacity. |
| **OCV** | Open Circuit Voltage — the voltage measured across battery terminals with no load connected and after sufficient rest time. |
| **Nominal Voltage** | The typical operating voltage of a battery chemistry; 3.2V per cell for LiFePO₄. |
| **Capacity (Ah)** | Ampere-hours — a measure of how much charge a battery can store. A 100Ah battery can theoretically deliver 100A for 1 hour or 10A for 10 hours. |
| **Internal Resistance** | The opposition to current flow within a battery, measured in milliohms (mΩ). Lower is better. |
| **Peukert Exponent** | A constant (k) describing how capacity decreases at higher discharge rates. k = 1.0 is ideal (no capacity loss); LiFePO₄ is typically 1.00–1.05. |
| **Parasitic Draw** | Small continuous current consumption from connected devices when the system is nominally "off." |
| **Self-Discharge** | The gradual loss of charge in a battery when not in use, due to internal chemical reactions. LiFePO₄ has very low self-discharge (~2–3% per month). |

---

## Statistics & Analysis

| Term | Definition |
|:-----|:-----------|
| **OLS** | Ordinary Least Squares — a standard linear regression method that minimizes the sum of squared differences between observed and predicted values. |
| **R²** | Coefficient of Determination — indicates how well the regression line fits the data. R² = 1.0 means perfect fit; R² = 0 means no linear relationship. |
| **σ (Sigma)** | Standard Deviation — a measure of the spread or dispersion of a dataset. Lower σ means data points are closer to the mean. |
| **SE** | Standard Error — the standard deviation of a statistic's sampling distribution. Often reported for regression coefficients. |
| **p-value** | The probability of observing results at least as extreme as measured, assuming the null hypothesis is true. Typically, p < 0.05 is considered statistically significant. |
| **MA-60s** | Moving Average, 60 Seconds — a time-based trailing rolling mean applied to high-frequency data. Uses `rolling('60s')` in pandas, which adapts to variable sampling intervals. |
| **Detrended** | Data with the linear trend removed, allowing analysis of residual variation around the trend. |
| **Residual** | The difference between an observed value and the value predicted by a model. |
| **Window Dependence** | The phenomenon where calculated statistics (like drift rate) vary depending on the time window selected for analysis. |

---

## Hardware & Sensors

| Term | Definition |
|:-----|:-----------|
| **Shelly Plus Uni** | A Wi-Fi-enabled sensor interface by Shelly, used here for voltage monitoring. Features ESP32 microcontroller with integrated ADC. |
| **ADC** | Analog-to-Digital Converter — circuitry that converts continuous analog signals (like voltage) into discrete digital values. |
| **ESP32** | A popular microcontroller by Espressif with integrated Wi-Fi and Bluetooth, used in the Shelly Plus Uni. |
| **Vref** | Reference Voltage — the known voltage that an ADC uses as a comparison standard. ESP32 has nominal 1100mV Vref with chip-to-chip variation of 1000–1200mV. |
| **eFuse Calibration** | Factory calibration values burned into ESP32 chips that can improve ADC accuracy. |
| **Home Assistant** | Open-source home automation platform used for data collection, logging, and integration in this study. |
| **InfluxDB** | A time-series database often used with Home Assistant for long-term data storage. |
| **Eco Mode** | A power-saving mode on Shelly devices that reduces power consumption but may affect sampling behavior. Enabled Dec 23, 2025 in this study. |

---

## Data & Measurement

| Term | Definition |
|:-----|:-----------|
| **Hourly Aggregate** | Data summarized per hour, typically as minimum, maximum, or mean values within that hour. |
| **High-Frequency Data** | Raw sensor readings at the fastest available rate (~3 seconds in this study). |
| **State-Change Logging** | A logging method where new records are only created when the measured value changes. Results in variable time intervals between records. |
| **Cadence** | The timing interval between measurements. Can be fixed (e.g., every 10 seconds) or variable (state-change logging). |
| **Spread** | The difference between maximum and minimum values within a time window. In this study: `Spread = Max - Min` for hourly data. |
| **Mid-Voltage** | The arithmetic mean of minimum and maximum voltage: `Mid = (Min + Max) / 2`. |
| **Quantization** | The discrete steps in ADC output. A 10mV quantization means the sensor can only report values in 10mV increments. |
| **EMI** | Electromagnetic Interference — unwanted electrical noise that can affect sensor readings. |
| **Artifact** | An anomaly in data caused by the measurement system rather than the phenomenon being measured. |

---

## Units & Conversions

| Unit | Name | Notes |
|:-----|:-----|:------|
| **V** | Volts | Electrical potential difference |
| **mV** | Millivolts | 1 mV = 0.001 V |
| **A** | Amperes | Electrical current |
| **mA** | Milliamperes | 1 mA = 0.001 A |
| **Ah** | Ampere-hours | Battery capacity |
| **mΩ** | Milliohms | Resistance (1 mΩ = 0.001 Ω) |
| **°F** | Degrees Fahrenheit | Temperature (used in this study) |
| **°C** | Degrees Celsius | Temperature (°C = (°F - 32) × 5/9) |
| **UTC** | Coordinated Universal Time | Standard time reference for high-frequency data |
| **EST/EDT** | Eastern Standard/Daylight Time | Local time zone for hourly data (UTC-5/UTC-4) |

### Temperature Conversion

```
°C = (°F - 32) × 5/9
°F = (°C × 9/5) + 32
```

### Common Values

| Description | Value |
|:------------|:------|
| LiFePO₄ cell nominal voltage | 3.2 V |
| LiFePO₄ cell full charge | 3.65 V |
| LiFePO₄ cell empty | 2.5 V |
| 4S pack nominal | 12.8 V |
| 4S pack full charge | 14.6 V |
| 4S pack empty | 10.0 V |
| Freezing point (charge cutoff) | 32°F / 0°C |

---

## See Also

- [Methodology](methodology.md) — Detailed explanation of analytical methods
- [Data Dictionary](../data/README.md) — Dataset structure and fields
- [FAQ](faq.md) — Frequently asked questions
