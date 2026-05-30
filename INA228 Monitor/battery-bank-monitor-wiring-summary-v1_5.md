# 12V 500Ah LiFePO4 Battery Bank Monitoring — Wiring Summary

**System:** 12 V / 500 Ah LiFePO4 battery bank with 2000 W inverter
**Monitor board:** UPS-Monitor-THT V1 (repurposed) + Adafruit INA228 breakout
**Current shunt:** Repurposed DROK 200 A / 75 mV manganin shunt
**Document revision:** 1.5 (high-side topology; INA228-in-INA260-footprint adaptation; Kelvin-sense fusing; tracks firmware V1.13)
**Author:** William Collis
**Status:** Pre-build reference

---

## Revision History

| Rev | Notes |
|---|---|
| 1.0 | Initial pre-build draft |
| 1.1 | Pololu Ideal Diode integration for reverse-polarity protection |
| 1.2 | LiTime 80A charger integration |
| 1.3 | **Topology: low-side → high-side**, prompted by the V1.11 firmware source-level review. **U2 header pin 5 lifted before solder** (INA228 puts VBUS where INA260 had ALERT; would drive ~13 V into GPIO20 trace). **R2 not populated.** **VBUS jumper now CLOSED** (was OPEN in V1.2). **Kelvin sense leads require inline fusing** (100–250 mA fast-blow) — high-side mitigation. Sign convention §6.2 rewritten as a single committed convention with explicit wiring (Option B from V1.2: positive=charging). INA228 LSB figures corrected from V1.2's 3.13 µV / 8.3 mA to actual datasheet values 312.5 nV / 0.83 mA at the shunt. §6 firmware section rewritten to reference V1.11 production firmware rather than the original UPS-baseline migration plan. Ground-loop verification reduced from mandatory to optional (high-side topology eliminates the parallel-path bypass risk that drove V1.2's mandatory tests). |
| 1.4 | **Tracks firmware V1.12** (cadence-correction + alignment pass). No hardware or topology change. §10.2 full-charge mechanism corrected to match firmware: the anchor fires on the **charger-stop edge** (gated by a sustained-absorption flag), **not** on a taper-current threshold (taper detection was removed in firmware). §5.2 / §6.3 annotate that `float_voltage` and `absorption_voltage` are **reference-only** values not consumed by any firmware lambda. Firmware references updated V1.11 → V1.12. INA228 telemetry cadence note added (firmware now polls at 2 s to match the ~1.58 s averaged-conversion cycle at 128× averaging — see §5.2). |
| 1.5 | **Tracks firmware V1.13** (robustness pass for the MANUAL / data-driven operating model). No hardware or topology change. Operating model clarified throughout: **no HA control of the bank** — manual transfer switch and panel breakers; the operator reads SOC and manually shuts the bank at ~20% SOC; charger is on/off only (no float); the bank powers the UPS during outages (the UPS runs a further ~220 min beyond bank exhaustion). New **§6.5 Robustness and fault handling** documents the V1.13 firmware guards: current-channel plausibility (≥350 A → freeze SOC + FAULT, catches a saturated/open-Kelvin-lead channel), bus-voltage plausibility (8–16 V drop-filter → watchdog FAULT on sustained garbage), the new **Current Channel Fault** diagnostic sensor, the disabled `reboot_timeout`s (continuous local SOC publishing), and `safe_mode`. §9.2 updated with the firmware-level protections; §10.1 quarterly Kelvin/sense-fuse check upgraded from **visual to electrical**. Firmware references updated V1.12 → V1.13. Adds the **signed-OTA** adoption item and **local SOC-readout** recommendation as commissioning to-dos. |

---

## 1. Purpose

Replace the standalone DROK display unit with a Wi-Fi-connected monitoring solution that reports current, voltage, temperature, accumulated Ah/Wh, and runtime estimates to Home Assistant in real time. Provides the same data quality as the UPS monitor but at battery-bank scale (200 A peak vs. 250 mA peak), enabling unified Home Assistant dashboard coverage of both 12 V systems.

**Engineering rationale:** The UPS-Monitor-THT board was designed with dual-use in mind. The INA260 (UPS application) and INA228 (battery-bank application) Adafruit breakouts share **the same 8-pin header footprint and identical pins 1–4 (VIN, GND, SCL, SDA)**, allowing the same PCB to host either chip for the power and I²C interface. **However pins 5–8 differ between the two chips** (V1.3 finding): INA260 routes ALERT/VBUS/Vin+/Vin− while INA228 routes VBUS/Vin+/Vin−/ALRT — pin 5 is the conflict. The PCB's pin 5 trace was designed for INA260 ALERT (routed through R2 to ESP32-C3 GPIO20). For INA228 use, the board requires the adaptation in §3.3: pin 5 lifted, R2 not populated, VBUS jumper closed so VBUS is sourced from VIN+ at the terminal block (high-side topology) rather than from the now-isolated header pin.

This document covers the INA228 + external shunt configuration for battery-bank deployment as adapted to the UPS-Monitor-THT board.

---

## 2. System Topology Overview

```
                    ┌─────────────────────────────────────────────────┐
                    │      BUSBAR (+) — 12 V positive                 │
                    │      (LOAD side of shunt)                       │
                    └──┬───────┬─────────────┬─────────────┬──────────┘
                       │       │             │             │
                  [Inverter+] [Charger+]  [Other loads+]   │
                                                           │
                                                  ┌────────┴────────┐
                                                  │      SHUNT      │  200 A / 75 mV
                                                  │     (DROK)      │  HIGH-SIDE
                                                  └────────┬────────┘
                                                           │
                                                       [Battery+]
                                                           │
                                                  ┌─────────────────┐
                                                  │ BATTERY BANK    │
                                                  │ 500 Ah LiFePO4  │
                                                  └─────────────────┘
                                                           │
                                                       [Battery−]
                                                           │
                    ┌──────────────────────────────────────┴────────┐
                    │     BUSBAR (−) — 12 V return (unbroken)       │
                    └──┬───────────────┬─────────────┬──────────────┘
                       │               │             │
                   [Inverter−]    [Charger−]    [Other loads−]
```

**Measurement configuration:** **High-side current sensing** (shunt in positive cable). *Topology change from V1.2, which placed the shunt in the negative cable.*

**Sign convention:** Positive current = battery charging, negative = battery discharging. *Same convention as UPS monitor and as V1.2 Option B. V1.3 commits to this as the single convention rather than V1.2's two-option choice — see §6.2.*

**Ground reference:** Single-point ground at the negative busbar. *Changed from V1.2's "battery-negative side of the shunt" since high-side topology makes the negative busbar the natural ground node.*

### 2.1 Why High-Side (V1.3 topology change)

V1.2 selected low-side as the inherited default. The V1.11 firmware source-level review surfaced a forcing function for re-examination: with U2 header pin 5 lifted (mandatory to prevent the INA228's VBUS pin from driving the GPIO20 trace on the PCB), the breakout's VBUS net is no longer accessible via the PCB header. Low-side measurement requires VBUS to be driven externally, which would require a discrete flying wire from battery+ to the breakout's VBUS test pad. High-side measurement (VBUS jumper closed, VBUS internally tied to VIN+) eliminates that wire and is mechanically simpler.

Beyond resolving the VBUS-drive question, high-side has independent merits for this install:

1. **Ground integrity.** With low-side shunt, every load's "ground" sits at +75 mV above true battery negative at 200 A peak. Any future ground-referenced instrumentation (second monitor, BMS link, isolated DC-DC) would see that shifting offset. High-side keeps all returns at true battery negative.
2. **Physical separation of heavy bus from instrumentation.** High-side puts the 200 A path through the shunt at the battery, with only thin Kelvin sense wires routed to the monitor board. Low-side routes the negative-return cable through the monitor area.
3. **Eliminates the V1.2 isolation constraint.** V1.2 §4.4 required the inverter's chassis NOT be bonded to DC negative internally, because such a bond would create a parallel path bypassing the low-side shunt. In high-side topology that bond is harmless — chassis ground equals battery negative equals the negative busbar at the same potential, and no current bypasses the shunt regardless.
4. **Detects ground faults.** A high-side shunt sees current leaving battery+ regardless of return path. A fault that returns through chassis instead of the negative cable is invisible to low-side but visible to high-side.

**One real cost (mitigated in §3.3 step 6):** the Kelvin sense leads now sit at ~13 V relative to chassis. A shorted sense lead would fault battery+ to ground through the shunt's Kelvin tap. Mitigation: inline 100–250 mA fast-blow fuse on each sense lead, close to the shunt end.

---

## 3. Hardware Bill of Materials

### 3.1 Main Components

| Item | Part | Source | Notes |
|---|---|---|---|
| Monitor PCB | UPS-Monitor-THT V1 | OSH Park | One of 3 boards from initial fab run |
| INA228 breakout | Adafruit 5832 (or 6349 INA228 variant) | Adafruit / DigiKey | **Onboard 15 mΩ shunt must be removed; VBUS jumper must be CLOSED; see §3.3** *(jumper-closed is changed from V1.2)* |
| Microcontroller | Seeed XIAO ESP32-C3 | Seeed Studio | Same as UPS board, OTA-flashable |
| Regulator | Pololu D24V7F3 | Pololu #2842 | 4–36 V → 3.3 V at 600 mA |
| Reverse-voltage protector | Pololu Ideal Diode 4-60V, 10A | Pololu #5382 | LM74700-Q1 + N-MOSFET ideal diode; installed inline with monitor power feed. Spare from UPS build. |
| Temperature sensor | DS18B20 module (with integral 4.7 kΩ pull-up) | Generic | Mount to battery case |
| Fuse | 1 A slow-blow 5×20 mm | Würth 696108003002 | Protects monitor board input (onboard PCB fuse F1) |
| **Kelvin sense fuses (V1.3)** | **2× 100–250 mA fast-blow, axial leaded or inline holder** | **Generic** | **One per Kelvin sense lead, close to shunt end. High-side mitigation against shorted sense wire faulting battery+ to chassis through the shunt's Kelvin tap.** |
| Current shunt | 200 A / 75 mV manganin | Repurposed from DROK display kit | Verify Kelvin sense terminals present |
| Bank charger | LiTime 12V (14.6V) 80A LiFePO4 | LiTime | Existing — AC-input wall charger, 120 V → 14.6 V DC. Permanently wired to busbars. |

### 3.2 Wiring Materials

| Item | Spec | Purpose |
|---|---|---|
| Battery main cables | 2/0 AWG | Battery ↔ shunt ↔ busbar high-current. **Topology change in V1.3:** the shunt now sits in the positive cable, not the negative. |
| Sense pair | 22 AWG twisted pair (unshielded) | DROK shunt Kelvin → INA228 VIN+/VIN−, **with inline fuses (V1.3)** |
| Monitor power feed | 18 AWG | Positive busbar → Pololu Ideal Diode VIN → TB1.2 (BATT_RAW) |
| Monitor ground | 18 AWG | Negative busbar → TB1.1 (GND) |
| DS18B20 cable | 3-conductor, ≥22 AWG | TB2 → battery case sensor |

*Note: V1.2's separate "bus voltage tap" (22 AWG from INA228 VBUS to positive busbar) is no longer required in V1.3. With the VBUS jumper closed on the breakout, VBUS is internally tied to VIN+; no external VBUS wire is installed.*

### 3.3 Critical Hardware Modifications Required

**Before installing the INA228 breakout in U2 socket, the following modifications are mandatory.** Items marked **(V1.3)** are new or changed from V1.2.

1. **Remove the onboard 15 mΩ shunt resistor** from the INA228 breakout PCB. The component is a small SMD resistor between the VIN+ and VIN− terminal block pads. Either cut it off with flush cutters or desolder with hot air. **This is mandatory** — without removal, the onboard shunt sits in parallel with the external DROK shunt. At 200 A measured, ~5 A would flow through the onboard SMD resistor, destroying it immediately.

2. **(V1.3 change — was OPEN in V1.2.)** **Solder the VBUS jumper CLOSED** on the back of the breakout (above the VIN+ and VBUS pins). Closing this jumper internally ties VBUS to VIN+, configuring the breakout for **high-side** measurement. *Rationale: with U2 pin 5 lifted (step 3), the breakout's VBUS net has no external drive path via the PCB header. Jumper-closed routes VBUS through the terminal block via VIN+. Open jumper + lifted pin 5 = no VBUS drive at all (the firmware would read garbage bus voltage).*

3. **(V1.3 addition.)** **Lift U2 header pin 5 before solder.** Position 5 on the UPS-Monitor-THT PCB is silkscreened "ALT" — designed for INA260's ALERT output, routed through R2 (pullup) to ESP32-C3 GPIO20. **INA228 puts VBUS on pin 5 instead**, which on this board's terminal block carries ~13 V (battery+ via VIN+ with the jumper closed). Driving 13 V into the 3.3 V GPIO trace would destroy the XIAO at first power-on through the ESD clamp path. **Mitigation: physically lift the pin from the header strip before solder** — clip it, bend it outward, or use a header with that position omitted. With pin 5 lifted, the breakout's VBUS net is electrically isolated from the PCB regardless of jumper state.

4. **(V1.3 addition.)** **Do not populate R2.** With U2 pin 5 lifted, R2 has no functional role — its pullup target (the lifted pin) is no longer connected to anything. Leave the pad empty. The V1.11 firmware enables the ESP32-C3 internal pullup on GPIO20 to clamp the now-floating trace to a defined level.

5. **Verify the DROK shunt has dedicated Kelvin sense terminals** — small screws in the middle of the manganin strip, separate from the heavy bolts at either end. If the shunt only has the two large terminals, accuracy degrades from ±1% to roughly ±5% due to bolt-junction resistance entering the measurement loop.

6. **(V1.3 addition.)** **Inline-fuse each Kelvin sense lead.** Add a 100–250 mA fast-blow fuse on each of the two Kelvin sense wires, **close to the shunt end** (so the fuse protects as much of the wire as possible). Use small inline glass-fuse holders or axial-leaded fuses with heat-shrink. *Rationale: in high-side topology the Kelvin sense leads sit at battery+ potential (~13 V relative to chassis). A shorted sense wire — pinch through insulation against a chassis edge, for example — would otherwise fault battery+ to ground through the shunt's Kelvin tap leads. Sense current is microamps in normal operation, so a 100 mA fuse has ~1000× headroom and opens in milliseconds on a short.*

---

## 4. Detailed Wiring Summary

### 4.1 High-Current Path

**Topology change in V1.3:** the shunt has moved from the negative cable to the positive cable. The positive cable is no longer continuous (battery+ → busbar); it is now battery+ → shunt → positive busbar. The negative cable is now continuous (battery− → negative busbar) with no shunt.

**Positive cable run** (2/0 AWG):

| From | To | Notes |
|---|---|---|
| Battery (+) terminal | Shunt battery-side terminal (large bolt) | Use crimped/torqued ring lug. Torque to shunt manufacturer's spec (typically 12–15 N·m for 2/0 AWG hardware). |
| Shunt load-side terminal (large bolt) | Positive busbar | Use crimped/torqued ring lug. Same torque spec. |

**Negative cable run** (2/0 AWG):

| From | To | Notes |
|---|---|---|
| Battery (−) terminal | Negative busbar | Direct, no shunt in this path. *(V1.3: this cable is now continuous; V1.2 placed the shunt here.)* |
| Negative busbar | Inverter (−), Charger (−), Loads (−) | Heavy distribution as before. |

**Note:** With the shunt in the positive leg, the **negative cables remain unbroken**. All loads return directly to battery negative via the negative busbar.

### 4.2 Sense Wiring — INA228 Inputs

**22 AWG twisted pair from DROK shunt to INA228 breakout** (~18" run, unshielded, **with inline fuses per §3.3 step 6**):

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| Sense A | Shunt's **battery-side** Kelvin terminal (small screw) → 100–250 mA inline fuse | INA228 breakout **VIN+** terminal block | VIN+ | Battery-side voltage (≈ battery+). With VBUS jumper closed, this also drives VBUS internally. *(V1.3: VIN+ is at battery-side — this is the Option B wiring from V1.2 §6.2 made into the committed convention. V1.2's §4.2 table had VIN+ on load-side and VIN− on battery-side, but V1.2 §6.2 then noted the sign would be inverted from the UPS convention and recommended Option B as the fix.)* |
| Sense B | Shunt's **load-side** Kelvin terminal (small screw) → 100–250 mA inline fuse | INA228 breakout **VIN−** terminal block | VIN− | Load-side voltage (≈ battery+ minus shunt drop). During discharge, VIN− is *lower* than VIN+ (current flows out of battery → shunt drops voltage in flow direction). |

*V1.2 had a separate "Bus voltage tap" entry here for a 22 AWG wire from positive busbar to INA228 VBUS terminal block. **Removed in V1.3** — VBUS is sourced internally via the closed jumper, no external VBUS wire needed.*

**Why no shielding:** at this distance with twisted pair and differential measurement, capacitively-coupled noise pickup is well below the INA228's measurement noise floor. Shielding adds termination complexity without measurable benefit. The differential ADC rejects common-mode noise (the dominant interference mode) automatically.

**Why the fuses (V1.3):** see §3.3 step 6 rationale. High-side topology puts the sense leads at battery+ potential, so a shorted sense wire is a hazard rather than a nuisance. *V1.2's "Why no fuses on sense lines" reasoning is superseded: that reasoning was correct for low-side (sense leads at ~ground potential) but doesn't apply to high-side.*

### 4.3 Monitor Board Power Feed

The monitor board power feed passes through the **Pololu Ideal Diode reverse-voltage protector** before reaching TB1.2. This provides protection against accidental polarity reversal at install time and during any future maintenance.

**Pololu module specifications:**
- Operating voltage: 4–60 V (well above 14.6 V LiFePO4 absorption)
- Max continuous current: 10 A (vs. ~100 mA monitor draw — 100× margin)
- Path resistance: ~10 mΩ when ON
- Voltage drop at monitor's typical 100 mA draw: ~1 mV (undetectable)
- Reverse protection rating: −60 V (vs. −14.6 V worst case — 4× margin)
- Controller: TI LM74700-Q1 ideal diode controller + N-channel MOSFET

**Pin assignments on Pololu module** (verify against silkscreen on the actual board):
- **VIN:** Input from positive busbar (load-side of shunt)
- **VOUT:** Output to monitor TB1.2 (BATT_RAW)
- **GND:** Common reference (connects to negative busbar — *V1.3 change from V1.2's "shunt battery-side terminal," consistent with the high-side topology and single-point ground at negative busbar*)

**Wiring:**

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| Monitor +12V (input) | Positive busbar (load-side of shunt) | Pololu module **VIN** | BATT_RAW (pre-protection) | 18 AWG |
| Monitor +12V (protected) | Pololu module **VOUT** | UPS-Monitor-THT TB1.2 | BATT_RAW (post-protection) | 18 AWG, short run (~5 cm to module) |
| Pololu GND | Negative busbar | Pololu module **GND** | GND | 18 AWG; *V1.3: terminates at negative busbar, not shunt battery-side as in V1.2* |
| Monitor GND | Pololu module **GND** node | UPS-Monitor-THT TB1.1 (GND) | GND | 18 AWG; single-point ground at negative busbar — see §4.4 |

**Important — monitor power path through the shunt:** the monitor board's positive feed taps from the **load-side** (positive busbar) of the shunt. This means the monitor's own supply current (~100 mA) **flows through the shunt** in the direction battery+ → shunt → busbar → Pololu → monitor → return → battery−. The Coulomb counter captures this draw as normal load. *Same outcome as V1.2, different physics: V1.2's low-side shunt captured the monitor's return current; V1.3's high-side shunt captures the monitor's supply current. Either way, no SOC blind spot.*

**Protection behavior:**

- **Correct polarity:** MOSFET turns on, ~10 mΩ in series with positive feed, ~1 mV drop at typical load. Monitor receives normal +12 V.
- **Reversed polarity at TB1:** MOSFET stays OFF. No current flows to monitor board. C4 electrolytic, Pololu D24V7F3 input, and INA228 power are all protected. LED on the monitor board will not illuminate, providing immediate visual indication of the wiring fault.

**Why include this protection on the battery-bank deployment:**

A 500 Ah LiFePO4 bank can deliver thousands of amps into a fault. Reverse-polarity at the monitor TB1 connector — possible during install or future maintenance — would destroy C4 instantly and likely damage the Pololu D24V7F3 input. With the LM74700-based protector inline, the worst case becomes "monitor doesn't power up; LED stays dark; check polarity and reconnect." Recoverable, no damage.

**Mechanical mounting:**

The Pololu module is small (~18 × 13 mm) with 4 M2-compatible mounting holes. Options:
1. Bracket-mount near the monitor board with short wires to TB1
2. Inline mount in the heat-shrunk cable run between busbar and TB1
3. Adhesive-mount to the inside of the monitor enclosure if one exists

Option 1 is cleanest mechanically. Use M2 or M2.5 standoffs to space the module off any conductive surface.

**Note:** The Pololu module does not replace the onboard 1 A SB fuse (F1). F1 still protects against downstream shorts and overcurrent. The Pololu module only protects against polarity reversal.

### 4.4 Ground Reference Strategy

**Single-point ground at the negative busbar.** *Changed from V1.2's "battery-negative side of the shunt" — high-side topology makes the negative busbar the natural single-point ground node, since negative busbar = battery negative at the same potential (no shunt in between).*

All ground references converge at this one physical node:
- INA228 GND pin (via socket → PCB GND pour → TB1.1 → 18 AWG to negative busbar)
- Monitor board GND (TB1.1)
- DS18B20 GND (via TB2.3)
- Pololu Ideal Diode GND
- Inverter chassis GND (typically tied to its DC negative input)

**Why this matters:** in high-side topology, the negative busbar is at true battery negative regardless of bank current. INA228's chip ground and all instrumentation references stay clean. The shunt drop (up to ±75 mV at 200 A) appears only on the small sense pair, where the differential ADC measures it correctly; it never appears between system grounds.

**V1.2's chassis-bonding constraint is removed in V1.3.** V1.2 §4.4 required the 2000 W inverter NOT to bond chassis ground to DC negative internally, because such a bond would create a parallel path bypassing the low-side shunt. In V1.3 high-side topology, **that constraint no longer applies**: chassis-to-DC-negative bonding is harmless because chassis ground equals battery negative equals the negative busbar at the same potential, and no current bypasses the high-side shunt regardless of where the inverter chassis is bonded.

**Optional verification** (one-time at commissioning):
1. Install all wiring per this document
2. Connect a known DC load (e.g., 100 W incandescent bulb on inverter output)
3. Measure voltage across the shunt at its heavy-bolt terminals with a DMM
4. Expected reading: shunt drop proportional to load — at 100 A discharge, expect ~37 mV across the shunt (load-side lower than battery-side); at 200 A, ~75 mV.
5. Sign check: shunt drop polarity confirms current direction. Battery-side higher than load-side ⇒ current flowing OUT of battery ⇒ discharging.

### 4.5 DS18B20 Temperature Sensor

| Wire | From | To | Notes |
|---|---|---|---|
| Red (3.3V) | TB2 pin 1 | DS18B20 module Vdd | |
| Yellow (DQ) | TB2 pin 2 | DS18B20 module DQ | Built-in 4.7 kΩ pull-up on module |
| Black (GND) | TB2 pin 3 | DS18B20 module GND | |

**Physical placement:** Mount sensor body against the battery case (or between two cells in the pack), not on the monitor board. The temperature being measured is the *battery temperature*, used for SOC compensation. Adhesive thermal pad or kapton tape works.

### 4.6 Wiring Diagram Summary

```
                                    ┌───────────────────────────┐
                                    │      Positive busbar      │
                                    │      (LOAD side of shunt) │
                                    └─────┬──────────┬──────────┘
                                          │          │
              ┌───────────────────────────┘          │ 2/0 AWG (load side)
              │ 18 AWG                               │
              │                                      │
       ┌──────┴──────┐                               │
       │ Pololu VIN  │                               │
       │ Ideal Diode │                               │
       │ LM74700-Q1  │                               │
       │ + N-MOSFET  │                               │
       │ Pololu VOUT │                               │
       └──────┬──────┘                               │
              │ 18 AWG                               │
              │ (protected)                          │
              │                                      │
        ┌─────┴─────┐                          ┌─────┴─────┐
        │ TB1.2     │                          │  SHUNT    │ 200 A / 75 mV
        │ BATT_RAW  │                          │  (DROK)   │ HIGH-SIDE
        └───────────┘                          │           │
                                               │ Kelvin    │←── 22 AWG ─┬── fuse ──┐
        ┌───────────┐                          │ sense     │ twisted    │ 100-250  │
        │ TB1.1 GND │ ←──── 18 AWG ───┐        │ (small    │ pair, ~18" │ mA F.B.  │
        └───────────┘                 │        │  screws)  │ unshielded │          │
                                      │        │           │            │          │
                            ┌─────────┴──┐     │           │←── 22 AWG ─┴── fuse ──┼─┐
                            │ Pololu GND │     │           │                       │ │
                            └─────────┬──┘     └─────┬─────┘                       │ │
                                      │              │ 2/0 AWG (battery side)      │ │
                                      │ 18 AWG       │                             │ │
        ┌─────────────┐               │       ┌─────┴─────┐                        │ │
        │ Neg busbar  │←──────────────┘       │ Battery + │                        │ │
        │ (unbroken)  │                       └─────┬─────┘                        │ │
        └─┬───────┬───┘                             │                              │ │
          │       │                                 │                              │ │
          │       │                          ┌─────┴─────┐                         │ │
        [Inv−] [Loads−]                      │  BATTERY  │                         │ │
          │                                  │  500 Ah   │                         │ │
          │                                  │  LiFePO4  │                         │ │
          │                                  └─────┬─────┘                         │ │
          │                                        │ 2/0 AWG (unbroken)            │ │
          │                                  ┌─────┴─────┐                         │ │
          └────────────── 2/0 AWG ───────────┤ Battery − │                         │ │
                                             └───────────┘                         │ │
                                                                                   │ │
                                                                  ┌────────────────┘ │
                                                                  │  ┌───────────────┘
                                                                  ▼  ▼
                                                          ┌─────────────────┐
                                                          │   INA228        │
                                                          │   VIN+    VIN−  │
                                                          │  (batt-   (load-│
                                                          │   side)    side)│
                                                          │                 │
                                                          │ VBUS internally │
                                                          │ tied to VIN+ via│
                                                          │ closed jumper — │
                                                          │ no external     │
                                                          │ VBUS wire       │
                                                          │                 │
                                                          │ GND ── PCB GND  │
                                                          │       pour ──   │
                                                          │       TB1.1     │
                                                          │ SDA SCL         │
                                                          │ (ALRT on pin 8, │
                                                          │  floating —     │
                                                          │  not used)      │
                                                          │ (pin 5 LIFTED;  │
                                                          │  R2 DNP)        │
                                                          └─────────────────┘

         Notes:
         • SHUNT is HIGH-SIDE: in positive cable between battery+ and busbar.
         • Negative cable is unbroken: battery− → negative busbar.
         • U2 header pin 5 LIFTED before solder. R2 not populated. INA228 VBUS
           jumper SOLDERED CLOSED on back of breakout.
         • Each Kelvin sense lead has 100–250 mA fast-blow fuse close to shunt.
         • Single-point ground at negative busbar (V1.3 change from V1.2's
           "shunt battery-side").
         • Monitor power tapped from positive busbar (load side of shunt) so the
           monitor's own ~100 mA draw flows through the shunt and is captured by
           the Coulomb counter (no SOC blind spot).
         • Monitor return goes to negative busbar.
```

### 4.7 LiTime 80A Charger Integration

The bank is charged by a **LiTime 12V (14.6V) 80A LiFePO4 charger** — an AC-input wall charger (120 V AC → 14.6 V DC, 80 A max). The charger is permanently wired to the busbars and operates whenever AC power is applied.

**Specifications:**
- Output: 14.6 V DC, 80 A max (3-stage CC/CV charging profile)
- Input: 100–240 V AC, 50/60 Hz, ~10 A max
- DC isolation: standard isolated SMPS topology (DC output floats relative to AC ground — see verification step below; *now optional in V1.3 — see below*)
- Connector: 120 A Anderson plug or M8 ring terminals (installation-dependent)

**Wiring:**

| Wire | From | To | Notes |
|---|---|---|---|
| Charger DC+ | Positive busbar (load-side of shunt) | Charger output positive | |
| Charger DC− | Negative busbar | Charger output negative | |
| Charger AC | 120 V wall outlet | Charger AC input | Standard 3-prong cord with safety ground |

**Why charger connection topology works in high-side:**

The charger's DC+ terminal lands on the positive busbar (load side of the shunt). Charging current flows:

```
Charger DC+ → Positive busbar → through SHUNT (measured as POSITIVE current = charging) →
Battery+ → through battery → Battery− → Negative busbar → Charger DC−
```

The INA228 sees full charging current with proper sign (positive = charging). This matches the UPS monitor convention.

**Critical: shunt sees all charging current**

For the INA228 to correctly measure charge/discharge balance, the charger's DC+ cable must terminate at the **positive busbar (load-side of shunt)**, never directly at the battery positive terminal. Direct termination at the battery positive post would bypass the shunt entirely and the INA228 would report 0 A during 80 A charging sessions.

✓ **Correct topology (high-side):** charger DC+ on positive busbar → charging current passes through shunt → INA228 reads correctly as positive (charging).

✗ **Wrong topology:** charger DC+ on battery positive terminal → charging current bypasses shunt → no charge measurement.

*(V1.2's analogous requirement was for charger DC− on the negative busbar. V1.3 flips this to the positive side, consistent with the shunt's new location.)*

**AC-DC isolation verification — REDUCED PRIORITY in V1.3:**

In V1.2's low-side topology, AC-DC isolation in the charger was critical: a non-isolated charger would create a parallel ground path (battery negative → charger DC− → AC ground → building ground) that bypassed the low-side shunt. In V1.3 high-side topology, **this concern is largely eliminated** — the shunt is on the positive side, and a chassis-to-DC-negative bond does not bypass the high-side shunt. AC-DC isolation in the charger is still good practice for noise reasons, but is no longer a measurement-integrity concern.

The original isolation check procedure remains as a one-time good-practice check, but is no longer a stop-the-build item if it fails:

1. Unplug charger from AC wall outlet
2. Disconnect charger DC leads from busbar (no battery connection)
3. Multimeter on continuity/resistance mode
4. Probe between **AC plug ground pin** (3rd pin) and **DC output negative terminal**
5. Expected reading: **open circuit** (> ~10 MΩ) — confirms isolation
6. If reading shows low resistance (< few kΩ): charger is non-isolated. **In V1.3 high-side topology, this is no longer a stopper** — the shunt still sees all charging current. Document the finding and proceed.

**Charging measurement impact:**

At 80 A continuous charging through the 200 A / 75 mV shunt:
- Shunt voltage drop: 80 × 0.000375 = 30 mV (well within INA228 ±163.84 mV range)
- Shunt power dissipation: 80² × 0.000375 = 2.4 W (manageable, ~15% of full-scale)
- INA228 shunt LSB at this current: ~0.83 mA at the shunt (312.5 nV LSB ÷ 375 µΩ — *see §5.2 correction from V1.2*)
- Practical resolution after averaging: ~5–10 mA — excellent for Coulomb integration

**Telemetry benefits of charger-through-shunt measurement:**

With the charger current flowing through the shunt, the firmware automatically captures:

1. **Charge events** in `ah_charged_cycle` and `wh_charged_lifetime` accumulators (positive sign)
2. **Coulombic efficiency** — comparing Ah-in vs. Ah-out across charge/discharge cycles (V1.7+ firmware feature)
3. **Self-discharge reconciliation** — V1.10 firmware computes unseen drain U at each clean full→full anchor
4. **Charger profile validation** — verify 3-stage CC/CV curve (constant ~80 A during bulk, tapering during absorption, stop at full)
5. **Charger session duration** for energy-cost accounting
6. **Battery acceptance** monitoring as the bank ages — capacity-to-full at fixed charge current trends downward over cycle count

These metrics enable battery-aging analysis comparable to commercial BMS systems.

**Operational notes:**

- The charger has its own safety protections (overvoltage, overcurrent, overtemperature, reverse polarity). The Pololu reverse-polarity protector on the monitor board does not protect against charger fault conditions — those are handled internally by the LiTime charger.
- During charging sessions, the inverter may simultaneously be drawing load. The INA228 reports the *net* current — `(charge rate) − (load draw)`. Positive net = net charge, negative net = net discharge. Firmware displays this clearly so the user doesn't confuse net measurements with individual component currents. *(V1.2's formulation had the signs reversed in this paragraph; V1.3 corrects this to match the committed sign convention §6.2.)*
- The charger's 14.6 V CV stage is well below the INA228's 85 V common-mode limit and well below the Pololu D24V7F3's 36 V input maximum. No protection-circuit margin concerns.

---

## 5. INA228 Configuration

### 5.1 I²C Address

- **Default:** 0x40 (A0 and A1 jumpers OPEN — factory state)
- **If A0 bridged:** 0x41
- **If A1 bridged:** 0x44
- **If both bridged:** 0x45

For this build, leave jumpers in factory state and use 0x40. The UPS-deployed board has A0 bridged to 0x41 (legacy from breadboard build); the battery-bank board can remain at 0x40 to avoid confusion.

### 5.2 Shunt Calibration

In ESPHome firmware (V1.13 uses the `ina2xx_i2c` platform):

```yaml
sensor:
  - platform: ina2xx_i2c
    model: INA228
    address: 0x40
    shunt_resistance: 0.000375 ohm
    max_current: 200.0 A
    adc_range: 0          # ±163.84 mV (mandatory for 75 mV at 200 A shunt)
    reset_on_boot: false  # preserve internal counters across ESPHome restarts
    adc_time: 4120us      # explicit (V1.12); per-channel ADC conversion time
    adc_averaging: 128    # explicit (V1.12); samples averaged per reported value
    update_interval: 2s   # ≥ the ~1.58 s averaged-conversion cycle (V1.12; was 1 s)
```

**Math check:** 75 mV / 200 A = 0.000375 Ω = 375 µΩ.

**Telemetry cadence (V1.12):** at 128× averaging across the three enabled channels
(shunt, bus, temperature), the INA228's full averaged-conversion cycle is
128 × (4120 + 4120 + 4120) µs ≈ **1.58 s** per fresh sample. The firmware therefore
polls at **2 s** (was 1 s in ≤V1.11, which polled mid-conversion ~40% of the time —
harmless to the dt-based Ah/Wh integrals, but the "1 s" telemetry claim was inaccurate).
128× averaging is retained deliberately: it holds the noise floor far below the 0.05 A
detection threshold, which is what makes the ~100 mA self-draw capture and the sub-mAh
self-discharge reconciliation clean. The bank's dynamics are slow (voltage slope sampled
at 60 s, SOC at 30 s, alarms debounce 10–60 s), so 2 s sampling is more than adequate.

At ±163.84 mV ADC range:
- Maximum measurable current: 163.84 mV / 0.375 mΩ = 437 A (some headroom above the 200 A shunt rating)
- INA228 shunt LSB: **312.5 nV** at the chip (per TI datasheet Table 8-1, ADCRANGE=0) → **~0.83 mA at the shunt** (312.5 nV ÷ 375 µΩ)
- 50 mA firmware threshold: ~60× the quantization step (ample margin against spurious-sign noise)
- Practical noise floor after averaging: ~5–10 mA

**Correction from V1.2:** V1.2 §5.2 listed "LSB resolution: ~10 µA equivalent at the chip → ~0.83 mA at the shunt (3.13 µV / 0.375 mΩ)". The 3.13 µV figure is 10× the actual datasheet LSB; the correct value is 312.5 nV at the chip, and a recomputation of "~10 µA at the chip" gives a different number too. Corrected here.

### 5.3 Hardware Modifications Recap

| Modification | Required | Location | Status vs V1.2 |
|---|---|---|---|
| Remove onboard 15 mΩ shunt | **Yes** | Adafruit breakout PCB, between VIN+ and VIN− terminal block pads | Unchanged |
| **Solder VBUS jumper CLOSED** | **Yes** | Back of breakout, above VIN+ and VBUS pins | **V1.3 change: was OPEN in V1.2** |
| **Lift U2 header pin 5 before solder** | **Yes** | Header strip between INA228 breakout and PCB | **V1.3 addition** |
| **R2 not populated** | **Yes** | UPS-Monitor-THT PCB | **V1.3 addition** |
| Verify Kelvin sense terminals on DROK shunt | **Yes** | Physical shunt — small screws on the manganin strip | Unchanged |
| **Inline-fuse each Kelvin sense lead** | **Yes** | Between shunt Kelvin tap and INA228 terminal block, close to shunt end | **V1.3 addition** |
| I²C address jumpers | No (leave at 0x40) | Back of breakout, A0 and A1 | Unchanged |

---

## 6. Firmware

The existing battery-bank monitor firmware (`battery-bank-monitor.yaml`, **V1.13**) is configured for the high-side topology. *This section is substantially rewritten from V1.2 §6 — V1.2 was forward-looking from the UPS-baseline migration perspective; V1.3 references the production firmware that resulted from that work.*

### 6.1 Pin Assignments (XIAO ESP32-C3, esp-idf framework)

| Pin | Function | Notes |
|---|---|---|
| GPIO6 | I²C SDA | To INA228 SDA (pin 4 of breakout header) |
| GPIO7 | I²C SCL | To INA228 SCL (pin 3 of breakout header) |
| GPIO10 | DS18B20 1-Wire | To TB2.2 |
| GPIO20 | Unused (was INA260 ALERT in original board design) | **(V1.3) U2 pin 5 lifted, R2 DNP, trace floating. V1.11 firmware enables ESP32-C3 internal pullup to clamp the pin via `binary_sensor: gpio` with `internal: true`.** |

### 6.2 Sign Convention (committed)

**POSITIVE current = CHARGING**, **NEGATIVE current = DISCHARGING**. Same as the UPS monitor.

Wiring detail that produces this convention:
- VIN+ → shunt **battery-side** Kelvin tap (closer to battery+ in cable order)
- VIN− → shunt **load-side** Kelvin tap (closer to positive busbar in cable order)
- When current flows from battery to load (**discharge**), conventional current direction is battery → shunt → busbar → load. Voltage drops in the flow direction across the shunt, so battery-side (VIN+) is *higher* than load-side (VIN−). The INA228's measured shunt voltage = V(VIN+) − V(VIN−) is positive. **However**, the firmware reports this as negative current via Option B sign convention (the INA228 chip's polarity is matched in firmware to the UPS monitor's "positive=charging" convention — see V1.2 §6.2 Option B background, which V1.3 commits to as a single convention.)
- When the charger drives current into the battery (**charge**), conventional current direction reverses: charger → busbar → shunt → battery+. VIN− is now higher than VIN+. The chip reports positive (matching Option B).

*V1.2 had this section as a two-option choice between firmware fix (Option A: multiply by -1) and wiring fix (Option B: swap VIN+/VIN− leads). V1.3 commits to Option B — the wiring choice that the V1.11 firmware was built against. No firmware sign-flip needed; the wiring choice in §4.2 produces the convention directly.*

### 6.3 System Parameters (V1.13 firmware values)

The V1.13 firmware substitutions are tuned to the actual measured bank (V1.2 had these as forward-looking placeholders):

```yaml
validated_capacity_ah:        "397"    # from Oct 2025 discharge test (99.3% of nominal 400Ah actual)
validated_capacity_wh:        "5082"   # 397 Ah × 12.80 V mean discharge — INFORMATIONAL (not referenced in any lambda)
float_voltage:                "13.262" # 130+ day stasis OCV (LiFePO4_Report_2026-03-06.md) — REFERENCE ONLY (not referenced in any lambda)
warning_voltage:              "12.40"
critical_voltage:             "12.20"
emergency_voltage:            "11.80"
overvoltage_threshold:        "14.80"  # above LiTime CV setpoint, catches runaway charger
full_charge_v_min:            "14.20"  # absorption detection floor
self_discharge_pct_per_month: "0.0"    # measured ~0% intrinsic at ~12°C basement storage
```

**Reference-only substitutions (V1.4 note):** `float_voltage`, `absorption_voltage` (14.60 V, the LiTime CV setpoint, not shown above), and `validated_capacity_wh` document measured/spec context but are **not consumed by any firmware lambda** — editing them has no runtime effect. The values that actually drive behavior are `warning_voltage` / `critical_voltage` / `emergency_voltage` / `overvoltage_threshold` / `full_charge_v_min` and `validated_capacity_ah`. The ±0.05 A standby band is enforced by fall-through past `discharge_threshold_a` / `charge_threshold_a` (the `standby_threshold_a` symbol is likewise reference-only).

See the firmware file's substitutions section for the complete authoritative list including all alarm thresholds, slope thresholds, and reconciliation parameters. Voltage thresholds and slope thresholds were validated against the 500 Ah bank's discharge curve before tuning alarms (V1.2 §6.3 noted this would be required).

### 6.4 Separate-YAML Decision

*V1.2 §6.4 recommended creating a separate ESPHome YAML for the battery-bank deployment rather than editing `ups-monitor.yaml`. **V1.3 confirms this decision was followed**: the battery-bank firmware is at `battery-bank-monitor.yaml` (V1.13) in the home-assistant-config repo; the UPS firmware remains at `ups-monitor.yaml` (independent, different I²C address 0x41 vs 0x40, different chip, different capacity, different alarm thresholds). The two configs evolve independently. Per V1.2's reasoning, this prevents accidental cross-contamination of settings.*

### 6.5 Robustness and Fault Handling (V1.13)

*This system is operated **manually**: no Home Assistant control of the bank. Transfer is by manual switch and panel breakers; the operator reads State of Charge and manually shuts the bank at **~20% SOC**. The charger is **on/off only — no float charging**. The bank powers the UPS during outages; if an outage exceeds bank capacity, the UPS runs a further ~220 minutes on its own reserve. In this model the **data is the safety system**, so the V1.13 firmware pass hardens SOC integrity, SOC visibility, and recovery — not automated actuation (the firmware alarms drive no automated action here; they are corroborating cues for the operator).*

**Sensor-fault handling — what the firmware catches, and what it does not.** The stale-bus watchdog (§ INA228 Watchdog sensor) catches a *hung* I²C bus: no new reads for >10 s → `bank_state` = FAULT and all Ah/Wh integration freezes. V1.13 adds two guards for the failure mode the watchdog cannot see — a bus returning *consistent garbage* that is non-NaN and non-stale (a real risk here: the I²C lines run beside 2/0 AWG cables carrying 200 A transients, and the INA228 has no PEC on its data registers):

- **Bus-voltage plausibility (8–16 V):** a reading outside this band is dropped at the sensor. A single glitch is silently rejected (the last good value holds for that cycle); *sustained* out-of-range voltage produces no watchdog refresh, so the existing watchdog trips FAULT at 10 s. A healthy 12 V LiFePO4 bus lives ~10.0–14.8 V, so 8/16 V flags only genuine garbage. This prevents a stuck-low reading from showing a false EMERGENCY or a misleading voltage on the dashboard.
- **Current-channel plausibility / health (≥350 A → fault):** a current magnitude above 350 A is non-physical — above the 200 A shunt rating and above any real *averaged* reading (sub-second inverter surges are averaged down by the 128× / ~1.58 s conversion), yet below the ~437 A ADC ceiling — so it indicates a saturated or garbage current channel. In particular it catches the **high-side open-Kelvin-lead failure**, whose floating differential input rails the reading high. When detected: the four SOC integration sources **freeze** (no phantom Ah accumulates against the bad value), `bank_state` shows **FAULT**, and a dedicated **Current Channel Fault** diagnostic binary sensor is set for the dashboard. This matters more in the manual model than alarm actuation would: SOC is the shutdown trigger, so a silently-corrupted current reading is the quiet way to act on a wrong number.

> **Documented limit (not papered over).** These bounds catch a *saturated/garbage* channel, not one reading *plausibly-but-wrong* — e.g. a partial or high-resistance Kelvin connection giving a believable-but-incorrect current, or a voltage corruption that lands *within* 8–16 V. A believable-but-wrong value is not bounds-detectable. Its mitigations are (a) the **quarterly electrical Kelvin/sense-fuse check** in §10.1, and (b) the **§7.1 clamp-meter calibration cross-check**. In the manual model a plausibly-wrong voltage only misleads the dashboard — it cannot auto-trip anything.

**Continuous local operation (`reboot_timeout` disabled).** Because the operator's shutdown decision depends on a live SOC readout, both the Wi-Fi and API `reboot_timeout` are set to **0 s (disabled)** in V1.13. A Wi-Fi blip, or a long outage during which Home Assistant is briefly unreachable (longer than the old 30-minute API timeout), must **not** reboot the device and blank the readout. The device keeps running its local logic and reconnects when the network returns. Recovery from a genuinely wedged stack relies on `safe_mode` (below) plus a manual feed power-cycle — always available on a manual system. *(If a wedge-recovery net is preferred over pure continuity, set a long finite timeout, e.g. 4 h, instead of 0 s — see the `api:` / `wifi:` blocks in the firmware.)*

**Crash-loop recovery (`safe_mode`).** An explicit `safe_mode:` block is configured (OTA enables safe mode implicitly; configuring it explicitly makes the behavior intentional and tunable). After `num_attempts` (10) boots that each fail before becoming "good," the device enters safe mode — logging + Wi-Fi + OTA only — so a bad config can be re-flashed **over the air** rather than requiring physical USB access to a port entangled with the bank feed. This is independent of the disabled `reboot_timeout`s: safe mode triggers on genuine crash-boot-loops, not on network loss.

**Firmware-update integrity (commissioning to-do — not yet enabled).** OTA is the only practical update path, and physical reflash is awkward (USB requires disconnecting the bank feed), so `signed_ota_verification` (ESPHome 2026.4.0+) is recommended as defense against accepting a corrupted or wrong binary. It is **not enabled in V1.13** pending verification: confirm the exact YAML schema against the signed-OTA documentation, confirm the XIAO ESP32-C3 chip revision supports the chosen Secure-Boot-V2 signing scheme, and **bench-test a full OTA round-trip** before relying on it (a verification-key build error was reported early in the 2026.4.x line). Treat as a sequenced step, not a flip-the-switch change.

**NVS persistence / flash wear (resolved).** The firmware's restore values (seven integration counters plus several globals) persist across reboots — including power loss — via ESP32 NVS, which is wear-leveled. ESPHome batches all restore/preference writes and flushes them as a single NVS transaction on `preferences: flash_write_interval` (default 60 s), so the cost is ~1 batched write per minute, not per update. Multi-year wear is not a concern at the default interval; the interval can be lengthened if ever desired.

---

## 7. Shunt Accuracy Notes

The repurposed DROK shunt is a standard 200 A / 75 mV manganin-strip type. Realistic specifications:

| Parameter | Expected value | Impact on system |
|---|---|---|
| Initial resistance tolerance | ±1% to ±2% | ±2–4 A at full-scale 200 A |
| Temperature coefficient | 50–100 ppm/°C | Up to 0.3% drift at full-load heating |
| Self-heating at 200 A | ~15 W dissipated | Locate in still air, not against heat source |
| Long-term drift | ~0.1–0.3% per year | Negligible for battery monitoring |

These tolerances are adequate for SOC tracking on a 500 Ah bank. ±2 A absolute uncertainty equates to ±0.4% of full scale — well below the resolution needed for capacity accounting.

### 7.1 Optional Calibration Procedure

If higher accuracy is desired:

1. Set up a known DC load (e.g., 1500 W resistive heater drawing ~115 A from battery)
2. Measure actual current with a calibrated reference (Fluke 87 + AC/DC clamp, or known-good DC ammeter)
3. Note INA228 reading at the same instant
4. Compute correction: `shunt_corrected = shunt_nominal × (INA228_reading / reference_reading)`
5. **(V1.3 update.)** Update the ESPHome firmware substitution `shunt_resistance` in the `ina2xx_i2c` block, recompile, and OTA-flash. *(V1.2 referenced an Arduino-style `setShunt(corrected_value, 200.0)` API call; V1.11 firmware uses the ESPHome `shunt_resistance:` configuration parameter instead.)*

This brings the system to within 0.1% of the reference, eliminating shunt tolerance as an error source.

---

## 8. Installation Checklist

### 8.1 Pre-Installation

- [ ] UPS-Monitor-THT V1 PCB received from OSH Park
- [ ] INA228 breakout obtained (Adafruit 5832 or 6349 variant)
- [ ] **Onboard 15 mΩ shunt removed from INA228 breakout (§3.3 step 1)**
- [ ] **(V1.3 change)** **VBUS jumper soldered CLOSED on back of INA228 breakout (§3.3 step 2)**
- [ ] **(V1.3 addition)** **U2 header pin 5 lifted before breakout solder (§3.3 step 3)**
- [ ] **(V1.3 addition)** **R2 not populated on PCB (§3.3 step 4)**
- [ ] Pololu Ideal Diode (4-60V, 10A) reverse-voltage protector on hand (spare from UPS build)
- [ ] Pololu module's VIN/GND/VOUT pin labels identified from silkscreen
- [ ] **(V1.3 addition)** **2× 100–250 mA fast-blow fuses + inline holders on hand for Kelvin sense leads (§3.3 step 6)**
- [ ] DROK shunt removed from existing location (was in negative cable in legacy install)
- [ ] DROK shunt's Kelvin sense terminals verified present
- [ ] DS18B20 sensor module sourced
- [ ] Battery-bank ESPHome YAML (V1.13) compiled with correct topology configuration
- [ ] **(V1.5 addition)** Four credential placeholders replaced (API key, OTA password, fallback-AP password) and Wi-Fi SSID/PSK moved to `!secret` before any public commit
- [ ] **(V1.5 addition)** `signed_ota_verification` evaluated per §6.5: schema confirmed, XIAO C3 chip-revision/scheme verified, full OTA round-trip bench-tested (enable only after the round-trip passes)
- [ ] **(V1.5 addition)** Local SOC readout decision made (small I²C OLED at the panel **or** a documented multimeter voltage-fallback rule) — see §6.5 rationale: the manual shutdown decision must not depend solely on the Wi-Fi → HA → phone path
- [ ] **(V1.3 demoted from mandatory to optional)** LiTime 80A charger AC-DC isolation check per §4.7 procedure *(no longer a stop-the-build item in high-side topology)*
- [ ] LiTime 80A charger: present wiring location of DC+ and DC− confirmed (should land on busbars, not battery terminals)

### 8.2 Wiring (Power Off — Disconnect Battery)

**Pre-rework:** unplug LiTime charger from AC wall and remove from busbars temporarily. Disconnect inverter from AC mains. Switch off any DC loads.

- [ ] **(V1.3 change)** Legacy shunt location in negative cable abandoned — remove shunt from negative cable
- [ ] **(V1.3 addition)** 2/0 AWG cable installed: **battery+ → shunt battery-side terminal**
- [ ] **(V1.3 addition)** 2/0 AWG cable installed: **shunt load-side terminal → positive busbar**
- [ ] **(V1.3 addition)** **Negative battery cable verified unbroken (no shunt in this path)**
- [ ] DROK display unit (legacy) disconnected and removed (or set aside as backup)
- [ ] **(V1.3 polarity per §4.2)** 22 AWG twisted pair: shunt **battery-side** Kelvin → inline fuse → INA228 **VIN+** terminal
- [ ] **(V1.3 polarity per §4.2)** 22 AWG twisted pair: shunt **load-side** Kelvin → inline fuse → INA228 **VIN−** terminal
- [ ] **(V1.3 removal)** ~~22 AWG: positive busbar → INA228 VBUS terminal~~ *(no external VBUS wire in V1.3 — VBUS sourced internally via closed jumper)*
- [ ] Pololu Ideal Diode mounted in accessible location near monitor board
- [ ] 18 AWG: positive busbar (load-side of shunt) → Pololu VIN terminal
- [ ] 18 AWG: Pololu VOUT terminal → TB1.2 (monitor BATT_RAW)
- [ ] **(V1.3 change)** 18 AWG: **negative busbar** → Pololu GND terminal *(was "shunt battery-side terminal" in V1.2)*
- [ ] 18 AWG: Pololu GND → TB1.1 (monitor GND)
- [ ] DS18B20 sensor wired to TB2 (with correct color convention)
- [ ] DS18B20 sensor body mounted to battery case with thermal contact
- [ ] LiTime charger DC+ reconnected to positive busbar (load-side of shunt)
- [ ] LiTime charger DC− reconnected to negative busbar
- [ ] **(V1.3: direction inverted from V1.2)** **VERIFY: LiTime charger DC+ lands on positive busbar, NOT at battery positive terminal directly** — wrong location bypasses shunt for charging measurement
- [ ] All sense wires mechanically routed (zip-tied or sleeved) away from heavy cables and sharp edges
- [ ] **(V1.3 addition)** Kelvin sense fuses mounted close to shunt end with strain relief; insulated fuse holders

### 8.3 Pre-Power-On Verification (Battery Disconnected)

- [ ] **(V1.3 addition)** **Visually verify U2 pin 5 is lifted (no electrical contact between breakout pin 5 and PCB pad 5)**
- [ ] **(V1.3 addition)** **Visually verify R2 pad is empty**
- [ ] **(V1.3 change)** **Visually verify VBUS jumper on breakout back is bridged with solder** *(was: "VBUS jumper confirmed OPEN" in V1.2)*
- [ ] Visual inspection of all solder joints under magnification
- [ ] Continuity check: no shorts between BATT_RAW and GND at TB1
- [ ] **(V1.3 change)** Continuity check: 18 AWG monitor GND traces back to **negative busbar** *(was: shunt battery-side)*
- [ ] **(V1.3 change)** Continuity check: Pololu VIN ↔ positive busbar, Pololu VOUT ↔ TB1.2, Pololu GND ↔ **negative busbar**
- [ ] Polarity check at Pololu module: VIN goes to positive (busbar), GND to negative (busbar) — re-verify against silkscreen labels
- [ ] **(V1.3 polarity)** Continuity check: VIN+ Kelvin sense pair traces to shunt **battery-side**, VIN− to shunt **load-side**, with inline fuses intact
- [ ] **(V1.3 removal)** ~~Continuity check: VBUS lead lands on positive busbar~~ *(no external VBUS lead in V1.3)*
- [ ] **(V1.3 change)** Continuity check: U2 socket pin 1 is +3V3, pin 2 is GND, pins 3-4 are SCL/SDA, **pin 5 is OPEN circuit to PCB** *(V1.2 expected ALERT here)*
- [ ] Multimeter check: shunt's Kelvin sense terminals show <1 mΩ to corresponding heavy bolt
- [ ] **(V1.3 addition)** Multimeter check: each Kelvin sense fuse shows <1 Ω closed-circuit (good fuse)

### 8.4 Initial Power-On

1. Insert U1 (XIAO), U2 (INA228 with shunt removed, jumper closed, pin 5 lifted), U3 (Pololu) in respective sockets
2. **Disconnect inverter from busbars** for initial test (no high-current loads active)
3. Connect battery to busbars (positive cable now runs through shunt — *V1.3 topology*)
4. Verify F1 doesn't blow
5. Measure +3V3 at U3 output: should read 3.30 V ±0.07 V
6. Verify LED illuminates
7. Measure battery draw from monitor: should be ~10–25 mA at 13.4 V
8. Flash firmware via USB (TB1 disconnected during flash)
9. Verify I²C device discovery returns INA228 at 0x40
10. **(V1.3 critical check)** Read INA228 bus voltage: should match measured battery voltage within ±0.5%. **If reading is ~3.3 V or 0 V instead, the VBUS jumper on the breakout is not actually bridged** — power off and resolder. This check confirms the jumper-closed configuration is working.
11. Read INA228 current: should read very close to 0 (only monitor self-consumption flowing through shunt, ~negative ~100 mA in discharge sign — *the monitor itself is a small load that the high-side shunt sees as discharge*)

### 8.5 Functional Verification

1. Reconnect inverter
2. Apply a known load to inverter output (e.g., 1500 W heater)
3. Compare INA228 current reading against expected: 1500 W / ~12.8 V = ~117 A discharge
4. **INA228 should read approximately -117 A** (negative = discharging, per V1.3 §6.2 committed sign convention)
5. Run for 1 hour, verify Ah accumulation: ~117 Ah delivered should match INA228's discharge Ah counter within ±2–3 Ah
6. Sign convention check: confirm Home Assistant dashboard shows discharge as negative current
7. **(V1.3 change)** ALERT pin functionality: **not used** *(V1.2 expected ALERT to be wired through R2 to GPIO20; in V1.3 the INA228 ALRT lands on the floating header pin 8 with U2 pin 5 lifted. V1.11 firmware does not depend on ALERT — see §11.2 firmware roadmap for the implication.)*

### 8.5.1 Charger Functional Verification

1. Disconnect inverter load
2. Connect LiTime charger to AC wall outlet
3. **(V1.3: sign inverted from V1.2)** **INA228 should read POSITIVE current with magnitude up to ~80 A (charging, per V1.3 §6.2 committed sign convention)**
4. Monitor charge cycle to completion:
   - Bulk phase: constant ~80 A at rising voltage (12.8 → 14.4 V)
   - Absorption phase: constant 14.4–14.6 V at tapering current
   - End: charger LED transitions to "full charge" status; INA228 current drops to near zero
5. Compare Ah accumulated during charge session against expected from charger:
   - LiTime delivers approximately 80 A × hours-in-bulk during bulk phase
   - For a typical session, Ah-in via INA228 should match charger's apparent output within ±3% (accounting for shunt tolerance and Coulomb efficiency)
6. Verify both charging and discharging events appear in HA history with correct signs and accumulator behavior

### 8.6 Ground-Loop Verification — Reduced Priority in V1.3

The detailed ground-loop verification tests in V1.2 §8.6 were necessary because low-side topology was vulnerable to parallel ground paths defeating the shunt measurement. **In V1.3 high-side topology, these tests are no longer mandatory** — the shunt is on the positive side and parallel ground paths on the negative side cannot bypass the measurement.

Optional sanity check (still worth doing once):

- [ ] Inverter running with known load (1500 W heater on AC output)
- [ ] Measure voltage across the shunt at heavy-bolt terminals with a DMM: should match expected shunt drop (37 mV at 100 A, 75 mV at 200 A)
- [ ] Sign convention check: battery-side higher than load-side during discharge

If the measured shunt drop disagrees with the INA228 reading by more than the shunt tolerance (±2%), investigate Kelvin sense wiring before commissioning.

---

## 9. Safety Considerations

### 9.1 Critical Hazards

**Battery short circuit:** A 500 Ah LiFePO4 bank can deliver thousands of amps into a short. Any time the heavy cables are disconnected and reconnected, treat as a high-energy work site:
- Remove all metal jewelry
- Use insulated tools
- Cover busbar surfaces with rubber mat or insulated cover when not actively working
- Never bridge battery+ and battery− with any tool or wire

**Inverter shock hazard:** The 2000 W inverter produces 120 V AC on its output. Verify inverter is OFF and unplugged from any load before working on adjacent DC wiring.

**Heat from heavy cables:** Under sustained high load (>100 A), 2/0 AWG cables warm noticeably. Crimped lugs that are loose dissipate significant power and can melt insulation. Torque all heavy-cable lugs to spec and re-torque after first full-load test.

**(V1.3 addition) Kelvin sense lead at battery+ potential:** In high-side topology the Kelvin sense leads carry ~13 V relative to chassis. A pinched or abraded sense wire shorting to chassis would fault battery+ to ground through the shunt's small Kelvin tap. **Mitigation:** mandatory 100–250 mA fast-blow inline fuses on each sense lead (§3.3 step 6). Without these, a single insulation failure could melt the sense lead and damage the shunt's Kelvin terminal.

### 9.2 Built-In Protection

- **F1 (1 A SB)** on monitor input protects board against shorts in the +12 V monitor feed
- **Pololu D24V7F3** survives input transients up to 36 V
- **INA228** rated to 85 V common-mode; well within 12 V system specs
- **DROK shunt** rated 200 A continuous, brief excursions to ~300 A acceptable
- **(V1.3)** **Kelvin sense inline fuses** protect against shorted sense leads in high-side topology
- **(V1.13) Stale-bus watchdog** — no INA228 read for >10 s → `bank_state` FAULT and Ah/Wh integration freezes (auto-recovers on the next good read)
- **(V1.13) Sensor plausibility guards** — bus voltage outside 8–16 V is dropped (sustained → watchdog FAULT); current magnitude ≥350 A freezes SOC integration and forces FAULT, catching a saturated/garbage current channel including an open Kelvin sense lead. Surfaced as the **Current Channel Fault** diagnostic sensor. See §6.5 (and its documented limit re: plausibly-but-wrong readings)
- **(V1.13) `safe_mode`** — repeated boot failures drop the device to logging + Wi-Fi + OTA only, enabling over-the-air recovery from a bad config without physical access. See §6.5

### 9.3 Reverse-Polarity Protection — Mitigated

This deployment uses an external **Pololu Ideal Diode reverse-voltage protector** (LM74700-Q1) inline between the positive busbar and TB1.2. See §4.3.

**Protection behavior:**
- Correct polarity: ~1 mV drop, normal operation
- Reversed polarity at TB1: MOSFET stays OFF, monitor doesn't power up, no damage

**Visual indication of polarity fault:** if TB1 is wired backwards, the LED on the monitor board will not illuminate. This is the expected behavior — disconnect, reverse polarity, reconnect. No component damage.

**Note:** Reverse polarity at the **Pololu module's** VIN/GND terminals (one stage upstream of the monitor board) would not be protected — the module itself would be in the reversed condition. The module *does* protect against reverse polarity downstream of itself (i.e., at TB1), which is the realistic install hazard. Polarity-check the Pololu module's input terminals carefully — they're labeled VIN and GND on the silkscreen.

---

## 10. Maintenance and Calibration

### 10.1 Routine Inspection

- **Monthly:** Visual check for loose connections at shunt and busbar terminals. Look for discoloration (sign of heating from poor connections).
- **Quarterly:** Re-torque heavy cable lugs. Verify monitor board reads battery voltage consistent with external meter. **(V1.3 addition; V1.5 upgraded to electrical)** Inspect Kelvin sense fuse holders for corrosion or strain damage **and verify each electrically**: with the bank disconnected, confirm <1 Ω end-to-end across each inline sense fuse (a good fuse) and <1 mΩ from each Kelvin tap to its heavy bolt. *This electrical check is the mitigation the firmware relies on for the failure modes its plausibility bounds cannot catch (a partial/high-resistance Kelvin connection reads plausibly-but-wrong — see §6.5). A blown VIN− sense fuse in particular is a silent failure: VBUS is sourced from VIN+, so bus voltage still reads and the stale-bus watchdog stays satisfied while the current channel is broken — the quarterly electrical check is how that is caught.*
- **Annually:** Re-run calibration procedure (§7.1) to detect long-term shunt drift.

### 10.2 SOC Recalibration

*V1.2 described SOC recalibration as a manual coulomb-counter reset; V1.3 updated to reflect the firmware's automatic anchor mechanism. V1.4 corrects the mechanism description to match the firmware exactly (the firmware uses no taper-current threshold).*

The V1.13 firmware maintains Coulomb counting anchored at each confirmed full charge (V1.7+ feature). Recalibration is automatic at full-charge anchors. The detection is two-stage:

- **Absorption confirmation:** the `Absorption Phase` binary sensor (firmware id `battery_fully_charged`) sets an internal `absorption_reached` flag when bus voltage is ≥14.20 V **and** current is in the charging direction (I > 0), sustained for 60 s. 14.20 V is below the 14.60 V CV setpoint but well above the ~13.26 V resting OCV, so it can only be held during CV absorption. **No taper-current threshold is used** — taper detection was removed in firmware (the `full_charge_taper_a` substitution no longer exists).
- **Anchor (automatic):** the full-charge event — reset cycle counters, set SOC = 100%, log the cycle summary — fires on the **charger-stop edge** (`is_charging` `on_release`, i.e. current falling back below the +0.05 A charging threshold for the debounce window) **provided `absorption_reached` is set**. A guard rejects the anchor if net current is below −1.0 A at charger-stop (that means a heavy load overpowered the charger rather than the charger completing). Firing on the charger-stop edge — rather than at the moment of absorption — reliably captures completion even when the LiTime cuts off sharply and the bus voltage sags from 14.6 V to OCV in under a second.
- **Manual anchor:** the "Mark as Fully Charged" button exposes a manual reset (clears `absorption_reached`, resets the cycle counters, anchors SOC = 100%) for cases where the absorption-confirmed anchor didn't fire but the bank is known to be at 100%.

*Edge note:* if a sustained discharge begins within ~30 s of the charger stopping, the `Discharging` sensor's `on_press` clears `absorption_reached` before the charger-stop anchor fires, so that full-charge anchor is skipped (a deliberate trade-off favouring "never falsely anchor to 100%" over "catch every true 100%"). Use the manual button in that rare case.

The V1.10 firmware feature also computes a **self-discharge reconciliation** at each clean full→full anchor (`U = recon_coul_eff × ah_in − ah_out`), logging a recommended `self_discharge_pct_per_month` value. Apply by editing the substitution; see firmware V1.10 changelog for the methodology.

---

## 11. Future Enhancements

### 11.1 V2 PCB Improvements (Battery-Bank-Specific)

If a dedicated battery-bank monitor board is designed as V2:

- **(V1.3 addition.) Native INA228 footprint** — eliminates the V1.3 adaptation overhead (pin 5 lift, R2 DNP, VBUS-jumper-closed workaround)
- **Integrated reverse-polarity protection** — LM74700-Q1 + N-channel MOSFET on-board (replacing the external Pololu module)
- **Dedicated shunt-sense terminal block** — 4-position terminal for VIN+/VIN−/Kelvin pair with optional 100 Ω + 0.1 µF input filters, and **(V1.3 addition)** integrated Kelvin-sense fuse footprints so inline fuses don't need to be field-added
- **TVS diode (P6KE18CA)** across BATT_RAW for inverter-bus transient protection
- **Test points** at BATT_RAW, +3V3, GND for field debugging
- **(V1.3 addition.)** Removable jumper or solder bridge between board GND and "system GND" to allow ground-loop investigation without rework

### 11.2 Firmware Roadmap

*V1.2 §11.2 listed forward-looking firmware items. By V1.3 (V1.11 firmware), several are implemented; V1.3 marks the status:*

- ✓ **(implemented in V1.11)** Temperature-compensated SOC monitoring (DS18B20 reading tagged with each measurement)
- ✓ **(implemented in V1.11)** Coulombic-efficiency tracking (Ah-in vs Ah-out across cycles, V1.7+ Coulombic Efficiency sensor)
- ✓ **(implemented in V1.11)** Cycle counter for battery aging analysis (`total_full_charge_count`)
- ✓ **(implemented in V1.11)** Self-discharge reconciliation logger (V1.10 feature)
- ✓ **(implemented in V1.11)** Per-outage energy capture (V1.9 outage event system)

Still on the roadmap:

- Apparent Ri trending (V1.8 provisional feature; awaits field validation per its changelog)
- Opportunistic capacity-fade recalibration of `validated_capacity_ah` from deep-discharge outages (rare events, opportunistic capture)
- **(V1.3 note.)** Migration from polling to ALERT-driven interrupt for sub-ms sampling — **blocked by V1.3 hardware**: with U2 pin 5 lifted, the INA228 ALRT pin lands on the floating header pin 8 instead of being routed to a GPIO. A V2 PCB with native INA228 routing would unblock this.

---

## 12. References

| Document | Source |
|---|---|
| UPS-Monitor-THT V1 design document | `UPS-Monitor-THT_Design_Document.md` |
| Battery-bank firmware V1.13 | `battery-bank-monitor.yaml` |
| INA228 datasheet | Texas Instruments SBOS951 (Rev A) |
| Adafruit INA228 breakout pinouts | https://learn.adafruit.com/adafruit-ina228-i2c-power-monitor/pinouts |
| Adafruit INA228 product page | https://www.adafruit.com/product/5832 |
| Adafruit INA228 PCB files | https://github.com/adafruit/Adafruit-INA228-PCB |
| DROK shunt installation reference | https://www.droking.com (model-specific PDF) |
| ESPHome INA2xx component | https://esphome.io/components/sensor/ina2xx.html |
| LiFePO4 battery study | https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks |
| LiFePO4 Technical Report (Mar 6, 2026) | `LiFePO4_Report_2026-03-06.md` in the battery study repo |

---

*End of document.*
