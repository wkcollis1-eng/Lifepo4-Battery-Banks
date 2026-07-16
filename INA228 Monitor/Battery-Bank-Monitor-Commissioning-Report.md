# Battery Bank Monitor — Commissioning Report

**System:** 12 V / 500 Ah LiFePO₄ battery bank (5 × 100 Ah parallel, mixed brands) with Giandel 1500 W inverter and LiTime 12 V (14.6 V) 80 A charger
**Monitor:** Battery_Bank-Monitor-THT V2 carrier · Seeed XIAO ESP32-C3 · Adafruit INA228 breakout (on-board 15 mΩ shunt removed) · DROK 200 A / 75 mV manganin shunt, low-side
**Commissioning window:** 2026-07-13 → 2026-07-16
**Firmware at completion:** `battery-bank-monitor.yaml` **V1.21** (V1.19 baseline + commissioning fixes; see §3.2)
**Author:** William Collis
**Status:** **COMMISSIONED.** All acceptance criteria met. First full-charge anchor fired 2026-07-16 19:50 UTC; SOC = 100.0 %, Total Full Charge Cycles = 1 (operator-verified).
**Companion documents:** Wiring Summary Rev 1.9 · LiFePO₄ study repo (capacity validation Oct 2025; stasis study)

---

## 1. Executive Summary

The monitor was brought from bench parts to a fully commissioned battery-management instrument over four days. Commissioning included a deliberate multi-level discharge campaign (41 W → 70 W → ~1 kW → inverter nameplate), a complete LiTime charge cycle with automatic full-charge anchoring, and live exercise of every protection layer — including a genuine over-power hardware alert and a double inverter-overload trip, both handled correctly.

**Key commissioned figures:**

| Parameter | Value | Basis |
|---|---|---|
| Bank DC internal resistance (2-min DC-IR) | **3.73 mΩ** @ 69 °F, ~80 % SOC | rest→80.5 A step |
| Ohmic component R₀ | **2.63 mΩ** | load-release edge |
| Firmware Ri trend metric (45 s dwell) | ~3.3–3.5 mΩ expected | V1.21 settled-step |
| Voltaic (round-trip voltage) efficiency | **95.8 %** | 13.17 V dis ÷ 13.745 V chg |
| Estimated round-trip energy efficiency | **~94.8 %** | voltaic × CE ≈ 0.99 |
| Charger AC→DC efficiency (LiTime 80 A) | **95.7 % ± 2.5 %** | 1586 Wh DC ÷ 1657 Wh AC (Kill-A-Watt) |
| Inverter DC→AC efficiency (Giandel 1500 W) | **87–94 % (provisional)** | window-alignment limited; see §8.1 |
| Voltage sag at inverter nameplate (~130 A) | **3.5 %** (Vmin 12.851) | 0.26C |
| OCV plateau slope | **6.0 mV / %SOC** (bank) | two rested OCV points |
| Post-load OCV validity | **τ₆₃ ≈ 7 min; 95 % ≈ 34 min** | relaxation fit |
| CV absorption time (trend baseline #1) | **16.8 min** | first anchored charge |
| Pack ΔT at 0.157C charge | **+2.7 °F** | DS18B20 |
| Self-discharge (from prior 92-day study) | ~0 %/month | unchanged; monitor now measures directly |

---

## 2. System Under Test

### 2.1 Measurement chain
AC grid → LiTime 80 A charger → busbars → **DROK 200 A / 75 mV shunt (375 µΩ), negative leg, low-side** → 500 Ah bank. INA228 (20-bit, ADCRANGE 0 = ±163.84 mV, 4120 µs × 128 averaging, 2 s polling) senses the shunt Kelvin taps; bus voltage via fused VBUS lead from the positive busbar; DS18B20 on the pack case (isolated mount); XIAO ESP32-C3 reports via ESPHome/Home Assistant. Local SSD1306 OLED (STEMMA, **0x3D**) with wake button. Single DC earth reference (inverter chassis bond at negative busbar).

Resolution demonstrated end-to-end: the INA228's 195.3125 µV bus-voltage LSB survives the full chain (ESPHome → HA recorder → CSV export) with zero degradation; intra-minute noise σ ≈ 0.10 mV (half an LSB).

### 2.2 Firmware architecture (V1.21)
CORE: 2 s polled acquisition, guarded left-rectangle integration (stale-bus watchdog 10 s; 8–16 V and ≥350 A plausibility guards), coulomb-counted SOC anchored at confirmed full-charge events (absorption ≥14.20 V sustained 60 s, then charger-stop edge). OBSERVABILITY: OLED (4 pages, normalized 12 px layout), status LED (slow-flash proof-of-life / solid active / fast FAULT), HA dashboard. PROTECTION: firmware alarms (12.40 / 12.20 / 11.80 / 14.80 V) plus **independent INA228 hardware alert limits** written at boot — BUVL 12.20 V, BOVL 14.80 V, SOVL +250 A, SUVL −250 A, POL 1500 W — latched on GPIO5 and decoded to `alert_reason` with operator acknowledge.

---

## 3. Commissioning Narrative — Defects Found and Resolved

Commissioning surfaced eight defects (three hardware, five firmware). All were root-caused with measurements; none required design changes to the carrier or topology.

### 3.1 Hardware
| # | Defect | Root cause | Resolution |
|---|---|---|---|
| H1 | +3V3 rail at 1.95 V, unloaded | **Defective Pololu D24V7F3 (unit 1 of 2)** regulating to ~59 % of setpoint. Correct part confirmed ordered (packing slip 1J613636, item 5592 ×2); D24V7Fx family PCB is unmarked for voltage variant. | Unit 2 installed, 3.30 V nominal. Unit 1 quarantined and labeled. **New SOP: every regulator module gets a 30 s standalone output verification and a measured-voltage label before installation** (family variants are visually identical — Pololu's own documented caveat). |
| H2 | Rail drag during 12 V bring-up | Short in the DS18B20 field wiring (TB2) | Rewired; sensor healthy (68–70 °F ambient tracking) |
| H3 | OLED dark, button entity alive | STEMMA-version Adafruit 938 ships **ADDR jumper open = I²C 0x3D**; firmware/doc assumed 0x3C | Firmware moved to 0x3D with explanatory comment; Wiring Summary §6.6 to be amended |

Item H from the Wiring Summary (regulator pin-order risk) **closes with an amended lesson**: the realized hazard was module *variant identity*, not pin order — a permanent property of this part family, now mitigated by SOP.

### 3.2 Firmware (V1.19 → V1.21)
| # | Defect | Symptom / discovery | Fix |
|---|---|---|---|
| F1 | `validated_capacity_ah: "397"` + `f` suffix → `397f`, ill-formed C++ | **V1.19 as archived could not compile** (SOC, runtime, self-discharge, reconciliation lambdas all failed); config-valid ≠ compilable | `"397.0"`, annotated. Reinforces the compile-gate rule: codegen does not compile lambdas |
| F2 | OLED health page showed 155.4 °F for a 68.5 °F pack | Display lambda re-applied °C→°F to an already-converted sensor | Print state directly; caught by cross-checking two rendering paths of one sensor |
| F3 | Idle power flatlined at 0.0 W | `signed_power` hard-returned 0 in the ±0.05 A deadband; 0.1 W quantization | True signed micro-power at mW resolution; idle self-draw (~−0.08 W) now visible |
| F4 | Outage #2: avg power 80.4 W > peak 73.6 W (impossible) | Duration anchor (`millis()`, non-restored) desynchronized from persisted Ah/Wh/peak after a mid-outage reboot; no `on_press` re-fires on boot-into-ON | **V1.20:** persisted 5 s duration accumulator sharing the exact reset/persistence class of Ah/Wh/peak. Outage #3 (after fix conditions): peak 1056.6 W > avg 905.4 W ✓ |
| F5 | Apparent Ri n=2 at 1.82 mΩ — below the 2.63 mΩ ohmic floor | 5 s dwell sampled where dV/dt ≈ 20 mV/s (polarization developing) with INA228 *sequential* V/I conversion windows → ±20 % phase scatter | **V1.21:** dwell 45 s + ±15 % current-stability gate; commissioning samples (n=2) struck from trend; expected repeatable ~3.3–3.5 mΩ |

Also in V1.21: **Acknowledge Alert** button (clears the sticky `alert_reason` breadcrumb; HA recorder retains the forensic row), `alert_reason` boot-initialized to `none`, OLED layout v7 (uniform 12 px / 13 px pitch / x=6; fixed row clipping at y≥54).

**Validation discipline:** every firmware revision passed the full gate — config validation → codegen → standalone lambda compile check → complete `esphome compile` to linked firmware, zero errors — before flashing (sandbox ESPHome 2026.6.5; device builds on 2026.4.3).

### 3.3 Corrected event ledger
| Event | As recorded | Corrected | Cause |
|---|---|---|---|
| Outage #2 | 753 min, 80.4 W avg, 73.6 W peak | **939 min, 64.5 W avg** (two-level 41 W/70 W profile), 76.13 Ah / 1009.5 Wh (correct), peak correct | F4: mid-event reboot at 23:02 UTC ate 186 min of the duration anchor. CSV integration reproduces the firmware's Ah/Wh to 0.15 % |
| Outage #3 | 16.5 min, 19.201 Ah, 249.38 Wh, 905.4 W avg, 1056.6 W peak | Valid as recorded (my independent integration: 19.47 Ah / 252.9 Wh, Δ1.4 % = window edges) | — |

---

## 4. Acceptance Tests and Results

### 4.1 INA228 post-rework qualification (three-tier)
The breakout's 15 mΩ shunt was removed for external-shunt operation; survival was proven in tiers: **Tier 1** — I²C ACK at 0x40, MANUFACTURER_ID 0x5449 ("TI"), DEVICE_ID die 0x228: die alive. **Tier 2** — inputs shorted: shunt-channel offset **0.9 µV** (≡ 2.4 mA at 375 µΩ — an order of magnitude inside the 10 µV pass gate and beneath the production 0.05 A detection band). **Tier 3** — known-current comparison and, ultimately, in-system validation against the Kill-A-Watt energy ledger. Cross-check: hardware charge accumulator behavior (charge ≠ 0 with energy = 0 at floating VBUS) matched the register model exactly.

### 4.2 Power-on and fail-loud behavior (§8.2 of Wiring Summary)
+3V3 = 3.30 V; I²C discovery 0x40 + 0x3D; VBUS lead validated (13.415 V pack reading, FAULT cleared). **Fail-loud demonstrated live:** with VBUS floating (bench), the 8–16 V plausibility guard produced NaN → `bank_state` FAULT, SOC integration froze while raw current kept publishing, and the BUVL hardware alert re-fired each 1.58 s averaged-conversion cycle — every element of the §6.5 design contract observed in operation, not inferred.

### 4.3 Protection subsystem — exercised in anger
| Layer | Event | Result |
|---|---|---|
| POL 1500 W hardware alert | Dryer-high spike, ~1670 W averaged DC | **True positive** at 17:52:37 UTC; latched, decoded `OVER-P`, latch self-cleared on DIAG_ALRT read |
| SUVL −250 A | ~146 A instantaneous peak (KAW-derived) | Correct non-fire at 40 % margin |
| Firmware knee/cliff | Slope −76 mV/min at load application (7.6× cliff threshold) | Correct non-fire — 12.65 V gate discriminated "load step" from "battery dying" |
| BUVL / warning / critical / emergency | Vmin 12.851 under 130 A | All correctly silent (≥450 mV margin) |
| BOVL 14.80 V | Charge Vmax 14.584 V | Correctly silent (216 mV margin) |
| Debounce integrity | Two inverter-overload trips (<60 s gaps) | `is_discharging` rode through: **one** outage event, no counter churn |

A full protection confusion-matrix diagonal — true positive, true negatives under provocation at both current extremes — was collected in a single afternoon.

### 4.4 Full-charge anchor
LiTime charge 18:13–19:50 UTC: absorption confirmed (≥14.20 V sustained), charger-stop edge detected, **anchor fired**: SOC snapped to 100.0 %, cycle counter → 1, cycle summary published (CE, peaks, mean discharge V, CV absorption time), counters reset. Operator-verified on the dashboard 2026-07-16.

---

## 5. Performance Characterization

### 5.1 Discharge campaign
| Leg | Duration | Mean / Peak | Vmin | Ah | Notes |
|---|---|---|---|---|---|
| 41 W | 187 min | 3.09 A | 13.27 | 9.63 | light-load leg |
| 70 W | 752 min | 5.31 / 5.56 A | 13.25 | 66.50 | overnight |
| ~1 kW (heater) | 16 min | 76.9 / 81.8 A | 12.962 | 19.47 | Kill-A-Watt companion test |
| ~1.05 kW + dryer | 12.7 min | 71.1 / 130.1 A (≈146 A inst.) | 12.851 | 15.09 | two inverter overload trips |

Total campaign extraction 110.7 Ah (27.9 % of validated capacity). At 0.26C the bank exhibits 3.5 % sag and no approach to the knee — the Peukert k = 1.003 characterization made visible.

### 5.2 Resistance decomposition (equivalent-circuit, measured)
| Term | Value | Method |
|---|---|---|
| R₀ (ohmic) | 2.63 mΩ | instantaneous load-release step (214 mV @ 81.3 A) |
| + fast polarization (≤2 min) | +1.1 mΩ | settled step minus R₀ |
| + diffusion (88 min) | +1.35 mΩ | 110 mV slow rebound |
| DC-IR (5 s / 60 s / 2 min) | 2.2 / 3.34 / 3.73 mΩ | dwell-dependence, textbook |

Ohmic fraction ≈ 52 % of total — consistent with published LFP equivalent-circuit splits (50–60 % with two RC branches). Per-battery allocation: ~15 mΩ DC including interconnect (~8–10 mΩ AC-IR-equivalent) — between premium spec (Battle Born 7 mΩ) and the conservative ≤40 mΩ manual figures; healthy for a mixed-brand bank. **Aging baseline: 3.73 mΩ (2-min) at 69 °F, ~80 % SOC; firmware trend metric: 45 s dwell samples, temperature-tagged. EOL flag: temperature-normalized doubling (~7 mΩ).**

### 5.3 OCV, plateau, and rest rules
Rested OCV points: 13.3185 V @ 80.8 % SOC and 13.292 V @ 75.9 % (3.330 / 3.322 V per cell — on published LFP tables; the coulomb-counted SOC axis and the electrochemistry agree via independent paths). Plateau slope **6.0 mV/%SOC (bank)** = 1.5 mV/% per cell — quantifying why voltage-based SOC is hopeless here and why the 0.2 mV-resolution instrument matters. Post-load relaxation: τ₆₃ 7.1 min, 95 % at 34 min — **the industry ~30-minute rest rule reproduced empirically**; a 5-minute reading after heavy load reads ~40 mV (~6 % SOC-equivalent) low. Post-charge surface decay: 14.58 → 13.97 V over 75 min and still falling — post-charge voltage is uninterpretable for hours, which is why the anchor is event-based, not voltage-based.

### 5.4 Charge characterization (LiTime 12 V 14.6 V 80 A)
CC 80 min at **78.6 A** (98.3 % of nameplate) → CV entry at 14.20 V → Vmax **14.584 V** (−16 mV of spec) → taper 66.7 → **6.48 A cutoff** (≈C/77) → stop. 115.39 Ah / 1586 Wh in 98 min at 0.157C. Firmware absorption clock 16.82 min vs. independently computed 17.3 min (Δ = designed sensor debounce). **BMS balancing signature captured:** 10.7 min above 14.4 V with 183 mV pk-pk oscillation, 8 reversals — reproducing the ~80–90 s cycles documented in the repo's Shelly-era study, now a countable weak-string trend metric.

### 5.5 Efficiency ladder
| Quantity | Value | Notes |
|---|---|---|
| Voltaic efficiency | **95.8 %** | mean discharge 13.17 V ÷ energy-weighted charge 13.745 V; predicted 95–96 % from the Ri model *before* the charge ran |
| Cycle-1 coulombic "efficiency" | 95.78 % — **accounting floor, not a measurement** | see §5.6 |
| True CE (predicted, cycle 2+) | ≥98.5 % | published LFP ≥99 % |
| Round-trip energy (steady-state est.) | **~94.8 %** | voltaic × CE; low edge of published 95–98 % band, expected at this test profile's atypically high C-rates |
| Charger AC→DC | **95.7 % ± 2.5 %** | 1586 Wh DC ÷ ~1657 Wh AC (112-min KAW window, idle-tail corrected); at/above typical 85–93 % class |
| Inverter DC→AC | **87–94 %, provisional** | two tests disagree beyond error bars due to unsynchronized measurement windows; definitive protocol in §8.1. Self-consumption ≈ 127 W at ~1 kW established |

### 5.6 Cycle-1 CE reconciliation (worked example)
Charged 115.39 Ah to replace 110.71 Ah discharged: excess 4.68 Ah. Ledger: true CE loss ≤1.1 Ah + BMS balancing + **~3.5 Ah pre-commissioning deficit** — the bank had rested since a July 5 full charge (5 × BMS standby ≈ 1.3–2.6 Ah over 11 days) and powered a lamp session (~2–3.5 Ah), consumption that predates the coulomb counter. Operator history brackets the deficit at 3–6 Ah: **the ledger balances.** First-cycle CE from an unanchored start is structurally a floor; cycle 2 provides the first valid CE sample.

### 5.7 Instrument roles and cross-checks
| Instrument | Role | Basis |
|---|---|---|
| INA228 chain | **Energy/authority** — integrations agree with independent CSV integration to 0.03–0.15 % | 1.58 s sequential averaging clips <2 s transients (recorded 130.1 A vs ≈146 A instantaneous): energy instrument, not peak instrument |
| Kill-A-Watt | AC energy + **max-hold peak** instrument | ±2 % class |
| Shelly Plus Uni | Independent voltage watchdog | reads 24–34 mV low, load-dependent (different sense-tap IR paths); tracks 300 mV sag faithfully; 10 mV quantization — cross-check, not calibration reference |
| DS18B20 | Pack thermal + Ri temperature tagging | +2.7 °F at 0.157C charge; ≤0.1 °F at 22 W discharge heating — thermal margin is a non-issue below ~0.5C |

---

## 6. Alarm Coordination Summary (as commissioned)

| Threshold | Setting | Worst observed approach | Margin |
|---|---|---|---|
| Voltage Warning | 12.40 V | 12.851 V (130 A) | 451 mV |
| Critical / BUVL (HW) | 12.20 V | 12.851 V | 651 mV |
| Emergency | 11.80 V | — | >1 V |
| Overvoltage / BOVL (HW) | 14.80 V | 14.584 V (charge) | 216 mV |
| SOVL (HW) | +250 A | +79.3 A | 68 % |
| SUVL (HW) | −250 A | ≈−146 A instantaneous | 42 % |
| POL (HW) | 1500 W | ~1670 W — **tripped, correctly** | true positive |
| Cliff (slope+V gate) | −10 mV/min AND <12.65 V | −76 mV/min at 13.0 V — correctly silent | gate validated |
| Operator SOC floor | 20 % | 72.1 % (campaign minimum) | — |

---

## 7. As-Built Deviations from Wiring Summary Rev 1.9

1. **Charger DC− lands on the shunt's load-side bolt**, not the busbar face — electrically the same node (§4.7's actual requirement is *load side of shunt*, satisfied). Stacked-lug joint added to the re-torque and quarterly discoloration checks. Amend §4.7 as-built note.
2. **OLED at I²C 0x3D** (STEMMA ADDR jumper open). Amend §6.6, including the vintage distinction (pre-2019 boards are SPI-default and reset-unmanaged; STEMMA boards are I²C-default with auto-reset).
3. **Status LED functional as installed** (idle slow-flash / active solid verified) — record the as-built LED wiring against §13 item K so Rev 1.1 fab notes reflect reality.
4. Item H closure amended per §3.1 (variant identity, not pin order).

---

## 8. Outstanding Items and Recommendations

### 8.1 Measurements
1. **Definitive inverter-efficiency run** (the one open number): single steady resistive load, Kill-A-Watt reset/stopped at photographed HA timestamps, ≥30 min. Pins η to ±1.5 %, replacing the 87–94 % provisional band.
2. **§7.1 shunt calibration** against a calibrated clamp at ~115 A: brings the ±1 % DROK tolerance to ~0.1 % of reference and tightens the charger-efficiency figure.
3. **Cycle 2 coulombic efficiency** — first valid CE sample; expect ≥98.5 %. Absorption-time trend continues (baseline 16.8 min).
4. First V1.21 Ri sample from a rest→heater step — predicted 3.3–3.5 mΩ; strike the n=2 commissioning samples from trends.

### 8.2 Housekeeping
5. Credentials to `secrets.yaml`; rotate API key and OTA password (checklist §8.1 item, still open).
6. Wiring Summary amendments per §7 above; reconcile the working tree so the archived YAML is the compiled YAML (F1 recurrence guard).
7. Bank entities into InfluxDB for multi-year Ri / CE / absorption-time retention (HA recorder purge outlives none of these trends).
8. Add the **Acknowledge Alert** button to the dashboard Device Health card.
9. NVS budget: ~29 persisted keys after V1.20/V1.21 — within the C3 partition; keep counting per rev.
10. Quarterly (§10): VBUS-lead fuse continuity, Kelvin taps <1 mΩ, stacked charger lug inspection, monitor-vs-DMM voltage check.

### 8.3 Known limits (documented, accepted)
- The full-charge anchor's press/release pairing is not reboot-proof (same structural class as the fixed outage defect); consequence is a missed anchor, mitigated by the Mark Full button and OLED page ④ guidance.
- INA228 averaging under-reports sub-2 s transients by design; SUVL (hardware, per-conversion) is the fast-transient guard.
- Ri trend samples require the load to persist 45 s and hold within ±15 % — deliberate; brief surges are not valid Ri stimuli.

---

## 9. Data Provenance

HA recorder CSV exports (voltage ×2 instruments, current, power, slope, temperature; 2 s native cadence, LSB-faithful), Kill-A-Watt energy/max-hold readings (three windows), Pololu packing slip 1J613636, device logs (boot arming, ALERT decodes, anchor event), and dashboard operator verifications. All firmware revisions validated through the four-layer compile gate before flash; independent Python re-integration of every headline Ah/Wh figure agreed with firmware accumulators to ≤1.4 % (window-edge limited) and ≤0.15 % (like-for-like windows).

---

*End of commissioning report.*
