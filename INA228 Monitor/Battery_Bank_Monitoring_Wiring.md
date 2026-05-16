# 12V 500Ah LiFePO4 Battery Bank Monitoring — Wiring Summary

**System:** 12 V / 500 Ah LiFePO4 battery bank with 2000 W inverter
**Monitor board:** UPS-Monitor-THT V1 (repurposed) + Adafruit INA228 breakout
**Current shunt:** Repurposed DROK 200 A / 75 mV manganin shunt
**Document revision:** 1.2 (added LiTime 80A charger integration)
**Author:** William Collis
**Status:** Pre-build reference

---

## 1. Purpose

Replace the standalone DROK display unit with a Wi-Fi-connected monitoring solution that reports current, voltage, temperature, accumulated Ah/Wh, and runtime estimates to Home Assistant in real time. Provides the same data quality as the UPS monitor but at battery-bank scale (200 A peak vs. 250 mA peak), enabling unified Home Assistant dashboard coverage of both 12 V systems.

**Engineering rationale:** The UPS-Monitor-THT board was designed with dual-use in mind. The INA260 (UPS application) and INA228 (battery bank application) Adafruit breakouts share the same 8-pin header footprint, allowing the same PCB to host either chip without a respin. This document covers the INA228 + external shunt configuration for battery-bank deployment.

---

## 2. System Topology Overview

```
                    ┌─────────────────────────────────────────────────┐
                    │      BUSBAR (+) — 12 V positive                 │
                    └──┬───────┬─────────────┬─────────────┬──────────┘
                       │       │             │             │
                   [Battery+] [Inverter+] [Charger+]  [Other loads+]
                       ↑                       ↑
                  ┌─────────┐           ┌──────────────┐
                  │ BATTERY │           │ LiTime 80A   │
                  │   BANK  │           │ AC LiFePO4   │
                  │ 500 Ah  │           │ charger      │
                  │ LiFePO4 │           │ 120 V AC in  │
                  └─────────┘           └──────────────┘
                       ↓                       ↓
                   [Battery−]              [Charger−]
                       │                       │
                       └─── 2/0 AWG ───┐       │
                                       │       │
                                  ┌────┴────┐  │
                                  │ SHUNT   │  │ 200 A / 75 mV
                                  │ (DROK)  │  │
                                  └────┬────┘  │
                                       │       │
                                       └─── 2/0 AWG ───┐
                                                       │
                    ┌──────────────────────────────────┴──┐
                    │   BUSBAR (−) — 12 V return          │
                    └──┬───────────────────────────┬──────┘
                       │                           │
                  [Inverter−]              [Other loads−]
```

**Measurement configuration:** Low-side current sensing (shunt in negative cable).
**Sign convention:** Positive current = battery charging, negative = battery discharging.
**Ground reference:** Single-point ground at the battery-negative side of the shunt.

---

## 3. Hardware Bill of Materials

### 3.1 Main Components

| Item | Part | Source | Notes |
|---|---|---|---|
| Monitor PCB | UPS-Monitor-THT V1 | OSH Park | One of 3 boards from initial fab run |
| INA228 breakout | Adafruit 5832 (or 6349 INA228 variant) | Adafruit / DigiKey | **Onboard 15 mΩ shunt must be removed** |
| Microcontroller | Seeed XIAO ESP32-C3 | Seeed Studio | Same as UPS board, OTA-flashable |
| Regulator | Pololu D24V7F3 | Pololu #2842 | 4–36 V → 3.3 V at 600 mA |
| Reverse-voltage protector | Pololu Ideal Diode 4-60V, 10A | Pololu #5382 | LM74700-Q1 + N-MOSFET ideal diode; installed inline with monitor power feed. Spare from UPS build. |
| Temperature sensor | DS18B20 module (with integral 4.7 kΩ pull-up) | Generic | Mount to battery case |
| Fuse | 1 A slow-blow 5×20 mm | Würth 696108003002 | Protects monitor board input (onboard PCB fuse F1) |
| Current shunt | 200 A / 75 mV manganin | Repurposed from DROK display kit | Verify Kelvin sense terminals present |
| Bank charger | LiTime 12V (14.6V) 80A LiFePO4 | LiTime | Existing — AC-input wall charger, 120 V → 14.6 V DC. Permanently wired to busbars. |

### 3.2 Wiring Materials

| Item | Spec | Purpose |
|---|---|---|
| Battery main cables | 2/0 AWG (existing) | Battery ↔ shunt ↔ busbar high-current |
| Sense pair | 22 AWG twisted pair (unshielded) | DROK shunt sense → INA228 VIN+/VIN− |
| Bus voltage tap | 22 AWG | INA228 VBUS → positive busbar |
| Monitor power feed | 18 AWG | Positive busbar → TB1.2 (BATT_RAW) |
| Monitor ground | 18 AWG | Battery−-side of shunt → TB1.1 (GND) |
| DS18B20 cable | 3-conductor, ≥22 AWG | TB2 → battery case sensor |

### 3.3 Critical Hardware Modifications Required

**Before installing the INA228 breakout in U2 socket:**

1. **Remove the onboard 15 mΩ shunt resistor** from the INA228 breakout PCB. The component is a small SMD resistor between the VIN+ and VIN− terminal block pads. Either cut it off with flush cutters or desolder with hot air. **This is mandatory** — without removal, the onboard shunt sits in parallel with the external DROK shunt. At 200 A measured, ~5 A would flow through the onboard SMD resistor, destroying it immediately.

2. **Leave the VBUS jumper OPEN** (default state, do not solder closed). This isolates VBUS from VIN+ so it independently reads the busbar voltage. The VBUS jumper is on the back of the breakout, above the VIN+ and VBUS pins. Soldering it closed would put the breakout in high-side measurement mode, which is *not* what this configuration is.

3. **Verify the DROK shunt has dedicated Kelvin sense terminals** — small screws in the middle of the manganin strip, separate from the heavy bolts at either end. If the shunt only has the two large terminals, accuracy degrades from ±1% to roughly ±5% due to bolt-junction resistance entering the measurement loop.

---

## 4. Detailed Wiring Summary

### 4.1 High-Current Path

**Battery negative cable run** (2/0 AWG, existing):

| From | To | Notes |
|---|---|---|
| Battery (−) terminal | Shunt battery-side terminal (large bolt) | Use crimped/torqued ring lug. Torque to shunt manufacturer's spec (typically 12–15 N·m for 2/0 AWG hardware). |
| Shunt load-side terminal (large bolt) | Negative busbar | Use crimped/torqued ring lug. Same torque spec. |

**Positive cable run** (2/0 AWG, existing — unchanged):

| From | To | Notes |
|---|---|---|
| Battery (+) terminal | Positive busbar | No shunt in this path. |
| Positive busbar | Inverter (+) and load (+) | Heavy distribution as before. |

**Note:** With the shunt in the negative leg, the **positive cables remain unbroken**. All loads tap from the positive busbar directly to battery positive.

### 4.2 Sense Wiring — INA228 Inputs

**22 AWG twisted pair from DROK shunt to INA228 breakout** (~18" run, unshielded):

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| Sense A | Shunt's **battery-side** Kelvin terminal (small screw) | INA228 breakout VIN− terminal block | VIN− | Battery-negative reference |
| Sense B | Shunt's **load-side** Kelvin terminal (small screw) | INA228 breakout VIN+ terminal block | VIN+ | Load-side voltage (rises +75 mV at 200 A discharge) |

**Bus voltage tap** (22 AWG, ~12–18"):

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| VBUS sense | Positive busbar | INA228 breakout VBUS terminal block | VBUS | INA228 reads this as bus voltage (~13.4 V nominal) |

**Why no fuses on sense lines:** at 18" run length with no AC wiring nearby, the realistic failure modes are wire pinch/abrasion. These are addressed by mechanical routing (sleeve or zip-tie the sense pair to a stable surface, away from sharp edges). Fuses on µA-scale sense lines would be defense-in-depth that's overkill for this geometry. The INA228 has internal input protection sufficient for non-fault operation.

**Why no shielding:** at this distance with twisted pair and differential measurement, capacitively-coupled noise pickup is well below the INA228's measurement noise floor. Shielding adds termination complexity without measurable benefit. The differential ADC rejects common-mode noise (the dominant interference mode) automatically.

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
- **VIN:** Input from positive busbar
- **VOUT:** Output to monitor TB1.2 (BATT_RAW)
- **GND:** Common reference (connects to shunt battery-side terminal, same node as TB1.1)

**Wiring:**

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| Monitor +12V (input) | Positive busbar | Pololu module **VIN** | BATT_RAW (pre-protection) | 18 AWG |
| Monitor +12V (protected) | Pololu module **VOUT** | UPS-Monitor-THT TB1.2 | BATT_RAW (post-protection) | 18 AWG, short run (~5 cm to module) |
| Pololu GND reference | Shunt's **battery-side** terminal | Pololu module **GND** | GND | 18 AWG; also tied to TB1.1 |
| Monitor GND | Pololu module **GND** node | UPS-Monitor-THT TB1.1 (GND) | GND | 18 AWG, single-point ground at shunt — see §4.4 |

**Protection behavior:**

- **Correct polarity:** MOSFET turns on, ~10 mΩ in series with positive feed, ~1 mV drop at typical load. Monitor receives normal +12 V.
- **Reversed polarity at TB1:** MOSFET stays OFF. No current flows to monitor board. C4 electrolytic, Pololu D24V7F3 input, and INA228 VBUS are all protected. LED on the monitor board will not illuminate, providing immediate visual indication of the wiring fault.

**Why include this protection on the battery-bank deployment:**

A 500 Ah LiFePO4 bank can deliver thousands of amps into a fault. Reverse-polarity at the monitor TB1 connector — possible during install or future maintenance — would destroy C4 instantly and likely damage the Pololu D24V7F3 input. With the LM74700-based protector inline, the worst case becomes "monitor doesn't power up; LED stays dark; check polarity and reconnect." Recoverable, no damage.

**Mechanical mounting:**

The Pololu module is small (~18 × 13 mm) with 4 M2-compatible mounting holes. Options:
1. Bracket-mount near the monitor board with short wires to TB1
2. Inline mount in the heat-shrunk cable run between busbar and TB1
3. Adhesive-mount to the inside of the monitor enclosure if one exists

Option 1 is cleanest mechanically. Use M2 or M2.5 standoffs to space the module off any conductive surface.

**Note:** The Pololu module does not replace the onboard 1 A SB fuse (F1). F1 still protects against downstream shorts and overcurrent. The Pololu module only protects against polarity reversal.

### 4.3.1 Monitor Board GND Reference

The monitor board's GND (TB1.1) routes to the **shunt's battery-side terminal** via the Pololu module's GND node. See §4.4 for full grounding strategy.

| Wire | From | To | Net | Notes |
|---|---|---|---|---|
| Monitor GND | Shunt's **battery-side** terminal | UPS-Monitor-THT TB1.1 (GND) | GND | Single-point ground at the shunt — see §4.4 |

### 4.4 Ground Reference Strategy

**Single-point ground at the battery-negative side of the shunt.**

All ground references converge at this one physical node:
- INA228 VIN− (via sense pair)
- INA228 GND pin (via socket → PCB GND pour → TB1.1 → 18 AWG to shunt battery side)
- Monitor board GND (TB1.1)
- DS18B20 GND (via TB2.3)

**Why this matters:** With the monitor board's GND at the battery-side of the shunt, INA228's chip ground and its VIN− reference are at exactly the same potential. Common-mode voltage at VIN− is zero, eliminating any I·R offset that would arise from routing GND elsewhere.

**Critical isolation check:** The 2000 W inverter must **not** have its chassis ground bonded to battery negative internally. Chassis ground travels via the AC plug to the circuit-breaker panel ground (separate path). If the inverter internally bonds chassis to DC negative, current would flow around the shunt through the chassis-ground path and the shunt would read 0 A regardless of actual load.

**Verification procedure** (perform once at commissioning):
1. Install all wiring per this document
2. Connect a known DC load (e.g., 100 W incandescent bulb on inverter output)
3. Measure voltage between inverter chassis and battery− with a DMM
4. Expected reading: 0 V or a tiny shunt drop (<1 mV at low load, up to 37 mV at 100 A draw)
5. If voltage is significantly different (>100 mV at low load, or 0 V at high load when shunt should be dropping voltage), there is a parallel ground path. **Stop and investigate before commissioning.**

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
                                    └─────┬──────────┬──────────┘
                                          │          │
              ┌───────────────────────────┘          │
              │ 18 AWG                               │ 22 AWG (VBUS)
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
        │ TB1.2     │                          │ INA228    │
        │ BATT_RAW  │                          │ VBUS      │
        └───────────┘                          │           │
                                               │ VIN+ ←────┼── 22 AWG ──┐
        ┌───────────┐                          │           │            │
        │ TB1.1 GND │ ←───── 18 AWG ──┐        │ VIN− ←────┼── 22 AWG ──┼──┐
        └───────────┘                 │        │           │            │  │
                                      │        │ GND ──────┼─ PCB GND ─┐│  │
                            ┌─────────┴──┐     │ SDA  SCL  │ pour      ││  │
                            │ Pololu GND │     │ ALRT      │           ││  │ Twisted
                            └─────────┬──┘     └───────────┘           ││  │ pair, ~18"
                                      │                                ││  │ unshielded
        ┌─────┴─────┐                 │ 18 AWG                         ││  │
        │ Battery + │                 │                                ││  │
        └─────┬─────┘                 │                                ││  │
              │ 2/0 AWG               │                                ││  │
              │ (battery loop         │                                ││  │
              │  unbroken on +)       │                                ││  │
        ┌─────┴─────┐                 │                                ││  │
        │  BATTERY  │                 │                                ││  │
        │  500 Ah   │                 │                                ││  │
        │  LiFePO4  │                 │                                ││  │
        └─────┬─────┘                 │                                ││  │
              │ 2/0 AWG               │                                ││  │
        ┌─────┴─────┐                 │                                ││  │
        │ Battery − │                 │                                ││  │
        └─────┬─────┘                 │                                ││  │
              │ 2/0 AWG               │                                ││  │
              │      ┌────────────────┴┐                               ││  │
              ├──────┤ Shunt batt side │                               ││  │
              │      │ (large bolt)    │                               ││  │
              │      │                 │                               ││  │
              │      │ Kelvin sense    │←─── 22 AWG (Kelvin sense) ────┘│  │
              │      │ (small screws)  │                                │  │
              │      │                 │                                │  │
              │      │  DROK 200A/75mV │←─── 22 AWG (Kelvin sense) ─────┘  │
              │      │                 │                                   │
              │      │ Shunt load side │                                   │
              │      │ (large bolt)    │                                   │
              │      └────────┬────────┘                                   │
              │               │ 2/0 AWG                                    │
              │               │                                            │
              │      ┌────────┴────────┐                                   │
              │      │ Negative busbar │                                   │
              │      └────────┬────────┘                                   │
              │               │                                            │
              │       [Inverter−, Loads−]                                  │
              │                                                            │
              └────────────────────────────────────────────────────────────┘
                                  (return to battery completes loop)

         Notes:
         • Pololu Ideal Diode (LM74700-Q1) inline between busbar and TB1.2
           protects monitor against reverse-polarity at TB1.
         • Single-point ground at shunt battery-side: Pololu GND, TB1.1, and
           INA228 VIN− sense all share this node.
         • VBUS sense to busbar+ is independent (no fuse — 22 AWG, ~12-18").
         • Battery+ cable goes directly to busbar; no shunt on positive side.
         • Battery− cable runs THROUGH the shunt (low-side measurement).
```

### 4.7 LiTime 80A Charger Integration

The bank is charged by a **LiTime 12V (14.6V) 80A LiFePO4 charger** — an AC-input wall charger (120 V AC → 14.6 V DC, 80 A max). The charger is permanently wired to the busbars and operates whenever AC power is applied.

**Specifications:**
- Output: 14.6 V DC, 80 A max (3-stage CC/CV charging profile)
- Input: 100–240 V AC, 50/60 Hz, ~10 A max
- DC isolation: standard isolated SMPS topology (DC output floats relative to AC ground — see verification step below)
- Connector: 120 A Anderson plug or M8 ring terminals (installation-dependent)

**Wiring (current state — unchanged when migrating to INA228):**

| Wire | From | To | Notes |
|---|---|---|---|
| Charger DC+ | Positive busbar | Charger output positive | Existing cable, no relocation required |
| Charger DC− | Negative busbar | Charger output negative | Existing cable, no relocation required |
| Charger AC | 120 V wall outlet | Charger AC input | Standard 3-prong cord with safety ground |

**Why the charger connection topology stays valid post-migration:**

When the DROK shunt moves from the positive cable to the negative cable (low-side INA228 configuration), the charger wiring requires zero changes. The charger's DC− terminal already lands on the negative busbar, which is *downstream* of the shunt. Charging current flows:

```
Charger DC+ → Positive busbar → Battery+ → through battery → Battery− →
2/0 AWG → SHUNT (measured as negative current = charging) →
Negative busbar → Charger DC-
```

The INA228 sees full charging current with proper sign convention (negative = charging) without any rewiring.

**Critical: shunt sees all charging current**

For the INA228 to correctly measure charge/discharge balance, the charger's DC− cable must terminate at the **negative busbar**, never directly at the battery negative terminal. Direct termination at the battery negative post would bypass the shunt entirely and the INA228 would report 0 A during 80 A charging sessions.

✓ **Current installation:** charger DC− on negative busbar → charging current passes through shunt → INA228 reads correctly.

✗ **Wrong topology:** charger DC− on battery negative terminal → charging current bypasses shunt → no charge measurement.

**AC-DC isolation verification** (one-time check, ~30 seconds with multimeter):

The charger should have its DC output isolated from AC line and chassis ground. This is standard for the device class but worth verifying once before final commissioning. Procedure:

1. Unplug charger from AC wall outlet
2. Disconnect charger DC leads from busbar (no battery connection)
3. Multimeter on continuity/resistance mode
4. Probe between **AC plug ground pin** (3rd pin) and **DC output negative terminal**
5. Expected reading: **open circuit** (> ~10 MΩ) — confirms isolation
6. If reading shows low resistance (< few kΩ): charger is non-isolated and you have a ground path from battery negative → charger DC- → AC ground → AC breaker panel → building ground. This would bypass the shunt in low-side configuration. If detected, contact LiTime support and re-evaluate topology (high-side would handle a non-isolated charger correctly).

**Charging measurement impact:**

At 80 A continuous charging through the 200 A / 75 mV shunt:
- Shunt voltage drop: 80 × 0.000375 = 30 mV (well within INA228 ±163.84 mV range)
- Shunt power dissipation: 80² × 0.000375 = 2.4 W (manageable, ~15% of full-scale)
- INA228 LSB at this current: ~0.83 mA
- Practical resolution after averaging: ~5–10 mA — excellent for Coulomb integration

**Telemetry benefits of charger-through-shunt measurement:**

With the charger current flowing through the shunt, the firmware automatically captures:

1. **Charge events** in `ah_delivered` and `wh_delivered` accumulators (with negative-sign convention)
2. **Round-trip Coulomb efficiency** — by comparing Ah-in vs. Ah-out across charge/discharge cycles
3. **Charger profile validation** — verify 3-stage CC/CV curve (constant 80 A during bulk, tapering during absorption, stop at full)
4. **Charger session duration** for energy-cost accounting
5. **Battery acceptance** monitoring as the bank ages — capacity-to-full at fixed charge current trends downward over cycle count

These metrics enable battery-aging analysis comparable to commercial BMS systems.

**Operational notes:**

- The charger has its own safety protections (overvoltage, overcurrent, overtemperature, reverse polarity). The Pololu reverse-polarity protector on the monitor board does not protect against charger fault conditions — those are handled internally by the LiTime charger.
- During charging sessions, the inverter may simultaneously be drawing load. The INA228 reports the *net* current — `(load draw) − (charge rate)`. Positive net = net discharge, negative net = net charge. Firmware should display this clearly so the user doesn't confuse net measurements with individual component currents.
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

In ESPHome / Arduino firmware:

```cpp
ina228.setShunt(0.000375, 200.0);   // 0.375 mΩ DROK, 200 A max
ina228.setAdcRange(0);              // ±163.84 mV (full range for 200 A)
```

**Math check:** 75 mV / 200 A = 0.000375 Ω = 375 µΩ.

At ±163.84 mV ADC range:
- Maximum measurable current: 163.84 mV / 0.375 mΩ = 437 A (some headroom above the 200 A shunt rating)
- LSB resolution: ~10 µA equivalent at the chip → ~0.83 mA at the shunt (3.13 µV / 0.375 mΩ)
- Practical noise floor: ~5–10 mA after averaging

### 5.3 Hardware Modifications Recap

| Modification | Required | Location |
|---|---|---|
| Remove onboard 15 mΩ shunt | **Yes** | Adafruit breakout PCB, between VIN+ and VIN− terminal block pads |
| Leave VBUS jumper OPEN | **Yes** | Back of breakout, above VIN+ and VBUS pins |
| Verify Kelvin sense terminals on DROK shunt | **Yes** | Physical shunt — small screws on the manganin strip |
| I²C address jumpers | No (leave at 0x40) | Back of breakout, A0 and A1 |

---

## 6. Firmware Updates (from UPS Monitor V1 baseline)

The existing `ups-monitor.yaml` ESPHome config requires the following changes for battery-bank deployment:

### 6.1 Required Changes

1. **I²C address:** Change `0x41` → `0x40` in 3 places (lines 110, 195 comment, 347)
2. **Sensor platform:** Change `platform: ina260` → `platform: ina228` (line 346)
3. **Shunt calibration:** Add the `setShunt(0.000375, 200.0)` call. ESPHome may handle this differently than Arduino — check ESPHome INA228 component documentation. (As of ESPHome 2026.x, an `ina2xx_i2c` or dedicated `ina228` component should expose `shunt_resistance:` and `max_current:` parameters.)
4. **ADC range:** Configure `adc_range: ±163.84 mV` or equivalent setting per ESPHome component.

### 6.2 Sign Convention Verification

With shunt low-side and VIN− at battery negative, VIN+ at load side:
- Battery **discharging** → current flows from battery+ through loads, returns through shunt from load side to battery side → VIN+ is at higher potential than VIN− → INA228 reads **positive** current
- Battery **charging** → current flows backward through shunt → VIN+ at lower potential than VIN− → INA228 reads **negative** current

**This is opposite to the existing UPS firmware sign convention** (`Positive = CHARGING, Negative = DISCHARGING`).

Two options:
- **Option A (firmware fix):** Invert the sign in firmware. Add `- multiply: -1.0` filter to the `current` sensor block.
- **Option B (wiring fix):** Swap the VIN+ and VIN− wires at the INA228 breakout terminal block. VIN+ to battery-side, VIN− to load-side. Reading then matches existing convention.

Option B is mechanically simpler. Document whichever is chosen so future maintenance doesn't get confused.

### 6.3 Recalibrate System Parameters

The following YAML substitutions are battery-specific and must be re-derived for the 500 Ah bank (vs. the UPS's 10 Ah cell):

```yaml
validated_capacity_ah:    "500"    # or actual usable Ah from D-test
validated_capacity_wh:    "6400"   # ~500 Ah × ~12.8 V mean discharge
typical_load_amps:        "X"      # measure actual standby + typical inverter load
```

Voltage thresholds (`float_voltage`, `on_battery_threshold_v`, `warning_voltage`, `critical_voltage`, `lvd_voltage`) and slope thresholds (`knee_slope_threshold`, `cliff_slope_threshold`) are battery-chemistry properties and will be similar for the same LiFePO4 cells, but should be re-validated against the 500 Ah bank's discharge curve before tuning alarms.

### 6.4 Recommended Approach

Create a separate ESPHome YAML for the battery-bank deployment (e.g., `battery-bank-monitor.yaml`) rather than editing `ups-monitor.yaml`. The two systems have different I²C addresses, different sensor chips, different capacity values, and different alarm thresholds. Keeping the configs separate prevents accidental cross-contamination of settings.

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
5. Update firmware: `setShunt(corrected_value, 200.0)`

This brings the system to within 0.1% of the reference, eliminating shunt tolerance as an error source.

---

## 8. Installation Checklist

### 8.1 Pre-Installation

- [ ] UPS-Monitor-THT V1 PCB received from OSH Park and assembled
- [ ] INA228 breakout obtained (Adafruit 5832 or DigiKey equivalent)
- [ ] Onboard 15 mΩ shunt removed from INA228 breakout
- [ ] VBUS jumper confirmed OPEN on INA228 breakout
- [ ] Pololu Ideal Diode (4-60V, 10A) reverse-voltage protector on hand (spare from UPS build)
- [ ] Pololu module's VIN/GND/VOUT pin labels identified from silkscreen
- [ ] DROK shunt removed from positive battery cable
- [ ] DROK shunt's Kelvin sense terminals verified present
- [ ] DS18B20 sensor module sourced
- [ ] Battery-bank ESPHome YAML written and compiled
- [ ] **LiTime 80A charger: AC-DC isolation verified per §4.7 isolation check procedure**
- [ ] **LiTime 80A charger: present wiring location of DC+ and DC− confirmed (should land on busbars, not battery terminals)**

### 8.2 Wiring (Power Off — Disconnect Battery)

**Pre-rework:** unplug LiTime charger from AC wall and remove from busbars temporarily. Disconnect inverter from AC mains. Switch off any DC loads.

- [ ] 2/0 AWG cable installed: battery− → shunt battery-side terminal
- [ ] 2/0 AWG cable installed: shunt load-side terminal → negative busbar
- [ ] Positive battery cable verified unchanged (no shunt in this path)
- [ ] **DROK shunt removed from positive cable; positive cable now goes directly battery+ → busbar**
- [ ] **DROK display unit (legacy) disconnected and removed (or set aside as backup)**
- [ ] 22 AWG twisted pair: shunt battery-side Kelvin → INA228 VIN−
- [ ] 22 AWG twisted pair: shunt load-side Kelvin → INA228 VIN+
- [ ] 22 AWG: positive busbar → INA228 VBUS terminal
- [ ] Pololu Ideal Diode mounted in accessible location near monitor board
- [ ] 18 AWG: positive busbar → Pololu VIN terminal
- [ ] 18 AWG: Pololu VOUT terminal → TB1.2 (monitor BATT_RAW)
- [ ] 18 AWG: shunt battery-side terminal → Pololu GND terminal
- [ ] 18 AWG: Pololu GND → TB1.1 (monitor GND) (can branch from Pololu GND node)
- [ ] DS18B20 sensor wired to TB2 (with correct color convention)
- [ ] DS18B20 sensor body mounted to battery case with thermal contact
- [ ] **LiTime charger DC+ reconnected to positive busbar** (no change from prior wiring location)
- [ ] **LiTime charger DC− reconnected to negative busbar** (no change from prior wiring location)
- [ ] **VERIFY: LiTime charger DC− lands on negative busbar, NOT at battery negative terminal directly** — wrong location bypasses shunt for charging measurement
- [ ] All sense wires mechanically routed (zip-tied or sleeved) away from heavy cables and sharp edges

### 8.3 Pre-Power-On Verification (Battery Disconnected)

- [ ] Visual inspection of all solder joints under magnification
- [ ] Continuity check: no shorts between BATT_RAW and GND at TB1
- [ ] Continuity check: 18 AWG monitor GND traces back to shunt battery-side
- [ ] Continuity check: Pololu VIN ↔ positive busbar, Pololu VOUT ↔ TB1.2, Pololu GND ↔ shunt batt-side
- [ ] Polarity check at Pololu module: VIN goes to positive (busbar), GND to negative (shunt batt-side) — re-verify against silkscreen labels
- [ ] Continuity check: VIN+ and VIN− leads land on correct shunt terminals
- [ ] Continuity check: VBUS lead lands on positive busbar
- [ ] Continuity check: U2 socket pin 1 is +3V3, pin 2 is GND, pins 3-5 are SCL/SDA/ALERT
- [ ] Multimeter check: shunt's Kelvin sense terminals show <1 mΩ to corresponding heavy bolt
- [ ] **LiTime charger AC-DC isolation check (per §4.7): unplug charger from AC and busbars, measure AC ground pin ↔ DC output negative. Expected: open circuit (>10 MΩ).**

### 8.4 Initial Power-On

1. Insert U1 (XIAO), U2 (INA228 with shunt removed), U3 (Pololu) in respective sockets
2. **Disconnect inverter from busbars** for initial test (no high-current loads active)
3. Connect battery to busbars
4. Verify F1 doesn't blow
5. Measure +3V3 at U3.1: should read 3.30 V ±0.07 V
6. Verify LED illuminates
7. Measure battery draw from monitor: should be ~10–25 mA at 13.4 V
8. Flash firmware via USB (TB1 disconnected during flash)
9. Verify I²C device discovery returns INA228 at 0x40
10. Read INA228 bus voltage: should match measured battery voltage within ±0.5%
11. Read INA228 current: should read very close to 0 (only monitor self-consumption flowing through shunt)

### 8.5 Functional Verification

1. Reconnect inverter
2. Apply a known load to inverter output (e.g., 1500 W heater)
3. Compare INA228 current reading against expected: 1500 W / ~12.8 V = ~117 A discharge
4. INA228 should read approximately -117 A (discharge sign convention)
5. Run for 1 hour, verify Ah accumulation: ~117 Ah delivered should match INA228's `Ah Delivered` sensor within ±2–3 Ah
6. Sign convention check: confirm Home Assistant dashboard shows discharge as negative current
7. ALERT pin functionality: trigger an INA228 alert threshold and verify ESP32-C3 receives the interrupt

### 8.5.1 Charger Functional Verification

1. Disconnect inverter load
2. Connect LiTime charger to AC wall outlet
3. INA228 should read **positive** current with magnitude up to ~80 A (charging — note sign is opposite to discharge)
4. Verify current sign convention matches firmware/dashboard expectation:
   - If firmware convention is "positive = charging," reading should match charger amperage directly
   - If firmware convention is "positive = discharging" (inverted), expect negative reading during charging
5. Monitor charge cycle to completion:
   - Bulk phase: constant ~80 A at rising voltage (12.8 → 14.4 V)
   - Absorption phase: constant 14.4–14.6 V at tapering current
   - End: charger LED transitions to "full charge" status; INA228 current drops to near zero
6. Compare Ah accumulated during charge session against expected from charger:
   - LiTime delivers approximately 80 A × hours-in-bulk during bulk phase
   - For a typical session, Ah-in via INA228 should match charger's apparent output within ±3% (accounting for shunt tolerance and Coulomb efficiency)
7. Verify both charging and discharging events appear in HA history with correct signs and accumulator behavior

### 8.6 Ground-Loop Verification

**Test 1 — Inverter active:**
- [ ] Inverter running with known load (1500 W heater on AC output)
- [ ] Measure voltage between battery− and inverter chassis: expected close to 0 V
- [ ] If voltage exceeds ~100 mV at low load OR is suspiciously 0 V at high load, **stop and investigate** — there is a parallel ground path defeating the shunt measurement

**Test 2 — Charger active:**
- [ ] LiTime charger plugged into AC and actively charging
- [ ] Measure voltage between battery− and charger DC− output terminal: expected to equal the shunt drop (~30 mV at 80 A charging — sign per measurement direction)
- [ ] Measure voltage between charger AC ground pin and battery−: expected close to 0 V if charger is isolated; non-zero indicates AC-DC bond inside the charger
- [ ] Sum check: INA228 reading + observed load current (if any) should equal the difference between charger output current and any active load. If the math doesn't balance, suspect a current path bypassing the shunt.

If either test reveals a parallel ground path, options are:
1. Identify and break the parallel path (e.g., isolation transformer on AC, isolated DC-DC, separate charger)
2. Migrate to high-side shunt configuration (the parallel ground path then doesn't bypass measurement)
3. Accept the measurement bias and document the calibration offset

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

### 9.2 Built-In Protection

- **F1 (1 A SB)** on monitor input protects board against shorts in the +12 V monitor feed
- **Pololu D24V7F3** survives input transients up to 36 V
- **INA228** rated to 85 V common-mode; well within 12 V system specs
- **DROK shunt** rated 200 A continuous, brief excursions to ~300 A acceptable

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
- **Quarterly:** Re-torque heavy cable lugs. Verify monitor board reads battery voltage consistent with external meter.
- **Annually:** Re-run calibration procedure (§7.1) to detect long-term shunt drift.

### 10.2 SOC Recalibration

The INA228 maintains Ah accumulation but, like all coulomb counters, gradually drifts from true SOC over weeks. Recalibration is needed when battery reaches a known SOC reference:

- **Full charge:** When battery voltage reaches ~14.4 V (absorption) with current dropping below ~5 A, SOC = 100%. Reset Ah counter via "Reset Outage Counters" button or HA automation.
- **LVD trip:** When LVD activates at ~11.8 V, SOC ≈ 0% (or whatever empirical value the bank shows at LVD).

For ongoing accurate SOC tracking, automate the 100% recalibration in HA: trigger reset of `ah_delivered_outage` when `battery_fully_charged` binary sensor fires.

---

## 11. Future Enhancements

### 11.1 V2 PCB Improvements (Battery-Bank-Specific)

If a dedicated battery-bank monitor board is designed as V2:

- **Integrated reverse-polarity protection:** LM74700-Q1 + N-channel MOSFET on-board (replacing the external Pololu module) — saves an external component and ~3 cm of wiring
- **Dedicated shunt-sense terminal block:** 3- or 4-position terminal for VIN+/VIN−/VBUS routed as Kelvin pair with optional 100 Ω + 0.1 µF input filters
- **Larger BATT_RAW trace:** 2.0 mm minimum for headroom in shared monitoring + light load applications
- **TVS diode (P6KE18CA)** across BATT_RAW for inverter-bus transient protection
- **Test points** at BATT_RAW, VIN, +3V3, GND for field debugging

### 11.2 Firmware Roadmap

- Migrate from polling current readings to ALERT-driven interrupt for sub-ms sampling
- Add temperature-compensated SOC algorithm using DS18B20 reading
- Implement Coulomb-efficiency correction (charge Ah accumulator > discharge Ah accumulator due to round-trip inefficiency)
- Add cycle counter for battery aging analysis

---

## 12. References

| Document | Source |
|---|---|
| UPS-Monitor-THT V1 design document | `UPS-Monitor-THT_Design_Document.md` |
| INA228 datasheet | Texas Instruments SBOS951 |
| Adafruit INA228 breakout pinouts | https://learn.adafruit.com/adafruit-ina228-i2c-power-monitor/pinouts |
| Adafruit INA228 product page | https://www.adafruit.com/product/5832 |
| Adafruit INA228 PCB files | https://github.com/adafruit/Adafruit-INA228-PCB |
| DROK shunt installation reference | https://www.droking.com (model-specific PDF) |
| ESPHome INA2xx component | https://esphome.io/components/sensor/ina2xx.html |
| LiFePO4 cell specs | (existing battery study repo) |

---

*End of document.*
