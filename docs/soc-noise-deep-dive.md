# Battery-bank SOC: noise root cause and INA228 accuracy (deep dive)

**Rev 3, 2026-09-25.** This revision adds three things:

- **Photos** of the enclosure and carrier. They show the INA228 input terminal
  block ~1 cm from the Pololu buck, and the ESP antenna next to both.
- **Bill's answers:**
  - Only the batteries, the monitor and the inverter are on the busbars.
  - The inverter is connected but off, and its AC side is unplugged.
  - Nobody knows what moved on the four step dates.
- **A per-minute analysis** of the three OLED-lit windows (§3.1).

**What changed from Rev 2** (R13):

- **The leading suspect is now the monitor's own buck regulator.** Rev 2's was
  the ESP's radio.
- **The 0.88 mA "noisy excess" is most likely a DC error, not real current.**
- **Rev 2's airtime model is demoted.** Its key premise fails (§3.3).

**Earlier revisions:**

- Rev 1 (`961e077`): written without datasheets or data.
- Rev 2 (`8b54cef`): added the datasheets and the 2026-09-25 HA exports.
  - `INA228 Monitor/ina228.pdf`: TI SLYS021A, revised May 2022
  - `INA228 Monitor/esp32-c3_datasheet_en.pdf`: v2.1

**Scope.** This reviews `docs/soc-accuracy-turnover.md` (the **turnover**)
and `docs/soc-v128-review.md` (the **review**) against:

- firmware **V1.27**, `INA228 Monitor/battery-bank-monitor.yaml`. Line
  numbers match both docs.
- the wiring summary (Rev 1.10) and the commissioning report
- the 2026-08-26 report
- the data in `data/` and Bill's exports

**Nothing is built.** V1.28 still waits on Bill's go (R12). Physical work is
Bill's call (R14).

**Evidence tags:**

- **[M]** measured
- **[D]** derived, with the chain shown
- **[S]** source read this session. "DS" means the INA228 datasheet, "C3" the
  ESP32-C3 datasheet.
- **[P]** seen in Bill's photos
- **[I]** inference, not yet checked

**Not verified:**

- the Pololu D24V7F3's efficiency (η = 0.80–0.90 assumed) and its light-load
  switching behaviour. Pololu's site is blocked here.
- antenna gains and distances [I]

---

## 0. Answers

### 0.1 The noise source

- **The noise is generated inside the monitor, and lighting the OLED
  switches it off** [M]. This is the new central fact.
  - Each time the OLED was lit (09-11, 09-18, 09-22), the per-conversion
    noise gauge fell within one minute to the same floor: **0.225–0.245 W**.
    That held in both regimes: 0.88–1.30 W before when noisy, 0.52 W before
    when quiet.
  - The 2-s sd fell to ~2 mA.
  - It came back within 1–2 min of the 5-min display timeout.
  - Across **21,114 minutes** of 60-s data, the floor appears **only** in
    those 16 lit minutes (§3.1).
  - The router's RF does not change when an OLED lights up. **So the router
    is effectively ruled out as the direct source.**
- **Prime suspect: the Pololu D24V7F3 buck (U3)** [P + I].
  - It sits ~1 cm below the INA228 input terminal block.
  - Its 22 µH inductor is marked "220" [P].
  - The sense wires leave the terminal block untwisted and run past it [P].
- **Proposed mechanism** [I]. The regulator runs at ~90 mA, where small
  bucks typically change switching mode. The ESP's load changes (TX bursts,
  CPU wake-ups) make it hop between modes. Its switching field or input
  ripple reaches the unfiltered INA228 inputs. TI flags exactly this: DS
  §8.1.4, "transients that occur at or very close to the sampling rate
  harmonics … at 1 MHz and higher".
- **How the observations fit:**
  - **OLED:** lit, it adds a steady ~8–9 mA at 3.3 V [D], which would hold
    the regulator in one mode.
  - **Regimes:** the router regime changes the ESP's activity pattern, and so
    how often the regulator hops.
- **Second suspect: the ESP's antenna**, "very close" per Bill and [P].
  Its near field at the breakout is 100× or more the router's (§3.2). But it
  does not explain why a lit OLED silences the noise.
- **The 0.88 mA noisy-state excess is most likely a DC error riding on the
  noise, not real radio current** [M, n = 3]. With the OLED lit, the drain
  read −10.25, −10.27 and −10.37 mA, whether the regime was noisy or quiet.
  Real extra TX current would have persisted.
- **The router coexistence stopgap still works** because it lowers the
  modulation. The monitor-side fix is in §6.4.

### 0.2 SOC and accuracy

- **The largest SOC term is still the unmeasured zero, and it is not the
  noise.**
  - The ESP32-C3's receive current is 84–87 mA [S: C3 Table 5-7], and the
    firmware keeps the receiver on (`WIFI_PS_NONE`).
  - So the monitor should draw 23.5–27.4 mA from the bank, or ≥ 21.2 mA even
    through a lossless regulator.
  - The shunt reads 7.3–8.2 mA: a **gap of 15–20 mA**.
  - **The lit-OLED state shows the gap is not the noise's DC part.** With the
    interference suppressed, the reading (−10.3 mA) still sits 15.6–19.5 mA
    short of the expected 25.9–29.8 mA (monitor + OLED) [D].
  - **The bus contents narrow it further.** Only the batteries, the monitor
    and the inverter (off) are on the busbars. No charger can trickle. The
    inverter's off-state draw goes *through* the shunt, which can only
    widen the gap.
  - Two explanations are left (§4):
    1. the ESP draws ~⅓ of its datasheet current, or
    2. a **static in-situ offset of +5.7–7.5 µV**
- **If it is an offset:**
  - V1.28 inherits **2.8–3.7 %/mo**.
  - The true SOC today is **~88–90 %**, not ~96.7 % [D, conditional].
- **How to settle it:** one DMM reading (P-1), or TB-1. With the radio off,
  any reading above −4.8 mA proves an offset.
- **The zero also steps by 1–3 mA** when the monitor or router is moved
  (08-04, 08-31, 09-22) [M, §3.5]. After an in-situ zero, the residual wander
  is ~±0.28 %/mo until the pickup is fixed.
- **V1.28's core design stands.** CHARGE accumulates *each conversion*,
  unaveraged [S: DS §7.3.1, Fig. 7-2]. It integrates zero-mean interference
  to zero.
- **Firmware items** (§6.2):
  - an in-situ offset term
  - 2× shunt integration time at the same cycle time [S: DS Table 8-2]
  - `max_current` 400 A, because the 350 A guard can never trip today
  - an honest RECON uncertainty
- **Possible firmware stopgap for the CURRENT channel:** keep the OLED "on"
  with a black frame (no burn-in), if TB-4 shows that suppresses the noise.

### 0.3 Next step and data

- **Cheapest decisive test:** TB-4, the remote OLED variants and a CPU-load
  variant (§5). It is firmware-only and needs nobody present.
- **The physical twin:** P-5, a resistor between the board's 3V3 and GND test
  points.
- **Still needed:** §8.2.

---

## 1. Signatures any explanation must meet

| # | Signature | Source |
|---|---|---|
| S1 | Noisy: mean −8.28 / sd 18.11 mA. Quiet: −7.22 / 5.44 mA | [M] turnover §3, review §2 |
| S2 | White at 2 s (lag-1 −0.004, both regimes) | [M] review §2; 09-24 export |
| S3 | Symmetric: skew 0.011–0.016. Positive readings: 5.3–8.7 % quiet (Sept), 17.5–19 % July | [M] turnover §4, review §7, exports |
| S4 | Hourly CHARGE scatter 0.39 mA = 18.11 / √2278 | [M/D] review §2 |
| S5 | The regime follows the router. Coexistence OFF gave 11 h quiet (sd 5.0 mA), no noisy block | [M] turnover §4, 09-24 export |
| S6 | Unlit, noisy reads 0.88 mA more drain than quiet (t = 10.7) | [M] turnover §3 |
| S7 | **Lit OLED: the noise gauge drops to 0.23 W and the drain reads −10.3 mA in both regimes; seen only when lit** | [M] §3.1 |
| S8 | The chip floor (0.16 mA per reading [D: DS Table 8-2]) is never reached, even when lit (~2 mA) | [M/D] |
| S9 | July idle: sd 7.2–7.8 mA, symmetric, white | [M] `data/ina228 Amperage.csv` |
| S10 | ENERGY idle rate: 0.46 W quiet, 1.44 W noisy, 0.82–0.85 W July, 0.23 W lit. The true power is ~0.1 W | [M] HW export |
| S11 | Drain and noise level step at physical events, and not in proportion | [M] §3.5 |
| S12 | ESP32 die ~0.5 °C warmer in noisy hours (r = 0.45) | [M, weak] ESP temperature export |

---

## 2. Why the noise is not in-band current

### 2.1 Sign

Nothing on the bus can charge the bank. The bus holds the batteries, the
monitor and the inverter, which is off; no charger is connected [Bill].
Every consumer returns through the shunt as discharge. Yet 5.3–8.7 % of
quiet samples and 17.5–19 % of July samples are positive [M]. **Those
readings are error.**

### 2.2 Shape

Suppose the scatter came from real discharge pulses sampled in the ADC's
conversion windows. For Poisson or clustered arrivals with positive pulse
sizes *a*:

```
mean contribution  m    = mu * E[a]
variance                = mu * E[a^2]
skew                    = E[a^3] / (E[a^2]^1.5 * sqrt(mu))
skew / (sd / m)         = E[a^3] * E[a] / E[a^2]^2  >= 1   (Cauchy-Schwarz)
```

So **skew ≥ sd / m**, with *m* ≤ |mean|:

| | sd | m ≤ | skew must be ≥ | measured skew |
|---|---|---|---|---|
| noisy | 18.11 mA | 8.28 mA | 2.19 | 0.016 |
| quiet | 5.44 mA | 7.22 mA | 0.75 | 0.012 |

Both miss by two orders of magnitude.

### 2.3 What this does *not* exclude

The argument covers current inside the ADC's passband (below ~121 Hz, the
first notch at 1 / (2 × 4.12 ms) [S: DS §7.3.4.1]).

It does not cover **high-frequency current or voltage near the ADC's
~1 MHz sampling harmonics** [S: DS §6.5 FOSC, §8.1.4]. Those alias into the
baseband as zero-mean, symmetric error. The buck's switching ripple is one
such source. It can reach the inputs two ways:

- through the shunt itself, because the monitor's return runs through it
- by coupling into the input wiring

Physically, that ripple is "current", but it reads as symmetric noise. The
fix for either path is the same: the §6.4 input filter.

---

## 3. Where the error comes from

### 3.1 The lit OLED switches it off

Per-minute rates from the 60-s `HW Energy` / `HW Net Charge` data [M]. ENERGY
is a per-conversion noise gauge: DS §7.3.1 / Fig. 7-2 says it accumulates
each conversion, unaveraged, and POWER is unsigned.

| press (UTC) | before: ENERGY / drain / drain scatter | lit: ENERGY / drain / drain scatter | after: ENERGY / drain |
|---|---|---|---|
| 09-11 18:22:52 (noisy) | 0.884 W / −8.95 / 1.94 mA | **0.280 W** (0.23 once settled) / **−10.25** / 0.42 mA | 0.944 W / −9.33 |
| 09-18 16:02:45 (noisy) | 1.299 W / −8.64 / 1.78 mA | **0.265 W** (0.23) / **−10.27** / 0.39 mA | 0.770 W / −7.74 |
| 09-22 18:16:32, then 4 presses to 18:21:47 (quiet) | 0.800 W* / −7.89 / 4.69 mA | **0.237 W** (sd 0.009) / **−10.37** / 0.45 mA | 0.535 W / −7.48 |

\*The 09-22 "before" window includes the router power-down (18:06–18:11Z).
Its last minutes before the press read 0.52–0.55 W.

**Timing:**

- The floor is reached in the first full minute after the press.
- It lasts exactly until the display times out (5 min after the last press).
- It is gone in the first minute after.
- On 09-22 the extra presses extended the lit time to 10 min, and the floor
  held all 10 minutes.

**Uniqueness.** In 21,114 per-minute rates (09-10 08:12Z → 09-25), the rate is
< 0.30 W only in these 16 minutes. The one other hit is a 0 W reading at a
reboot. The lowest unlit rate is 0.35 W.

**What changes when the OLED is lit** [S: ESPHome `ssd1306_base.cpp`,
`ssd1306_i2c.cpp`]:

- **The I²C traffic does not change.** `update()` renders and writes the full
  1 KB buffer every second whether the panel is on or off. `turn_off()` only
  sends 0xAE.
- **What does change:**
  - the panel is on
  - its internal charge pump runs [I]
  - it draws pixel current
  - on these three occasions, a person was present
- **The person is unlikely to be the cause.** The noise tracked the display
  timeout to the minute three times, including a 10-min extension.
  Presence can't be fully excluded; TB-4 does that.

**Quantities** [D]:

- **The OLED's current:** 09-22 (quiet) went from −7.89 to −10.37 mA, so
  ΔI_b = 2.5 mA at the bank. At 3.3 V: 2.5 × 13.3 × (0.80–0.90) / 3.3 =
  **8–9 mA**.
- **The noisy excess disappears when lit:**
  - Lit minus before is −1.30 and −1.63 mA in the two noisy cases, against
    −2.48 mA in the quiet one.
  - So the unlit noisy readings carried an extra −0.85 to −1.18 mA.
  - That extra is gone when lit: −10.25 / −10.27 vs −10.37 mA.
  - **The turnover's 0.88 mA is therefore most likely a DC error of the
    interference, not current** [n = 3].
- **The lit per-conversion error:** 0.23 W / 13.29 V = 17.3 mA mean |I|. With
  μ = −10.3 mA, that inverts to σ ≈ **19 mA (7 µV)**.
  - For comparison: 42 mA quiet, 136 mA noisy, and 2 mA for the chip alone
    [D: DS Table 8-2, 16.0 bits at 4120 µs].
  - A smaller residual remains even when lit.

### 3.2 What the photos show

[P], approximate distances:

1. **U2 (INA228 breakout) sits directly above C1 and U3 (the Pololu buck).**
   The breakout's VIN+/VBUS/VIN− terminal block is on its lower edge, facing
   U3, ~1 cm from the 22 µH inductor ("220").
2. **The input wires are red and look untwisted** from the terminal block
   until they pass U3/C4 and head to the lower-left gland. The wiring summary
   specifies a twisted pair.
3. **The XIAO (ESP32-C3, U.FL) sits right beside the INA228 breakout.** The
   antenna pigtail loops over the board. Bill: "very close".
4. **The OLED harness crosses U3 and the INA228 terminal block** in long
   untwisted loops (SDA/SCL/3V3/GND).
5. **TB1 (black/white) leaves by its own gland**, apart from the sense wires.
   Good. The outside routing is not shown.
6. **The breakout's own power LED is lit.** That is consistent with the
   ~0.13 mA budget item.
7. **Photo 3 is probably from July** (13.41 V, SOC 100 %, a page layout with
   "IDLE" that V1.27 does not draw). The wiring may have changed at the
   08-04 or 08-31 rewires. A current photo of the terminal-block area would
   help (§8.2).

**Fields at the breakout** [D/I]:

- **Router,** from RSSI of −30 to −39 dBm with a 2 dBi antenna: **0.44–0.16
  V/m**. The aperture is A = 1.58 × 0.125² / 12.57 = 0.00197 m², and
  E = √(377 × P / A).
- **ESP**, 20 dBm, 2–5 cm away: E ≈ √(30 × 0.1 × 1.6) / d = **44–110 V/m**.
  This is far-field arithmetic in the near field, so it is order-of-magnitude
  only. That is 100–700× the router in amplitude.

### 3.3 Mechanisms, ranked

| mechanism | explains regimes? | explains lit-OLED collapse? | explains the zero steps at moves? | status |
|---|---|---|---|---|
| **A. Buck switching** (mode hopping at ~90 mA, modulated by the ESP's load) into the unfiltered inputs: magnetic pickup at the untwisted terminal fan-out ~1 cm from U3, and/or HF ripple through the shunt | yes, via the ESP's activity pattern | **yes**: a steady +8–9 mA holds the regulator in one mode [I] | yes: moving wires near U3 changes the coupling | **leading** |
| **B. ESP antenna near field** on the breakout/leads | yes, via TX airtime | no obvious way | yes | second |
| **C. Router RF** | yes | **no** | partly | effectively ruled out |
| **D. Supply rejection** (3V3 droop) | — | — | — | unlikely: ±0.5 µV/V max [S: DS §6.5] → ≤ 0.05 µV per 100 mV |

**Rev 2's airtime model (B), demoted.**

- **Its arithmetic stands if its premise holds.** 11.08× variance ratio;
  TX − RX = 191–251 mA [S: C3 Table 5-7]; 53–78 mA per burst at the bank;
  0.11–0.17 % / 1.2–1.8 % airtime.
- **Its premise was that the 0.88 mA noisy excess is real TX current.** §3.1
  now says it is not.
- **The ESP's warmer die in noisy hours** (S12) remains weak and possibly
  time-of-day confounded. It no longer carries the model.

**The ENERGY vs averaged-sd check still holds** [M/D; Gaussian inversion]:

| state | σ per conversion | sd_avg × √128 | variance ratio |
|---|---|---|---|
| noisy | 136 mA | 215 mA | 2.5 |
| quiet | 42 mA | 57 mA | 1.8 |
| lit | 19 mA | ~23 mA (sd ~2 mA) | ~1.4 |

The error is correlated across conversions or impulsive. Burst-mode
switching gives exactly that. TB-3 (AVG = 1) measures it directly.

### 3.4 Where in the chain: a test tree

The trees below split the paths. Each branch is one cheap step; details are
in §5.

- **P-5, a preload resistor** (3V3 TP to GND TP; 220–330 Ω = 10–15 mA):
  - noise collapses as it does with the OLED → **the load level drives it
    (A)**
  - no change → the OLED panel itself does it (TB-4 variants)
- **P-2a, short the inputs at the INA228 terminal block:**
  - noise persists → **board-level pickup:** the buck's or ESP's field on
    the breakout
  - noise gone → it is in the leads or the shunt. Go to P-2b.
- **P-2b, short the inputs at the shunt end, leads kept:**
  - noise persists → **pickup in the lead loop**
  - noise gone → **HF ripple through the shunt itself**

### 3.5 The zero moves with the RF/physical environment

Daily means [M] (from Rev 2):

| period | ENERGY (W) | drain (mA) | RSSI (dBm) | at the start |
|---|---|---|---|---|
| 07-21 → 08-04 | 0.82–0.92 | −5.6 to −6.9 | −33 to −35 | (post-charge) |
| 08-05 → 08-18 | 0.65–0.72 | −8.2 to −9.0 | −29 to −30 | 08-04 20Z: rewire; RSSI +4 dB; drain −2.8 mA |
| 08-19 → 08-31 | 0.76–0.90 | −6.6 to −8.2 | −30 → −34.7 | 08-18 22Z: ENERGY up, drain +1.2 mA, no RSSI change |
| 09-01 → 09-21 | 0.74 → 1.34 | −8.3 to −9.3 | −29.5 to −33 | 08-31 ~21Z: INA228 power loss (rewire); RSSI +3.5 dB; drain −1.2 mA |
| 09-22 → 09-25 | 0.40–0.60 | −7.0 to −7.6 | −36 to −39 | router power-down; coexistence OFF 09-24 |

- **The steps are 1–3 mA (0.4–1.1 µV).** They coincide with RSSI steps at the
  physical events, and they are not proportional to the noise level. Bill
  doesn't know what moved (§8.2).
- **Under A**, these are changes in coupling geometry near U3 and the
  terminal block. They move both the noise and its DC part.
- **The steps exceed the chip.** The INA228's drift is ±10 nV/°C max [S], so
  steps of this size are external to it.

### 3.6 Coexistence-OFF baseline, and what a working black frame should show

**Baseline** [M]. 2-s current from 09-24 15:15Z → 09-25 11:57Z (20.7 h,
n = 36,420), from Bill's two exports joined. HW counters are available to
09-25 02:12Z.

| quantity | coexistence OFF (measured) | black frame, *if* it behaves like the three lit windows (projected) | + §6.2 ADC timing (projected) |
|---|---|---|---|
| 2-s sd | 4.98 mA (hourly 4.69–5.34) | **~2.0 mA** (lit 1-min sd 1.7–2.9 mA, review §8.2) | ~1.4 mA |
| positive readings | 5.6 % (~2,600 a day) | ~1 a day [D: P(N(−8, 2) > 0) = 3 × 10⁻⁵] | ~0 |
| daily extremes | −36 / +20 mA | about −17 / +1 mA [D: ±4.3σ] | about −14 / −2 mA |
| sd of 1-min means (2-s samples) | 0.94 mA | ~0.37 mA [D: 2.0 / √29] | ~0.26 mA |
| per-minute CHARGE drain scatter | 0.78 mA | ~0.4 mA (lit: 0.39–0.45 mA) | ~0.3 mA |
| hourly CHARGE drain scatter | 0.13 mA (10 h) | 0.1 mA or less; the slow component may set the floor | — |
| ENERGY gauge | 0.455 W | ~0.22 W [D: σ_conv 19 mA, μ −8 mA] | — |
| mean drain | −7.71 (2 s) / −8.01 (CHARGE) mA | the same, plus the panel-on current, ~0.3 mA at the bank for ~1 mA at 3.3 V [I] | same |
| SW ledger (±50 mA deadband) | books **0 %**: nothing crossed ±50 mA in 20.7 h | books **0 %**; the displayed SOC stays frozen | 0 % |

**What a working black frame changes for SOC**, with coexistence already OFF:

- **Almost nothing today.** The quiet state already has no regime DC error to
  remove.
- **It fixes neither the frozen SOC display nor B1.** V1.28 fixes the
  display. P-1 fixes B1.
- **Its SOC value is insurance.** A router reset turns coexistence back ON by
  default (turnover §4). Then the unlit monitor returns to ~18 mA sd, with a
  ~0.9 mA DC error while noisy (≤ 0.16 %/mo). The lit windows held −10.3 mA
  and 0.23 W in both regimes. On 09-22 the unlit drain moved ~0.9 mA across
  the router change while the lit drain did not (−10.26 → −10.37) [M, n = 1
  per side].

**What it changes for the CURRENT channel:**

- 2.5× less noise
- positive readings essentially gone
- a mean that no longer depends on the router

That helps the runtime display, the idle state thresholds and HA graphs.

**What it leaves.** The lit per-conversion error (σ ≈ 19 mA) is still ~10×
the chip's 2 mA. The §6.4 filter and lead dress are still needed to reach
the 0.16 mA per-reading floor.

**TB-4(b) pass criteria:**

- Within one minute of lighting a black frame, 3 times out of 3, nobody
  present:
  - 5-min sd ≤ 3 mA
  - per-minute ENERGY ≤ 0.25 W
- The noise returns within 2 min of switching the frame off.

**What the result would mean:**

- **If (b) passes,** the panel-on state suppresses the noise, not the load.
  That would argue against A's load-level mechanism (§3.3) and point the root
  cause at an interaction between the panel and the 3V3 rail.
- **If (b) fails but (a)/(c) pass,** the load level drives it. A holds, and
  P-5 is the hardware twin.

### 3.7 Offline gaps: the counters bridge them, and the noise drops in every one

**Why the counters can see an offline window.** CHARGE and ENERGY accumulate
inside the INA228 whether or not the ESP is on the network. The firmware
keeps reading them every 60 s over I²C (lines 1659–1712), so the first value
published after a gap gives the average over the gap [S: firmware; DS
§7.3.1].

**Every data gap ≥ 150 s in the 60-s record** [M] (09-10 08:12Z → 09-25):

| gap (UTC) | length | ENERGY in gap | ENERGY 10 min before | drain in gap | drain 10 min before | likely cause [I] |
|---|---|---|---|---|---|---|
| 09-12 21:54 → 21:57 | 2.9 min | **0.225 W** | 0.627 W | −9.31 mA | −7.18 mA | unknown: no `unavailable` in the Display Button export |
| 09-15 13:54 → 15:01 | 66.9 min | **0.384 W** | 1.082 W | −9.96 mA | −8.79 mA | HA down. Button shows `unavailable` at 15:01:24 and `off` at 15:01:26, the restart-then-reconnect pattern |
| 09-18 15:11 → 15:14 | 2.9 min | 0.696 W | 1.255 W | −9.20 mA | −9.60 mA | a restart or flash that day (button `unavailable` 15:10:49 and 15:13:55) |
| 09-18 23:44 → 23:48 | 4.1 min | 0.537 W | 1.267 W | −10.61 mA | −9.84 mA | HA restart pattern at 23:48:33 |

**What the gaps show:**

- **The noise gauge fell in all four gaps,** by 45–65 %.
- **The 67-min gap is the clean one.** If HA was down, the ESP stayed on
  Wi-Fi and simply stopped sending API traffic. The gauge went from 1.08 W
  to 0.38 W in a noisy period.
- **So the ESP's own traffic looks like part of the modulator.** That is B,
  or A driven by the TX load. It is not the router.
- **Caveats:**
  - The causes are inferred. Bill should confirm the HA restarts.
  - Each gap includes up to ~1 min of normal operation at each edge.
  - The drain in the gaps also moved, 0.4–2 mA more negative in three of
    four. It is not yet known whether that is real current or DC error.

---

## 4. The energy balance (review B1)

**Firmware.** `power_save_mode: none` becomes `WIFI_PS_NONE` [S: ESPHome].

**Expected draw, 3.3 V side** [S: C3 Table 5-7, DS §6.5; D]:

| item | current |
|---|---|
| ESP receiving | 84 / 87 mA |
| INA228 | 0.64 mA |
| breakout LED | ~0.13 mA |
| status LED | 0.6 mA |
| **total** | **85.4–88.4 mA**, plus 0.2–4.6 mA of TX |

**Expected draw, bank side:** I = 3.3 × I₃V₃ / (η × 13.30).

- η = 0.90: **23.5 mA**
- η = 0.80: **27.4 mA**
- even at η = 1: **21.2 mA**

**Measured:** 7.3–8.2 mA [M].

- **Gap: 15.3–20.1 mA** (≥ 13.0 at η = 1).
- That is **5.7–7.5 µV**, or 6–7× the datasheet's ±1 µV offset limit.

**The lit-OLED check.** With the interference suppressed, the bank reads
−10.3 mA. The expected value is (23.5–27.4) + 2.5 = 25.9–29.8 mA. The gap,
15.6–19.5 mA, is the same, so **the gap is not the noise's DC part.**

**Bus contents** [Bill]. Only the batteries, the monitor and the inverter
(connected, off) are on the bus.

- No charger, so there is no charge source that could make the reading too
  small.
- The inverter's off-state draw, if any, is on the load side, so it adds to
  the true discharge and widens the gap.

**What is left:**

1. The ESP draws ~⅓ of its datasheet receive current with power save off.
   [I, unlikely]
2. **A static in-situ offset of +5.7–7.5 µV**, for example thermal EMF at
   dissimilar-metal joints or the board. Bill rules out a bypass by
   construction.

**The 08-26 report.** Report §7.1 reconciled 7.4 mA with a DTIM power-save
draw, which the firmware does not use. The header's "~100 mA" (line 79)
matches the 3.3 V side. The report's R13 note needs its own R13.

**SOC consequence if (2) holds:**

- **Rate.** 1 mA-month = 0.184 % of 397 Ah, so the error is 15.3–20.1 ×
  0.184 = **2.8–3.7 %/mo**.
- **Since the 07-16 anchor** (1,686 h):
  1. 15.3 × 1,686 = 25.8 Ah = 6.5 %
  2. 20.1 × 1,686 = 33.9 Ah = 8.5 %
  3. Both come on top of the turnover's 3.3 %, so the true SOC is **~88–90 %**.

**Temperature split** (Rev 1). The report §7.5 link is mostly the monitor's
own heating, and it changed 4× at the rewire. The ambient coefficient,
0.36–0.45 µV/°C, is 36–45× the DS's ±10 nV/°C.

**How to settle it:**

- **P-1, the DMM reading.** Do it lit and unlit.
  - Zero ≥ reading + I_TB1. The inverter's off-draw can only add to the
    true discharge.
  - **Prediction:** I_TB1 ≈ 23–28 mA.
- **TB-1, radio off.**
  - The ESP drops to 16–28 mA [S: C3 Table 5-8], which is **4.8–9.1 mA** at
    the bank.
  - Readings above −4.8 mA prove an offset.
  - Under A, radio off also changes the load on the buck. Read the noise part
    of TB-1 with that in mind.

---

## 5. Tests

### 5.1 One diagnostic build (firmware only, controlled at runtime from HA)

**Built:** `INA228 Monitor/battery-bank-monitor-diag.yaml` (V1.27-diag1). The
run sheet, with install steps, run order, how to read results and exports,
is `INA228 Monitor/diag-test-runsheet.md`.

**Validation, on ESPHome 2026.9.0:**

- blast radius: only 3 version lines changed
- config valid
- codegen OK
- all 42 DIAG lambdas compile against stubs of the real signatures

**Not validated here:** the full compile. The sandbox could not reach
`api.registry.platformio.org`, so Device Builder's compile is the final gate.

**Deviation from the plan below:** TB-4(d) uses a **1 ms** loop interval,
not 0. At 0, ESPHome's loop never sleeps, which would starve the idle task
and risk a watchdog reset.

**When:** run it now, in the quiet state. **Scope:** keep it separate from
V1.28. **Gate:** `esp-firmware-validation`.

**TB-4: OLED and load variants, nobody present, 5 min each, 3 times each. Run
this first.**

| variant | how | if A (load level) | if the panel itself | if presence |
|---|---|---|---|---|
| a. lit, normal page | `turn_on`, page_main | low | low | high |
| b. lit, black frame, contrast 0 | panel on, ~no pixel current | high | low | high |
| c. lit, all white | maximum pixel current | low | low | high |
| d. panel off, CPU spinning | `App.set_loop_interval(0)` for 5 min; the CPU stops idling, adding ~7 mA [S: C3 Table 5-8, 16 → 23 mA] | low | high | high |

- **"Low"** means ENERGY ≈ 0.23 W and 2-s sd ≈ 2 mA.
- **About (d):** `Application::set_loop_interval()` exists, with a default of
  16 ms [S: ESPHome `core/application.h`, dev]. Two things are [I]: whether
  0 keeps the CPU from idling, and whether the call behaves the same in
  2026.9.0. P-5 is the cleaner load test.
- **If (b) is low,** a black lit panel is a burn-in-free stopgap for the
  CURRENT channel.

**TB-1: Wi-Fi off, 10 min.**

- **How:** `wifi.disable` → 10 min → `wifi.enable`. On the device, keep n,
  mean, sd, min and max of the 2-s current, plus ΔCHARGE/Δt and ΔENERGY/Δt.
  Publish them on reconnect.
- **Expected:**
  - The mean should rise 15–22 mA (B1).
  - B (radio): noise → floor.
  - A: noise changes with the new, lighter load; the direction is not
    predicted.

**TB-2: TX-power ladder.**

- **How:** `esp_wifi_set_max_tx_power(dBm × 4)`, 20.5 → 8.5 dBm, 15 min per
  step.
- **Expected:**
  - B (radiated): sd × 0.27 at −11.5 dB.
  - A: a smaller change, because the load steps shrink.
  - C: flat.

**TB-3: averaging ladder.**

- **How:** AVG ∈ {1, …, 1024}, 5 min each.
- **Expected:** AVG 1 gives the per-conversion σ and kurtosis directly.
  CHARGE is untouched [S: DS §7.3.1].

**TB-5: preview §6.2 item 2.**

- **How:** ADC_CONFIG = 0xFDC5.
- **Expected:** sd × 0.71.

**Passive additions:**

- a 5-min on-device sd
- the AP bandwidth, from `esp_wifi_sta_get_ap_info()`
- the reset reason

**Notes, unchanged from Rev 2:**

- **TX power.** The script must restore it. ESPHome re-applies nothing,
  because `output_power` is unset.
- **TB-3 and the SW ledger** books ≤ 0.6 mAh per 5-min step.
- **TB-3 and the ALERT limits** compare averaged values (SLOWALERT).

### 5.1a Getting data while Wi-Fi is off

HA records nothing while the ESP is off the network. Three sources still
work:

1. **INA228 counters (free, any firmware).** ΔCHARGE/Δt and ΔENERGY/Δt
   across the gap give the mean current and the per-conversion noise gauge
   (§3.7).
   - Edge dilution: the average includes up to ~1 min of normal operation at
     each end. A 30-min window keeps that under ~7 %, and the on-state rate
     corrects it.
2. **On-device statistics (test build).** During the window the ESP keeps
   n, Σi, Σi², Σi³, min, max, the count > 0, and the lowest and highest 1-min
   sd of the 2-s current. It also snapshots CHARGE and ENERGY at the start
   and end, then publishes it all after `wifi.enable`.
   - RAM cost: a few dozen bytes.
   - The same code runs a matched Wi-Fi-on window just before and just
     after, so the comparison is like for like.
3. **Optional raw replay (test build).** Keep the 300 × 2-s samples of a
   10-min window in RAM (1.2 KB). After reconnect, publish them as a burst on
   a diagnostic sensor.
   - HA stores them with arrival times, but the order and values survive, and
     the sample spacing is known (2 s).

**Ways to create the offline window:**

| method | radio state | firmware | tests |
|---|---|---|---|
| **Disable the device in HA** (Settings → Devices & services → ESPHome → the device → Disable), 30 min, then re-enable | on, associated, ~no API traffic | none | "does the ESP's own traffic drive the noise?" The 09-15 gap suggests yes |
| router off | on, scanning (probe TX) | none | not radio-off; mixed |
| **`wifi.disable` → 10 min → `wifi.enable`** (TB-1) | **off** | test build | radio vs not; B1 sign test (mean should go positive) |

**Safety of TB-1.**

- CORE keeps running locally: SOC integrators, watchdog, alarms, OLED, LED.
- `reboot_timeout: 0s` on api and wifi (lines 536, 555), so losing the API
  does not reboot the device.
- `enable_on_boot` defaults to true [S: ESPHome], so any reboot brings Wi-Fi
  back.
- Cost: HA sees nothing for the window. Run it at idle.

### 5.2 Physical tests (Bill's call, R14)

**P-5: preload.** Clip a 220–330 Ω resistor (¼ W: 3.3² / 220 = 50 mW) between
the carrier's **3V3** and **GND** test points [P] for 10 min, then remove it.

- It reproduces the OLED's load with no display and no person.
- It is the physical twin of TB-4 (d).

**P-1: DMM in series with TB1 BATT_RAW.**

- **Avoiding a reboot:** clip the DMM across the F1 holder, then pull F1.
- **Reading:** a ≥ 1 min average, taken both lit and unlit, with the HA
  current over the same minutes.

**P-2a and P-2b: shorts.** At the INA228 terminal block, then at the shunt
end (§3.4).

**P-4: dress the input wires.**

- Twist VIN+/VIN− tightly right into the terminal.
- Route them away from U3/C4 and from the OLED harness.
- Compare noise before and after.
- It is cheap. Under A, it may be most of the fix.

**P-6 (optional): an oscilloscope, if one is available.**

- **Probe:** the buck's 3V3 output ripple or switch-node timing.
- **Compare:** OLED on vs off, and with the P-5 preload. It shows mode hopping
  directly.

---

## 6. SOC and accuracy updates

### 6.1 Keep from the two docs

Keep the V1.28 core:

- CHARGE-based SOC with the anchor
- B2 (a)–(c)
- the B3 ladder
- O1 and O2
- the review §4–§5 budgets

**Datasheet checks** [S: DS]:

- POR at VS < 1.26 V
- SHUNT_CAL resets to 1000h, ADC_CONFIG to FB68h, TEMP_LIMIT to 7FFFh
- the oscillator is ±0.5 % / ±1 %

**Budget row, corrected by Rev 3.** The review's "noisy excess 0.88 mA, if
none is real: ≤ 0.16 %/mo, only while noisy" **stands** (§3.1). Rev 2 had
called the excess real. It is a DC error of the interference, which CHARGE
integrates as if it were drain. The P-4, §6.4 and stopgap fixes remove it.

### 6.2 Firmware items

1. **An in-situ offset term.**

   ```
   ah_net = (hw_charge_ah - anchor) - I_off_A * hours_since_anchor
   soc    = 100 + ah_net / ${validated_capacity_ah}f * 100
   ```

   - `I_off` defaults to 0 until P-1 measures it. Publish its value and
     source.
   - The anchor re-seed resets the hours, and the term applies to the
     provisional anchor too.
   - Publish Ah-below-full.

2. **Double the shunt integration time at the same cycle time.**
   - **Config:**
     `adc_time: {bus_voltage: 2074us, shunt_voltage: 4120us, temperature: 50us}`
     and `adc_averaging: 256`.
   - **Arithmetic:**

     | | now | proposed | change |
     |---|---|---|---|
     | cycle | 1.582 s | 256 × 6.244 ms = 1.598 s | ≈ same |
     | shunt time per reading | 0.527 s | 1.055 s | × 2 |
     | bus time per reading | 0.527 s | 0.531 s | ≈ same |

   - **Noise table** [S: DS Table 8-2]: 2074 × 256 = 19.7 bits, the same as
     4120 × 128.
   - **Effect:** external white interference sd × 1/√2. The bus channel
     scaling is [I]; TB-5 checks it.

3. **`max_current` 200 → 400 A.**
   - CURRENT spans ±max_current [S: DS Eq. 3, §7.6.1.8], so today it spans
     ±200 A.
   - **So the 350 A guard (line 339; uses at 1347, 1369, 1396, 1413, 2002)
     can never trip.** An open Kelvin lead reads ≤ 200 A.
   - **Above the range,** MATHOF means "current and power data may be
     invalid" [S: DS DIAG_ALRT bit 9].
   - **The coincident peak is out of range:** CHANGELOG 2026-08-27 records
     274–297 A.
   - **At 400 A,** SHUNT_CAL = **3750** [S: DS Eq. 2]. That is distinct from
     the POR value 4096, so B2(a)'s readback still works.
   - **Review §9 becomes mandatory:** one substitution drives the lambda
     literal (lines 1676 and 1707) and `max_current`.

4. **Freshness predicate (B2c).** Add the now-reachable |I| test.

5. **RECON uncertainty** (lines 2346–2352).
   - "Offset ~mAh negligible" is wrong: ±2.67 mA × 1,440 h = 3.8 Ah, and B1's
     gap is 22–29 Ah over 60 days.
   - Add σ_offset × hours to sigma.
   - U = offset + invisible drain + CE error, which is the lumped term SOC
     needs.

6. **Re-zero** after any shunt, lug, monitor-wiring or router move (§3.5).

7. **Optional stopgap.** A "noise-suppression" mode keeps the panel on with a
   black frame at contrast 0, or whichever TB-4 variant proves sufficient.
   - Cost: the panel-on current, CHARGE-counted. At most ~2.5 mA × 730 h =
     1.8 Ah/mo of real drain (0.46 %/mo) if a lit page were needed.
   - It helps the CURRENT channel (runtime, thresholds, Ri) and removes the
     regime-dependent DC error. Not a substitute for §6.4.

8. **Comment corrections.**

   | line | now says | should say |
   |---|---|---|
   | 79 | "~100 mA" | 3.3 V side; add the bank-side figure after P-1 |
   | 345 | the 50 mA comment | 50 mA = 131 LSB; floor 0.16 mA |
   | 1267–1270 | the `reset_on_boot` comment | load-bearing under V1.28 |

   Also wiring summary §5.2's "5–10 mA floor", which is interference.

### 6.3 Observability

- **ENERGY idle rate as a live noise gauge.** 0.23 W means suppressed;
  0.4–0.6 W quiet; 0.9–1.4 W noisy.
- A 5-min on-device sd.
- The AP bandwidth.

### 6.4 Hardware, ordered by how likely each is to matter under A

1. **Input filter at the breakout terminal block** [S: DS §8.1.4, Fig. 8-1]:
   - **10 Ω in series with each input.** TI's dV/dt value. Gain error
     20 / 92,020 = 0.022 %, against R_DIFF = 92 kΩ [S: DS §6.5].
   - **1 µF ceramic across VIN+/VIN−.** The corner is 1 / (2π × 20 Ω × 1 µF)
     = 8 kHz, about 40 dB down at 1 MHz.
   - **Plus 100 pF–1 nF C0G at the pins,** for 2.4 GHz [I].
   - Bias-current offset ≤ 2.5 nA × 10 Ω = 25 nV (0.07 mA) [D].
2. **Lead dress (P-4).** Twisted to the terminal; away from U3/C4 and the
   OLED harness.
3. **Regulator.** Only if P-5 or P-6 confirm mode hopping:
   - a permanent small preload, or
   - a regulator with forced PWM, or
   - move U3 or put a ferrite/LC on its input, or
   - increase the U2–U3 spacing on a Rev 1.2 board.
4. **Antenna.** Move it away from the breakout, ideally outside the enclosure,
   and/or lower `output_power`. RSSI −30 to −39 dBm leaves room.
5. **Standing zero (optional).** A second, unmodified INA228 (15 mΩ, 0x41) in
   series with BATT_RAW: ±0.07 mA [D]. Valid while the bus is otherwise idle.

### 6.5 Idle accuracy after each step

| state | idle SOC error | basis |
|---|---|---|
| today, SW ledger, quiet | 1.34 %/mo low against the measured drain | turnover |
| V1.28 as designed, if B1 is an offset | 2.8–3.7 %/mo high | §4 |
| V1.28, if B1 closes | ≤ 0.49 %/mo + wander + noisy DC ≤ 0.16 %/mo + invisible | review §4, §3 |
| V1.28 + P-1 zero | ~0.1 %/mo + ±0.28 %/mo wander + noisy DC + invisible | [D] |
| + filter / lead dress, if they remove wander and DC | ~0.1 %/mo + invisible | acceptance: ENERGY ~0.23 W or lower unlit; §3.5 table flat across a move |

---

## 7. Corrections to records (R13)

1. **Report 08-26 §7.1.** The DTIM premise is wrong. Monitor 23.5–27.4 mA
   [S].
2. **Report 08-26 §7.5.** The temperature link is mostly the monitor's own
   heating.
3. **Report 08-26 §7.3.** The 08-04 step came with an RSSI step and a noise
   change. Geometry near U3 is a candidate alongside thermal EMF.
4. **Firmware.** The 350 A guard is unreachable at 200 A.
5. **Firmware.** The RECON "offset ~mAh" comment.
6. **Wiring summary §5.2.** The noise floor.
7. **Review §8.2 / Q1.** The third state = the lit OLED. Closed.
8. **Rev 2 of this doc (self-correction).**
   - "The 0.88 mA is real radio current": wrong on the lit-OLED evidence.
   - "Most probably the ESP's radio": superseded by A.
   - The review's budget row stands.
9. **Turnover §4.** Candidates (a) own radio and (b) router RF on the leads
   become A (buck), B (radio), C (router, effectively out).
10. **Wiring summary §4.2.** The sense pair should be twisted; the photo
    suggests it is not inside the enclosure [P, to confirm].

---

## 8. Data

### 8.1 Received, 2026-09-25

| item | finding | section |
|---|---|---|
| Display Button (09-10 →) | third state = the lit OLED | §3.1 |
| HW Energy / Net Charge (07-17 →) | per-conversion gauge; lit-OLED collapse; zero steps | §3.1, §3.5 |
| WiFi Signal (07-28 →) | router field 0.16–0.44 V/m; RSSI steps at moves | §3.2, §3.5 |
| current, 2 s (09-24/25) | 11 h quiet since coexistence OFF | §0.1 |
| temperatures | the ESP warmer when noisy (weak) | S12 |
| photos | U3 ~1 cm from the INA228 terminal block; untwisted inputs; antenna beside the breakout | §3.2 |
| bus contents | batteries, monitor, inverter (off) only | §4 |
| step dates | cause unknown | §3.5 |

### 8.2 Still needed

1. **A current photo** of the INA228 terminal block, the input wires and U3.
   Photo 3 looks like July.
   - Are VIN+/VIN− twisted?
   - Which red wire is which?
   - How do the wires run outside the box to the shunt?
2. **Commissioning Tier 2:**
   - Where were the inputs shorted?
   - What sign did the 0.9 µV have?
   - What was the sd while shorted?
   - Was Wi-Fi on?
3. **The Kelvin screw metal and lug plating** (for thermal EMF, B1).
4. **Whether an oscilloscope is available** (P-6).
5. **Optional exports:**
   - Display Button for July
   - 2-s current for 09-10 → 09-24

**Tests** (each needs Bill's go):

- TB-4 first, then TB-1, TB-2, TB-3 and TB-5
- P-5, P-1, P-2a/b and P-4

---

## 9. Suggested order

1. **TB-4 and P-5.** Cheap, and they decide A vs the panel vs presence.
2. **TB-1.** Settles B1's sign test, and radio vs not.
3. **P-1, lit and unlit.** Sets `I_off`.
4. **P-4 (lead dress) and the §6.4 filter.**
   - Acceptance: unlit ENERGY near 0.23 W or lower, and the unlit 2-s sd near
     2 mA, in both regimes (coexistence toggled).
   - Then a deliberate router move shows a flat §3.5 table.
5. **The R1 statement for V1.28:**
   - §6.2 items 1–6 (and 7 if wanted)
   - plus B2, B3, O1 and O2
   - then turnover gates 2–6
