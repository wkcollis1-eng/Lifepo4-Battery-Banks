# LiFePO4 Top-Off / Balance Charger — Design

**System:** bench top-off and balance-hold charger for two 12 V LiFePO4 packs: the DIY UPS's Cyclenbatt 12V 10Ah (charged off the UPS bus) and the 12 V 500 Ah bank (a hold after the LiTime 80 A has finished)
**Controller:** Battery_Bank-Monitor-THT **V2 Rev 1.1** carrier + XIAO ESP32-C3 + Adafruit INA228 (#5832), a second build of the board in `../INA228 Monitor/`
**Document revision:** 0.2 — **pre-build design draft, 2026-09-21.** Nothing here is built or tested. 0.2: Q1 answered by the owner (Cyclenbatt label). The P1 ceiling, the temperature gate and a single setpoint for both packs are now set; nothing is blocked on the owner.
**Author:** William Collis (draft prepared with Claude Code)

Provenance tags follow the house convention: **[M]** measured, **[S]** spec (document + page), **[D]** derived (formula shown), **[I]** inferred (with its falsifier). Fuse interrupt ratings taken from distributor listings are **[I]**, not [S]: their datasheets could not be retrieved on 2026-09-21, and the falsifier is the datasheet itself (O2).

---

## 1. The unattended moment

A session is running and the owner is away. Wi-Fi or Home Assistant is down, the ESP32 hangs, or the PSU's voltage regulation fails high.

**"Working" at that moment means:**

1. The session ends by itself within its time cap.
2. The pack never sits above its voltage ceiling for longer than one sample period.
3. No fault the battery can feed can burn a conductor.
4. Nothing restarts a charge after a reboot or an AC blip.

Every protection layer in §8 exists for one of those four clauses.

---

## 2. Why this exists

| Pack | Reason | Evidence |
|---|---|---|
| UPS Cyclenbatt 10 Ah | The HDR-60-12 floats it at 13.3 V, so the cells never reach balancing voltage. On the 09-15 test it delivered 2.5331 Ah LVD-to-LVD, against 4.179 Ah on 05-06 | [M, one test each; `DIY-LiFePO4-UPS/data/2026-09-15_full_discharge_survival_test/README.md`]. Its OCV overlay favours a non-uniform pack. This charger is the tool for that report's Open Item 16: a coulomb-counted recharge to termination |
| Bank 500 Ah | The LiTime stops at a 6.48 A taper and gave 10.7 min of balancing activity | [M, one charge, 2026-07-16; `reports/LiFePO4_Report_2026-08-26.md` §3]. The bus-level study cannot see cells inside the five drop-ins, so for the bank this is maintenance, not a measured repair |

**What it cannot do:** balance a pack whose BMS has no balancer. The Cyclenbatt is sealed, with no balance taps [M, owner-confirmed 2026-09-15], and its label gives no balance details [owner, 2026-09-21]. Whether it balances cannot be settled from documentation. The matched-load capacity test in §10.2 is the only measure. A full charge is still worth running for Open Item 16 and to reach the capacity the 13.3 V float never uses.

---

## 3. Requirements

| ID | Requirement | Value | Basis |
|---|---|---|---|
| RQ-1 | Charge current into the 10 Ah pack | **≤ 5.0 A (0.5 C)** | Owner, 2026-09-21, from the Cyclenbatt documentation |
| RQ-2 | The PSU physically cannot exceed RQ-1, under any overload behaviour | ≤ 3.64 A worst case | [D] §4 |
| RQ-3 | Charge stops with no network, no HA, and a hung CPU | — | §1 |
| RQ-4 | Nothing restarts after a reboot or an AC loss | — | §1 |
| RQ-5 | Every conductor the battery can feed is fused at the battery end, with an interrupt rating ≥ the battery's prospective fault current | — | §6 |
| RQ-6 | Reversed battery connection is impossible | — | §6.3 |
| RQ-7 | The UPS pack is never charged on the UPS bus | XB7 validated envelope 11.71–13.11 V | [`DIY-LiFePO4-UPS/UPS-Monitor/boost-subsystem-design.md` R5] |
| RQ-8 | Bank charge current is visible to the bank's own monitor | The charger's return lands on the negative busbar | [`../INA228 Monitor/battery-bank-monitor-wiring-summary-v1_10.md` §4.1, §4.7] |
| RQ-9 | No charging at or below freezing | Charge only above 32 °F | Owner, 2026-09-21, Cyclenbatt label. Applied to the bank too [I: the bank batteries' own labels are not read; it is a conservative floor for an indoor bank] |
| RQ-10 | Charge voltage within the 10 Ah pack's rating | 14.4–14.6 V | Owner, 2026-09-21, Cyclenbatt label |

---

## 4. PSU selection — HDR-30-15, not HDR-60-15

The HDR series has no current setpoint. During bulk the battery holds the output near its own voltage, and the PSU runs at its overload limit: **105–160% of rated output power** [S, HDR-30-SPEC and HDR-60-SPEC, both dated 2026-04-03, p.2].

| | HDR-60-15 | **HDR-30-15** |
|---|---|---|
| Rated | 4 A / 60 W [S, HDR-60-SPEC p.2] | **2 A / 30 W** [S, HDR-30-SPEC p.2] |
| Adj. range | 13.5–18 V [S] | 13.5–18 V [S] |
| OVP | 18.8–22.5 V [S] | 18.8–22.5 V [S] |
| Efficiency (typ.) | 89% [S] | 89% [S] |
| Current in overload, into 13.2 V | **4.77–7.27 A** [D: 63–96 W ÷ 13.2 V] | **2.39–3.64 A** [D: 31.5–48 W ÷ 13.2 V] |
| Meets RQ-1 (≤ 5.0 A)? | **No** — the upper part of the band exceeds it | **Yes, at the band's ceiling** |

The sibling HDR-60-12 on the UPS was measured inside that band. Its total output was 143.8% of nameplate at 11:00:13, decaying to 96.0% by 11:07:58 [D in the 09-15 README; one recharge, with the true peak earlier and unobserved]. So the band is not a paper number.

**Decision: HDR-30-15.** Its datasheet ceiling (3.64 A [D]) is below RQ-1, whatever the overload circuit actually does.

- The 10 Ah pack took ≥ 4.4465 A on the 09-15 outage recharge [M, one firmware peak, a lower bound], so 3.64 A is inside its service history.
- For the bank hold, 2–3.6 A is ample: the hold's job is time at voltage, not current.
- Heat is 3.71 W at rated load [D: 30 W ÷ 0.89 − 30 W].

13.2 V is used as a conservative low battery voltage; the current is lower at any higher voltage.

---

## 5. Architecture

```text
 AC 120 V ── plug-in COUNTDOWN TIMER (no network; layer L6) ── 2-wire cord / IEC C8 ─┐
                                                                                     │
┌──────────────────────────── ABS enclosure, vented ─────────────────────────────────┴──┐
│                                                                                        │
│   Mean Well HDR-30-15  (V_SET on trimpot, lacquered)                                   │
│      +V ──────────┬──────────────────────────────┐                                     │
│      −V ─┐        │                              │                                     │
│          │        │ W3                           │ W2                                  │
│          │   TB1-2 BATT_RAW                 Pololu #2815 VIN                           │
│          │   (V2 board, F1 1 A SB)          Big MOSFET Slide Switch, HP                │
│          │                                  slide LOCKED OFF · ON ◄── control net ─┐   │
│          │                                     VOUT                                │   │
│          │                                      │ W7                               │   │
│          │                                  Pololu #5382 ideal diode IN → OUT      │   │
│          │                                      │ W8                               │   │
│          │                                  INA228 VIN+  (= VBUS, jumper CLOSED)   │   │
│          │                                     15 mΩ onboard shunt (KEPT)          │   │
│          │                                  INA228 VIN−                            │   │
│          │                                      │ W9                               │   │
│          │                                  lead + ─────────────► strain relief ───┼───┼──► keyed connector
│    STAR ─┴── TB1-1 GND · #2815 GND · #5382 GND · lead − ──────────► strain relief ───┼───┼──► keyed connector
│   (PSU −V)                                                                         │   │
│   V2 board J2-1 (GPIO4) ── 1 kΩ ── ON node ── 10 kΩ ── GND                           │   │
│                                     └──►|── ALERT test point  (optional L4)  ────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘

 keyed connector ══ battery pigtail: [FUSE at the battery end] ── battery +
                                                               ── battery − (bank: NEGATIVE BUSBAR)
```

The order of the power path is deliberate:

- **Switch → ideal diode → shunt.** The switch interrupts forward current. The ideal diode blocks the battery from back-feeding the PSU (the job it already does in the UPS [`DIY-LiFePO4-UPS/docs/bom.md`]). The shunt sees only battery current, not the board's supply.
- **The board is fed upstream of the switch**, from the PSU side. It is alive whenever AC is on, draws nothing from the battery when AC is off, and keeps reading the pack while the switch is open.
- **VBUS is on the battery side.** With the switch open, VIN+ is tied to the battery through the idle shunt, so VBUS reads the pack's open-circuit voltage before every start.

### 5.1 Wiring list — enclosure

STAR = the HDR-30-15's −V terminal. Every ground lands there, and nothing else joins grounds. HDR terminal numbers: read them off the unit's silk (datasheet p.4 [S]).

| W# | From | To | Conductor | Notes |
|---|---|---|---|---|
| W1 | AC cord L / N (through the countdown timer) | HDR-30-15 AC/L, AC/N | 2-conductor cord, strain relief (or an IEC C8 inlet) | Class II: the HDR has no earth terminal [S, p.4]. In an ABS box nothing needs earthing |
| W2 | HDR +V | #2815 VIN | 18 AWG red | Power path |
| W3 | HDR +V | V2 board **TB1-2 (BATT_RAW)** | 22 AWG red | Board supply, **upstream of the switch**. On-board F1 (1 A SB) protects it |
| W4 | STAR | V2 board **TB1-1 (GND)** | 22 AWG black | |
| W5 | STAR | #2815 GND | 22 AWG black | Control reference |
| W6 | STAR | #5382 GND | 22 AWG black | Ideal-diode controller reference |
| W7 | #2815 VOUT | #5382 VIN | 18 AWG red | |
| W8 | #5382 VOUT | INA228 breakout **VIN+** terminal | 18 AWG red | VBUS jumper closed, so VBUS = this node. Confirm 18 AWG fits the breakout's 3.5 mm terminal block |
| W9 | INA228 breakout **VIN−** terminal | flying lead + | 18 AWG → 16 AWG | Splice or terminal strip inside the strain relief |
| W10 | STAR | flying lead − | 18 AWG → 16 AWG | Charge return |
| W11 | Flying lead +/− | keyed connector, charger half | 16 AWG red/black | Length to suit; R_series measured at T10 |
| W12 | V2 board **J2-1 (GPIO4_BTN)** | Rs (1 kΩ) → #2815 ON | 24–26 AWG, JST-XH 2-pin | §7.2 |
| W13 | V2 board **J2-2 (GND)** | #2815 GND | 24–26 AWG | |
| W14 | #2815 ON | Rpd (10 kΩ) → #2815 GND | component leads | Fit at the #2815 |
| W15 (opt.) | #2815 ON | Dx anode; Dx cathode → V2 board **ALERT test point** | 24–26 AWG | L4, §7.2 |
| W16 (opt.) | V2 board **TB2** (1 GND, 2 GPIO10_DQ, 3 +3V3) | DS18B20 on the battery case | 3-conductor, ≥ 22 AWG | As `wiring-summary` §4.5 |
| W17 (opt.) | V2 board **J1** (1 SDA, 2 SCL, 3 GND, 4 +3V3) | OLED | 4-conductor | As `wiring-summary` §6.6 |

### 5.2 Wiring list — battery pigtails (permanent, one per battery)

| P# | From | To | Conductor | Notes |
|---|---|---|---|---|
| P1+ | Cyclenbatt **+** F2 tab (6.3 mm insulated female QD) | **ATC-5** inline holder, within inches → keyed connector + | 16 AWG red | §6 |
| P1− | Cyclenbatt **−** F2 tab | keyed connector − | 16 AWG black | |
| P2+ | Bank **positive busbar** stud (ring lug) | **KLKD005** inline 10×38 holder, close to the lug → keyed connector + | 16 AWG red | §6 |
| P2− | Bank **NEGATIVE BUSBAR**, load side of the shunt (ring lug) | keyed connector − | 16 AWG black | **Never battery − directly.** That would bypass the bank monitor's shunt (RQ-8) |

---

## 6. Fusing and the battery connection

### 6.1 Where the fuse goes

The energy that burns wire comes from the **battery**. The PSU limits itself to ≤ 160% of rated power [S] and hiccups below 50% Vout [S, HDR-60-SPEC p.2; the HDR-30 extraction did not preserve that line — confirm].

A short in the external lead (clips touching, insulation chafed) is fed from the battery and never passes a fuse at the charger end. **So the fuse goes at the battery end of the + conductor, as close to the battery terminal as the holder allows.** Everything downstream of it is then protected: pigtail, connector, flying lead, and every node inside the enclosure the battery can reach. A second fuse at the charger end would add nothing for battery-fed faults.

The negative conductor is not fused (standard practice: fuse the ungrounded conductor).

### 6.2 Rating and interrupt capacity

| | 10 Ah pack pigtail | Bank pigtail |
|---|---|---|
| Normal current | ≤ 3.64 A [D, §4] | ≤ 3.64 A [D, §4] |
| Fuse rating | **5 A** | **5 A** |
| Prospective fault current | Bounded by the pack and a 10 A BMS; below 1 kA [I — falsifier: none cheap; use the bank fuse here too if in doubt] | **≥ 3.6 kA** [D: 13.3 V ÷ 3.73 mΩ; the 2-min DC-IR [M, `README.md`] overstates ohmic resistance, so this is a lower bound] |
| Fuse | Bussmann **ATC-5** blade, 1,000 A at 32 VDC [I: distributor listing of Eaton Technical Data 2009; falsifier: that datasheet] in an inline blade holder | Littelfuse **KLKD005**, 10×38 mm fast-acting, 50 kA at 600 VDC [I: distributor listing of the Littelfuse KLKD datasheet; falsifier: that datasheet] in an inline 10×38 holder rated ≥ the fuse |
| Why | 1 kA covers this pack [I] | A 1 kA blade is **not** rated to clear a bank fault. The KLKD's rating covers it without depending on whether the bank has its own Class T (unknown to this doc) |

The fuse protects the **wire**. It does not enforce RQ-1: a 5 A fuse carries 5 A indefinitely. RQ-1 is enforced by the PSU choice (§4) and the firmware I_max stop (§9).

### 6.3 No alligator clips — fused pigtails and a keyed connector

Clips fail this design in two ways:

1. **A clip that slips can bridge busbars.** That short runs through the clip jaw, upstream of every fuse in the lead. On the bank only the bank's own protection stands behind it.
2. **Clips allow a reversed connection.** VBUS is tied to the battery side (jumper closed). A reversed pack puts about −13 V on VBUS and back through the #5382's MOSFET body diode, and the only thing racing the damage is the fuse [I].

**Design:**

- The charger's flying lead (16 AWG red/black) ends in a **keyed polarized connector** (XT60 or equivalent, rated well above 5 A). Each battery gets a **permanent pigtail** carrying its fuse at the battery end.
- **10 Ah pigtail:** insulated 6.3 mm female quick-disconnects for the Cyclenbatt's F2 terminals [`DIY-LiFePO4-UPS/docs/bom.md`] → ATC-5 holder within a few inches → 16 AWG → mating connector.
- **Bank pigtail:** ring lugs sized to the busbar studs. + goes on the **positive busbar**; − goes on the **negative busbar, the LOAD side of the shunt** (RQ-8). Then the KLKD005 holder close to the + lug → 16 AWG → mating connector. The bank pigtail can stay installed and capped between sessions.

If clips are used anyway, the fuse still goes within inches of the + clip, and RQ-6 is not met.

### 6.4 Conductors

- **External lead and pigtails:** 16 AWG, 4.016 mΩ/ft [S, standard AWG table, 20 °C].
- **Internal power path** (W2, W7–W10): 18 AWG, short runs.
- **Voltage drop** between VBUS and the pack terminals: I × R_series, where R_series = shunt (15 mΩ [S, Adafruit #5832]) + fuse + both lead conductors + contacts. Measure it once per lead set at commissioning (T10), and have the firmware report V_batt = VBUS − I × R_series [D]. Worked example, lead alone: 5 ft each way of 16 AWG = 40 mΩ [D: 10 ft × 4.016 mΩ/ft] → 146 mV at 3.64 A [D]. The drop falls toward zero as the current tapers, which is where termination decisions are made.

---

## 7. Board configuration — deltas from the bank-monitor build

Board pin map below is from `Battery_Bank-Monitor-THT-V2 - Rev_1.kicad_pcb`. It was cross-checked against the **fabricated copper**: the Gerber F_Cu X2 net attributes (exported 2026-06-25) give the same net on every pin used here, 62 attributed pads, none ambiguous [M, 2026-09-21]. The `.kicad_pcb` was saved after the Gerbers (06-26 22:03), so the Gerbers, not the board file, are the authority for what was built.

| Item | Bank-monitor build | **Charger build** | Why |
|---|---|---|---|
| INA228 onboard 15 mΩ shunt | removed | **KEEP** | It is the charger's shunt. At 3.64 A: 55 mV [D], inside the ±163.84 mV range [D: 312.5 nV × 2¹⁹, from `battery-bank-monitor.yaml`]; the board is sold for up to 10 A [S, Adafruit #5832 page] |
| Breakout VBUS jumper | open | **CLOSED** (VBUS = VIN+) | High-side use [S, Adafruit #5832 page]. U2 pin 5 (VBUS) is a carrier no-connect [M, Gerber net attribute N/C], so the closed jumper reaches nothing on the board |
| VBUS lead to busbar | fitted | **none** | VBUS comes from the jumper |
| **R3** (10 kΩ, GPIO4_BTN ↔ +3V3) | fitted | **DO NOT FIT — mandatory** | GPIO4 powers up high-impedance with no internal pull (reset state "1") and is not in the power-up glitch table [S, ESP32-C3 datasheet pp.20–21]. With R3 fitted, ON sits at 3.3 V through every boot, watchdog reset and flash, so **the charger turns on whenever the ESP32 is not running** |
| J2 (GPIO4_BTN / GND) | wake button | **#2815 ON control** (§7.2) | The only broken-out spare pin |
| TB1 feed | positive busbar | **PSU +V, upstream of the #2815** | Board alive whenever AC is on; zero battery drain when AC is off |
| TB2 (DS18B20) | battery case | battery case (**REQUIRED**) | RQ-9: charge only above 32 °F. No sensor reading, no charge (FW-3, FW-4) |
| J1 (OLED) | fitted | optional | The wake button is gone; if fitted, show status during a session |
| ALERT (GPIO5, test point "ALERT") | alert input | alert input **+ optional Schottky to ON** (L4) | Firmware-independent over-voltage cutoff |
| F1 (1 A slow-blow, BATT_RAW → V_FUSED), U3 D24V7F3 | as built | unchanged | D24V7F3 takes 4–36 V [`wiring-summary` §3.1], which covers the PSU's 22.5 V OVP ceiling [S] |

### 7.1 XIAO pin map (charger)

| XIAO | GPIO | Net | Charger function |
|---|---|---|---|
| D2 | GPIO4 | GPIO4_BTN → J2-1 | **Charge enable** output, active-high. Boot-safe only with R3 not fitted |
| D3 | GPIO5 | ALERT | INA228 ALERT input (latched, active-low) |
| SDA/SCL | GPIO6/7 | SDA/SCL | INA228 (+ OLED) |
| D10 | GPIO10 | GPIO10_DQ | DS18B20 |
| D7 | GPIO20 | GPIO20LED | Status LED |

### 7.2 Switch control net (off-board, at the #2815)

| Ref | Part | Connects | Purpose |
|---|---|---|---|
| Rs | 1 kΩ ¼ W | J2-1 → ON node | Lets ALERT (L4) overpower a high GPIO |
| Rpd | 10 kΩ ¼ W | ON node → GND | Holds ON low with the GPIO high-impedance. The GPIO high gives 3.0 V [D: 3.3 × 10/11], above #2815's ~1 V threshold [S, Pololu #2815 page] |
| Dx (optional) | THT Schottky | anode → ON node, cathode → board ALERT test point | L4. ALERT low clamps ON to Vf + ALERT V_OL; that must stay below ~1 V [I — proven only by test T5] |
| — | J2-2 GND → #2815 GND | reference | |

The **#2815 slide switch must be locked in OFF**: external ON control works only with the slide OFF [S, Pololu #2814 page, same family; confirm on the #2815 at T1]. Glue or lacquer it.

---

## 8. Protection ladder

| Layer | What stops the charge | Catches | Does not catch | Proven by |
|---|---|---|---|---|
| L1 | Firmware normal end (taper / time at voltage, §9) | normal completion | everything below | T11 |
| L2 | Firmware hard stops: V ceiling, I_max, T_max, temperature, sensor loss, BMS-trip signature | PSU regulation fault, wrong profile, sensor faults | firmware logic error, hang | T4, T6–T8 |
| L3 | ESP32 watchdog reset → GPIO4 high-impedance → Rpd → OFF | CPU hang | logic error that keeps the loop alive | T3 |
| L4 (opt.) | INA228 BOVL comparator → ALERT → Dx → ON low | firmware logic error on over-voltage | #2815 failed short; INA228 unpowered (the ESP32 is then down too → L3) | T5 |
| L5 | `restore_mode: ALWAYS_OFF`, and the profile resets to P1 at boot | auto-resume after a blip or reboot | — | T9 |
| L6 | AC **countdown timer** (standalone, no network) | everything electronic, **including a #2815 failed short** | nothing inside its time | T12 |
| L7 | The pack's own BMS (OVP/OCP) | last resort | — | not tested (inside the pack) |
| L8 | Battery-end fuse (§6) | battery-fed faults in the lead or enclosure | over-charge (a fuse is not a limiter) | continuity only |

Pololu's own caveat: *"Do not use this switch as an emergency cutoff or similar safety disconnect in applications where failure to cut power could lead to injury or property damage."* [S, Pololu #2814 page, same family]. MOSFETs usually fail shorted. **The #2815 is the operational stop; L6 and L7 are the safety layers.**

---

## 9. Firmware requirements (new firmware; not written)

This is a new, small configuration, **not** `battery-bank-monitor.yaml`. It is gated by the `esp-firmware-validation` skill (real compile, `src/main.cpp.o` 0 errors), compiled on the Device Builder add-on's ESPHome version.

**States:** IDLE → CHARGING → DONE | FAULT(reason). DONE and FAULT are latched until acknowledged.

| ID | Requirement |
|---|---|
| FW-1 | Enable switch on GPIO4, `restore_mode: ALWAYS_OFF`. Only the state machine drives it |
| FW-2 | Profile select: **P1 = UPS 10 Ah**, **P2 = bank hold**. Resets to **P1** at every boot, so P2 is always a deliberate choice |
| FW-3 | Start preconditions: V_batt (switch open) > 10.0 V (Cyclenbatt BMS UVP [`DIY-LiFePO4-UPS/docs/supplemental-analysis.md`]) and < the profile ceiling; battery-case temperature above 32 °F (RQ-9); no latched fault |
| FW-4 | **Hard stops** (any → switch OFF, FAULT latched): V_batt > profile ceiling; I > I_max (P1: 5.0 A, RQ-1); session time > T_max; temperature ≤ 32 °F, or the DS18B20 missing or NaN; INA228 read failure or NaN on consecutive reads; ALERT asserted |
| FW-5 | **BMS-trip signature:** current falls from charging to ~0 within one sample while V sits at the source voltage → OFF, FAULT "BMS trip", and publish the **last V_batt before the step**. A plain "at voltage and I < tail" rule would read this as "full". This is the first per-cell evidence the sealed pack can give. With a per-cell cutoff V_ovp, a trip at V_batt puts the other three cells at an average of (V_batt − V_ovp)/3 [D]. V_ovp is undocumented for this pack (O7), so the figure stays a formula until it is known |
| FW-6 | **Normal end:** P1: current taper below I_tail, held for a dwell. P2: time at or above V_hold for T_hold. **All four values TBD**, set from the first supervised runs (T11), not chosen in advance |
| FW-7 | **One trimpot serves both packs.** V_SET = **14.40 V**. That is inside the Cyclenbatt's 14.4–14.6 V (RQ-10) and below the bank's measured 14.5842 V LiTime peak. It leaves 200 mV [D: 14.60 − 14.40] to the P1 ceiling and 180 mV [D: 14.58 − 14.40] to the P2 ceiling. Raise it within 14.4–14.5 V only if T11 data give a reason. No switching regulation is needed |
| FW-8 | Sampling ≥ 1 Hz while charging. Termination and stops are local; HA is not in the loop. Decide `api:` / `wifi:` `reboot_timeout` (either choice is safe: a reboot ends the session through FW-1) |
| FW-9 | Publish to HA: VBUS, V_batt (compensated), I, P, Ah this session, state, fault reason, V_before_trip, profile. Controls: Start/Stop, profile select, fault acknowledge |
| FW-10 | INA228 at boot: shunt 0.015 Ω; ADC range ±163.84 mV; BOVL written at the P2 ceiling + margin (L4); ALERT latched |

**Profile ceilings:**

- **P2 (bank):** at most 14.58 V, the LiTime's measured peak [M, 14.5842 V, report §3], and below the bank's 14.80 V BOVL [S, `battery-bank-monitor.yaml`]. Balancing appeared above 14.4 V [report §3]; the hold runs at V_SET (FW-7).
- **P1 (UPS):** **14.60 V**, the top of the label's charge-voltage range [owner, 2026-09-21] (RQ-10).

---

## 10. Procedures

### 10.1 Every session

1. Countdown timer OFF (AC dead). Mate the pigtail connector.
2. Set the timer to the profile's T_max plus a margin, and switch on. The board boots with the switch **OFF**.
3. In HA or on the ESPHome web page: select the profile, check the OCV reading, press Start.
4. The session ends by itself (DONE or FAULT). Then set the timer OFF and unmate.

### 10.2 UPS pack (P1) — off the bus only (RQ-7)

- Remove the pack with **OP-1**: battery last-off, first-on; EN jumpered low across any battery connection [`DIY-LiFePO4-UPS/UPS-Monitor/boost-subsystem-design.md` §9]. The host has no backup while the pack is out, so keep sessions short.
- **Before reconnecting**, read the pack's rest voltage. A freshly topped pack rests above the 13.3 V float [I]. Bleed it to ≤ 13.3 V so the bus stays inside the XB7's validated envelope. Falsifier: the UPS INA260 bus reading right after reconnection.
- Charge only above 32 °F (RQ-9), with the DS18B20 taped to the pack case. FW-3 and FW-4 enforce it.
- **Success measure:** the matched-load LVD-to-LVD capacity test, before and after (UPS Open Item 14a). Nothing else in this design shows whether the top-off helped.

### 10.3 Bank (P2)

- Run the LiTime to termination first. Then mate the bank pigtail and start P2. Do not use this charger for bulk: from 100 Ah down it could take up to 42 h [D: 100 Ah ÷ 2.39 A, the overload band's low end].
- The bank monitor sees this current (RQ-8) and fires its full-charge anchor when the hold ends (V ≥ 14.20 V, then charging releases [`battery-bank-monitor.yaml`]). The 08-26 report orders its ledger fix (§6.5 step 1) **before** the next anchor, so confirm that is done first. The tail of a hold may sit under that monitor's ±50 mA deadband.
- Whether the hold balances cells inside the five drop-ins **cannot be verified** from the bus. That is the study's standing caveat.

---

## 11. Commissioning tests — both directions (R2 / R7)

Run T1–T9 on a **resistive load, no battery** (for example 5 Ω, ≥ 50 W → about 2.9 A at 14.4 V [D]). Each fault test must **fire**, and the clean run must stay **silent**.

| # | Inject | Must | Silent direction |
|---|---|---|---|
| T0 | — | V_SET measured at the PSU terminals, output open; trimpot lacquered | — |
| T1 | Power up with the XIAO **removed** from its socket | Load current 0; ON < 1 V | — |
| T2 | Hold RESET; reflash OTA; power-cycle | ON < 1 V throughout (scope the ON node) | Commanded ON conducts |
| T3 | Test build: infinite loop in a lambda while charging | Watchdog reset → OFF | Normal build runs a full session |
| T4 | Test build: P-ceiling below V_SET | OFF, FAULT "over-voltage" | Ceiling above V_SET: no trip |
| T5 (if L4) | Test build that ignores ALERT and holds GPIO4 high; BOVL below V_SET | OFF through Dx alone | BOVL above V_SET: stays on |
| T6 | Test build: I_max below the load current | OFF, FAULT "over-current" | — |
| T7 | Unplug the INA228 I²C mid-session | OFF, FAULT "sensor" | — |
| T8 | Test build: T_max = 1 min | OFF at 1 min | — |
| T9 | Pull AC mid-session, then restore | Stays OFF; profile back to P1 | — |
| T10 | On the battery, at a steady known current | DMM at the pack terminals vs VBUS → **R_series** | — |
| T11 | First **supervised** session on each pack | Record the taper; set FW-6 values from the data | — |
| T12 | Let the countdown timer expire mid-session | Everything dark | — |
| T13 | Unplug the DS18B20 mid-session; then a test build with the 32 °F floor set above room temperature | OFF, FAULT "temperature" both times; Start refused | Normal floor, sensor fitted: no trip |

Any firmware edit re-runs T1–T9 and T13 (R7: a gate untested against a known-bad input is not a gate).

---

## 12. Open items

| # | Item | Status |
|---|---|---|
| Q1 | Cyclenbatt label: charge voltage, charge temperature range, and does the BMS balance (above what voltage)? | **Answered 2026-09-21:** 14.4–14.6 V; charge above 32 °F; no balance details. Balancing stays unknown, and §10.2's capacity test is the measure |
| O1 | Charge current limit, 10 Ah | **Closed:** 0.5 C = 5.0 A, owner 2026-09-21 |
| O2 | Confirm ATC-5 (1 kA at 32 VDC) and KLKD005 (50 kA DC) against their datasheets | [I] until read — before purchase |
| O3 | Confirm HDR-30 overload behaviour below 50% Vout (hiccup) | The HDR-60 datasheet says hiccup [S, HDR-60-SPEC p.2]; the HDR-30 text extraction did not preserve that line |
| O4 | Charger firmware | Not written; FW-1…FW-10 are the spec |
| O5 | FW-6 values (I_tail, dwell, V_hold, T_hold) and T_max per profile | Set from T11 data |
| O6 | Enclosure, venting, DIN rail, strain reliefs | Not specified beyond "ABS, vented" (the XIAO's U.FL antenna needs an RF-transparent box [`wiring-summary` §8.2, item J]) |
| O7 | `DIY-LiFePO4-UPS/docs/component-selection.md` gives 14.4–14.6 V as the BMS **over-voltage cutoff**. The label gives that range as the **charge voltage**, so the BMS cutoff value is undocumented [I: a maker would not rate charging at its own cutoff] | Correct that doc; this one no longer relies on it |

---

## 13. Purchase list (everything else is on hand)

| Item | Note |
|---|---|
| Mean Well **HDR-30-15** | §4 |
| Pololu **#2815** Big MOSFET Slide Switch, HP | 4.5–40 V, 16 A, 8.6 mΩ max at 10 V [S, Pololu #2815 page] |
| ABS enclosure, vented; DIN rail offcut | |
| Keyed connector pairs (XT60 or equivalent) × 3 | charger lead + two pigtails |
| ATC-5 + inline blade holder | 10 Ah pigtail |
| KLKD005 + inline 10×38 holder | bank pigtail |
| 16 AWG red/black; 6.3 mm insulated female QDs; ring lugs for the busbar studs | |
| Plug-in countdown timer (mechanical or standalone digital, **no Wi-Fi**) | L6 |
| 1 kΩ, 10 kΩ, THT Schottky | §7.2 (possibly on hand) |

**On hand:** a V2 Rev 1.1 board and parts, XIAO ESP32-C3, Adafruit INA228, D24V7F3, DS18B20, and the spare Pololu #5382 (bought as a pair, one used [`DIY-LiFePO4-UPS/docs/bom.md`]).

---

## 14. Sources

- Mean Well HDR-30-SPEC and HDR-60-SPEC, both "File Name … 2026-04-03", p.2 (spec table), p.4 (terminals — use the unit's silk for pin numbers).
- Pololu product pages #2815 and #2814 (Big MOSFET Slide Switch with Reverse Voltage Protection, HP / MP), and #5382 (ideal diode, LM74700-Q1), read 2026-09-21.
- Adafruit #5832 product page (INA228 breakout: 15 mΩ shunt, up to 10 A, VBUS jumper), read 2026-09-21.
- Espressif ESP32-C3 Series Datasheet (copy in `DIY-LiFePO4-UPS/UPS-Monitor/esp32-c3_datasheet.pdf`), pp.20–21: IO MUX reset states and power-up glitch table.
- Eaton Bussmann Technical Data 2009 (ATC); Littelfuse KLKD datasheet — neither retrievable 2026-09-21; figures from distributor listings, carried as [I] (O2).
- House: `DIY-LiFePO4-UPS` (09-15 survival-test README, component-selection.md, boost-subsystem-design.md, bom.md, supplemental-analysis.md); this repo (`README.md`, `reports/LiFePO4_Report_2026-08-26.md`, `INA228 Monitor/`).
