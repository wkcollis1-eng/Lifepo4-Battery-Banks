# Battery_Bank-Monitor-THT-V2 Rev 2: fixing the INA228 current-channel noise (design note)

**Status.** Draft, pre-fabrication. Reviewed against the Rev 2 KiCad file
of 2026-10-01 (the 11:19 save). The first review, of the 2026-09-28 file, is
kept where its figures differ, marked "09-28". Nothing here is built or
measured on Rev 2 yet.

**Problem it fixes.** On the built board (V2 Rev 1.1), the INA228 current
reading carries interference from the on-board 3.3 V buck regulator. The
interference adds per-conversion noise about 9× the chip's own floor, and
it moves the zero reading by 1–3 mA whenever wiring or equipment is moved.

**Companion documents.**

- `battery-bank-monitor-wiring-summary-v1_10.md`: the Rev 1.1 board,
  wiring and BOM. §4.6 has a pin-map error that this note corrects (§5.5).
- `docs/soc-noise-deep-dive.md`: the noise investigation and the
  2026-09-25 diag2 test results this design rests on.

**Evidence tags:** [M] measured, [D] derived, [S] source or datasheet,
[I] inference, [P] photo, [K] parsed from the KiCad board files.

---

## 0. Summary

| | |
|---|---|
| **Symptom** | Excess noise and a moving zero on the INA228 current channel. The noise grows as the 3.3 V load falls. |
| **Leading cause** | The Pololu D24V7F3 buck (U3), which runs in a light-load mode at the monitor's ~25 mA. Its switching sits near the INA228's 1 MHz sampling clock. |
| **Rev 1.1 layout** | The INA228 breakout sits 3.8 mm from the buck. The shunt sense leads land on the breakout's own terminal block, about 1 cm from the buck's inductor, and fan out untwisted. There is no input filter. |
| **Rev 2 fix** | Move the INA228 to the far end of the board. Bring the sense lines in at a new edge terminal block (TB3) as a routed pair. Add TI's input RC filter. Add a ceramic capacitor at the buck input. |
| **Expected result** | Magnetic pickup largely removed (~131× less stray field at the sense path [I]; ~46× on the 09-28 layout). Anything left, from any path, attenuated 42 dB at 1 MHz by the filter [D]. |
| **Not fixed** | The INA228's own offset (±1 µV, ±2.67 mA [S]). The external shunt run was listed here too. It is already a twisted pair, and with it in place §8.1 found the 2-s scatter at the quantization floor. |
| **Status** | On the 2026-10-01 layout, §7 has four items still open before fabrication: two value fields, the mechanical checks (including C7's height under U2), refilling zones before the Gerbers, and a board-size typo on the back silk. The §8.1 tests ran on the Rev 1.1 board on 2026-09-28. The pickup entered at the untwisted fan-out beside U3 (path 1), and twisting it there took the 2-s scatter to the floor. The twist also moved the idle zero by about 10 mA, which is unexplained (§8.1). |

---

## 1. The problem on Rev 1.1

### 1.1 Symptoms

All figures come from `docs/soc-noise-deep-dive.md` (§3.1, §3.5, §10.2).

- **Per-conversion noise** in the quiet state is σ ≈ 18.7 mA, against about
  2 mA for the INA228 alone [D, from the ENERGY register rate].
  - The idle ENERGY noise gauge reads 0.231 W. A clean chip at this drain
    would read about 0.14 W [D: 13.30 V × 10.5 mA].
- **The zero steps by 1–3 mA** at physical events: rewiring, moving the
  monitor, moving the router [M].
  - That is 0.4–1.1 µV at the shunt. The INA228's drift spec is
    ±10 nV/°C [S], so a step this large comes from outside the chip.
  - As a SOC error: 1 mA × 720 h = 0.72 Ah/month, or 0.18 %/month of
    397 Ah [D]. So a 1–3 mA step costs 0.18–0.54 %/month.
- **Firmware already did what it could.** V1.28 set 11 dBm TX power and the
  0xFDC5 ADC timing. The unlit 2-s sd fell to the lit-OLED floor, about
  1.8 mA [M]. The remaining per-conversion error is the hardware part.

### 1.2 What the tests established (diag2, 2026-09-25)

| Condition | 2-s sd ratio vs baseline | 3.3 V load |
|---|---|---|
| Panel on, all-black frame | 1.05 (no change) | +~0 |
| Text page lit | 0.50 | + some pixel current |
| All-white frame | 0.36 | + full pixel current |
| 1 ms CPU loop | 1.24 (worse) | burstier |
| Wi-Fi radio off | 1.67 (worse); ENERGY ×2.08 | lighter |

[M, deep-dive §10.2]

- **The load level drives it, not the panel state.** More steady load means
  less noise; lighter or burstier load means more.
- **Why that points at the buck.** Pololu says the D24V7F3 switches at a
  fixed 1.1 MHz at normal loads and lowers its frequency at light loads
  [S: Pololu]. The monitor's ~25 mA is light load for a 600 mA regulator.
- **Why the INA228 is vulnerable.** Its sampling runs from a 1 MHz clock
  [S: SLYS021A §6.5, FOSC]. TI warns that transients "at or very close to the
  sampling rate harmonics" cause problems, and recommends an input filter
  [S: §8.1.4].
- **Supply rejection is ruled out.** The INA228's shunt offset shifts at
  most ±0.5 µV per volt of supply [S: §6.5]. Producing the 7.0 µV residual
  (18.7 mA × 375 µΩ) that way would need 7.0 / 0.5 = 14 V of 3.3 V rail
  ripple [D]. So adding supply capacitance is not the fix.

### 1.3 The Rev 1.1 geometry

- **Stacking.** The INA228 breakout (U2) sits directly above C1 and the
  buck (U3) [P].
- **Sense-lead entry.** The breakout's VIN+/VBUS/VIN− terminal block faces
  U3, about 1 cm from its 22 µH inductor (marked "220") [P].
- **Lead dress.** The sense wires leave the terminal block untwisted and run
  past U3 and C4 [P]. The OLED harness also crosses the area [P].
- **Parsed from the board file.** The breakout outline ends 3.8 mm above the
  Pololu outline. The two are 18.5 mm centre to centre [K].
- **No input filter**, and no ceramic capacitor at the buck input; only C5
  (0.1 µF) plus the C4 electrolytic 5.6 mm away [K].

---

## 2. How the interference reaches the reading

Three paths are possible. **Path 1 dominated on Rev 1.1** [M, 2026-09-28,
§8.1]. Twisting the fan-out and moving it about 6.4 mm off U3 took the 2-s
scatter from 1.29 mA to 0.32 mA, against a 0.22 mA quantization floor. Paths
2 and 3 were not separated; between them they leave only the remainder above
that floor.

| # | Path | Mechanism | Rev 2 response |
|---|---|---|---|
| 1 | **Into the sense leads** | The buck's magnetic field induces a voltage in the loop that the untwisted VIN+/VIN− fan-out forms beside U3 | Removed by distance plus a tight routed pair; the filter then attenuates any residual |
| 2 | **Onto the breakout itself** | The same field couples into the breakout's short input traces and the chip | Removed by distance (35.3 mm body gap; 29.3 mm on 09-28) |
| 3 | **Through the shunt** | The board's return current runs through the shunt in the low-side topology, so the buck's high-frequency ripple is a real voltage across the shunt | Only the RC filter (−42 dB at 1 MHz) and C6 reach it; routing cannot |

---

## 3. Design changes, Rev 1.1 → Rev 2

| Change | Rev 1.1 | Rev 2 | Purpose |
|---|---|---|---|
| INA228 socket (U2) | (32.08, 31.00), rotated −90° | (40.50, 26.83), top-right, rotated 180°; header pins along x = 39.5 (09-28: (27.50, 8.67), top edge) | Distance from the buck (paths 1 and 2) |
| Sense entry | Breakout's own terminal block, facing U3 | **TB3**, 3-pin 3.81 mm side-entry block (footprint Phoenix MKDS 1/3-3.81), top-left corner (18.0, 7.5–15.1): pin 1 VIN+RAW, 2 VIN−RAW, 3 VBus. (09-28: Phoenix PT 1.5/3-3.5-H at (5.0, 7.5–14.5), pin 1 VBus, 2 VIN−, 3 VIN+.) | Keeps the external leads away from U3 and the other harnesses |
| Sense routing | Loose wires | On-board traces to U2 header pins 5–7 | Small, fixed loop over the ground plane |
| Input filter | None | R5, R6 (10 Ω), C7 (1 µF), §4. (C8, C9, R7 and C10 were removed on 2026-10-01; §4.1) | Attenuates all paths, including path 3 |
| Zero-test jumper (JP) | None | 2-pin 2.54 mm header across U2 pins 7 and 6, at (43.9, 11.5–14.04), right edge | In-place zero of the INA228 (§7.1) |
| Buck input ceramic | None (C5 0.1 µF only) | **C6, 10 µF X7R**, 7.5 mm from the U3 VIN pin | Keeps switching current local instead of flowing through the TB1 leads and the shunt |
| Wake button (J2, R3) | GPIO4 button | Removed | Matches firmware V1.29 (VEML7700 light wake) |
| J1 (OLED / VEML7700) | Right edge | (43.9, 27.0), right edge, beside U2 (09-28: (21.0, 9.0), top edge) | Board re-flow |
| Mounting holes | H1–H4 | H2–H4 (TB3 occupies the H1 corner) | See §7 item 6 |

All positions are in mm, from the KiCad files [K].

---

## 4. Input filter

### 4.1 Circuit (TI SLYS021A §8.1.4, Fig. 8-1)

```
TB3.1  VIN+RAW ── R5 10 Ω ──┬──────────┬──── U2.7  VIN+
                            │          │
                         C7 1 µF      JP   zero jumper, open in service (§7.1)
                            │          │
TB3.2  VIN−RAW ── R6 10 Ω ──┴──────────┴──── U2.6  VIN−

TB3.3  VBus ───────────────────────────────── U2.5  VBUS   (fused 100–250 mA at the busbar)
```

- **The capacitor goes across the pair only.** Capacitors from each input
  to ground are left out on purpose: any mismatch between them would turn
  common-mode noise into a differential error.
- **Order along the path:** resistors, then C7, then the pins. JP reaches
  U2 pins 7 and 6 by its own stubs, on the chip side of C7 (§5.2).

**Removed on 2026-10-01.** The 09-28 design had C8 (100 pF C0G) across the
pair beside C7. The 2026-09-30 board then carried C8 and C9 (10 nF C0G,
each input to GND) and a VBUS RC (R7 100 Ω, C10 0.1 µF). All four came out
after review:

- C8 and C9 to GND are the input-to-ground capacitors the first bullet
  above rules out.
- R7 in series with VBUS's 0.8–1.2 MΩ input impedance [S: SLYS021A §6.5]
  reads 83–125 ppm low, 1.1–1.7 mV at 13.3 V [D: 100 Ω / 1.2 MΩ and
  100 Ω / 0.8 MΩ].
- TI's Fig. 8-1 has one differential capacitor and no VBUS filter [S].
- With the fan-out twisted, the unfiltered Rev 1.1 board already reads
  0.23–0.32 mA of 2-s scatter against the 0.22 mA quantization floor
  (§8.1) [M]. There is little left for extra filtering to remove.

### 4.2 Parts

| Ref | Part | Decoded | Status |
|---|---|---|---|
| R5, R6 | Stackpole **RNMF14FTC10R0** | 10.0 Ω ±1%, ¼ W metal film, 50 ppm/°C; body 3.30 ± 0.30 × 1.78 ± 0.08 mm; 0.44 ± 0.05 mm leads; fits the DIN0204 5.08 mm footprint, with 0.74–1.04 mm from body to bend [D] | Bill's choice, 2026-10-01; confirmed from the datasheet [S: Stackpole RNF/RNMF, rev 2011-10-14, p.2–3]. Replaces the 09-28 pick, YAGEO CFR-25JT-52-10R (5% carbon film, DIN0207) |
| C7 | TDK **FK14X7R1H105K**(R020), the 09-28 pick | 1 µF ±10%, 50 V, X7R, dipped radial, 2.5 mm lead spacing; footprint C_Disc_D5.0mm_W2.5mm_P2.50mm [K] | Value, voltage and dielectric confirmed [S]. **No MPN in the 2026-09-30 BOM.** Body size, seated height (under 8 mm, §7.6) and the R020 suffix not yet confirmed |
| JP | 2-pin 2.54 mm header plus a shunt | PinHeader_1x02_P2.54mm_Vertical [K] | No MPN chosen |

### 4.3 Numbers

| Quantity | Calculation | Result |
|---|---|---|
| Corner frequency | 1 / (2π × 20 Ω × 1 µF) | **7.96 kHz** |
| Attenuation at 1 MHz | 20·log₁₀(1 MHz / 7.96 kHz) | **42 dB** |
| Gain error | 20 Ω / (92 kΩ + 20 Ω), with 92 kΩ the INA228 input impedance [S] | 0.022% |
| Gain drift from R5/R6 | 50 ppm/°C [S] × 20 Ω × 10 °C / 92 kΩ | 1.1 × 10⁻⁷ of reading per 10 °C; negligible |
| Worst bias-current offset | 2.5 nA [S] × 10.5 Ω | 26 nV = 0.07 mA at 375 µΩ |
| Resistor thermal noise | √(4kT × 10 Ω) | 0.41 nV/√Hz each |
| Filter time constant | 20 Ω × 1 µF | 20 µs, against 4.12 ms conversions; no effect on readings or ALERT |
| C7 leakage | Assumed ≥ 100 MΩ (not from TDK): 75 mV / 100 MΩ × 20 Ω | ≤ 15 nV = 0.04 mA |
| C7 self-resonance | Assumed ~3 nH of lead inductance: 1 / (2π√(3 nH × 1 µF)) | ~2.9 MHz [I] |
| Above C7's self-resonance | Its ~3 nH acts against the 20 Ω: 2πf × 3 nH | ~−21 dB at 100 MHz, ~−1 dB at 2.4 GHz [I]. The 09-28 design's C8 (100 pF, ~290 MHz) covered this; it was removed (§4.1) |
| Sense-trace resistance | 1 oz copper assumed, all 0.25 mm; TB3 → U2, JP stubs excluded: VIN+ 17.6 mm, VIN− 17.0 mm [K] | 35 mΩ (VIN− 33 mΩ); error 0.82 µA × 0.1 Ω = 82 pV. 09-28: 48 and 53 mΩ |

**Why X7R is fine for C7.** The voltage across it is at most 75 mV, so
X7R's capacitance loss under DC bias and its microphonic effect do not
apply. Its ±15% temperature change only moves the corner frequency.

**No RF capacitor now.** C8 covered RF, including 2.4 GHz, as insurance.
Without it the filter is weak at RF (table above). Antenna pickup is not the
main path (deep-dive §10.3), and Rev 1.1, which has no filter at all,
reached the 2-s floor once its fan-out was twisted (§8.1).

**Thermocouple voltages.** R5 and R6 sit in the DC path, and 1 µV at the
inputs reads as 2.67 mA. They are placed 2.5 mm apart in the same
orientation, so any junction voltages match and cancel [K]. C7 carries no
DC, so its lead material does not matter (09-28: 3 mm apart; C8's
steel-core leads were in the same position).

**Trace width.** Widening the sense or I²C traces changes nothing
measurable. The resistance and capacitance figures above set the scale.
Pickup is set by loop area and spacing, not width.

---

## 5. Layout review of Rev 2 (KiCad file, 2026-10-01 11:19 save)

The 09-28 file's figures are kept in their own column or in brackets.

### 5.1 Distance from the buck

| | Rev 1.1 | Rev 2, 09-28 | Rev 2, 10-01 |
|---|---|---|---|
| Breakout body to Pololu body | 3.8 mm [K] | 29.3 mm [K] | **35.3 mm** [K] |
| Breakout centre to Pololu centre | 18.5 mm [K] | 48.0 mm [K] | 55.5 mm [K] |
| Sense entry to Pololu | ~10 mm, terminal block to inductor [P] | 43.8 mm [K] | 49.9 mm, TB3 courtyard to Pololu outline [K] |
| Nearest sense copper to Pololu outline | Loose wires past U3 [P] | 35.8 mm (U2 pin 7) [K] | 50.8 mm (U2 pin 6, pad edge) [K] |

- **Field estimate.** A small inductor's stray field falls roughly as
  1/r³. (50.8 / 10)³ ≈ 131×, about 42 dB less at the nearest sense copper
  [I]. On 09-28 it was (35.8 / 10)³ ≈ 46×, about 33 dB.
- **How much to trust it.** The 1/r³ rule is rough at 10 mm. The Rev 2
  distance is measured to the Pololu outline, so the true distance to its
  inductor is somewhat larger. Whether the Pololu's inductor is shielded is
  unknown.

### 5.2 Loops

- **After the filter** (C7 to U2 pins 6 and 7): about 3 mm of trace,
  enclosing **8.8 mm²** [K] (09-28: 8.5 mm², from C8).
- **JP's stubs** run 4.3 mm from JP to the same two pins on their own
  tracks [K]. JP is open in service, so they close no loop.
- **Before the filter** (TB3 → R5/R6 → C7): **49.4 mm²** [K] (09-28:
  69.5 mm²). This loop sits ahead of the filter, which attenuates what it
  picks up (§7.5).
- **Why loop area matters little here.** The pickup is an AC voltage, and the
  INA228 averages 256 conversions of 4.12 ms per reading, so its mean
  cancels; above 7.96 kHz the filter takes it down as well. The external
  shunt leads enclose far more area than either loop on the board [I].

### 5.3 Coupling to other nets

Nearest approach of each net, centre to centre. No signal net runs within
1.5 mm of either section. The GND stitching vias come within 1.20 mm of the
filtered section; GND is the reference, so that does not count as coupling
[K].

| Net | To the unfiltered section | To the filtered section | 09-28 (unfiltered / filtered) |
|---|---|---|---|
| SDA | 9.26 mm | 5.08 mm (socket pins) | > 4 / 1.82 mm |
| VBus | 2.67 mm | 2.54 mm | 2.47 / 2.55 mm |
| ALERT | **1.88 mm** | 2.45 mm | > 4 / 2.54 mm |
| LED | > 6 mm | > 6 mm | > 4 / 3.65 mm |

- **ALERT now passes 1.88 mm from TB3 pin 1 (VIN+RAW).** It runs along the
  top edge at y = 5.6 and down the left edge behind TB3 [K]. It is not a
  concern:
  - The V1.29 firmware sets DIAG_ALRT to 0xA000, so ALERT is a latched
    fault line. Conversion-ready is not enabled, so ALERT does not toggle
    in service [S: `battery-bank-monitor.yaml`].
  - The unfiltered section is driven from the 375 µΩ shunt through the
    leads, and the RC filter follows it.
- An earlier Rev 2 draft ran SDA 0.88 mm and VBus 0.42 mm from the pair for
  16–25 mm. The 09-28 version fixed that, and the 10-01 version keeps it
  fixed.

### 5.4 Ground plane and power paths

- **Ground.** Both layers carry a GND fill. Fifteen GND vias stitch the
  sense area, some between VIN+ and VIN−. In the saved fill, the
  bottom-layer ground is unbroken under the sense traces except for the
  clearance cut-outs around the through-hole pads. Nothing is routed on the
  bottom layer [K]. Refill the zones before the Gerbers anyway (§7.7).
- **3.3 V to the XIAO.** The run from U3 through C1 and C3 is 1.5 mm wide
  and 64.1 mm long, so 21 mΩ with 1 oz copper. A 300 mA Wi-Fi transmit peak
  dips it by 6.3 mV [D] (09-28: about 52 mm, 17 mΩ, 5 mV).

### 5.5 Pin map: correction to the wiring summary

- **The actual header order** on the Adafruit INA228 (5832), from Adafruit's
  silkscreen photo [S]: VIN, GND, SCL, SDA, **VBUS, VIN−, VIN+**, ALRT.
- **Rev 2 is correct:** U2 pin 5 = VBus, pin 6 = VIN−, pin 7 = VIN+ [K].
- **The wiring summary is wrong.** Its §4.6 says pin 6 = VIN+ and
  pin 7 = VIN−. That never mattered on Rev 1.1, where pins 5–7 are not
  connected. It needs correcting (§9).
- **The breakout ships with its own terminal block soldered on**
  [S: Adafruit]. It stays connected to the same nets. Leave it empty.

---

## 6. What Rev 2 does not fix

- **The external shunt leads.** The 20 cm or so of lead from the shunt to TB3
  is already a twisted pair [Bill, 2026-09-28]. Keep it routed away from the
  200 A cables and the J1 harness. On Rev 1.1, with the in-enclosure end
  twisted, it added nothing measurable above the 2-s floor (§8.1).
- **The INA228's own offset**, ±1 µV max, which is ±2.67 mA [S]. §7.1 adds a
  way to measure it in place.
- **Ripple through the shunt is attenuated, not removed.** The filter takes
  it down 42 dB at 1 MHz and C6 reduces it at the source.
- **SOC math is unchanged.** The CHARGE register already integrates
  zero-mean noise to zero. What Rev 2 improves is the DC part (the 1–3 mA
  zero steps), the 2-s current readout, and the ENERGY register.

---

## 7. Open items before fabrication

In priority order. Status as of the 2026-10-01 11:19 save [K].

1. **Zero-test jumper: done, as JP** (the 09-28 note called it J3). It is
   a 2-pin 2.54 mm header at (43.9, 11.5) and (43.9, 14.04), on the right
   edge, outside U2's outline. Its own stubs go to U2 pins 7 and 6, on the
   chip side of C7.
   - Fitting a jumper shorts the INA228's filtered inputs, which gives its
     real zero in place, at any time, without touching field wiring. This
     is the P-2a measurement, and the input for `soc_offset_ma`.
   - It is safe with the shunt connected: at most 75 mV / 20 Ω = 3.75 mA
     flows through R5/R6, which is 0.28 mW.
   - JP's pad 1 is round where the library footprint's is square. That is
     the one library-mismatch warning left in DRC, and it is harmless.
2. **C6 at 50 V: done** ("CAP CER 10UF 50V X7R RADIAL"). V_FUSED reaches
   14.6 V, no surge suppressor is fitted (wiring summary item G), and X7R
   loses capacitance under DC bias.
3. **Value fields: open for two parts.** R5, R6, C7, C6 and TB3 now carry
   part descriptions. JP and J1 still show the footprint name. Set them so
   the BOM exports correctly (the same hygiene as wiring-summary item L).
   The 2026-09-30 BOM export is stale: it has no MPN for R5, R6, C7 or TB3,
   and no JP.
4. **Silkscreen: done, one typo open.**
   - TB3 is labelled VIN+ / VIN− / VBus, top to bottom, matching pins 1–3.
     (A 10:20 save on 2026-10-01 had the labels reversed against the
     copper; the 11:19 save fixed it.)
   - The back silk now reads "Oct, 2026 / OSH PARK - Fabricator", the
     designer and the file name.
   - **Open:** it says "Board Size: 33mm x 75mm". The outline is
     32.0 × 75.0 mm, and the inch figure on the same line (1 1/4 × 2 15/16 in)
     matches 32 mm.
   - Optionally, mark the breakout's own terminal block "do not use".
5. **Unfiltered pair: tightened, 69.5 → 49.4 mm².** Closed; see §5.2 for
   why going further is not worth it.
6. **Mechanical.**
   - U1, U2 and U3 sit on pin headers with 8 mm or more of clearance below
     [Bill, 2026-10-01]. R5, R6 and C7 sit under U2. R5 and R6 lie flat at
     1.78 mm [S]. **C7 has no MPN yet; confirm its seated height is under
     8 mm**, and that its body fits the C_Disc 5.0 mm footprint.
   - Confirm in the 3D viewer that TB3's wire openings face the board edge.
     The same check is open for TB1.
   - Three mounting holes remain (H2–H4). Check the corner doesn't flex when
     TB3's screws are tightened, and that the enclosure still fits.
   - R2 and C3 sit under the XIAO: solder them first and check height
     clearance.
7. **Refill zones, run KiCad's own DRC, then regenerate the Gerbers.** DRC
   on the 11:19 save gives 34 violations, all warnings, 0 errors and 0
   unconnected items [K: kicad-cli 10.0, `--severity-all`]. That is the same
   set as at 10:20; the 2026-09-30 backup had 39.

---

## 8. Verification plan

### 8.1 Before fabrication, on the Rev 1.1 board

These show which path dominates, and so how much of Rev 2's benefit to
expect (deep-dive §3.4, §5.2).

| Test | Action | Reading |
|---|---|---|
| P-2a | Short VIN+ to VIN− at the breakout terminal block | Noise remains → paths 1–2 on the board. Rev 2's distance fixes it. |
| P-2b | Move one sense lead onto the other lead's shunt screw, so both leads see one potential while their loop is kept | Noise remains → pickup in the leads. Rev 2's routing plus twisted leads fix it. Noise gone → path 3; Rev 2's filter and C6 are what help. |
| P-4 | Twist the leads to the terminal; route away from U3/C4 | Previews the routing benefit (but not the distance benefit) |

A wire held across the two shunt screws does not short the shunt. It sits
in parallel with 375 µΩ, which 10 AWG copper matches in about 11 cm [D].
The first P-2b run did that, so it was a null test (deep-dive §7, item 20).
Moving a lead off the shunt floats the INA228 input, and the counters book
false charge for as long as it floats (below).

#### Results on Rev 1.1, 2026-09-28

Firmware V1.28 at 11 dBm, bank idle except during the load check. The
figures are [M] from HA history: the 2-s current, and per-minute rates from
the 60-s `HW Energy` and `HW Net Charge` registers. "2-s scatter" is the sd
of first differences / √2, so slow drift does not count toward it. Its
floor is 0.22 mA [D: 0.763 mA LSB / √12]. Times are EDT.

| window | state | ENERGY | CHARGE | 2-s n | 2-s scatter |
|---|---|---|---|---|---|
| 15:00:33–15:46:33 | baseline | 0.2548 W | −11.87 mA | 1380 | 1.61 mA |
| 15:55:33–16:01:33 | first P-2b: wire held across the shunt screws (null test) | 0.2734 W | +15.17 mA | 180 | 1.51 mA |
| 16:05:33–16:08:33 | P-2a: wire held across VIN+/VIN− at the breakout terminal block | 0.0171 W | −0.80 mA | 90 | 0.82 mA |
| 16:21:33–16:48:33 | baseline 2 | 0.2713 W | −12.75 mA | 810 | 1.81 mA |
| 16:56:33–17:08:33 | P-2b: both leads on one shunt screw | 0.2710 W | −15.52 mA | 360 | 1.45 mA |
| 17:14:01–17:15:33 | leads back on the shunt, fan-out untwisted | — | −5.82 mA (2-s mean) | 46 | 1.29 mA |
| 17:23:33–17:28:33 | P-4: fan-out twisted, ~6.4 mm off U3 | 0.0082 W | −2.34 mA | 150 | 0.23 mA |
| 17:43:33–18:41:33 | P-4, the hour after the load check | 0.0097 W | −2.54 mA | 1740 | 0.32 mA |

What each shows:

- **P-2a.** Shorting at the breakout cut the scatter to 0.82 mA (F = 0.21
  against baseline 2, df 88/808, p = 5e-16) and ENERGY to 0.0171 W. Most
  of the noise enters upstream of the breakout's terminal.
- **P-2b.** With the lead loop kept and the shunt voltage removed, ENERGY
  did not move: 0.2710 against 0.2713 W (Welch t = −0.10, p = 0.92; 12 and
  27 one-minute rates). The per-conversion noise is picked up in the lead
  loop, not carried through the shunt, so path 3 is not the main path.
  - The 2-s scatter did fall, 1.45 against 1.81 mA (F = 0.64, df 358/808,
    p = 2e-6).
  - That fall was not shunt signal: the twisted input, with the shunt in
    circuit, reads 0.32 mA. The new landing changed the loop.
- **P-4.** The external run was already a twisted pair. Bill twisted "the
  last couple inches inside the enclosure" and moved them "about .25 inch
  off of the buck" [Bill].
  - The 2-s scatter fell from 1.29 mA to 0.32 mA (F = 0.061, df 1738/44,
    p = 7e-101). ENERGY fell from 0.2713 W (baseline 2) to 0.0097 W.
  - So the pickup entered in the fan-out beside U3: path 1.
  - VBUS scatter did not change (0.082 against 0.074 mV), so the chip did
    not become quieter in general.
  - It is not the OLED: a lit OLED holds ENERGY near 0.23 W (deep-dive
    §3.1), against 0.0097 W here.
- **Load check: the twisted input reads the full shunt voltage.** An
  inverter and an LED lamp drew −1.052 A from 17:32:24 to 17:41:20.
  - The voltage steps give 2.07 mΩ at switch-on and 2.06 mΩ at switch-off
    [D: ΔV/ΔI]. The commissioning report's apparent Ri is 2.185 and
    1.818 mΩ (F5, n = 2) [M]. An input reading only part of the shunt
    voltage would inflate this figure in proportion.
  - Over four clean load minutes, ENERGY was 14.176/14.179/14.158/14.143 W
    against a 2-s V × |I| of 14.238/14.212/14.191/14.176 W: 0.28 % low
    (paired t = 5.55, df 3, p = 0.012). The shortfall is real; its cause
    is unknown. CHARGE matched the 2-s current to within 0.6 mA.
  - Near zero, ENERGY reads low (deep-dive §3.1 note).

What this does not establish:

- **Twist and distance** were changed together, so their shares are not
  separated.
- **A power cycle** (17:15:35–17:22:33, Bill's, for the wiring work) came
  between the untwisted and twisted windows. The twist is taken as the
  cause [I: falsified if untwisting the fan-out, with nothing else changed,
  does not bring the scatter back].
- **The first five minutes after the twist** read 0.23 mA and the later
  hour 0.32 mA (F = 0.52, df 148/1738, p = 1e-6). Both are near the floor;
  the difference is not explained.
- **The zero-move test** (§8.2 step 4) has not been run on the twisted
  board, so the 1–3 mA zero steps are not shown to be gone.

**The idle zero moved by about 10 mA, and why is unknown.** Before the
twist the idle current read −12.75 mA (baseline 2). After it, it read
−2.54 mA, stable for the hour (six 10-min means from −2.42 to −2.48 mA)
[M]. Twisting wires adds no load. So unless the power cycle changed the
monitor's draw, at least one of the two readings is off by 5.1 mA or more
[D: half of 10.21 mA]. That is outside the INA228's ±2.67 mA offset spec
[S]. Candidates, all [I]:

- rectified pickup biased the untwisted readings;
- re-landing the leads changed a thermal EMF at a terminal;
- B1's bypass reading (deep-dive §10.4, reading ii): if some of the
  monitor's return shares a path with a sense lead, re-landing the leads
  changes the split.

P-1 (a DMM in series with TB1, deep-dive §5.2) decides which reading is
right. Until it is run, the FAQ's 7.4 ± 2.4 mA monitor draw (measured on
the untwisted leads) and the SOC's idle drain both carry this uncertainty.
Each 1 mA is 0.72 Ah/month (§1.1).

**Outcome, 2026-09-28 (late): P-1 is superseded.** Neither reading
contained the monitor. As built, the shunt is in the busbar → inverter
cable and TB1 GND sat on the physical busbar, so the monitor's return
never crossed the shunt (Bill, Q7). The 10.2 mA move is therefore still
unexplained, and it is not the monitor's draw. The third candidate above
(a split of the monitor's return across the shunt) does not apply as
stated, since none of the return crossed it. With TB1 GND moved to the
shunt's inverter-side bolt at 20:33 EDT, the idle current stepped
-22.7 mA [M: Welch on 30-s blocks, p<1e-300]; the monitor draws
22.6 mA with the OLED dark [D]. The zero-move test is now the only open
input to the Rev 2 call below.

**Side effect: false charge from the lead moves.** While a lead was off the
shunt, the counters booked:

- −0.2022 Ah and +4.354 Wh, 16:49:30–16:51;
- −0.5082 Ah and +7.77 Wh, 17:11:33–17:14:33 [D: counter differences].

The −0.71 Ah stays in the SOC until the next Mark-as-Full; it is 0.14 % of
500 Ah [D]. The power cycle was bridged as designed: "counters BRIDGED
from the last saved -6.613 Ah / 602.9 Wh - SOC anchor KEPT" [M:
reset_check].

**For Rev 2.** Its path-1 fix (relocation and a routed pair) is aimed at
the right path. Whether Rev 1.1 with a twisted fan-out already does enough
is Bill's call; the zero-move test and P-1 are its inputs.

### 8.2 After building Rev 2

Firmware V1.29, 11 dBm, bank idle.

1. **Sign check.** A discharge reads negative (Option B). The pin order is
   now right by construction; this confirms it.
2. **Zero, with a jumper fitted on JP.** Record the reading: it is the
   INA228's in-place offset. Use it with the recharge bracket to set
   `soc_offset_ma`.
3. **Noise, with the jumper removed.**

   | Metric | Rev 1.1 (V1.28 / 11 dBm) | Rev 2 target (proposed) |
   |---|---|---|
   | ENERGY idle gauge | 0.231 W [M] | ≤ 0.20 W, trending toward 0.14 W |
   | Per-conversion error from ENERGY | ~18.7 mA [D] | Toward ~2 mA |
   | "Noisy" episodes (gauge ≥ 0.40 W) | Occur whenever TX power or the router changes | None |

   The Rev 1.1 column predates P-4. With the fan-out twisted, Rev 1.1 reads
   0.0097 W on the gauge (§8.1), below the 0.14 W "clean chip" figure. That
   figure assumed the register sums |P| faithfully near zero, and it does
   not (deep-dive §3.1 note). Re-set these targets from post-P-4 Rev 1.1
   data before judging Rev 2 against them.

4. **Zero-move test.** Move the harnesses and the enclosure on purpose. The
   drain step should be under 0.3 mA, against 1–3 mA on Rev 1.1.
5. **Lit vs dark OLED.** The difference should be only the OLED's real
   current, about 2.5 mA at the bank [D], with no change in the noise
   gauge.

---

## 9. Follow-ups

- **Wiring summary** (`battery-bank-monitor-wiring-summary-v1_10.md`):
  - New revision entry for PCB Rev 2.
  - §3.1 BOM: add R5, R6, C7, JP and TB3; remove J2, R3 and the 1505
    button; C6 at 50 V.
  - §4.6: new connector map, and the pin-map correction from §5.5.
  - §6.6: light wake replaces the button.
  - §8.5: a Rev 2 verification record.
- **Firmware:** no change required. Rev 2 has no J2, which matches V1.29.
  The JP zero procedure could be added to the commissioning steps.

---

## 10. References

- TI INA228 datasheet SLYS021A (`INA228 Monitor/ina228.pdf`): §6.5
  (92 kΩ input impedance, ±0.5 µV/V supply rejection, 2.5 nA bias current,
  1 MHz clock); §8.1.4 and Fig. 8-1 (input filter: ≤ 100 Ω, 0.1–1 µF).
- Pololu D24V7F3 product page: 1.1 MHz switching, lower frequency at light
  load. <https://www.pololu.com/product/5592>
- Adafruit INA228 guide, pinouts and photos (header order; terminal block on
  the top edge). <https://learn.adafruit.com/adafruit-ina228-i2c-power-monitor/pinouts>
- Stackpole RNF/RNMF Series datasheet, rev date 2011-10-14: p.2
  mechanical specifications, p.3 how to order (R5, R6).
  <https://datasheet.octopart.com/RNMF14FTC27R4-Stackpole-Electronics-datasheet-10789848.pdf>
- TDK FK series catalog (General, up to 50 V). The YAGEO CFR datasheet
  (V.3, 2024-04-03) and KEMET C1049 Goldmax C0G datasheet (2025-08-05)
  covered the 09-28 picks for R5/R6 and C8.
- `docs/soc-noise-deep-dive.md` §3.1–§3.5, §6.4, §10.2–§10.6.
- `battery-bank-monitor.yaml` V1.29: the DIAG_ALRT write (0xA000).
- KiCad files: `Battery_Bank-Monitor-THT-V2_-_Rev_1.kicad_pcb` (Rev 1.1) and
  `Battery_Bank-Monitor-THT-V2_-_Rev_2.kicad_pcb` (2026-10-01, 11:19 save;
  first reviewed at 2026-09-28). Neither is in this repository.
