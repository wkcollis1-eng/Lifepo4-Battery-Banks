# ❓ Frequently Asked Questions

Common questions about this study, the methodology, and DIY battery systems.

---

## Contents

- [System Design](#system-design)
- [Data & Methodology](#data--methodology)
- [Safety & Best Practices](#safety--best-practices)
- [Replication](#replication)
- [Technical Details](#technical-details)

---

## System Design

### Why mixed brands? Isn't that risky?

The **architectural immunity** hypothesis posits that parallel-connected cells self-balance through the shared bus connection. When cells are connected in parallel, Kirchhoff's laws force them to the same voltage. Any cell at higher voltage will discharge into lower-voltage cells until equilibrium is reached.

This study provides empirical evidence supporting this principle: 94+ days of monitoring show no divergence at the bus potential, and no growing instability signatures.

**However:** This doesn't mean you should deliberately mismatch cells. The claim is that *if* you have mixed-brand cells (common in budget builds), parallel connection provides inherent balancing.

### Do I need a BMS?

**Yes, always.** Architectural immunity does not replace cell protection.

A BMS protects against:
- **Overcharge** — Cells exceeding 3.65V
- **Overdischarge** — Cells dropping below 2.5V
- **Overcurrent** — Excessive discharge rates
- **Temperature** — Charging below 0°C (32°F)
- **Short circuit** — Catastrophic failure protection

The architectural immunity concept addresses *voltage matching* between parallel cells, not any of these safety functions.

### What's the advantage of 4S (12V) over 8S (24V) or 16S (48V)?

This study uses a 4S configuration (12.8V nominal) for several reasons:

1. **Compatibility** — Works with common 12V appliances, inverters, and RV/marine systems
2. **Simplicity** — Fewer series connections means fewer potential failure points
3. **BMS availability** — 4S BMS units are common and inexpensive
4. **Safety** — Lower voltage is inherently safer for DIY work

Higher voltage systems (24V, 48V) are more efficient for high-power applications due to lower current for the same power (P = V × I), but require more sophisticated BMS and wiring.

### Can I add more capacity later?

Yes, with caveats:

1. **Same chemistry** — Only add LiFePO₄ to LiFePO₄
2. **Similar SOC** — Charge new cells to match existing bank before connecting
3. **Adequate wiring** — Ensure bus bars and cables can handle increased current capacity
4. **BMS capacity** — Verify your BMS can handle the total capacity

The architectural immunity principle suggests mixed-brand additions will self-balance, but starting with similar SOC minimizes initial current flow between new and existing cells.

---

## Data & Methodology

### Why time-based rolling mean instead of sample-count?

Variable sampling cadence (from state-change logging) means a fixed sample count represents different time windows depending on how frequently the voltage changes.

For example, with ~3-second median cadence:
- 20 samples ≈ 60 seconds during normal operation
- 20 samples could be 5+ minutes during stable periods (fewer state changes)

**Time-based rolling** (`rolling('60s')`) ensures consistent smoothing regardless of sampling irregularity. This is critical for fair comparison across different time periods.

### How accurate is the parasitic draw figure?

**It is now measured, not inferred: 7.4 ± 2.4 mA**, time-weighted over 41 quiescent days and 1.79 M samples at 2 s on a 375 µΩ shunt, 99.93% integrated coverage.

**And it is the monitor.** The Shelly and the DROK panel meter are retired and the inverter is off, so the INA228 monitor — powered from the busbars, its return through the shunt — is the only load on the bus. 99 mW at 13.35 V is what a Wi-Fi-associated XIAO ESP32-C3 behind an 87% buck should draw. **The bank's own external parasitic load is effectively nil.** See [report §7](../reports/LiFePO4_Report_2026-08-26.md).

The earlier answer here gave 13–20 mA inferred from voltage drift, and listed direct bus-current measurement as the highest-value improvement. That measurement was made in July 2026, and the inferred band turned out to be **42–63% high** — a useful calibration on how much to trust drift-derived currents on a flat OCV curve.

**What still limits the measured figure:**

1. **Instrument offset** — the INA228's shunt-channel offset measured 0.9 µV ≡ 2.4 mA at commissioning. The 41-day mean is robust against that, but day-to-day structure at the 1–3 mA scale is not established as physical.
2. **One season, one SOC** — 68–70 °F pack, ~100% SOC. No cold-storage figure exists.
3. **It is a property of the load set, not of the bank** — the drain stepped by +2.9 mA on 2026-08-04 with no established cause, and the retired Shelly was part of the older figure.

**The highest-value improvement now** is shunt calibration against a clamp meter at ~115 A, which would take the DROK's ±1% tolerance to ~0.1% of reference.

### Why are there multiple drift rates reported?

Drift rates are **window-dependent** on a non-linear relaxation curve. The battery voltage follows an exponential-like approach to equilibrium, not a linear decline.

| Window | Rate | What It Represents |
|:-------|:-----|:-------------------|
| Full stasis (70 days) | −0.67 mV/day | Average decline over entire monitoring period |
| Last 30 days | −0.17 mV/day | Rate near equilibrium |
| Last 7 days | ~0.0 mV/day | Approaching stable storage voltage |

This isn't a contradiction—it's expected behavior for a system approaching equilibrium. The 75% rate reduction from full-period to last-30-days is the clearest evidence of stabilization.

### What caused the spread increase on Dec 23?

The spread increase correlates precisely with enabling **Eco Mode** on the Shelly Plus Uni sensor at Dec 23, 2025 ~15:40 local time.

Eco Mode reduces device power consumption but triggers a reboot and may change sampling behavior. The spread increase is a **measurement-regime artifact**, not electrochemical divergence.

Evidence:
- Step change coincides exactly with known configuration change
- No corresponding change in mean voltage
- No trending instability after the transition

### How do I know the data is trustworthy?

Several factors support data quality:

1. **Reproducibility** — Analysis scripts are provided; results can be regenerated
2. **Raw data access** — All source data is publicly available
3. **Evidence mapping** — Each claim links to specific data, code, and figures
4. **Methodology documentation** — Methods are explicitly described
5. **Known limitations acknowledged** — Caveats and uncertainties are stated clearly

The [Evidence Map](evidence_map.md) provides full traceability from claims to supporting data.

---

## Safety & Best Practices

### What fuse should I use?

**Class T fuses** are recommended for lithium battery banks:

| Bank Capacity | Fuse Rating | Notes |
|:--------------|:------------|:------|
| 100 Ah | 100–150A | Size for expected max load + margin |
| 200 Ah | 150–200A | Consider wire gauge limits |
| 500 Ah | 200–400A | Multiple fuses may be needed |

Fuses should be placed **as close to the battery terminals as possible**—ideally within 6 inches of the positive terminal.

### Can I charge in cold weather?

**Never charge LiFePO₄ below 0°C (32°F).**

Charging below freezing causes lithium plating on the anode, which:
- Permanently damages cells
- Reduces capacity
- Creates internal short-circuit risk

Most quality BMS units have low-temperature charging cutoff. If yours doesn't, add external temperature protection.

**Discharging** in cold weather is generally safe, though capacity is reduced.

### What's the fire risk?

LiFePO₄ is one of the **safest lithium chemistries**:

- More thermally stable than NMC or LCO chemistries
- Higher thermal runaway threshold (~270°C vs ~150°C for some lithium-ion)
- No cobalt (reduces fire intensity if failure occurs)

**However**, any high-capacity battery can be dangerous:
- Short circuits can cause fires and explosions
- Physical damage can lead to internal shorts
- Overcharging can cause venting and fire

Always use proper fusing, BMS protection, and follow safe handling practices.

---

## Replication

### What hardware do I need to replicate this study?

**Minimum requirements:**

| Component | Purpose | Example |
|:----------|:--------|:--------|
| LiFePO₄ battery bank | Subject of study | Any capacity |
| Voltage sensor | Measurement | Shelly Plus Uni, INA226 |
| Data logger | Recording | Home Assistant, Node-RED |
| Temperature sensor | Environmental correlation | Any digital sensor |

See [Replication Guide](replication.md) for detailed setup instructions.

### Can I use different sensors?

Yes, with considerations:

| Sensor Type | Pros | Cons |
|:------------|:-----|:-----|
| Shelly Plus Uni | Easy setup, Wi-Fi, Home Assistant integration | ~10mV resolution, ESP32 ADC limitations |
| INA226/INA219 | High precision, current + voltage | Requires microcontroller, more complex |
| Victron SmartShunt | Professional quality, Bluetooth | Expensive, proprietary ecosystem |
| Multimeter logging | Very accurate | Manual or expensive auto-logging |

Higher-resolution sensors will show less quantization noise but may reveal more high-frequency variation.

### How long should I monitor?

Minimum useful monitoring periods:

| Goal | Duration | Notes |
|:-----|:---------|:------|
| Basic health check | 1 week | Sufficient for gross problems |
| Drift characterization | 30+ days | Captures relaxation behavior |
| Seasonal effects | 3+ months | Temperature variation |
| Long-term storage viability | 6+ months | Full discharge curve |

This study's 94+ days provides good drift characterization and storage viability data.

---

## Technical Details

### Why is the temperature coefficient positive?

The observed **+1.0 mV/°F** coefficient is **system-level**, not pure LiFePO₄ electrochemistry.

It includes:
- Pack electrochemical response
- ADC reference voltage temperature drift
- Wiring and contact resistance changes
- Sensor housing thermal effects

Pure LiFePO₄ OCV temperature coefficient is typically **negative** (voltage decreases with increasing temperature) at moderate SOC. The positive observed coefficient suggests measurement-chain effects dominate in this system.

### What's the ADC resolution limit?

The Shelly Plus Uni uses an ESP32 ADC with:
- 12-bit resolution (4096 steps)
- ~1100mV internal reference (varies 1000–1200mV by chip)
- Practical resolution of ~10mV after scaling to 0–30V range

This means voltage changes smaller than ~10mV are not reliably detectable with this sensor. The MA-60s smoothing helps extract trends from quantized data.

### Why state-change logging instead of fixed interval?

Home Assistant's default behavior logs new records only when values change. This:

**Advantages:**
- Reduces database size
- Captures all changes (nothing missed between polls)
- Works well for slowly-changing values

**Disadvantages:**
- Variable time intervals complicate analysis
- Gaps during stable periods
- Not suitable for spectral analysis (FFT)

For future work, fixed-interval logging would be preferable for advanced signal analysis.

---

## Still Have Questions?

- **Technical questions:** Open a [Discussion](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/discussions)
- **Bug reports:** Use [Issues](https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks/issues)
- **Methodology critiques:** Welcome via Issues or Discussions

---

## See Also

- [Methodology](methodology.md) — Detailed analytical methods
- [Glossary](glossary.md) — Terms and definitions
- [Replication Guide](replication.md) — Build your own monitoring setup
