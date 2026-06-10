# 12V 500Ah LiFePO4 Battery Bank Monitoring — Wiring Summary

**System:** 12 V / 500 Ah LiFePO4 battery bank with Giandel 1500 W inverter (manual transfer switch, floating neutral bonded at the main panel)
**Monitor board:** Battery_Bank-Monitor-THT **V2** (native Adafruit INA228 footprint) + Adafruit INA228 breakout
**Current shunt:** Repurposed DROK 200 A / 75 mV manganin shunt, **in the negative cable (low-side)**
**Document revision:** 1.9 (tracks firmware **V1.19**; status LED added on GPIO20 — PCB Rev 1.1 LED-circuit fix required before fab (§13 item K); INA228 ALERT now **armed** (no longer "provisioned, not wired"); CV/absorption-time telemetry added; R4 = 1 kΩ)
**Author:** William Collis
**Status:** Pre-build reference — **V2 Rev 1 routed and connectivity-verified, but NOT fab-ready: the Rev 1 LED circuit is defective (§13 item K). Fab from Rev 1.1 (LED re-route + R4 = 1 kΩ) after zone refill + KiCad DRC.**

---

## Revision History

| Rev | Notes |
|---|---|
| 1.0–1.2 | Initial pre-build drafts; Pololu ideal-diode reverse protection; LiTime 80 A charger integration. Low-side topology (inherited default). |
| 1.3–1.6 | **High-side era.** Shunt moved to the positive cable to resolve the V1-carrier VBUS-on-pin-5 problem and to make the measurement immune to negative-side grounding. Required on the V1 carrier: U2 pin-5 lift, R2 DNP, breakout VBUS jumper closed, and inline fuses on both Kelvin sense leads (sense leads sat at battery+ potential). 1.4 tracked firmware V1.12 (cadence/anchor corrections); 1.5 tracked V1.13 (manual-model robustness); 1.6 tracked V1.14 (local OLED panel + wake button). |
| 1.7 | **Two coupled changes.** (1) **Topology reverted to low-side** — the shunt stays in the negative cable where it is physically installed today, eliminating all 2/0 high-current rework. The decision rests on two facts established in review: with USB used only for the *first* flash (bench, 12 V disconnected) and OTA thereafter, the USB ground-loop path never coexists with a live bus; and with a single DC earth reference (the inverter chassis bond at the negative busbar) maintained, a negative-leg shunt has no parallel path to bypass. The earlier high-side move solved a measurement-integrity problem that, for this specific install, is solved instead by *grounding discipline* — at the cost of one fused VBUS lead instead of two Kelvin-lead fuses and a 200 A cable relocation. (2) **Board changed to Battery_Bank-Monitor-THT V2**, a clean carrier with a native INA228 8-pin socket: the V1 adaptation hacks (pin-5 lift, R2 DNP, jumper-closed workaround) are gone, ALERT now lands on a real GPIO, and the button moved off the UART pin. **All shunt-sense and bus-voltage connections are made at the INA228 breakout's own VIN+/VBUS/VIN− terminal block — no carrier trace required.** Adds §13 *Open Risks / Pre-Fab To-Do*. Inverter corrected from the doc's stale "2000 W" to the actual Giandel 1500 W. |
| **1.8** | **PCB cross-reference alignment pass.** Firmware reference updated V1.14 → V1.15. §6.1 pin-map defect (§13D) **closed**: firmware button pin changed GPIO21 → GPIO4 (D2); GPIO20 pullup clamp removed (dead code on V2 — U1 GPIO20 pad carries no net). §13F BOM placeholders **closed**: KiCad PCB Description fields confirm R2 = 10K ¼W (ALERT pull-up ✓), C4 = 47 µF 50 V radial (≥25 V requirement satisfied ✓), C1 = 10 µF 25 V X7R. C4 polarity note added: pad 1 → VIN (positive rail). §4.6 connector map updated to reflect V1.15 pin assignments. No wiring or topology changes. |
| **1.9** | **Firmware V1.19 + LED alignment pass.** Tracks firmware V1.19 (production review fixes V1.18 + features V1.19). (1) **Status LED added** — 3 mm green on U1 GPIO20 via R4: slow flash = idle (proof-of-life), solid = charging/discharging, fast flash = FAULT. **Rev 1 PCB LED circuit is defective as drawn** (cathode on the drive node, R4 fed from +3V3 — LED reverse-biased in every GPIO state); §13 item K records the Rev 1.1 fix (GPIO20 → R4 → anode, cathode → GND, active-high) and **R4 changed 220 Ω → 1 kΩ** (~1.2 mA). (2) **INA228 ALERT armed** (V1.16–V1.18): BUVL 12.20 V / BOVL 14.80 V / SOVL +250 A / SUVL −250 A / POL 1500 W, decoded `alert_reason` on GPIO5 — supersedes "provisioned, not wired". (3) **CV/absorption-time telemetry** (V1.19): per-session absorption duration as a charger-health trend metric. (4) §12 INA228 datasheet lit number corrected SBOS951 → **SLYS021** (per TI EVM guide SBOU241 literature table; SBOSA20 is the INA237). No wiring or topology changes. |

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
| Monitor PCB | **Battery_Bank-Monitor-THT V2** | OSH Park (target) | Native INA228 8-pin socket. **Rev 1 routed; fab from Rev 1.1 (LED-circuit fix, §13 item K).** |
| INA228 breakout | Adafruit 5832 (or 6349 INA228 variant) | Adafruit / DigiKey | **Onboard 15 mΩ shunt must be removed; VBUS jumper LEFT OPEN (low-side default); see §3.3** |
| Microcontroller | Seeed XIAO ESP32-C3 | Seeed Studio | OTA-flashable. Confirm antenna choice (onboard vs. U.FL) at build. |
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

The VIN+/VIN− assignment above is the starting point; **confirm the sign at commissioning** (§8.5) and swap the pair if current reads inverted. In low-side the polarity relationship is the reverse of high-side, so the assignment is verified empirically, not assumed.

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

### 4.6 V2 Board Connector / Socket Map (as drawn)

| Ref | Type | Pinout (pad → net) |
|---|---|---|
| TB1 | 2-pos Phoenix MKDS-1.5-3.81 | 1 = GND, 2 = BATT_RAW |
| F1 | 5×20 fuse | BATT_RAW ↔ VIN |
| U3 | Pololu D24V7F3 (1×03 socket) | 1 = +3V3 (VOUT), 2 = GND, 3 = VIN — **verify against module silk** |
| U2 | INA228 (1×08 socket) | 1 = +3V3, 2 = GND, 3 = SCL, 4 = SDA, **5 = VBUS (NC)**, **6 = VIN+ (NC)**, **7 = VIN− (NC)**, 8 = ALERT |
| U1 | XIAO ESP32-C3 | 3V3 = +3V3, GND = GND, SDA = GPIO6, SCL = GPIO7, GPIO10 = DQ, **D2/GPIO4 = button**, **D3/GPIO5 = ALERT**, **D7/GPIO20 = status LED (Rev 1.9)** |
| J1 | 4-pin JST-XH (OLED I²C) | 1 = SDA, 2 = SCL, 3 = GND, 4 = +3V3 |
| J2 | 2-pin JST-XH (button) | 1 = GPIO4_BTN, 2 = GND |
| TB2 | 3-pin JST-XH (DS18B20) | 1 = GND, 2 = GPIO10_DQ, 3 = +3V3 |
| R2 | ALERT pull-up | ALERT ↔ +3V3 — **10 kΩ ¼W 5% axial (confirmed in PCB)** |
| R3 | 10 k | GPIO4_BTN ↔ +3V3 (button pull-up) |
| **R4** | LED series resistor | **GPIO20 ↔ LED anode — 1 kΩ ¼W 5% axial (Rev 1.1 topology; Rev 1 value field says 220 Ω — use 1 kΩ)** |
| **LED1** | 3 mm green THT | **anode ← R4, cathode → GND (Rev 1.1 fix — as drawn in Rev 1 the LED is reverse-biased; see §13 item K)** |
| C1 | output cap | +3V3 ↔ GND — **10 µF 25 V X7R radial (confirmed in PCB)** |
| C2, C3 | 0.1 µF | +3V3 decoupling |
| C4 | radial electrolytic | VIN ↔ GND — **47 µF 50 V radial (confirmed in PCB; pad 1 = VIN = positive rail — verify silk polarity mark)** |
| C5 | 0.1 µF | VIN bypass |

> **Net-name caution.** The carrier net **"VIN"** is the post-fuse ~13 V board rail. The INA228 breakout's pin 1 is *also* labeled "VIN" but is its 3.3 V logic supply and is correctly tied to **+3V3** on the carrier — not to the 13 V "VIN" net. Consider renaming the rail (e.g. `V_FUSED`) in a future board rev to prevent a mis-wire that would put 13 V into the INA228's 5.5 V-max supply.

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

**POSITIVE = CHARGING, NEGATIVE = DISCHARGING** (firmware Option B). In low-side the physical relationship between flow direction and VIN+/VIN− polarity is the reverse of high-side, so the §4.2 lead assignment is the starting point and the sign is **confirmed empirically at commissioning** (§8.5); swap VIN+/VIN− if inverted. No firmware sign-flip — the convention is produced by the wiring.

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

> **Bus pull-up caution.** Both the 938 and the INA228 breakout carry onboard I²C pull-ups; two in parallel lower effective resistance. Normally fine at 400 kHz on short runs. If the bus misbehaves with both connected, remove the 938's onboard pull-ups. Verify the bus with **both** devices present at commissioning.

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
- [ ] Battery_Bank-Monitor-THT **V2 Rev 1.1** — **LED circuit re-routed (GPIO20 → R4 → anode, cathode → GND), R4 value 1 kΩ, zones refilled, KiCad DRC clean, Gerbers regenerated** (§13 item K)
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
- Rename the 13 V rail off "VIN" to avoid the breakout-VIN naming collision (§4.6).
- Test points at BATT_RAW / VIN+ / VIN− / VBUS for field debug.

### 11.2 Firmware Roadmap
- **ALERT armed (done — V1.16–V1.18):** BUVL/BOVL/SOVL/SUVL/POL hardware limits with latched interrupt and decoded `alert_reason` on GPIO5. Polled 2 s remains the primary acquisition path; the ALERT pin serves as an independent hardware alarm, not a sampling trigger. Known limit: while a latched condition persists, a second different alert in that window is not re-decoded.
- Apparent-Ri trending (awaits field validation); opportunistic capacity-fade recalibration from deep-discharge outages.

---

## 12. References

| Document | Source |
|---|---|
| Battery-bank firmware V1.19 | `battery-bank-monitor.yaml` |
| V2 PCB | `Battery_Bank-Monitor-THT-V2_-_Rev_1.kicad_pcb` (KiCad 10) — **fab from Rev 1.1 after §13K fix** |
| INA228 datasheet | TI **SLYS021** (Rev 1.8 cited SBOS951 — corrected per TI EVM guide SBOU241 lit table; note SBOSA20 = INA237, a common mix-up) |
| Adafruit INA228 breakout pinout | learn.adafruit.com/adafruit-ina228-i2c-power-monitor/pinouts |
| LiFePO4 study / Technical Report | github.com/wkcollis1-eng/Lifepo4-Battery-Banks |

---

## 13. Open Risks / Pre-Fab To-Do (updated Rev 1.9)

*Items D and F closed in Rev 1.8 / firmware V1.15. Item K added in Rev 1.9 — **OPEN, fab-blocking** until PCB Rev 1.1. Remaining open items: C (accepted), E (discipline), G (deferred), H (verify at build), I (cosmetic), J (confirm at build), **K (fab-blocking)**.*

| # | Item | Severity | Resolution |
|---|---|---|---|
| **A** | ~~VBUS unrouted for low-side~~ — **resolved, not a defect.** U2 pin 5 (VBUS) is a carrier NC *by design*; bus voltage is sourced at the breakout's VIN+/VBUS/VIN− terminal block (jumper open), so no carrier trace is needed. *(Original Rev 1.7 draft wrongly flagged this as a missing path.)* | — | Wire VBUS at the terminal block, inline-fused (§3.3, §4.3). No board change. |
| **B** | ~~Board is placement-only / no GND pour~~ — **withdrawn, parsing error.** The board is fully routed: 82 track segments, 100 vias, 2 GND zones present in the file. | — | None. |
| **C** | **No reverse-polarity protection (on-board or external) — ACCEPTED.** Bare TB1→F1→buck; a reversed feed puts reverse voltage on C4 (electrolytic) and the buck input. | Accepted | Single self-wired build; builder verifies TB1 polarity before energizing (§4.4). No device added. V2-next optional: on-board LM74700. |
| **D** | ~~Firmware pin-map mismatch. Button on GPIO4 (board) vs GPIO21 (firmware); ALERT now on GPIO5; GPIO20 clamp vestigial.~~ — **CLOSED in V1.15.** Button changed to GPIO4; GPIO20 clamp removed. *(Rev 1.9 annotation: the closure note "GPIO20 is true NC on V2" was true of Rev 1 as reviewed; GPIO20 is now REUSED as the status-LED output — V1.18+ firmware, Rev 1.1 PCB. Closure stands; superseded, not reopened.)* | ~~High~~ **Closed** | Done. Flash V1.19. |
| **E** | **Second DC earth reference** would bypass the low-side shunt. (User-acknowledged; restated for completeness.) | Medium | Maintain a single DC earth reference (inverter chassis bond at neg busbar); isolate the DS18B20 mount; no battery-negative ground rod. |
| **F** | ~~Placeholder BOM values — R2, C1, C4.~~ — **CLOSED.** KiCad PCB Description fields confirmed: R2 = 10 kΩ ¼W 5%; C4 = 47 µF 50 V radial (≥25 V satisfied); C1 = 10 µF 25 V X7R. Verify C4 silk polarity mark (pad 1 = VIN = positive rail) before populating. J1 and TB1 footprints are correct in PCB; no further action needed. | ~~Medium~~ **Closed** | Done — values reflected in §4.6. |
| **G** | **No transient suppression on the battery rail** (§11.1 TVS absent) while I²C runs beside 200 A cabling. | Low–Medium | Consider P6KE18CA across the rail in V2-next. |
| **H** | **Pololu D24V7F3 pin order** (socket VOUT/GND/VIN) — a VIN/VOUT swap is fatal. | Verify | Confirm against the module silk before fab. |
| **I** | **"VIN" net-name collision** (13 V rail vs breakout VIN pin). | Low | Rename rail in a future rev (§4.6). |
| **J** | **XIAO antenna choice** (onboard vs U.FL) not determinable from the carrier. | Low | Confirm at build given enclosure/siting. |
| **K** | **Rev 1 LED circuit defective — FAB-BLOCKING.** As drawn: R4 pad 1 → +3V3; net "LED" ties R4 pad 2 + GPIO20 + LED **cathode** (pad 1); LED pad 2 → GND. The LED is reverse-biased in every GPIO state and can never light; the topology is wrong even with the part physically flipped (GPIO must continuously sink to light it; a dead/hi-Z MCU shows solid-on — masquerades as healthy; push-pull HIGH would source unlimited current through the un-resistored flipped LED). | **High (open)** | **Rev 1.1:** swap LED pad nets (pad 1 → GND so the silk cathode mark stays truthful; pad 2 → drive net, re-land the trace stub on pad 2), break the +3V3 tie at R4 and place R4 in series GPIO20 → R4 → anode; **R4 = 1 kΩ**. Refill zones, run KiCad native DRC, regenerate Gerbers before OSH Park upload. |

---

*End of document.*
