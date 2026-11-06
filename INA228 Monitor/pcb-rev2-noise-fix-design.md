# Battery_Bank-Monitor-THT-V2 Rev 2: fixing the INA228 current-channel noise (design note)

**Status.** Rev 2 built and installed 2026-11-05. The first five hours of
Rev 2 results are in §8.2 ("Results on Rev 2"). The design review below was
made before fabrication, against the Rev 2 KiCad file of 2026-10-01 (the
11:19 save). The first review, of the 2026-09-28 file, is kept where its
figures differ, marked "09-28".

**Problem it fixes.** On the built board (V2 Rev 1.1), the INA228 current
reading carries interference from the on-board 3.3 V buck regulator. The
interference adds per-conversion noise about 9× the chip's own floor, and
it moves the zero reading by 1–3 mA whenever wiring or equipment is moved.
Since the fan-out was twisted on 2026-09-28, Rev 1.1 idles at the
converter's resolution. What that leaves for Rev 2 is in §8.1 (the
2026-09-30 results).

R13, 2026-11-05: the comparison above against "the chip's own floor" has
no derivation in this note, in any version since 362909a, and that floor
is the 0.16 mA typical-table figure that the §8.1 note shows is not a
measured floor. What was measured: the interference left an unlit 2-s sd
of about 1.8 mA at the 0xFDC5 settings [M, §1.1], and the chip's own
noise at those settings is at most 0.176 mA [D, §8.2 "Against the chip's
own noise"].

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
| **Measured (first 5 h, 2026-11-05)** | Idle noise before the quantizer fell from σ = 0.206 to 0.172 mA [D: z = −14.7, 22 Rev 2 blocks against 4,226 Rev 1.1, §8.2]. Most of the calmer display is position, not the board: Rev 2's zero sits near a code centre, and Rev 1.1's had drifted near a code boundary. That share of the calm will go when the zero drifts [I]. |
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
  - **Revised 2026-10-01** (results below). The shortfall is a constant
    of about −0.040 W [D: mean of the four pair differences], not a 0.28 %
    gain error: at a 25.6 mA idle on 09-30, ENERGY ran 0.038 W below
    V × |I| as well.
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

#### Results on Rev 1.1, 2026-09-30 to 10-01

Board as left on 09-28: fan-out twisted (P-4), and TB1 GND on the shunt's
inverter-side bolt since 20:33 that evening, so the monitor's own draw now
crosses the shunt. Firmware V1.29 (build 2026-09-28 22:08, 11 dBm), up since
09-30 14:19 [M: HA ESPHome-version and uptime entities]. One discharge and
one charge at about 80 A, then 15 h idle. Figures are [M] from the HA 2-s
current and voltage, forward-filled onto the 2-s publish grid because HA
stores a value only when it changes, and from the 60-s `HW Energy` and
`HW Net Charge` registers. Scatter is defined as above. Times are EDT.

*R13 2026-11-05: "Firmware V1.29" above is wrong. The 2026-09-28 22:08
build was V1.28, a comments-only rebuild (H:/CHANGELOG.md, 2026-09-28), and
V1.29 was never flashed: on 2026-11-05 the device still exposed V1.28's
`Display Button` entity [M: HA /api/states]. The figures in this section
stand; only the version label was wrong. The same error is in §8.2 and §9.*

| window | state | 2-s n | mean | 2-s scatter | Allan dev. 20 s / 200 s |
|---|---|---|---|---|---|
| 09-30 14:30–14:48:50 | idle, before | 565 | −25.63 mA | 0.349 mA | 0.138 / 0.065 mA |
| 15:05–15:30 | discharge hold, inverter | 751 | −80.768 A | 106 mA | 35 / 121 mA |
| 15:45–16:07:20 | idle, after the discharge | 671 | −26.25 mA | 0.239 mA | 0.105 / 0.196 mA |
| 16:10–16:45 | charge, constant-current hold | 1051 | +78.745 A | 1.86 mA | 4.6 / 30 mA |
| 16:52–18:00 | idle, after the charge | 2041 | −25.08 mA | 0.282 mA | 0.089 / 0.058 mA |
| 18:00–10-01 09:00 | idle, overnight | 27,001 | −25.59 mA | 0.335 mA | 0.105 / 0.036 mA |

What each shows:

- **At idle the reading is at the INA228's resolution.**
  - 99.86 % of the overnight samples sit on two adjacent codes, −33 and
    −34 [M, n = 27,001]. The noise left is the last bit toggling.
  - The quantization floor is 0.22–0.24 mA [D: the 0.763 mA CURRENT LSB and
    the 0.833 mA ADC step (312.5 nV / 375 µΩ), each / √12]. A mean that sits
    on a step boundary toggles more, up to 0.38–0.42 mA [D: half a step].
  - The chip's own noise is about 0.16 mA rms [D: SLYS021A Table 8-2,
    19.7 noise-free bits at 4.12 ms × 256], below one step.
    - R13, 2026-11-05: the tag is stronger than the figure. The arithmetic
      is 327.68 mV / 2^19.7 / 6.6 / 375 µΩ = 0.155 mA [D]. But 19.7 bits
      is a peak-to-peak of 1.23 codes of the 312.5 nV shunt register
      [D: 2^(20 − 19.7)], so at this row the table is at the register's
      own resolution. Dividing by 6.6 assumes Gaussian tails that a one-
      or two-code spread cannot show. The table also reads 19.7 at every
      period from 527 to 2,124 ms [S: SLYS021A Table 8-2, pp. 33–34],
      where white noise would gain 1.0 bit [D: ½ log2(2,124 / 527)].
      Figure 7-5 (12.5 µV/div) cannot resolve it either. So 0.16 mA is
      the datasheet's typical figure, not a measured floor. JP fitted
      (§8.2 step 2) measures it.
  - VBUS scatter was 0.073–0.147 mV against a 0.056 mV floor [D: 195.3 µV
    / √12].
- **Averaging gains as white noise would, out to 200 s.**
  - Overnight Allan deviation was 0.335 / 0.105 / 0.036 mA at 2 / 20 /
    200 s. White noise predicts 0.106 and 0.034 [D: 0.335 / √10, / √100].
  - It levels at 0.032 mA at 30 min [M, 30 blocks]. An hour's mean is good
    to about 0.03 mA. No interference or 1/f term shows above that.
- **Under load, the scatter is the load.** The charger's output wanders by
  30 mA over 200 s, and the inverter's draw scatters 106 mA. Neither is
  measurement noise, so neither bears on the filter.
- **The idle zero moved by up to 1.9 mA during the test: two sudden steps
  and one smooth drift.** The figures are 1-min means [M].
  - Before the test it read −25.41 to −25.69 mA (14:44–14:47).
  - At 14:48 it stepped by −0.66 mA, just before the inverter came on.
  - After the discharge it held flat at −25.91 to −26.09 mA for 14 min.
  - At 15:59 it stepped by −0.8 mA and held flat until the charge began
    at 16:07.
  - After the charge it rose smoothly from −25.5 to −24.8 mA over 20 min,
    was back to −25.2 mA by 18:30, and read −25.8 mA by 08:00.
  - The full range of 5-min means was 1.94 mA [D].
- **The two steps.**
  - They are sudden and then flat. That is the shape of the 1–3 mA zero
    steps seen when the harness is moved (deep-dive §3.5), not of heating.
  - If the cables were handled at 14:48 and 15:59, the steps are an
    unplanned zero-move result on the twisted board. Whether they were is
    Bill's to say [I until then].
- **The post-charge drift.**
  - It is smooth over 20 min, which is the shape of a thermal process.
  - It is not the monitor's draw following battery voltage. The voltage
    fell from 14.06 to 13.91 V. A constant-power load would then draw
    more, which moves the reading the other way [D].
  - Overnight, battery voltage covers only 0.21 of the 0.65 mA drift [D:
    constant-power fit on 30-min means].
  - It is not chip drift. 0.7 mA is 0.26 µV at the shunt; at 10 nV/°C
    [S: SLYS021A §6.5] that would need about 26 °C of die heating [D].
  - Working model [I]: thermocouple EMF at the shunt or its lugs after
    the 80 A. It is falsified if shunt and lug temperatures, logged
    through a post-charge idle, stay flat while the zero moves.
- Each 1 mA held is 0.72 Ah/month of SOC error (§1.1).
- **The idle residual is about −3.0 mA.**
  - The overnight mean of −25.59 mA, less the monitor's 22.6 mA draw [D,
    from the 09-28 20:33 step], leaves −3.0 mA [D]. That is about the size of
    the ±2.67 mA offset spec [S].
  - The 22.6 mA is itself [D], so this is not a measurement of the offset.
    §8.2 step 2 (JP fitted) measures the offset directly on Rev 2.
- **ENERGY's "0.28 % low" on 09-28 is a constant shortfall of about
  0.04 W, not a gain error.**
  - Overnight, ENERGY ran 0.3153 W against a 2-s V × |I| of 0.3536 W.
  - Hour by hour, the difference was −0.0383 W, sd 0.0027 W [M: n = 15
    hours, one-sample t = −54.3, p = 1e-17].
  - The three shorter idle windows gave −0.041, −0.037 and −0.037 W [M].
  - The 09-28 load minutes at −1.05 A averaged −0.040 W [D: mean of the
    four pairs].
  - A 0.28 % gain error would make the idle shortfall 0.001 W [D], against
    0.038 W measured.
  - Cost: about 0.9 Wh/day of ENERGY [D: 0.0383 W × 24 h]. CHARGE, which
    drives the SOC, does not carry it.
  - The cause is unknown. 0.038 W is 2.8 mA at 13.82 V [D], close to the
    −3.0 mA residual above. So one reading is that CURRENT and CHARGE carry
    an offset that ENERGY does not [I]. SLYS021A §7.3.2 [S] says power and
    energy are computed from the same current result, which argues against
    it.
  - A charging check at 1–5 A decides it. A fixed ENERGY shortfall reads
    about 0.04 W low in both directions. A current offset makes ENERGY read
    about 0.04 W **high** while charging.
- **CHARGE reads about 0.06 % above the 2-s current, at every level and in
  both directions.**
  - Compare the register rate with the 2-s mean over the same register
    window [M]:
    - charge hold: +78.798 against +78.748 A (z ≈ 870);
    - discharge hold: −80.828 against −80.776 A (z ≈ 13);
    - overnight: −25.606 against −25.590 mA (z ≈ 8).
  - Those are +0.063 %, +0.064 % and +0.061 % in magnitude [D]. Each z is
    the difference over the 2-s sampling error, scatter / √n [D].
  - On 09-28, CHARGE matched to within 0.6 mA at 1.05 A, which is
    consistent with this.
  - At 80 A, ENERGY also reads high: +0.06 % (charge) and +0.11 %
    (discharge) above V × |I| [D]. At that power the 0.04 W shortfall is
    under 0.004 % and cannot be seen.
  - Working model [I]: the INA228's internal time base. CHARGE and ENERGY
    count each conversion at its nominal length, so a clock running 0.06 %
    fast books 0.06 % more per wall-clock hour. That is inside the ±0.5 %
    oscillator tolerance at 25 °C [S: SLYS021A §6.5, FOSC_TOL]. Falsified
    if the ratio differs from 1.0006 by more than its sampling error in
    some window, at any current or sign.
  - For SOC it is 0.3 Ah over a full 500 Ah [D]. It inflates both
    directions alike, so over a cycle that returns the charge it took,
    most of it cancels.
- **The charger cut off cleanly.** It tapered from 78 A to 7.1 A over 2.2 min,
  then fell to −0.027 A within 4 s, from 16:49:30 to 16:49:34, with one
  partial sample between [M]. |I| never fell below 24.4 mA in the 18.6 h [M, n = 33,426],
  so no idle window crossed zero.

What this does not establish:

- **One test day**, with one 80 A discharge, one charge and one 15 h idle.
- **No independent current reference.** Scatter and Allan deviation
  describe the INA228's repeatability, not its accuracy. Gain is unverified
  until a clamp reading lands (open question to Bill, 09-30), and the
  shunt's tolerance is unknown.
- **The 22.6 mA monitor draw is [D]**, so the −3.0 mA residual inherits
  its uncertainty.
- **Every cause above is [I]:** the steps, the thermal drift, the time
  base and the ENERGY shortfall.
- **The zero-move test** (§8.2 step 4) has still not been run on purpose
  on the twisted board.

**For Rev 2.** At idle, Rev 1.1 with a twisted fan-out is already at the
converter's resolution. No filter can lower a number that is the last bit
toggling. So the case for Rev 2 rests on what this run cannot show:

- the zero's robustness to harness movement. If the 14:48 and 15:59
  steps were handling, Rev 1.1 still has the problem, and Rev 2's routing
  is aimed at it;
- input protection (R5/R6);
- the in-place zero (JP).

The other accuracy terms are offset, the thermal drift, gain and the ENERGY
shortfall. None of them is noise, and Rev 2 changes none of them.

### 8.2 After building Rev 2

Firmware V1.29, 11 dBm, bank idle.

*R13 2026-11-05: read V1.30 (V1.29 was never flashed - see the note under
"Results on Rev 1.1"). V1.30 keeps 11 dBm, and by their changelog entries
neither V1.29 nor V1.30 touches acquisition. But against the Rev 1.1 runs
(V1.28) it adds the VEML7700 on the INA228's I2C bus, read every 500 ms. That
is a second change beside the board: if a Rev 2 figure differs from Rev 1.1,
the poll stays a candidate cause until ruled out [I; falsified if the figure
is unchanged with `light_poll` set to 60 s].*

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

#### Results on Rev 2, 2026-11-05

The first five hours of Rev 2 at idle, set against five weeks of Rev 1.1.
Times are EST (UTC−5) unless marked Z. Rev 1.1 dates before 11-01 were EDT,
so the matched-hours comparison below matches UTC hours.

**In short.**

- **Rev 2's analog noise is lower.** "Analog noise" means σ before the
  converter's quantizer, fitted as described under "Method".
  - Rev 2: 0.1717 mA. Rev 1.1: 0.2060 mA [D].
  - The difference is −0.034 mA, se 0.0023, z = −14.7 [D: block bootstrap,
    22 Rev 2 blocks against 4,226 Rev 1.1 blocks].
  - Matched to the same UTC hours of day: −0.036 mA, z = −13.2 [D: 893
    Rev 1.1 blocks].
- **Most of the calm you can see on the display is where the zero sits, not
  the board.** With noise below one code, the reading flickers more when its
  mean sits near a code boundary.
  - In its last week, Rev 1.1's idle mean had drifted near a boundary: 30.3 %
    of samples were off the most common code [M: 969 blocks].
  - Rev 2 idles near a code centre: 5.3 % [M: 22 blocks].
  - On days when Rev 1.1 also idled near a centre, it showed 7.6 % [M: 720
    blocks, 10-11 to 10-15].
- **That part of the calm will go when the zero moves [I].**
  - On a boundary, the fitted σ gives about 0.38 mA of 2-s scatter on either
    board [D].
  - Rev 2's fitted mean is about 0.28 mA from the nearer boundary [D].
  - Over five weeks, Rev 1.1's idle mean moved over a 1.6 mA range [M: daily
    medians −25.07 to −26.69 mA].
  - Falsified if Rev 2's 2-s scatter stays near 0.18 mA after its idle mean
    reaches −27.85 or −27.08 mA.
- **ENERGY's constant shortfall is unchanged.**
  - Rev 2: −0.0378 W [M: 2 h].
  - Rev 1.1: −0.0385 W [M: 161 h, sd 0.0003 W].
  - It is not noise, and Rev 2 was not expected to change it.
- **The noise gauge measures the monitor's own draw, not noise.** Its
  thresholds have been stale since 09-28 (below).
- **Not run yet:** the JP zero (step 2) and the zero-move test (step 4). The
  idle zero stepped by about −1 mA at the swap, and its cause is open.

**Setup.**

- **Board.** Rev 2, with the INA228 powered on at 14:50:33 (19:50:33Z). It
  reuses the Rev 1.1 Adafruit breakout, onboard 15 mΩ shunt still removed,
  so chip-to-chip spread plays no part. JP is open (Bill; H:/CHANGELOG.md
  2026.11.05).
- **Firmware.**
  - Timeline: V1.28 for the first 17 min, then V1.30 (15:08:04), V1.31
    (15:37:22) and V1.32 (16:49:29) [M: HA uptime].
  - The INA228 block is identical in V1.28 and V1.32 [M: diff of all 100
    lines]: ADC_CONFIG 0xFDC5, AVG 256, 2 s update, ADCRANGE 0, 375 µΩ,
    400 A max current. Both run 11 dBm.
  - What differs is the VEML7700, polled every 500 ms on the INA228's I2C
    bus, and the OLED light wake (R13 note above).
- **Data.**
  - HA's 2-s current, rebuilt onto the 2-s grid as in §8.1. 99.98 % of
    voltage-change intervals are whole multiples of 2 s [M: 10-12,
    n = 12,702].
  - The unit is a 10-min block that meets all of these:
    - idle throughout, |I| < 0.1 A;
    - OLED dark, with the lit spans plus 60 s after each excluded;
    - no reboot in the block or the 2 min before it;
    - no stored value held over 15 min.
- **Rev 2 set.**
  - 15:10–20:10 (20:10Z–01:10Z): 22 blocks, 6,603 samples [M].
  - Outside it or excluded:
    - two loads, at 15:01:02–15:01:44 (to −4.26 A) and 17:43:30–17:46:28
      (to −4.09 A);
    - three lit spans.
- **Rev 1.1 set.** 10-01 09:00 EDT to 11-05 12:30 EST, after the §8.1
  overnight run ended: 5,066 blocks [M].

**Method check.** The same rebuild on the §8.1 overnight window (09-30
18:00 – 10-01 09:00 EDT) gives these [M], all matching the §8.1 table except
the 20-s Allan figure there (0.105):

- n 27,001;
- mean −25.59 mA;
- 2-s scatter 0.335 mA;
- Allan 0.106 / 0.036 mA;
- 99.86 % on two adjacent codes.

**The quantizer is the CURRENT register's LSB.**

- It is 0.7629 mA [S: firmware, 400 A / 2^19], not the 0.833 mA ADC step.
- Codes such as −18, −6, 6, 18 and 30 occur [M: 09-28 to 11-05].
- ADC counts relabelled into CURRENT units would skip every 12th code:
  −30, −18, −6, 6, 18, 30 [D: round(k × 0.833 / 0.7629)]. Since those codes
  occur, the readings are not relabelled counts.
- So the floor for a mean placed at random is 0.220 mA [D: 0.7629 / √12].
  This settles which end of §8.1's 0.22–0.24 mA range applies.

**Raw scatter depends on where the mean sits.** Below one code of noise,
a reading whose mean sits on a code boundary splits between two codes. A
reading whose mean sits at a code centre mostly stays on one.

| distance of the block mean from the nearest code boundary | Rev 1.1 blocks | median 2-s scatter | samples off the most common code |
|---|---|---|---|
| 0.0–0.1 code (on a boundary) | 268 | 0.380 mA | 44.4 % |
| 0.1–0.2 code | 614 | 0.364 mA | 34.5 % |
| 0.2–0.3 code | 808 | 0.334 mA | 25.3 % |
| 0.3–0.4 code | 1,213 | 0.272 mA | 14.9 % |
| 0.4–0.5 code (code centre) | 2,241 | 0.212 mA | 8.0 % |
| Rev 2, all at 0.43–0.50 code | 22 | 0.177 mA | 5.3 % |

[M: Rev 1.1 idle blocks 09-30 20:00 EDT – 11-05 12:30 EST, n = 5,144; this
window starts 13 h before the Rev 1.1 set above.] The block mean here is the
mean of the quantized readings. The quantizer pulls it toward the code
centre, so a row-five block can have its analog mean well off centre. Rev
2's blocks do: median 0.14 code [D: fitted].

**Why Rev 1.1 looked worse in its last week.**

- Its daily idle mean moved from about −26.67 to −26.43 mA in the week
  before the swap [M: daily medians]. That put it in the 0.1–0.2-code row.
- Its median 2-s scatter that week was 0.354 mA [M: 969 blocks]. Earlier
  windows gave 0.203 mA (10-11 to 10-15) and 0.212 mA (10-24 to 10-28) [M:
  720 blocks each].
- Its fitted σ did not change (next table). The mean moved; the board did
  not get noisier.

**Method: analog σ through the quantizer.**

- Each 10-min block is modelled as Gaussian noise with its own mean and
  with one σ shared by all of a board's blocks. The noise passes through
  the 0.7629 mA quantizer.
- σ is fitted by maximum likelihood, with each block's mean profiled out.
- On synthetic data the fit recovers σ down to about 0.2 code when the mean
  is off a boundary, but not when it sits on one [D: synthetic test]. So
  only blocks whose quantized mean is at least 0.2 code from a boundary are
  fitted, on both boards.
- **Check on the real data.** The pooled σ, with each block's fitted mean,
  predicts the share of samples off the most common code [D]. Measured [M]:
  - Rev 2: 5.27 % predicted, 5.26 % measured;
  - Rev 1.1: 13.30 % predicted, 13.24 % measured.

| window | blocks fitted (of idle) | median 2-s scatter | σ, 95 % profile interval |
|---|---|---|---|
| Rev 1.1, 09-30 18:00 – 10-01 09:00 EDT (§8.1 overnight) | 48 (of 90) | 0.347 mA | 0.198 [0.192, 0.203] mA |
| Rev 1.1, 10-11 to 10-15 | 720 (of 720) | 0.203 mA | 0.207 [0.207, 0.207] mA |
| Rev 1.1, 10-24 to 10-28 | 719 (of 720) | 0.212 mA | 0.206 [0.206, 0.207] mA |
| Rev 1.1, 10-30 to 11-05 12:30 EST | 450 (of 969) | 0.354 mA | 0.203 [0.202, 0.205] mA |
| Rev 2, 15:10–20:10 | 22 (of 22) | 0.177 mA | 0.171 [0.166, 0.176] mA |
| Rev 2, V1.32 only | 17 (of 17) | 0.176 mA | 0.173 [0.166, 0.179] mA |

[D: profile likelihood on the [M] blocks.]

- Rev 1.1's σ held at 0.198–0.207 mA across four windows whose raw scatter
  ran from 0.203 to 0.354 mA.
- V1.32 alone gives the same σ as V1.30–V1.32 together.
- The profile intervals assume independent samples and are too narrow. The
  comparison uses a block bootstrap (B = 2,000) instead [D]:

| comparison | Rev 1.1 σ | Rev 2 σ (22 blocks, 6,603 samples) | difference | z |
|---|---|---|---|---|
| all idle: 4,226 of 5,066 blocks, 1,268,729 samples | 0.2060 mA, se 0.0004 | 0.1717 mA, se 0.0023 | −0.0343 mA, se 0.0023 | −14.7 |
| same UTC hours, 20:10–01:10Z, 35 evenings: 893 of 1,049 blocks | 0.2075 mA, se 0.0014 | 0.1717 mA, se 0.0023 | −0.0359 mA, se 0.0027 | −13.2 |

- **Intervals.** The bootstrap 95 % intervals are [0.1663, 0.1755] mA for
  Rev 2, [0.2052, 0.2068] for all of Rev 1.1, and [0.2052, 0.2106] for the
  matched hours [D].
- **Per evening.** 31 Rev 1.1 evenings had at least 10 fitted blocks. None
  fitted at or below Rev 2's 0.1717 mA [D]: min 0.1991, median 0.2068, max
  0.2426 mA.

**What the σ change means on the display.** These are 2-s scatter figures
for independent samples [D: σ through the quantizer]:

- With the mean at a code centre: 0.193 mA on Rev 1.1, 0.124 mA on Rev 2.
- With the mean on a boundary: 0.382 and 0.381 mA. The quantizer hides the
  difference there.
- Rev 2's measured 0.177 mA falls between the two. Its fitted mean sits
  0.14 code from the centre of code −36 (median over the 22 blocks) [D].

**Against the chip's own noise.**

- §8.1 put the INA228's own noise at about 0.16 mA rms [D: SLYS021A Table
  8-2].
- Taking that as given, the noise above the chip is about 0.13 mA on Rev 1.1
  and about 0.06 mA on Rev 2 [D: √(σ² − 0.16²)].
- That rests on a typical-table figure. At 0.150 or 0.165 mA instead,
  Rev 2's excess is 0.08 or 0.05 mA [D]. So Rev 2 is near the chip's own
  noise, and what is left above it cannot be sized from this data.
- R13, 2026-11-05: "near the chip's own noise" claims more than the data
  holds. The 0.16 mA is the table read at the shunt register's own
  resolution (§8.1 note), so it cannot fix the floor to the 0.01 mA these
  excesses turn on. What holds without it:
  - The re-spin removed 0.114 mA rms in quadrature, 95 % [0.107, 0.121]
    [D: √(0.2060² − 0.1717²), se from the two bootstrap se]. Over the
    same UTC hours, 0.117 [0.108, 0.125] [D]. Both builds used the same
    breakout, so the chip's share drops out, if it did not change between
    them.
  - The chip's own noise at these settings is at most Rev 2's total,
    0.176 mA at the top of its 95 % interval [D], if the sources are
    independent.
  - The split of Rev 2's 0.172 mA is open: about 0.05 mA above the chip
    if the chip is at 0.165 mA, 0.14 mA if it is at 0.10 mA
    [D: √(0.1717² − floor²)]. Whether a Rev 3 has anything left to remove
    turns on that split. JP fitted measures it, provided JP's fixed zero
    sits away from a code boundary (the fit uses centred blocks only).

**Allan deviation** (mA, non-overlapping) [M]:

| run | 2-s n | 2 s | 20 s | 200 s | 600 s | 1800 s |
|---|---|---|---|---|---|---|
| Rev 2, 17:52–20:10 | 4,140 | 0.169 | 0.056 | 0.013 | 0.011 | 0.008 |
| Rev 1.1, 10-12 16:00–21:10 EDT (mean near a code centre) | 9,300 | 0.199 | 0.059 | 0.019 | 0.014 | 0.012 |
| Rev 1.1, 09-30 overnight (mean near a boundary) | 27,001 | 0.335 | 0.106 | 0.036 | 0.026 | 0.031 |

- Rev 2 averages down as white noise would, out to 200 s: 0.053 and 0.017
  predicted [D: 0.169 / √10, / √100], against 0.056 and 0.013 measured.
- At 20 s the two centred runs are within 0.003 mA.
- At 200 s Rev 2 is 0.006 mA lower, about 3 se [D: Allan uncertainty
  1/√(2(N − 1)) on 41 and 93 blocks].
- Rev 2's 600 s and 1800 s figures rest on 13 and 4 blocks, which leaves
  them uncertain by about 20 % and 40 % [D: same formula]. No difference
  is claimed beyond 200 s.

**ENERGY against V × |I|.**

- Rev 2 (V1.32, 2 clean hours): ENERGY 0.3280 W, V × |I| 0.3658 W, a
  difference of −0.0378 W [M].
- Rev 1.1 (10-30 to 11-05, 161 h): −0.0385 W, sd 0.0003 W [M]. §8.1 found
  −0.0383 W on 09-30.
- So the shortfall is the same to within 0.0007 W [D]. With n = 2 hours, no
  test of the difference is meaningful.

**The noise gauge no longer measures noise.**

- Since TB1 GND moved to the shunt's inverter-side bolt (09-28 20:33 EDT),
  the monitor's own draw crosses the shunt. The gauge, an idle ENERGY rate,
  reads that draw.
- Rev 1.1 medians [M]:
  - 09-29 to 10-01: 0.2965 W (n = 2,753);
  - 10-01 to 10-15: 0.3155 W (n = 20,103);
  - 10-15 to 11-01: 0.3154 W (n = 24,477);
  - 11-01 to 11-05 12:30: 0.3137 W (n = 6,809).
- From 10-01 on, every publication fell between the 0.25 W "quiet" and
  0.40 W "noisy" thresholds. So `noise_state` read "elevated" all the time
  [M: 51,389 publications, range 0.3076–0.3287 W].
- Rev 2 (V1.32, 16:52–20:10): median 0.3286 W [M: n = 192]. That is
  +0.015 W on Rev 1.1's last days. The 1.07 mA larger idle draw at 13.3 V
  accounts for 0.014 W of it [D: 0.00107 A × 13.3 V].
- Rev 2's 26 "noisy" publications (≥ 0.40 W) fall in two runs [M]:
  - 7 at 15:01:38–15:07:38, after the load at 15:01:02–15:01:44;
  - 19 at 17:44:27–18:02:27, after the load at 17:43:30–17:46:28.
  - Each run starts within a minute of its load and ends 6 and 16 min after
    the load ends.
  - That is the gauge's ~5-min average carrying the load, not noise [D:
    timing].
- The gauge publishes only when |I| < 0.5 A at the 60-s read. So it reports
  the tail of a load, never the load itself.
- **Since 09-28, "elevated" means "the monitor is drawing current", and
  "noisy" means "a load just ended".** See §9.

**VBUS.**

- Median block scatter: 0.0577 mV on Rev 2 (n = 22) against 0.0716 mV on
  Rev 1.1's last week (n = 969) [M]. The floor is 0.056 mV [D: 195.3 µV /
  √12].
- Mann–Whitney p = 0.085. 32 % of Rev 1.1 blocks were at or below Rev 2's
  median [M]. No VBUS difference is claimed.

**The zero.**

- Rev 2 idles at −27.47 to −27.52 mA [M: 22 dark blocks].
- Rev 1.1 read −26.43 mA on its last idle day. Over its last 16 nights it
  read −26.57 mA, sd 0.10 [M: 06–10Z; H:/open_questions.yaml, 2026-11-05].
- So the step at the swap is −0.9 to −1.1 mA [D].
- That is inside the range Rev 1.1's own zero covered over five weeks [M:
  daily medians −25.07 to −26.69 mA]. On its own, the step says nothing
  about the board.
- Candidate causes:
  - (a) **A real rise in the monitor's draw:** the VEML7700 board, whose
    green power LED is lit (Bill, 2026-11-05), or V1.30's 500 ms poll.
  - (b) **An offset change from re-landing the sense leads on TB3.** The
    step is 0.40 µV at the shunt [D: 1.07 mA × 375 µΩ], inside the ±1 µV
    offset spec (§0).
- SOC books a real draw correctly. It does not book an offset correctly.
  Two tests tell them apart:
  - JP fitted (step 2) reads the offset alone;
  - unplugging the VEML cable for 10 min with Light Wake off reads the
    board's draw (H:/open_questions.yaml, 2026-11-05).

**OLED lit against dark (step 5, in part).**

- **Spans used.** Two lit spans had no load and no reboot [M]:
  - 15:41:40–15:47:30;
  - 17:35:56–17:43:28, cut 2 s before the 17:43:30 load.
  - The first 10 s after switch-on are dropped from each.
- **Draw.**
  - The first span read −28.905 mA [M: 175 samples]. The dark windows read
    −27.494 mA in the 10 min before (that window includes the 15:37:22
    reboot) and −27.511 mA in the 10 min starting 1 min after.
  - The second read −29.245 mA [M: 226 samples], against −27.496 mA in the
    10 dark minutes before.
  - So the lit OLED draws 1.39–1.41 and 1.75 mA at the bank [D], against
    about 2.5 mA expected [D, step 5].
- **Spread.** The sample sd is 0.36–0.68 mA lit, against 0.15–0.20 mA dark
  [M]. Pages change every 10 s, so the likely cause is the panel's draw
  following what it shows [I]. Falsified if a lit span held on one page
  shows the dark sd.
- **Gauge.** It cannot be judged on spans this short, because it averages
  over about 5 min.

**§8.2 steps after day 1.**

| step | status |
|---|---|
| 1. Sign | Done [D]. The monitor's own draw is a discharge, and it reads −27.5 mA. That is the same sign as on Rev 1.1, where an 80 A discharge read −80.8 A (§8.1). The two ~4 A loads also read negative. |
| 2. JP zero | Not run. |
| 3. Noise | This section. The step-3 table was set in noise-gauge terms before P-4 and before the GND move. The gauge no longer measures noise, so judge Rev 2 by σ. |
| 4. Zero-move | Not run. With nothing moved, Rev 2's zero held at −27.47 to −27.52 mA across 22 blocks. |
| 5. Lit vs dark | In part: the current step is 1.4–1.75 mA. The gauge was not judged. |

**What this does not establish.**

- **Five hours, one afternoon and evening, 22 blocks.**
  - Rev 2's se of 0.0023 mA comes from resampling those 22 blocks. It
    leaves out any day-to-day change in σ.
  - Rev 1.1's per-evening σ ranged 0.199–0.243 mA (n = 31) [D], so σ does
    vary from day to day.
  - The Rev 2 figure stands only after a week of evenings and nights.
- **Two changes at once.**
  - Rev 2 runs V1.30 or later, which polls the VEML7700 on the INA228's bus
    every 500 ms. Rev 1.1 ran V1.28, without it.
  - Extra bus activity seems unlikely to lower noise, but that is [I].
    Setting `light_poll` to 60 s for a few hours would rule it out.
- **The model.**
  - The fit assumes Gaussian noise that is constant within a block, with
    one σ for every block.
  - It reproduces the off-code share to within 0.06 percentage points on
    both boards [D]. That supports the model; it does not prove it.
- **Fitted blocks only.** Only blocks with their quantized mean at least 0.2
  code from a boundary are fitted: 4,226 of 5,066 Rev 1.1 blocks and all 22
  of Rev 2.
- **No independent current reference.** Everything here is repeatability.
  Gain waits on the clamp reading (open question, 09-30).
- **Untested.** This run does not touch the case §8.1 made for Rev 2: zero
  robustness, input protection and the JP zero. Steps 2 and 4 have not been
  run, and the cause of the −1 mA zero step is open.

---

## 9. Follow-ups

- **Noise gauge (2026-11-05).** Its 0.25 W and 0.40 W states have been stale
  since the 09-28 GND move (§8.2, "Results on Rev 2"). Two options:
  - re-base them on the idle draw, about 0.31–0.33 W [M];
  - replace the state with a measure that tracks noise. The share of
    samples off the most common code is one, but it follows the mean's grid
    position as well.
- **Rev 2 σ, again.** Re-fit after a week that includes nights, and again
  once the idle mean has drifted near a code boundary.
- **Wiring summary** (`battery-bank-monitor-wiring-summary-v1_10.md`):
  - New revision entry for PCB Rev 2.
  - §3.1 BOM: add R5, R6, C7, JP and TB3; remove J2, R3 and the 1505
    button; C6 at 50 V.
  - §4.6: new connector map, and the pin-map correction from §5.5.
  - §6.6: light wake replaces the button.
  - §8.5: a Rev 2 verification record.
- **Firmware:** no change required. Rev 2 has no J2, which matches V1.29.
  The JP zero procedure could be added to the commissioning steps.
  *R13 2026-11-05: true of V1.29, but the device ran V1.28, which has the
  button, so Rev 2 needs a flash. It gets V1.30: V1.29's light wake, a 10 s
  page cycle, and no Charge page. V1.30's header adds Rev 2's TB1, whose
  polarity is reversed from Rev 1.1 (pin 1 = BATT_RAW "+", pin 2 = GND).*

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
