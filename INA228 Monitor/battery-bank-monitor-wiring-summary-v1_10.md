# 12V 500Ah LiFePO4 Battery Bank Monitoring — Wiring Summary

**System:** 12 V / 500 Ah LiFePO4 battery bank with Giandel 1500 W inverter (manual transfer switch, floating neutral bonded at the main panel)
**Monitor board:** Battery_Bank-Monitor-THT **V2** (native Adafruit INA228 footprint) + Adafruit INA228 breakout
**Current shunt:** Repurposed DROK 200 A / 75 mV manganin shunt, **in the negative cable (low-side)**
**Document revision:** 1.10 (PCB **Rev 1.1 verified fab-ready** — LED fix confirmed, item K closed; items I and J closed (rail renamed **V_FUSED**, antenna = included **U.FL external**); §6.6 pull-up caution **closed** (keep both onboard sets — analysis in §6.6); test points added; Rev 1.1 verification record in §8.5)
**Author:** William Collis
**Status:** Pre-build reference — **V2 Rev 1.1 electrically verified fab-ready** (independent review 2026-06-10: connectivity, GND return, clearance, decoupling, I²C margins all pass — §8.5). Remaining before Gerber upload: cosmetic file hygiene (§13 item L) + native DRC re-run after final edits.

---

## Revision History

| Rev | Notes |
|---|---|
| 1.0–1.2 | Initial pre-build drafts; Pololu ideal-diode reverse protection; LiTime 80 A charger integration. Low-side topology (inherited default). |
| 1.3–1.6 | **High-side era.** Shunt moved to the positive cable to resolve the V1-carrier VBUS-on-pin-5 problem and to make the measurement immune to negative-side grounding. Required on the V1 carrier: U2 pin-5 lift, R2 DNP, breakout VBUS jumper closed, and inline fuses on both Kelvin sense leads (sense leads sat at battery+ potential). 1.4 tracked firmware V1.12 (cadence/anchor corrections); 1.5 tracked V1.13 (manual-model robustness); 1.6 tracked V1.14 (local OLED panel + wake button). |
| 1.7 | **Two coupled changes.** (1) **Topology reverted to low-side** — the shunt stays in the negative cable where it is physically installed today, eliminating all 2/0 high-current rework. The decision rests on two facts established in review: with USB used only for the *first* flash (bench, 12 V disconnected) and OTA thereafter, the USB ground-loop path never coexists with a live bus; and with a single DC earth reference (the inverter chassis bond at the negative busbar) maintained, a negative-leg shunt has no parallel path to bypass. The earlier high-side move solved a measurement-integrity problem that, for this specific install, is solved instead by *grounding discipline* — at the cost of one fused VBUS lead instead of two Kelvin-lead fuses and a 200 A cable relocation. (2) **Board changed to Battery_Bank-Monitor-THT V2**, a clean carrier with a native INA228 8-pin socket: the V1 adaptation hacks (pin-5 lift, R2 DNP, jumper-closed workaround) are gone, ALERT now lands on a real GPIO, and the button moved off the UART pin. **All shunt-sense and bus-voltage connections are made at the INA228 breakout's own VIN+/VBUS/VIN− terminal block — no carrier trace required.** Adds §13 *Open Risks / Pre-Fab To-Do*. Inverter corrected from the doc's stale "2000 W" to the actual Giandel 1500 W. |
| **1.8** | **PCB cross-reference alignment pass.** Firmware reference updated V1.14 → V1.15. §6.1 pin-map defect (§13D) **closed**: firmware button pin changed GPIO21 → GPIO4 (D2); GPIO20 pullup clamp removed (dead code on V2 — U1 GPIO20 pad carries no net). §13F BOM placeholders **closed**: KiCad PCB Description fields confirm R2 = 10K ¼W (ALERT pull-up ✓), C4 = 47 µF 50 V radial (≥25 V requirement satisfied ✓), C1 = 10 µF 25 V X7R. C4 polarity note added: pad 1 → VIN (positive rail). §4.6 connector map updated to reflect V1.15 pin assignments. No wiring or topology changes. |
| **1.9** | **Firmware V1.19 + LED alignment pass.** Tracks firmware V1.19 (production review fixes V1.18 + features V1.19). (1) **Status LED added** — 3 mm green on U1 GPIO20 via R4: slow flash = idle (proof-of-life), solid = charging/discharging, fast flash = FAULT. **Rev 1 PCB LED circuit is defective as drawn** (cathode on the drive node, R4 fed from +3V3 — LED reverse-biased in every GPIO state); §13 item K records the Rev 1.1 fix (GPIO20 → R4 → anode, cathode → GND, active-high) and **R4 changed 220 Ω → 1 kΩ** (~1.2 mA). (2) **INA228 ALERT armed** (V1.16–V1.18): BUVL 12.20 V / BOVL 14.80 V / SOVL +250 A / SUVL −250 A / POL 1500 W, decoded `alert_reason` on GPIO5 — supersedes "provisioned, not wired". (3) **CV/absorption-time telemetry** (V1.19): per-session absorption duration as a charger-health trend metric. (4) §12 INA228 datasheet lit number corrected SBOS951 → **SLYS021** (per TI EVM guide SBOU241 literature table; SBOSA20 is the INA237). No wiring or topology changes. |
| **1.10** | **PCB Rev 1.1 verification + closures.** Independent file-level review of the corrected board (LED fix as built: footprint rotated/pads renumbered onto the *same two drilled holes* — drive trace and zone copper untouched; polarity marks verified at the GND pad). **Item K CLOSED.** **Item I CLOSED** — 13 V rail renamed **V_FUSED**. **Item J CLOSED** — antenna = XIAO's included **U.FL external** (placement guidance §8.2). Six test points added (V_FUSED, +3V3, GND, SDA, SCL, ALERT). §6.6 pull-up caution **closed**: keep both onboard pull-up sets (5 kΩ effective; 0.66 mA sink vs 3 mA limit; τ ≈ 250 ns vs 1000 ns standard-mode limit — removing the 938's resistors would *halve* the margin). New §8.5 verification record. New item L (cosmetic pre-Gerber hygiene). No wiring or topology changes. |

---

## 1. Purpose

Replace the standalone DROK display unit with a Wi-Fi-connected monitoring solution that reports current, voltage, temperature, accumulated Ah/Wh, and runtime estimates to Home Assistant in real time, plus a local panel readout for the manual shutdown decision. Same data quality as the UPS monitor at battery-bank scale (200 A peak vs. 250 mA).

**Engineering rationale (V2 board).** The original UPS-Monitor-THT carrier was designed around the INA260 footprint; hosting an INA228 on it required lifting header pin 5 (INA228 puts VBUS where the INA260 had ALERT), leaving R2 unpopulated, and closing the breakout's VBUS jumper. The **V2 board is laid out natively for the INA228 8-pin header**, so those adaptations are retired: the carrier connects only the logic side (VIN/GND/SCL/SDA on pins 1–4) and the ALERT pin (pin 8) to a real GPIO, and leaves the three measurement pins (VBUS pin 5, VIN+ pin 6, VIN− pin 7) as carrier no-connects **by design** — these three signals are landed instead on the **INA228 breakout's own 3-position terminal block (VIN+ / VBUS / VIN−)**, where they belong. No carrier trace carries shunt-sense or bus-voltage current, which is correct: the measurement connections are all field-wired at the breakout terminal block (§3.3, §4.2–4.3).

This document covers the INA228 + external shunt configuration in **low-side (negative-cable) topology** on the V2 board.

---

## 2. System Topology Overview

```
                    ┌─────────────────────────────────────────────────┐
                    │      BUSBAR (+) — 12 V positive (UNBROKEN)      │
                    └──┬───────┬─────────────┬─────────────┬──────────┘
                       │       │             │             │
                  [Inverter+] [Charger+]  [Other loads+]  [Battery+]  ← direct, no shunt
                                                                │
                                                        ┌───────┴───────┐
                                                        │ BATTERY BANK  │
                                                        │ 500 Ah LiFePO4│
                                                        └───────┬───────┘
                                                            [Battery−]
                                                                │
                                                       ┌────────┴────────┐
                                                       │      SHUNT      │ 200 A / 75 mV
                                                       │     (DROK)      │ LOW-SIDE
                                                       └────────┬────────┘
                                                                │
                    ┌───────────────────────────────────────────┴────────┐
                    │     BUSBAR (−) — 12 V return (LOAD side of shunt)  │
                    └──┬───────────────┬─────────────┬──────────────┘
                       │               │             │
                   [Inverter−]    [Charger−]    [Other loads−]
```

**Measurement configuration:** **Low-side current sensing** — shunt in the negative cable between battery− and the negative busbar. *Reverted from the Rev 1.3–1.6 high-side topology; this matches the shunt's existing physical location.*

**Sign convention:** Positive current = battery charging, negative = discharging. Unchanged (firmware Option B). The physical VIN+/VIN− assignment that produces this convention differs from high-side and is verified at commissioning — see §6.2.

**Ground reference:** Single-point ground at the **negative busbar** (load side of the shunt). This is the system-ground node and is earth-referenced through the inverter chassis bond; the board's GND, the INA228 GND, and all instrumentation reference it.

### 2.1 Why Low-Side (Rev 1.7 reversion)

The high-side era (1.3–1.6) was driven by two real concerns: the V1-carrier VBUS-on-pin-5 hazard, and the vulnerability of a low-side shunt to a parallel ground path bypassing the measurement. The V2 board and a closer reading of *this* install dissolve both:

1. **The VBUS-on-pin-5 hazard was a V1-carrier artifact, not a topology fact.** The V2 board leaves VBUS (U2 pin 5) as a carrier no-connect — bus voltage is sourced at the breakout's own terminal block, not through any GPIO — so there is no GPIO to drive 13 V into regardless of topology. The pin-5 lift / R2 DNP / jumper-closed stack is gone.

2. **The parallel-path risk is a function of how many earth references straddle the shunt, not of the leg per se.** A low-side shunt only mis-reads if current reaches battery-negative by a path that skips it — which requires a *second* earth reference on the battery-negative side. In this install every load, the charger, and the inverter land on the **negative busbar (load side)**, and the inverter chassis bond earths the system there. The battery-negative *terminal* (battery side of the shunt) has no earth reference. With one earth point, earth is a dead-end stub, not a bypass conductor. The only way to break this is to run a separate earth bond to the battery-negative terminal — a deliberate act that the build does not include (see §13 item E and §9).

3. **This is how the now-retired DROK coulometer worked trouble-free** — it was a galvanically self-contained island sharing no ground with other equipment. The INA228 board necessarily shares logic ground with the XIAO, but the *only* additional shared-ground hazard it introduces is the USB connection during flashing, which is removed by discipline (below).

**The one real cost of low-side on this board:** the INA228 must measure bus voltage relative to its near-ground GND, so **VBUS must be driven from battery+** — landed on the breakout's VBUS terminal (§3.3, §4.3). That VBUS lead is the single wire at battery+ potential and must be fused (§3.3). This replaces the high-side cost (two Kelvin-lead fuses + a 200 A cable relocation) with one fused terminal lead.

**Operating discipline this topology depends on (both easy to maintain):**
- **USB only for the first flash, on the bench, with TB1 disconnected.** OTA thereafter. Never connect USB while the 12 V bus is live — this prevents both the USB→PC ground loop around the shunt and a 3V3 source conflict between the buck output and the XIAO's USB-fed LDO.
- **One DC earth reference only** — the inverter chassis bond at the negative busbar. Do not add a separate battery-negative-to-earth bond.

---

## 3. Hardware Bill of Materials

### 3.1 Main Components

| Item | Part | Source | Notes |
|---|---|---|---|
| Monitor PCB | **Battery_Bank-Monitor-THT V2 Rev 1.1** | OSH Park (target) | Native INA228 8-pin socket. **Electrically verified fab-ready (§8.5); item L hygiene before Gerber export.** |
| INA228 breakout | Adafruit 5832 (or 6349 INA228 variant) | Adafruit / DigiKey | **Onboard 15 mΩ shunt must be removed; VBUS jumper LEFT OPEN (low-side default); see §3.3** |
| Microcontroller | Seeed XIAO ESP32-C3 | Seeed Studio | OTA-flashable. **Antenna: included U.FL external flex (item J closed)** — placement per §8.2. |
| Regulator | Pololu D24V7F3 | Pololu #2842 | 4–36 V → 3.3 V at 600 mA. **Verify VIN/GND/VOUT pin order against module silk before fab (§13 item H).** |
| Reverse-voltage protector | (none on board) | — | **Accepted risk for this single self-wired build: the V2 board has NO on-board or external reverse protection (§13 item C). Be deliberate about TB1 polarity at connect time — a reversed feed puts reverse voltage on C4 (electrolytic).** |
| Temperature sensor | DS18B20 module (integral 4.7 kΩ pull-up) | Generic | Mount to battery case (isolated from any conductive surface). |
| Board input fuse | 1 A slow-blow 5×20 mm | Würth 696108003002 | F1 — protects the board power feed only (not the sense/VBUS leads). |
| **VBUS lead fuse (Rev 1.7)** | **1× 100–250 mA fast-blow, inline holder** | **Generic** | **On the VBUS terminal lead, at the busbar end. The low-side VBUS lead is the one wire at battery+ potential.** |
| Current shunt | 200 A / 75 mV manganin | Repurposed DROK | **Stays in the negative cable.** Verify Kelvin sense terminals present. |
| Bank charger | LiTime 12V (14.6V) 80A LiFePO4 | LiTime | Existing AC wall charger, permanently wired to busbars. |
| Local display | Adafruit 938 — 1.3″ 128×64 OLED (SSD1306, I²C 0x3C) | Adafruit | Via J1 (4-pin I²C). See §6.6. |
| Wake button | Adafruit 1505 — 16 mm momentary | Adafruit | Via J2 (2-pin). **Now on GPIO4 (D2), not GPIO21 — see §6.1.** |
| **Status LED (Rev 1.9)** | **3 mm THT LED, green** | Generic | On-board, GPIO20-driven (§6.7). Specify **green** in the LED value field for BOM clarity. |
| **R4 (Rev 1.9)** | **1 kΩ ¼W 5% axial** | Generic | LED series resistor — **1 kΩ, not the 220 Ω in the Rev 1 value field** (~1.2 mA lit). |

### 3.2 Wiring Materials

| Item | Spec | Purpose |
|---|---|---|
| Battery main cables | 2/0 AWG | Battery− ↔ shunt ↔ negative busbar; battery+ → positive busbar (direct). **No change from existing install.** |
| Sense pair | 22 AWG twisted pair (unshielded) | DROK shunt Kelvin → INA228 **VIN+/VIN− terminal block**. **No inline fuses — sense leads sit near ground in low-side.** |
| **VBUS lead** | **22–24 AWG, inline-fused** | **Positive busbar → INA228 VBUS terminal (jumper open). Carries µA; fused at busbar end against a short.** |
| Monitor power feed | 18 AWG | Positive busbar → TB1 BATT_RAW (no reverse-protection device inline — accepted) |
| Monitor ground | 18 AWG | Negative busbar → TB1 GND |
| DS18B20 cable | 3-conductor, ≥22 AWG | TB2 → battery case sensor |

### 3.3 Critical Hardware Modifications Required

**Before installing the INA228 breakout in U2:**

1. **Remove the onboard 15 mΩ shunt resistor** from the breakout (SMD part between the VIN+/VIN− terminal pads). Mandatory — otherwise it parallels the external DROK shunt and is destroyed at bank currents.

2. **Leave the VBUS jumper OPEN** (the breakout's default; on the back, above the VIN+/VBUS pins). Open = low-side configuration: VBUS is independent of VIN+ and must be driven externally (step 3). *Per Adafruit: for low-side bus-voltage measurement, leave the jumper open and connect the VBUS pin to the voltage bus.*

3. **Wire VBUS at the terminal block (low-side requirement).** The INA228 breakout's 3-position terminal block exposes **VIN+ / VBUS / VIN−**. Land the **positive busbar** on the **VBUS** terminal, through a 100–250 mA inline fuse at the busbar end. With the jumper open, the three terminals are independent, so VBUS is sourced here and the carrier needs no trace for it (U2 pin 5 stays a no-connect). Without this connection the INA228 reports a floating/garbage bus voltage and the firmware's voltage-dependent logic (14.20 V absorption detection, 8–16 V plausibility guard, SOC context) is invalid.

4. **Verify the DROK shunt's Kelvin sense terminals** — small screws on the manganin strip, separate from the heavy bolts. Without them, accuracy degrades from ±1 % to ~±5 %.

> **No pin-5 lift, no R2 DNP, no Kelvin-lead fuses.** All three were V1-carrier / high-side artifacts. On the V2 board with low-side sensing they do not apply: ALERT lands natively on U2 pin 8 → a GPIO, VBUS pin 5 is a carrier no-connect, and the sense leads sit near ground.

---

## 4. Detailed Wiring Summary

### 4.1 High-Current Path (unchanged from existing install)
**Positive cable** (2/0 AWG): Battery (+) → Positive busbar. Direct, **no shunt** — the positive cable is continuous.

**Negative cable** (2/0 AWG): Battery (−) → **shunt battery-side bolt**; shunt **load-side bolt** → Negative busbar. The shunt sits in the negative leg. All loads, charger, and inverter return to the negative busbar (load side of the shunt).

Crimp/torque all ring lugs to the shunt manufacturer's spec (typically 12–15 N·m for 2/0 hardware).

### 4.2 Sense Wiring — INA228 Inputs

**22 AWG twisted pair, INA228 terminal block to shunt Kelvin taps, no inline fuses:**

| Wire | From (shunt Kelvin) | To (INA228 terminal block) | Net |
|---|---|---|---|
| Sense A | **Battery-side** Kelvin terminal | **VIN+** | VIN+ |
| Sense B | **Load-side** Kelvin terminal (busbar side) | **VIN−** | VIN− |

The VIN+/VIN− assignment above is the starting point; **confirm the sign at commissioning** (§8.4) and swap the pair if current reads inverted. In low-side the polarity relationship is the reverse of high-side, so the assignment is verified empirically, not assumed.

**Why no shielding / no fuses:** the differential ADC rejects common-mode pickup, and in low-side the sense leads are within ±75 mV of ground — there is no battery+ potential on them to protect against. (The battery+ hazard in this build lives on the VBUS lead, §4.3.)

### 4.3 VBUS Lead (low-side bus-voltage source)

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| VBUS lead | Positive busbar → 100–250 mA inline fuse | INA228 **VBUS** terminal | (off-carrier) | Drives the INA228 bus-voltage channel. Breakout jumper OPEN. µA load; fused against a short. |

**Reading note:** GND is at the negative busbar, so the measured VBUS = (positive busbar) − (negative busbar) = pack voltage minus the negative-leg shunt drop (signed). At a full 200 A that drop is ≤75 mV (~0.5 %); at the low currents where the 14.20 V absorption threshold lives it is sub-millivolt. Negligible, but expect a reading a hair below a meter placed directly at the battery posts under heavy load.

### 4.4 Monitor Power Feed and Ground Reference

Power: Positive busbar → **TB1 BATT_RAW** → on-board F1 (1 A SB) → VIN rail → C4/C5 → U3 (Pololu D24V7F3) → +3V3. (No reverse-protection device in the feed — accepted, see below.)

Ground: Negative busbar → **TB1 GND** → board GND pour → INA228 GND, XIAO GND, regulator GND. **Single-point ground at the negative busbar.**

**Monitor self-draw is captured.** The board's supply current returns via GND → negative busbar → through the negative-leg shunt → battery−, so the ~10–25 mA self-draw flows through the shunt and the Coulomb counter sees it (a small constant discharge offset). The status LED adds ~1.2 mA while lit ((3.3 V − ~2.1 V Vf) / 1 kΩ), ~0.6 mA average at idle (50 % slow-flash duty) — also through the shunt, also captured. No SOC blind spot. *(Keep GND on the busbar side for this reason; referencing it to the battery-negative side would clean up the VBUS reading but would route the self-draw around the shunt — a worse trade.)*

**Reverse-polarity protection — none, accepted.** The V2 board has no on-board reverse protection and this build adds no external device. For a single, self-wired install where the builder controls and double-checks polarity at connect time, the residual risk is accepted. The only consequence to keep in mind: a reversed TB1 connection puts reverse voltage on C4 (polarized electrolytic) and the buck input, so **confirm TB1 polarity before energizing**. Power-up tell: the status LED is *firmware-driven* (GPIO20, §6.7), not a power-rail indicator, and the XIAO ESP32-C3 has no power LED — so the tell is the LED staying **dark beyond ~10 s** after power-up (boot + first pattern tick complete well inside that). F1 does not block reverse voltage.

### 4.5 DS18B20 Temperature Sensor (TB2)

| TB2 pin | Net | DS18B20 |
|---|---|---|
| 1 | GND | GND |
| 2 | GPIO10_DQ | DQ (module has integral 4.7 kΩ pull-up) |
| 3 | +3V3 | Vdd |

Mount the sensor body against the battery case, **electrically isolated** from any conductive surface (kapton/thermal pad or a sealed probe) — a conductive pack case contacting the sensor ground would tie battery-side potential to system ground (§13 item E note).

> **Probe-cable routing.** 1-Wire is the most EMI-susceptible net in the system (high-impedance, off-board). Keep the TB2→probe cable short, route it away from the 200 A battery cables, and cross them at 90° if a crossing is unavoidable. Failure mode is benign — the DS18B20's CRC plus the firmware stale-data watchdog turn corruption into visible NaN, never a silent wrong reading.

### 4.6 V2 Board Connector / Socket Map (as drawn)

| Ref | Type | Pinout (pad → net) |
|---|---|---|
| TB1 | 2-pos Phoenix MKDS-1.5-3.81 | 1 = GND, 2 = BATT_RAW |
| F1 | 5×20 fuse | BATT_RAW ↔ V_FUSED |
| U3 | Pololu D24V7F3 (1×03 socket) | 1 = +3V3 (VOUT), 2 = GND, 3 = V_FUSED (module VIN) — **verify against module silk (item H)** |
| U2 | INA228 (1×08 socket) | 1 = +3V3, 2 = GND, 3 = SCL, 4 = SDA, **5 = VBUS (NC)**, **6 = VIN+ (NC)**, **7 = VIN− (NC)**, 8 = ALERT |
| U1 | XIAO ESP32-C3 | 3V3 = +3V3, GND = GND, SDA = GPIO6, SCL = GPIO7, GPIO10 = DQ, **D2/GPIO4 = button**, **D3/GPIO5 = ALERT**, **D7/GPIO20 = status LED (Rev 1.9)** |
| J1 | 4-pin JST-XH (OLED I²C) | 1 = SDA, 2 = SCL, 3 = GND, 4 = +3V3 |
| J2 | 2-pin JST-XH (button) | 1 = GPIO4_BTN, 2 = GND |
| TB2 | 3-pin JST-XH (DS18B20) | 1 = GND, 2 = GPIO10_DQ, 3 = +3V3 |
| R2 | ALERT pull-up | ALERT ↔ +3V3 — **10 kΩ ¼W 5% axial (confirmed in PCB)** |
| R3 | 10 k | GPIO4_BTN ↔ +3V3 (button pull-up) |
| **R4** | LED series resistor | **GPIO20 ↔ LED anode — 1 kΩ ¼W 5% axial** (confirmed: PCB Description field + back-silk legend; Value field still holds the footprint name — item L) |
| **LED1** | 3 mm green THT | **anode (pad 2, 43.0/52.5) ← R4; cathode (pad 1, 40.46/52.5) → GND — Rev 1.1 fix VERIFIED (§8.5).** Note: pad shapes were swapped in the fix, so the **square pad is the ANODE** (counter to the square-pad-equals-cathode habit); the silk flat, fab cathode bar, and explicit +/− marks are at the correct ends — **populate by the silk marks** |
| C1 | output cap | +3V3 ↔ GND — **10 µF 25 V X7R radial (confirmed in PCB)** |
| C2, C3 | 0.1 µF | +3V3 decoupling |
| C4 | radial electrolytic | V_FUSED ↔ GND — **47 µF 50 V radial (confirmed; pad 1 = V_FUSED = positive rail; +/− silk marks verified present)** |
| C5 | 0.1 µF | V_FUSED bypass |
| TP×6 | THT test points 2.0 mm pad / 1.0 mm drill | **V_FUSED** (silk still reads "VIN" — item L), **+3V3, GND, SDA, SCL, ALERT** — added Rev 1.1 for field debug |

> **Net-name caution — CLOSED (Rev 1.1 / item I).** The 13 V rail is now named **V_FUSED** in the PCB, eliminating the collision with the INA228 breakout's "VIN" pin (its 3.3 V logic supply, correctly tied to +3V3). Residual: the V_FUSED **test point's silk label** still reads "VIN" — cosmetic, listed under item L. The breakout's VIN+/VBUS/VIN− *terminal block* naming is unchanged and unrelated.

### 4.7 LiTime 80 A Charger Integration (low-side)

The bank is charged by a **LiTime 12V (14.6V) 80A** AC-input wall charger, permanently wired to the busbars.

| Wire | From | To |
|---|---|---|
| Charger DC+ | Positive busbar | Charger output + |
| Charger DC− | **Negative busbar (load side of shunt)** | Charger output − |
| Charger AC | 120 V wall outlet | Charger AC input |

**Critical for low-side:** the charger DC− must land on the **negative busbar (load side of the shunt)**, never directly on the battery-negative terminal. Charging current then flows charger+ → positive busbar → battery+ → battery → battery− → **shunt** → negative busbar → charger−, and the INA228 sees it (positive = charging). Terminating DC− at the battery-negative post would bypass the shunt and the monitor would read 0 A during an 80 A charge.

**AC-DC isolation note.** A non-isolated charger that bonds its DC− to AC ground would create a second earth reference. Because the charger DC− is on the **load side** of the negative-leg shunt (same side as the inverter bond), that bond does **not** bypass the shunt — it sits on the same side as the existing earth reference. It remains good practice for noise; verify once (open circuit > ~10 MΩ between AC ground pin and DC− with the charger disconnected) but it is not a measurement-integrity stopper.

At 80 A through the 375 µΩ shunt: 30 mV drop, 2.4 W dissipation (~15 % of full-scale) — well within the INA228 ±163.84 mV range.

---

## 5. INA228 Configuration

### 5.1 I²C Address
Default **0x40** (A0/A1 open). Leave at factory. (UPS board uses 0x41.)

### 5.2 Shunt Calibration (ESPHome `ina2xx_i2c`, V1.14)

```yaml
sensor:
  - platform: ina2xx_i2c
    model: INA228
    address: 0x40
    shunt_resistance: 0.000375 ohm   # 75 mV / 200 A
    max_current: 200.0 A
    adc_range: 0          # ±163.84 mV (mandatory for 75 mV @ 200 A)
    reset_on_boot: false
    adc_time: 4120us
    adc_averaging: 128
    update_interval: 2s   # ≥ the ~1.58 s averaged-conversion cycle
```

LSB at the chip: **312.5 nV** (ADCRANGE=0) → **~0.83 mA at the shunt**; practical noise floor after 128× averaging ~5–10 mA. Max measurable: 163.84 mV / 375 µΩ = 437 A (headroom above the 200 A shunt). 128× averaging is retained to hold the noise floor far below the 0.05 A detection band — what makes the self-draw capture and sub-mAh self-discharge reconciliation clean.

---

## 6. Firmware

Firmware: `battery-bank-monitor.yaml` (**V1.19**). Since Rev 1.8 (V1.15): **V1.16–V1.18** armed the INA228 ALERT subsystem and passed a source-level production review (parse fix; raw-I2C register writes — `i2c::I2CBus` has no `write_register()`; DIAG_ALRT bit map corrected to the INA228 register map (TI SLYS021, cross-checked vs the Apache Mynewt INA228 driver) — V1.16's positions were each one bit high and MEMSTAT was inverted; DIAG_ALRT init corrected to 0xA000; SUVL armed at −250 A to cover discharge-direction over-current, which SOVL alone misses in Option B); **V1.18** added the status LED driver (§6.7); **V1.19** swapped the LED idle/active semantics and added CV/absorption-time telemetry (§6.8). The measurement logic, sign convention, parameters, and robustness guards are unchanged. Reviewed against ESPHome 2026.5.x source.

### 6.1 Pin Assignments — V2 board (current: firmware V1.19)

| Function | V1.14 firmware (V1 carrier) | **V2 board / V1.19 firmware** | Status |
|---|---|---|---|
| I²C SDA | GPIO6 | GPIO6 | unchanged |
| I²C SCL | GPIO7 | GPIO7 | unchanged |
| DS18B20 1-Wire | GPIO10 | GPIO10 | unchanged |
| Wake button | **GPIO21** (TX pad) | **GPIO4 (D2)** | updated in V1.15 |
| INA228 ALERT | unused (GPIO20 dead-trace clamp) | **GPIO5 (D3)** — **ARMED** (V1.16–V1.18): BUVL/BOVL/SOVL/SUVL/POL limits, latched active-low, decoded to `alert_reason` | supersedes Rev 1.8 "provisioned, not wired" |
| Status LED | — (none) | **GPIO20 (D7)** — output, active-high via R4 (§6.7). U0RXD pad, free because `logger: baud_rate: 0`. | **added V1.18; semantics V1.19; needs PCB Rev 1.1 (§13K)** |

### 6.2 Sign Convention (committed)

**POSITIVE = CHARGING, NEGATIVE = DISCHARGING** (firmware Option B). In low-side the physical relationship between flow direction and VIN+/VIN− polarity is the reverse of high-side, so the §4.2 lead assignment is the starting point and the sign is **confirmed empirically at commissioning** (§8.4); swap VIN+/VIN− if inverted. No firmware sign-flip — the convention is produced by the wiring.

### 6.3 System Parameters (values unchanged since V1.14; current firmware V1.19)

```yaml
validated_capacity_ah:        "397"
warning_voltage:              "12.40"
critical_voltage:             "12.20"
emergency_voltage:            "11.80"
overvoltage_threshold:        "14.80"
full_charge_v_min:            "14.20"   # absorption detection floor — depends on a valid VBUS (§3.3)
self_discharge_pct_per_month: "0.0"
```
`float_voltage`, `absorption_voltage`, and `validated_capacity_wh` are reference-only (not consumed by any lambda). Behavior is driven by the alarm/overvoltage/full-charge thresholds and `validated_capacity_ah`.

### 6.4 Separate YAML
Battery-bank firmware (`battery-bank-monitor.yaml`, 0x40) is independent of `ups-monitor.yaml` (0x41); the two evolve separately.

### 6.5 Robustness and Fault Handling (V1.13, unchanged)

Manual operating model — no HA control of the bank; the operator reads SOC and shuts the bank at ~20 %. The **data is the safety system**, so the firmware hardens SOC integrity:

- **Stale-bus watchdog:** no INA228 read > 10 s → `bank_state` FAULT, integration freezes.
- **Bus-voltage plausibility (8–16 V):** out-of-band readings dropped; sustained garbage trips the watchdog. *Depends on a valid VBUS lead (§3.3) — a floating VBUS in a mis-built low-side board would sit out-of-band and FAULT, which is at least fail-loud.*
- **Current-channel plausibility (≥350 A → FAULT):** freezes SOC integration and sets the **Current Channel Fault** diagnostic, catching a saturated/open-Kelvin channel.
- **Documented limit:** these bounds catch *garbage*, not *plausibly-but-wrong* (a partial/high-resistance Kelvin connection). Mitigations: the §10.1 quarterly electrical check and the §7.1 clamp-meter cross-check.
- **`reboot_timeout` disabled** (continuous local SOC publishing); **`safe_mode`** for OTA crash-loop recovery; **NVS** wear-leveled restore persistence.

### 6.6 Local Panel Display (added V1.14, layout revised V1.17; via J1/J2)

Adafruit 938 OLED (SSD1306, 0x3C) on the shared I²C bus (J1: SDA/SCL/GND/3V3); Adafruit 1505 momentary wake button (J2: GPIO4/GND). Four button-cycled pages (V/I/W/SOC; runtime+slope+knee/cliff; health/trust incl. Current Channel Fault; charge/absorption), 5-min auto-sleep, dark by default (SSD1306 burn-in). Display only *reads* published states — a display/button fault cannot affect SOC integrity or backup readiness.

> **Bus pull-up caution — CLOSED (Rev 1.10): keep BOTH onboard pull-up sets; do not modify the 938.** Analysis: 938 (10 kΩ) ∥ INA228 breakout (10 kΩ) = **5 kΩ effective**. Logic-low sink = 3.3 V / 5 k = **0.66 mA**, a fifth of the 3 mA I²C limit — nowhere near "too stiff." Rise time: bus capacitance ≈ 40–60 pF (two breakouts + ~90 mm board trace + short display harness), so τ ≈ 5 k × 50 pF ≈ **250 ns vs the 1000 ns standard-mode limit** — 4× margin at the firmware's 100 kHz. Removing the 938's resistors would double τ and halve that margin for zero benefit, and is rework risk on the display. Parallel pull-ups only become a concern at ~4–5 stacked device sets (≲2 kΩ effective). Verify the bus with both devices present at commissioning, as before.

> **Button siting.** The 1505 is not gasketed; the dry basement makes the non-sealed sidewall hole acceptable. Relocate to a damp/outdoor environment ⇒ swap for a gasketed 16 mm metal momentary (same hole, same 2-wire).

### 6.7 Status LED (added V1.18, semantics V1.19)

3 mm green LED, GPIO20 (D7) → R4 (1 kΩ) → anode, cathode → GND (active-high; requires PCB Rev 1.1, §13 item K). OBSERVABILITY layer — reads published states, cannot affect CORE. Semantics:

| Pattern | Meaning |
|---|---|
| **Slow flash** (0.5 Hz, 1 s/1 s) | Bank idle, no faults — **proof-of-life**: continuous evidence the firmware's 250 ms loop is running. A stuck-solid or stuck-dark LED is therefore unambiguously a fault tell (frozen MCU / dead board). |
| **Solid** | Charging or discharging (tracks the 30 s debounced charge/discharge sensors — no flicker on threshold noise) |
| **Fast flash** (2 Hz) | FAULT — mirrors `bank_state` (stale I²C bus, NaN, \|I\| > 350 A plausibility trip) |
| **Dark > ~10 s after power-up** | Commissioning fault tell (§4.4, §8.2) — board unpowered, reversed, or firmware not running |

Draw ~1.2 mA lit, ~0.6 mA average at idle; flows through the shunt, so the Coulomb counter captures it (§4.4).

### 6.8 CV/Absorption-Time Telemetry (V1.19)

Per-charge-session time spent in CV/absorption (V ≥ 14.2 V with charge current, per the existing absorption-phase sensor), as a **charger/bank-health trend metric**: absorption duration creeping upward across months at comparable depth-of-discharge is an early indicator of capacity fade or a weak parallel string. Two entities: **CV Absorption Time** (last completed full-charge session, NVS-persisted) and **CV Absorption Elapsed** (live, current session). Accumulation handles V-sag exit/re-entry within a session; partial sessions (no full-charge anchor) are **discarded** — only completed absorption profiles are valid trend samples. Constant ~−30 s offset vs true CV time from sensor debounce (irrelevant for trending). Single samples are noisy — read the trend, not the point. In-progress timing is lost on reboot (transient, consistent with `absorption_reached`).

---

## 7. Shunt Accuracy

200 A / 75 mV manganin: ±1–2 % initial tolerance, 50–100 ppm/°C tempco, ~15 W at 200 A — adequate for SOC on a 500 Ah bank (±2 A ≈ ±0.4 % FS).

### 7.1 Optional Calibration
Apply a known load (~115 A from a 1500 W heater), compare INA228 against a calibrated clamp, compute `shunt_corrected = shunt_nominal × (INA228 / reference)`, update the `shunt_resistance:` substitution, recompile, OTA-flash. Brings the system to ~0.1 % of reference.

---

## 8. Installation Checklist

### 8.1 Pre-Installation
- [x] Battery_Bank-Monitor-THT **V2 Rev 1.1** — LED circuit corrected and **independently verified** (§8.5); item K closed
- [ ] **Item L hygiene before Gerber export:** back-silk rev text "Rev 1" → "Rev 1.1"; Value fields on R2/R4/C1/C4 set to component values (currently footprint names; back-silk legend already correct); V_FUSED test-point silk "VIN" → "V_FUSED" (optional); confirm TB1 wire openings face the board edge in the 3D viewer
- [ ] Zones refilled + **native KiCad DRC re-run after item L edits** (expect only cosmetic silk warnings), Gerbers regenerated
- [ ] INA228 breakout: onboard 15 mΩ shunt removed; **VBUS jumper OPEN**
- [ ] **VBUS lead fuse (100–250 mA) + holder on hand**
- [ ] DROK shunt Kelvin terminals verified (shunt stays in negative cable)
- [ ] DS18B20 sourced; isolated mounting planned
- [ ] **Firmware V1.19 compiled** (V2 pin map, ALERT armed, status LED, CV-time telemetry all incorporated)
- [ ] Display bring-up planned: 938 at 0x3C alongside INA228 at 0x40; button cycles 4 pages; 5-min sleep
- [ ] I²C integrity to be verified with **both** devices connected
- [ ] Credentials moved to `!secret`; `signed_ota_verification` evaluated (bench round-trip first)

### 8.2 Initial Power-On
1. Seat U1 (XIAO), U2 (INA228, shunt removed, jumper open), U3 (Pololu) — verify U3 orientation.
2. **Disconnect inverter** for initial test.
3. **Bench-flash firmware via USB with TB1 disconnected**, then reconnect TB1.
4. Connect battery; verify F1 holds.
5. Measure +3V3 at U3 output: 3.30 V ±0.07 V; status LED should begin its idle **slow flash within ~10 s** of power-up (§6.7).
6. **Antenna placement (item J):** attach the XIAO's included U.FL flex antenna to the enclosure wall or clear lid — ABS is RF-transparent; maximize distance from the internal 12 V wiring and the external 200 A battery cables, and do not lay the antenna flat against the PCB ground-plane side. Dress the U.FL pigtail with a gentle strain-relief loop (U.FL is rated ~30 mating cycles — connect once, leave it).
6. Confirm I²C discovery: INA228 at 0x40, OLED at 0x3C.
7. **Read INA228 bus voltage: must match battery voltage within ±0.5 %. If it reads ~0 V or ~3.3 V, the VBUS terminal lead is missing/open or the breakout jumper is closed (§3.3) — fix before proceeding.**
8. Read INA228 current: ~0, only the monitor self-draw (small discharge) through the shunt.

### 8.3 Functional Verification
1. Reconnect inverter; apply a known load (e.g. 1500 W heater ≈ ~117 A discharge).
2. **Confirm sign:** discharge should read **negative**. If positive, swap VIN+/VIN− (§4.2) and re-verify.
3. Run 1 h; verify Ah accumulation matches ~117 Ah within ±2–3 Ah.
4. Charger check: connect LiTime; current should read **positive** up to ~80 A (LED goes **solid**); ride to absorption and confirm the `absorption_reached` flag and **CV Absorption Elapsed** counting, then charger-stop anchor (verify **CV Absorption Time** publishes the session total).
5. ALERT (armed in V1.16+): with the bank at rest, verify no alert; then force a benign trip (e.g. momentarily lower BUVL in a bench build, or observe a real >14.8 V/OV event) and confirm GPIO5 fires and `alert_reason` decodes correctly. The latch clears when DIAG_ALRT is read by the handler.

### 8.4 Ground / Sign Sanity (one-time)
- [ ] DMM across the shunt heavy bolts under known load: ~37 mV @ 100 A, ~75 mV @ 200 A; polarity confirms direction.
- [ ] Confirm only **one** DC earth reference exists (inverter chassis bond at negative busbar); no separate battery-negative-to-earth bond (§9, §13 item E).

### 8.5 Rev 1.1 PCB Verification Record (independent file-level review, 2026-06-10)

Method: custom s-expression parse of the KiCad 10 board; rotation convention **empirically calibrated** against trace-endpoint/pad-center coincidence (25/25 on rotated footprints) rather than assumed; connectivity by union-find including T-junction (endpoint-into-segment-body) and pad-body-crossing joins; zone membership by point-in-polygon ring sampling. Complements — does not replace — native KiCad DRC.

| Check | Result |
|---|---|
| Net connectivity (11 nets) | All single-island, incl. V_FUSED rename and 6 test points |
| GND return | 14/14 pads zone-spoked (B.Cu plane monolithic); 94/94 stitching vias bridge both fills; nearest via to any GND pad 1.78–2.24 mm |
| Signal layer discipline | All signals on F.Cu over unbroken B.Cu return plane; **zero signal vias** (no return-path plane crossings) |
| Clearance / edge | 0 violations at 0.15 mm copper floor / 0.25 mm edge (board rule is 0.20 mm); annular rings ≥0.30 mm pads, 0.15 mm vias |
| LED polarity (item K) | Verified: GPIO20 → R4 → anode (pad 2) → cathode (pad 1) → GND; silk flat + fab cathode bar + explicit +/− marks all at the GND pad. Fix implemented by footprint rotation/pad renumbering onto the **same two drilled holes** — no copper changes |
| Decoupling proximity | C2→INA228 4.0 mm; C3→XIAO 4.1 mm; C1→buck out 4.0/7.0 mm; C5→buck in 4.0 mm; C4 bulk 5.6/9.9 mm — at THT package limits |
| I²C | SDA 49.1 mm / SCL 39.5 mm, F.Cu only; ≥14.9 mm from V_FUSED; τ ≈ 250 ns vs 1000 ns limit at 100 kHz with 5 kΩ effective pull-ups (§6.6) |
| 1-Wire | 37.5 mm on-board, 38.8 mm from V_FUSED; off-board cable guidance §4.5 |
| EMI/RF | Buck switching loop confined to the Pololu module (board sees DC both sides); antenna off-board via U.FL — no PCB keep-out required; solid plane under U1 is the correct reference |
| Ground loops | None by topology: single system ground tie at TB1; display/probe/button all board-powered; each harness carries its own return |
| Hand-solder access | Tightest inter-component pad gap 1.85 mm (U1.D3↔R2.1), all else ≥2.19 mm; both zones use thermal-relief pad connects (0.5 mm clearance) — no solid-welded GND pads |
| Silkscreen | Pin labels at every connector; +/− polarity marks at C4, TB1, TB2, LED verified consistent with nets; back-silk carries full BOM legend, board name, dimensions, author |

Caveats of this review: pads modeled as bounding circles for clearance (KiCad DRC is authoritative there); zone shapes taken from the stored fill (refill + native DRC required after any further edit); TB1 wire-entry direction not provable from pad data (item L visual check).


---

## 9. Safety Considerations

**Battery short circuit:** a 500 Ah bank delivers thousands of amps. Insulated tools, no jewelry, cover busbars when not working, never bridge + and −.

**Inverter shock hazard (Giandel 1500 W, floating neutral):** the inverter floats its AC output; the neutral is referenced via the main panel's neutral-ground bond. **This requires the manual transfer switch to be solid-neutral** (it must *not* switch the neutral) so the panel bond stays in the inverter's neutral path on backup — otherwise the output floats with no bond and GFCI protection is defeated. Verify on backup power with a 3-light outlet tester (correct reading = bond path intact). Treat the AC output as live 120 V; verify the inverter is off before working on adjacent DC wiring. *(AC-side N-G/transfer-switch detail added in Rev 1.7; it is the real safety exposure of the backup use case and was previously undocumented.)*

**Heat from heavy cables:** torque all 2/0 lugs and re-torque after first full-load test.

**VBUS lead at battery+ potential (Rev 1.7):** in low-side the VBUS terminal lead is the one wire carrying ~13 V relative to chassis. A pinched/abraded lead shorting to chassis would fault battery+ to ground. **Mitigation:** the mandatory 100–250 mA inline fuse at the busbar end (§3.3). *(The Kelvin sense leads, which carried this hazard in the high-side era, now sit near ground and need no fuse.)*

**Single DC earth reference:** the inverter chassis bond earths the DC-negative bus at the negative busbar. Adding a second DC-negative-to-earth bond (e.g. a separate battery-negative ground rod) creates a parallel path around the low-side shunt and corrupts the measurement. Keep one reference.

### 9.1 Built-In Protection
- **F1 (1 A SB)** protects the board power feed only — not the sense or VBUS leads.
- **Reverse-polarity protection: none (accepted)** — no on-board or external device; confirm TB1 polarity before energizing (§4.4, §13 item C).
- **INA228** rated 85 V common-mode; **Pololu D24V7F3** input to 36 V; **DROK shunt** 200 A continuous.
- **Firmware:** stale-bus watchdog, 8–16 V / ≥350 A plausibility guards (Current Channel Fault), `safe_mode`.

---

## 10. Maintenance and Calibration

- **Monthly:** visual check of shunt/busbar terminals for discoloration (heating).
- **Quarterly:** re-torque heavy lugs; verify monitor voltage vs. external meter; **electrically** verify the VBUS lead fuse (<1 Ω closed) and the Kelvin taps (<1 mΩ to their bolts). *A blown VBUS-lead fuse is a silent failure mode: the current channel still reads, but bus voltage goes invalid — caught here and by the firmware's 8–16 V guard.*
- **Annually:** re-run §7.1 to detect shunt drift.

### 10.1 SOC Recalibration (unchanged)
Coulomb counting anchors at each confirmed full charge: `absorption_reached` sets when bus ≥14.20 V with charging current sustained 60 s; the full-charge anchor (SOC = 100 %, counter reset, cycle logged) fires on the charger-stop edge provided `absorption_reached` is set, with a guard rejecting it if net current < −1.0 A at charger-stop. Manual "Mark as Fully Charged" button for the rare missed anchor. V1.10 self-discharge reconciliation runs at each clean full→full anchor.

---

## 11. Future Enhancements

### 11.1 V2-next Board Improvements
- **On-board reverse-polarity protection** (LM74700-Q1 + N-MOSFET) — optional; the current build accepts no protection (§13 item C).
- **TVS (P6KE18CA) across the battery rail** for inverter-bus transients (§13 item G).
- ~~Rename the 13 V rail~~ — done Rev 1.1 (**V_FUSED**, item I closed).
- ~~Test points~~ — done Rev 1.1 (V_FUSED/+3V3/GND/SDA/SCL/ALERT on-carrier). Remaining candidates: VIN+/VIN−/VBUS live on the breakout's terminal block, accessible there.

### 11.2 Firmware Roadmap
- **ALERT armed (done — V1.16–V1.18):** BUVL/BOVL/SOVL/SUVL/POL hardware limits with latched interrupt and decoded `alert_reason` on GPIO5. Polled 2 s remains the primary acquisition path; the ALERT pin serves as an independent hardware alarm, not a sampling trigger. Known limit: while a latched condition persists, a second different alert in that window is not re-decoded.
- Apparent-Ri trending (awaits field validation); opportunistic capacity-fade recalibration from deep-discharge outages.

---

## 12. References

| Document | Source |
|---|---|
| Battery-bank firmware V1.19 | `battery-bank-monitor.yaml` |
| V2 PCB | `Battery_Bank-Monitor-THT-V2_-_Rev_1.kicad_pcb` (KiCad 10) — **Rev 1.1 contents verified fab-ready (§8.5); rename file + silk to Rev 1.1 per item L** |
| INA228 datasheet | TI **SLYS021** (Rev 1.8 cited SBOS951 — corrected per TI EVM guide SBOU241 lit table; note SBOSA20 = INA237, a common mix-up) |
| Adafruit INA228 breakout pinout | learn.adafruit.com/adafruit-ina228-i2c-power-monitor/pinouts |
| LiFePO4 study / Technical Report | github.com/wkcollis1-eng/Lifepo4-Battery-Banks |

---

## 13. Open Risks / Pre-Fab To-Do (updated Rev 1.9)

*Items D/F closed Rev 1.8; items **I, J, K closed Rev 1.10** (PCB Rev 1.1 verified — §8.5). Item L added Rev 1.10 (cosmetic pre-Gerber hygiene). Remaining open: C (accepted), E (discipline), G (deferred — last call before fab), H (verify at build), **L (pre-Gerber)**.*

| # | Item | Severity | Resolution |
|---|---|---|---|
| **A** | ~~VBUS unrouted for low-side~~ — **resolved, not a defect.** U2 pin 5 (VBUS) is a carrier NC *by design*; bus voltage is sourced at the breakout's VIN+/VBUS/VIN− terminal block (jumper open), so no carrier trace is needed. *(Original Rev 1.7 draft wrongly flagged this as a missing path.)* | — | Wire VBUS at the terminal block, inline-fused (§3.3, §4.3). No board change. |
| **B** | ~~Board is placement-only / no GND pour~~ — **withdrawn, parsing error.** The board is fully routed: 82 track segments, 100 vias, 2 GND zones present in the file. | — | None. |
| **C** | **No reverse-polarity protection (on-board or external) — ACCEPTED.** Bare TB1→F1→buck; a reversed feed puts reverse voltage on C4 (electrolytic) and the buck input. | Accepted | Single self-wired build; builder verifies TB1 polarity before energizing (§4.4). No device added. V2-next optional: on-board LM74700. |
| **D** | ~~Firmware pin-map mismatch. Button on GPIO4 (board) vs GPIO21 (firmware); ALERT now on GPIO5; GPIO20 clamp vestigial.~~ — **CLOSED in V1.15.** Button changed to GPIO4; GPIO20 clamp removed. *(Rev 1.9 annotation: the closure note "GPIO20 is true NC on V2" was true of Rev 1 as reviewed; GPIO20 is now REUSED as the status-LED output — V1.18+ firmware, Rev 1.1 PCB. Closure stands; superseded, not reopened.)* | ~~High~~ **Closed** | Done. Flash V1.19. |
| **E** | **Second DC earth reference** would bypass the low-side shunt. (User-acknowledged; restated for completeness.) | Medium | Maintain a single DC earth reference (inverter chassis bond at neg busbar); isolate the DS18B20 mount; no battery-negative ground rod. |
| **F** | ~~Placeholder BOM values — R2, C1, C4.~~ — **CLOSED.** KiCad PCB Description fields confirmed: R2 = 10 kΩ ¼W 5%; C4 = 47 µF 50 V radial (≥25 V satisfied); C1 = 10 µF 25 V X7R. Verify C4 silk polarity mark (pad 1 = VIN = positive rail) before populating. J1 and TB1 footprints are correct in PCB; no further action needed. | ~~Medium~~ **Closed** | Done — values reflected in §4.6. |
| **G** | **No transient suppression on the battery rail** (§11.1 TVS absent) while I²C runs beside 200 A cabling. **Last call — the Rev 1.1 order closes the respin window.** | Low–Medium | Decide before Gerber export: P6KE18CA across V_FUSED after F1 (or P6KE20CA for more standoff margin above the 14.6 V absorption setpoint). Declining = accepted risk, like item C. |
| **H** | **Pololu D24V7F3 pin order** (socket VOUT/GND/VIN) — a VIN/VOUT swap is fatal. | Verify | Confirm against the module silk before fab. |
| **I** | ~~"VIN" net-name collision (13 V rail vs breakout VIN pin).~~ — **CLOSED in PCB Rev 1.1:** rail renamed **V_FUSED** and verified in the net list (§8.5). Residual silk label on the test point → item L. | ~~Low~~ **Closed** | Done. |
| **J** | ~~XIAO antenna choice (onboard vs U.FL).~~ — **CLOSED:** the XIAO's included **U.FL external flex antenna** will be used. No PCB keep-out required (radiator is off-board; the module's RF section is self-contained chip→U.FL, and the solid B.Cu plane under U1 is the correct reference). Placement: §8.2 step 6 (ABS wall/lid, away from DC wiring and 200 A cables, not flat against the ground plane; strain-relieve the pigtail — ~30 mating cycles). | ~~Low~~ **Closed** | Done. |
| **K** | ~~Rev 1 LED circuit defective (reverse-biased; R4 fed from +3V3; no series R in a flipped-part scenario).~~ — **CLOSED in PCB Rev 1.1, independently verified (§8.5).** Fixed in two stages: (1) R4 moved in series GPIO20 → R4 → LED, +3V3 tie removed; (2) LED footprint rotated/pads renumbered onto the **same two drilled holes** so the cathode (pad 1, with silk flat + fab bar + "−" mark) lands on GND and the anode (pad 2, "+") on the drive net — zero copper changes. *Convention note: the pad-shape swap leaves the **square pad on the ANODE**, counter to the square-pad-equals-cathode habit; the silk marks are authoritative — populate by silk (§4.6 LED1 row).* | ~~High~~ **Closed** | Done. Verified §8.5. |
| **L** | **Cosmetic pre-Gerber hygiene (added Rev 1.10).** (1) Back-silk text still reads "Rev 1" — bump to "Rev 1.1" (and rename the file) so the physical board self-identifies. (2) Value fields on R2/R4/C1/C4 hold footprint names — set to component values for BOM-export hygiene (back-silk legend is already correct). (3) V_FUSED test-point silk reads "VIN" — rename for consistency (optional). (4) Visually confirm TB1 wire openings face the board edge (3D viewer — not provable from pad data). | Low | 10 minutes in KiCad, then refill zones → native DRC → Gerbers. |

---

*End of document.*
