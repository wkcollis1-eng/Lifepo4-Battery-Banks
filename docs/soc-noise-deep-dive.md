# Battery-bank SOC: noise root cause and INA228 accuracy (deep dive)

**Rev 2, 2026-09-25.** Rev 1 (commit `961e077`) was written without the
datasheets or Bill's exports. Rev 2 adds both:

- **Datasheets**, now in the repo:
  - `INA228 Monitor/ina228.pdf`: TI SLYS021A, January 2021, revised May 2022
  - `INA228 Monitor/esp32-c3_datasheet_en.pdf`: Espressif, version 2.1
- **Bill's HA exports:**
  - `current` (2 s): 09-24 14:16 → 09-25 02:16 UTC
  - `HW Net Charge` and `HW Energy`: 07-17 → 09-25. Hourly statistics until
    09-10 08:00Z, then 60 s.
  - `WiFi Signal` (RSSI), from 07-28
  - `Display Button`, from 09-10
  - three temperatures: ESP32 internal, INA228 die, pack

The exports are not committed here. The derived hourly table is described in
§3.6.

**Scope.** This reviews `docs/soc-accuracy-turnover.md` (the **turnover**)
and `docs/soc-v128-review.md` (the **review**) against:

- firmware **V1.27**, `INA228 Monitor/battery-bank-monitor.yaml` (2,705
  lines). Line numbers are this copy's and match both docs.
- the wiring summary (Rev 1.10) and the commissioning report
- the 2026-08-26 report
- the INA228 data in `data/`

**Nothing is built.** V1.28 still waits on Bill's go (R12). Physical work is
Bill's call (R14).

**Evidence tags:**

- **[M]** measured
- **[D]** derived, with the chain shown
- **[S]** source document read this session. "DS" means the INA228 datasheet
  and "C3" the ESP32-C3 datasheet.
- **[I]** inference, not yet checked

**What remains unverified:**

- the Pololu D24V7F3 efficiency. The site is blocked, so η = 0.80–0.90 is
  [I].
- antenna gains and distances [I]

**Other sources read:**

- ESPHome `dev` source (2026.10.0-dev, commit `4a2f17b`; the device runs
  2026.9.0)
- Adafruit's `Adafruit-INA228-PCB` design files

---

## 0. Answers

### 0.1 The noise source

- **The noise is not current** (§2):
  - It reads positive when nothing on the bus can charge the bank.
  - Its skew is about 100× too small for any train of sampled discharge
    pulses.
  - The monitor's real Wi-Fi bursts add at most ~0.35 mA of scatter.
- **It is an error voltage inside the measurement.** It is 2–7 µV rms per
  averaged reading, and ~16–51 µV rms per single conversion [M/D, §3.3]. It
  enters at inputs with **no filtering between the field wiring and the
  silicon** [S: Adafruit schematic]. TI's own input-filter guidance names
  exactly this risk. DS §8.1.4: "transients that occur at or very close to
  the sampling rate harmonics can cause problems … at 1 MHz and higher …
  managed by incorporating filtering at the input".
- **The source is very probably the monitor's own ESP32-C3 transmitting.**
  Three independent lines point there:
  1. **One model fits both regimes and the drain difference.** Noise variance
     ∝ the ESP's TX airtime. It reproduces both regimes and the 0.88 mA
     noisy-state drain with 0.11–0.17 % (quiet) and 1.2–1.8 % (noisy) airtime
     [D, §3.2].
  2. **The ESP chip runs warmer when the noise is higher.** This does not
     involve the INA228 at all [M, weak, §3.2].
  3. **The router's measured field at the monitor is far weaker than the
     ESP's own.** RSSI of −30 to −39 dBm means 0.16–0.44 V/m from the router,
     against an estimated 11–22 V/m from the ESP's antenna if it sits
     10–20 cm away [D/I, §3.1].

  The router's coexistence setting changes *how much the ESP transmits*. It
  does not change the coupling path. **This is still [I] until TB-1 and TB-2
  run (§5).** Both are firmware-only and can run now, in the quiet state.
- **The "third state" is the OLED being lit** [M]. `Display Button` was
  pressed at 14:22:52, 12:02:45 and 14:16:32 EDT. Those are exactly the
  starts of review §8.2's three windows (09-11, 09-18, 09-22).
  - The +3.2 mA is the OLED's own current, and the shunt sees it.
  - Why the noise falls to ~2 mA while it is lit is still open (TB-4).
- **Coexistence OFF held for the 11 h exported** [M]:
  - sd 5.0 mA, skew 0.011
  - no 5-min block above 9 mA

  That partly scores the review §8.1 prediction.

### 0.2 SOC and accuracy

- **The largest SOC term is the unmeasured zero, and the datasheet makes it
  larger than Rev 1 said.**
  - `power_save_mode: none` becomes `WIFI_PS_NONE` [S: ESPHome], so the
    receiver is always on.
  - Receive current is **84 mA (HT20) / 87 mA (HT40)** [S: C3 Table 5-7].
  - The monitor should therefore draw **23.5–27.4 mA** from the bank. Even
    through a lossless regulator it would draw **21.2 mA**.
  - The shunt reads **7.3–8.2 mA** [M].
  - **Gap: 15–20 mA** (≥ 13 mA at η = 1) [D, §4].
- **If the gap is an in-situ offset:**
  - V1.28 inherits **2.8–3.7 %/mo**.
  - The true SOC today is **~88–90 %, not ~96.7 %** [D, conditional].
- **The zero also moves.** The CHARGE-register drain steps by 1–3 mA at
  physical events: the 08-04 rewire, the 08-31 power loss, the 09-22 router
  power-down. RSSI steps at the same hours. There was also one step with no
  RSSI change, on 08-19 [M, §3.6]. So a one-time zero is necessary but not
  sufficient. The RF pickup has to go, or RECON has to track the residual.
- **How to settle the gap:**
  - One DMM reading (P-1).
  - TB-1 does it for free if the monitor is on the shunt. With the radio off
    the true draw is 4.8–9.1 mA [S: C3 Table 5-8; η I], so the reading
    should go **positive** (≈ +7 to +15 mA). Any reading above −4.8 mA
    proves an offset.
- **V1.28's core design stands.** CHARGE accumulates *each conversion*,
  unaveraged [S: DS §7.3.1, Fig. 7-2]. So it integrates zero-mean
  interference to zero.
- **Firmware items beyond the review** (§6.2):
  - an in-situ offset term
  - 2× shunt integration time at the same cycle time. The noise table shows
    the bus channel loses nothing [S: DS Table 8-2].
  - `max_current` 400 A, because the 350 A guard can never trip today
  - an honest RECON uncertainty

### 0.3 Data

- Received and used: §8.1.
- Still needed: §8.2.

---

## 1. Signatures any explanation must meet

| # | Signature | Source |
|---|---|---|
| S1 | Noisy: mean −8.28 / sd 18.11 mA. Quiet: −7.22 / 5.44 mA | [M] turnover §3, review §2 |
| S2 | White at 2 s (lag-1 −0.004 in Bill's 09-24 export, both regimes) | [M] review §2; this review |
| S3 | Symmetric: skew 0.011–0.016 in the long windows. Positive readings: 8.7 % (quiet, Sept) and 17.5–19 % (July). 6.1–6.2 % of noisy samples > +20 mA | [M] turnover §4, review §7, this review |
| S4 | Hourly CHARGE scatter 0.39 mA = 18.11 / √2278 | [M/D] review §2 |
| S5 | The regime follows the router. Coexistence OFF gave 11 h of quiet (sd 5.0 mA) with no 5-min block > 9 mA | [M] turnover §4, review §8.1, 09-24 export |
| S6 | Noisy draws 0.88 mA more (t = 10.7) | [M] turnover §3 |
| S7 | Third state = OLED lit: the button press precedes each window by < 1 min | [M] `Display Button` export |
| S8 | The chip floor (0.16 mA per reading [D: DS Table 8-2]) is never reached | [M/D] review §7 |
| S9 | July idle: sd 7.2–7.8 mA, skew 0.02–0.20, lag-1 ≤ 0.02 | [M] `data/ina228 Amperage.csv` |
| S10 | ENERGY at idle: 0.46 W quiet, 1.44 W noisy, 0.82–0.85 W through July. The true power is ~0.1 W | [M] HW export, §3.3 |
| S11 | Drain and noise level step at physical events, and not in proportion | [M] HW and RSSI exports, §3.6 |
| S12 | The ESP32 die runs ~0.5 °C warmer in noisy hours | [M] ESP temperature export, §3.2 |

---

## 2. Why the noise is not current

### 2.1 Sign

At idle, nothing on the bus charges the bank (the inverter is off; the
charger's state is question §8.2-1). Every consumer, the monitor included,
returns through the shunt as discharge. A true reading can never be positive,
yet 5.3–8.7 % of quiet samples and 17.5–19 % of July samples are [M].
**Those readings are error.** A trickling charger would add a DC current,
never zero-mean scatter.

### 2.2 Shape

Suppose the scatter came from real discharge-direction pulses: Wi-Fi TX,
CPU, the LED. The INA228 samples them in its shunt conversion windows.

For Poisson or clustered arrivals with positive pulse sizes *a*, one reading
has:

```
N pulses per reading ~ Poisson(mu)
mean contribution  m    = mu * E[a]
variance                = mu * E[a^2]
skew                    = E[a^3] / (E[a^2]^1.5 * sqrt(mu))
skew / (sd / m)         = E[a^3] * E[a] / E[a^2]^2  >= 1   (Cauchy-Schwarz)
```

So **skew ≥ sd / m**, and *m* cannot exceed the whole mean:

| | sd | m ≤ | skew must be ≥ | measured skew |
|---|---|---|---|---|
| noisy | 18.11 mA | 8.28 mA | 2.19 | 0.016 |
| quiet | 5.44 mA | 7.22 mA | 0.75 | 0.012 |

Both miss by two orders of magnitude.

### 2.3 Size

Take the airtime model of §3.2: ~1.5 % extra TX airtime in the noisy state,
in pulses of ~53–78 mA at the bank.

1. For 0.2–1 ms frames, the pulse rate is 15–75 per second.
2. Each reading has 0.527 s of shunt time, so it catches N = 8–40 pulses.
3. Each pulse moves a reading by ~63 mA × d / 0.527 s = 0.024–0.12 mA.
4. The scatter is (per-pulse shift) × √N = **0.15–0.34 mA** [D].

Real radio current appears in the mean, not in the noise.

---

## 3. Where the error enters

### 3.1 The input is wide open, and the ESP is the strongest transmitter nearby

- **No filter on the breakout inputs.** Net VIN+ is IC1, X1-3, R1, SJ1 and
  JP2-7. Net VIN− is IC1, X1-1, R1 and JP2-6. There is no R or C on either
  [S: `Adafruit INA228 I2C Power Monitor.sch`, parsed]. R1 (15 mΩ) was
  removed.
- **TI's recommended filter is absent.** The recommendation: R ≤ 100 Ω and
  0.1–1 µF ceramic. Also, "10-Ω resistors in series with each input"
  protect against dV/dt events [S: DS §8.1.4, Fig. 8-1].
- **Why RF matters here.** The ADC's time base is a 1 MHz oscillator [S: DS
  §6.5, FOSC]. TI flags interference "at or very close to the sampling rate
  harmonics". Broadband RF energy, or RF demodulated by the input
  structures, lands there.
- **The sense pair** is 22 AWG, twisted, unshielded. Its length and
  untwisted fan-out are not recorded.
- **The antenna.** The XIAO's U.FL antenna is in the same enclosure (wiring
  summary §8.2 step 6).

**Fields at the monitor:**

- **Router, from measured RSSI** [D; 2 dBi assumed]. The effective aperture
  is A = G λ² / 4π = 1.58 × 0.125² / 12.57 = 0.00197 m².
  - −30 dBm (1 µW): S = 1 µW / A = 5.1 × 10⁻⁴ W/m², so
    E = √(377 × S) = **0.44 V/m**.
  - −39 dBm: **0.16 V/m**.
  - RSSI ran −29 to −39 dBm over the record [M], so the router is close.
- **ESP's own antenna**, estimated [I: distance and TX level]. With 20 dBm
  (0.1 W), 2 dBi and d = 0.1–0.2 m, E = √(30 × 0.1 × 1.6) / d =
  **11–22 V/m**.
- **Comparison.** The ESP's field is ~25–140× the router's in amplitude,
  during its own transmissions.

**Supply coupling is unlikely** [D, with the AC behaviour I]. Shunt offset
vs supply is ±0.5 µV/V max [S: DS §6.5 PSRR]. A 100 mV droop of the 3V3 rail
during TX would shift the input by ≤ 0.05 µV. That is ~40–140× below the
2–7 µV to explain, even before accounting for TX's ~1 % duty. It works only
if the rejection at the burst frequencies is far worse than the DC figure.

### 3.2 One model fits both regimes: noise variance ∝ the ESP's TX airtime

**Assumption.** Each ESP TX burst adds an independent error at the input.
Then:

- noise variance ∝ airtime *T*
- extra real drain = ΔT × ΔI_b

**Arithmetic:**

1. Variance ratio: 18.11² / 5.44² = 328.0 / 29.6 = **11.08** [D from M].
2. TX minus RX current at 3.3 V [S: C3 Table 5-7]:
   - 278 − 87 = 191 mA (HT40 MCS7 @ 18.5 dBm)
   - 335 − 84 = 251 mA (802.11b @ 21 dBm)
3. At the bank, ΔI_b = ΔI × 3.3 V / (η × 13.30 V):
   - 191 × 3.3 / (0.90 × 13.3) = **53 mA**
   - 251 × 3.3 / (0.80 × 13.3) = **78 mA**
4. ΔT = 0.88 / (53–78) = 1.66–1.13 %.
5. T_quiet = ΔT / 10.08 = **0.17–0.11 %**.
6. T_noisy = 11.08 × T_quiet = **1.8–1.2 %**.

**Independent support: the ESP runs warmer when noisy** [M, weak].

- The ESP32 internal temperature minus pack temperature rises with the
  hourly ENERGY rate, which is the noise gauge of §3.3.
- Slope: +1.19 °F per W, r = 0.45, n = 163 h (09-10 → 09-24).
- The noisy-to-quiet change (~1.3 → ~0.47 W) predicts ≈ 1.0 °F (0.55 °C).
- The daily means match: ESP − pack fell from 34.5 °F (09-18 → 09-20) to
  33.2 °F (09-23/24).
- At a θ of 50–100 °C/W [I], 0.55 °C means ~5–11 mW. The model's extra TX
  power is 0.88 mA × 13.3 V × 0.85 ≈ 10 mW.
- The sensor steps in 0.5 °C, so this corroborates the model; it does not
  prove it. It is the only evidence here that does not pass through the
  INA228.

**What the model predicts:**

- **Wi-Fi off:** sd falls to the chip floor. That is 0.16 mA per reading
  [D: DS Table 8-2, 19.7 noise-free bits → 327.68 mV / 2^19.7 =
  0.385 µV p-p ÷ 6.6 = 0.058 µV rms ÷ 375 µΩ], in either regime.
- **Lower TX power:**
  - Radiated: sd × 10^(ΔdBm/20), i.e. × 0.27 from 20 to 8.5 dBm.
  - Conducted: about × 0.5 [I, TX current vs power level not tabulated].
  - Router as the source: flat.

**What would break it:** sd unchanged with Wi-Fi off.

### 3.3 ENERGY measures the per-conversion error, and it is not white-independent

**Why ENERGY is a gauge.** CHARGE and ENERGY accumulate *each conversion*,
and "the INA228 averaging function is not applied to these" [S: DS §7.3.1,
Fig. 7-2]. POWER is unsigned. So ENERGY's idle rate is the mean
|V × I| of *single* 4.12 ms conversions, and that makes it a per-conversion
error gauge.

**Result**, over simultaneous windows from Bill's exports [M/D; Gaussian
folded-normal inversion with μ = the CHARGE drain]:

| window (UTC) | ENERGY rate | mean \|I\| per conversion | σ per conversion | sd_avg (2 s) | σ if independent (sd_avg × √128) | variance ratio |
|---|---|---|---|---|---|---|
| noisy, 09-24 14:17–15:14 | 1.442 W | 108.5 mA | 136 mA | 19.00 mA | 215 mA | 2.5 |
| quiet, 09-24 15:20 → 09-25 02:12 | 0.456 W | 34.3 mA | 42 mA | 5.00 mA | 57 mA | 1.8 |

**What it means.** The averaged readings carry 1.8–2.5× more variance than
independent conversions with the ENERGY-implied spread would give. Two
explanations fit, and **TB-3 (AVG = 1) separates them**:

- the error is **correlated** across successive conversions (tens to hundreds
  of ms), or
- it is **impulsive**: it hits a subset of conversions hard. Heavy tails make
  mean |X| understate σ.

Either one describes bursty radio traffic. Neither describes a steady
broadband carrier sampled independently.

**Size relative to the chip.** The quiet per-conversion σ of 42 mA
(16 µV) is 21× the chip's own per-conversion noise: 2.0 mA [D: DS Table
8-2, 16.0 bits at 4120 µs × 1].

### 3.4 The third state is the lit OLED

| window (EDT) | Display Button presses (EDT) | lit until (5-min timeout) |
|---|---|---|
| 09-11 14:23–14:26 | 14:22:52 | 14:27:52 |
| 09-18 12:03–12:06 | 12:02:45 | 12:07:45 |
| 09-22 14:17–14:26 | 14:16:32, then 14:21:25 / :32 / :37 / :47 | 14:26:47 |

**The drain step is the OLED's real current.** The +3.2 mA at the bank is
~11 mA at 3.3 V [D: 3.2 × 13.3 × 0.85 / 3.3]. That is plausible for a
mostly dark SSD1306 [I]. The shunt sees the monitor's own load step, which
is consistent with the monitor being on the shunt.

**Why the noise falls while lit is open.** Candidates [I]:

- The 1 s display refresh (~1 KB over I²C at 100 kHz ≈ 0.1 s) changes the
  ESP's loop and TX timing.
- A person at the monitor changes the RF geometry.

TB-4 lights the OLED remotely with nobody present, which separates the two.

**July.** The July low-noise windows (07-15 16:30Z, 07-16 11:35Z and
20:00Z) are probably the same thing. The button export starts 09-10, so
the July history is needed to confirm it (§8.2).

### 3.5 The 2026-08-04 rewire changed RSSI, drain and noise in the same hour

Hourly, from Bill's exports [M]:

| UTC | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|
| RSSI (dBm) | −33.4 | −33.4 | −35.5 | −29.5 | −29.3 |
| drain (mA) | −6.04 | −6.08 | −5.55 | −8.33 | −9.07 |
| ENERGY (W) | 0.83 | 0.82 | 0.81 | 0.89 | 0.87 |

Something RF-relevant moved during the rewire: the antenna, the leads, or the
router. From the next day, ENERGY settled lower (0.63–0.70 W). So the
per-conversion noise *fell* while the drain grew ~3 mA more negative.

That cannot be the airtime model, which ties more drain to *more* noise
(§3.2). The report's reading of a thermal-EMF shift (report §7.3) is still
possible. An RF-geometry DC term is now equally possible.

### 3.6 The zero moves with the RF environment

Daily means from the HW exports [M]. The hourly table was built from
`HW Energy` / `HW Net Charge` differences, excluding reset and charge hours.

| period | ENERGY (W) | drain (mA) | RSSI (dBm) | what changed at the start |
|---|---|---|---|---|
| 07-21 → 08-04 | 0.82–0.92 | −5.6 to −6.9 | −33 to −35 | (post-charge) |
| 08-05 → 08-18 | 0.65–0.72 | −8.2 to −9.0 | −29 to −30 | 08-04 20Z: rewire; RSSI +4 dB |
| 08-19 → 08-31 | 0.76–0.90 | −6.6 to −8.2 | −30 → −34.7 | 08-18 22Z: ENERGY up, drain +1.2 mA, **no RSSI change** |
| 09-01 → 09-21 | 0.74 → 1.34 | −8.3 to −9.3 | −29.5 to −33 | 08-31 ~21Z: INA228 power loss (rewire); RSSI +3.5 dB, drain −1.2 mA |
| 09-22 → 09-25 | 0.40–0.60 | −7.0 to −7.6 | −36 to −39 | router power-down; coexistence OFF 09-24 |

**Findings:**

- **The drain level steps by 1–3 mA (0.4–1.1 µV).** It steps at the same
  hour as RSSI steps when something is physically moved: 08-04, 08-31 and
  09-22.
- **One step had no RSSI change** (08-18 22Z).
- **The steps are not proportional to the noise level.** 08-05: less noise,
  more drain. 09-22: less noise, less drain.
- **The 1–3 mA steps exceed the chip.** They are larger than anything the
  INA228's offset drift can do: ±10 nV/°C [S: DS §6.5] is ≤ 0.03 mA/°C.
- **For SOC:**
  - A single in-situ zero (P-1) removes the 15–20 mA question.
  - It leaves a ±1.5 mA wander (±0.28 %/mo) that moves whenever the RF
    geometry does.
  - Removing the pickup (§6.4) should remove the wander. Re-running this
    table after the fix is the acceptance test.

---

## 4. The energy balance (review B1), from the datasheets

**Firmware.** `power_save_mode: none` (line 554) becomes `WIFI_PS_NONE` [S:
ESPHome `wifi_apply_power_save_()`]. The receiver never sleeps.

**Expected draw, 3.3 V side:**

| item | current | source |
|---|---|---|
| ESP32-C3 receiving | 84 mA (HT20) / 87 mA (HT40) | [S: C3 Table 5-7] |
| INA228 | 0.64 mA typ | [S: DS §6.5, IQ] |
| breakout power LED | ~0.13 mA | [D: (3.3 − ~2.0 V) / 10 kΩ; S: Adafruit R7, D1] |
| status LED | 0.6 mA average | line 756 |
| **total** | **85.4–88.4 mA** | a lower bound: TX adds 0.2–4.6 mA [D: T × ΔI] |

**Expected draw, bank side:** I = 3.3 V × I₃V₃ / (η × 13.30 V).

- η = 0.90: 85.4 × 3.3 / 11.97 = **23.5 mA**
- η = 0.80: 88.4 × 3.3 / 10.64 = **27.4 mA**
- Even at η = 1.0: 85.4 × 3.3 / 13.3 = **21.2 mA**

**Measured:** 7.3–8.2 mA [M]. So:

- **Gap = 15.3–20.1 mA**, which is ≥ 13.0 mA even at η = 1.
- That is **5.7–7.5 µV** at 375 µΩ.
- The datasheet offset limit is ±1 µV. The gap is 6–7× that.

**The 08-26 report's reconciliation.** Report §7.1 reconciled 7.4 mA with a
25 mA DTIM power-save draw, but the firmware does not use power save. The
header's "Monitor ~100 mA" (line 79) matches the 3.3 V side (85–93 mA). The
report's R13 note calling it "14× high" needs its own R13 correction.

**The OLED step (§3.4).** The shunt sees a ~11 mA (3.3 V) load step at about
the expected size. This argues that the monitor *is* on the shunt.

**Remaining explanations:**

1. The ESP draws ~⅓ of its datasheet receive current with power save off.
   [I, unlikely]
2. **An in-situ offset of +5.7–7.5 µV**, so the reading is less negative
   than the truth.
3. A source on the battery side of the shunt. Bill rules out a bypass by
   construction. A trickling charger would be real charge current, harmless
   to SOC.

**SOC consequence if (2) holds:**

- **Rate.** 1 mA for a month = 0.73 Ah = 0.184 % of 397 Ah. V1.28 would read
  high by 15.3–20.1 × 0.184 = **2.8–3.7 %/mo**.
- **Since the 07-16 anchor** (1,686 h to 09-25 02:00Z):
  1. 15.3 × 1,686 = 25.8 Ah = 6.5 %
  2. 20.1 × 1,686 = 33.9 Ah = 8.5 %
  3. Both come on top of the turnover's 3.3 %, so the true SOC is **~88–90 %**.

**Temperature split.** Kept from Rev 1: the drain–temperature link in report
§7.5 is mostly the monitor's own heating (die − pack), and it changed 4× at
the rewire.

| segment | hours | pack coef (mA/°F) | die − pack coef (mA/°F) | r² |
|---|---|---|---|---|
| pre-rewire | 373 | −0.54 ± 0.07 | −1.57 ± 0.21 | 0.19 |
| post-rewire | 517 | −0.66 ± 0.03 | −6.83 ± 0.22 | 0.76 |

The ambient coefficient converts to 0.36–0.45 µV/°C. That is 36–45× the
DS's ±10 nV/°C maximum [S], so if it is real, it is not the chip.

**How to settle it:**

- **P-1 (DMM):** the clean way.
- **TB-1 (radio off):** free, if the monitor is on the shunt.
  - The radio-off draw is 16–28 mA [S: C3 Table 5-8, modem-sleep at
    160 MHz] + 1.4 mA. At the bank that is **4.8–9.1 mA** [D, η I].
  - The reading is ≈ −7.9 mA today. It should rise by 15–22 mA, to about
    **+7 to +15 mA**.
  - **Any reading above −4.8 mA proves an offset.**
  - If it rises by only a few mA, the ESP draws far less than its datasheet:
    explanation 1.

---

## 5. Tests

### 5.1 One diagnostic build (firmware only, controlled at runtime from HA)

**When to run it.** Run it now, in the quiet state. The quiet state is 5.0
mA against a 0.16 mA floor (31×), so it discriminates without a router
change.

**Scope.** Keep it separate from V1.28 (turnover §7). The gate is
`esp-firmware-validation`.

**TB-1: Wi-Fi off, 10 min.**

- **How:** `wifi.disable` → 10 min → `wifi.enable`. On the device, keep n,
  mean, sd, min and max of the 2-s current, plus ΔCHARGE/Δt and ΔENERGY/Δt.
  Publish them on reconnect.
- **Expected:**
  - ESP as the source: sd falls to ~0.16–0.3 mA. The mean rises by
    15–22 mA. The ENERGY rate falls to about |mean reading| × V, roughly
    0.1–0.2 W, because the chip's ~2 mA per-conversion noise no longer
    dominates.
  - Router or other external source: sd unchanged.

**TB-2: TX-power ladder.**

- **How:** a template `number` calls `esp_wifi_set_max_tx_power(dBm × 4)`.
  Step 20.5 → 17 → 14 → 11 → 8.5 dBm, 15 min each.
- **Expected:**
  - Radiated: sd ∝ 10^(ΔdBm/20).
  - Conducted: ≈ × 0.5.
  - External: flat.

**TB-3: averaging ladder.**

- **How:** a `select` writes ADC_CONFIG AVG ∈ {1, 4, 16, 64, 128, 256, 1024},
  5 min each.
- **What AVG = 1 gives:** the per-conversion σ and its tails directly.
  Compare with the 42 mA from ENERGY (§3.3):
  - kurtosis ≫ 0 → impulsive error
  - sd ≈ 42 mA with a 1/√N fall only at large N → correlated error
- **CHARGE is untouched**, because it accumulates per conversion [S: DS
  §7.3.1].

**TB-4: OLED lit remotely, 5 min, nobody present, three times.**

- **Expected:**
  - The 2 mA state follows → the monitor's own activity modulates the
    error.
  - It does not → presence/geometry.

**TB-5: preview §6.2 item 2.**

- **How:** VBUSCT 2074 µs, VSHCT 4120 µs, VTCT 50 µs, AVG 256.
  ADC_CONFIG = 0xFDC5.
- **Expected:** sd × 0.71.

**Passive additions:**

- 5-min on-device current sd/mean
- the AP bandwidth or secondary channel from `esp_wifi_sta_get_ap_info()`
  every 60 s, to test review §8.1's 20 MHz fallback directly [I: whether it
  tracks live HT operation]
- the reset reason
- ENERGY rate is already a free regime gauge (§3.3), and needs nothing new

**Notes:**

- **TX-power range.** 8.5–20.5 dB is ESPHome's `output_power` range [S].
  With no `output_power` configured, ESPHome re-applies nothing on
  reconnect. The script must restore the value; a reboot also restores it.
- **TB-3 and the SW ledger.** At AVG 1 the 2-s samples scatter ~40–200 mA.
  The SW ledger books both tails, netting ≤ 0.6 mAh per 5-min step and
  ~2 mAh for the whole ladder [D: Gaussian].
- **TB-3 and the ALERT limits.** Limits compare the averaged value
  (SLOWALERT = 1, line 516) [S: DS DIAG_ALRT bit 13]. At AVG 1 that is one
  conversion. It stays far from ±250 A and 12.2 V.

### 5.2 Physical tests (Bill's call, R14)

**P-1: DMM in series with TB1 BATT_RAW.**

- **Avoiding a reboot:** clip the DMM, on a mA range, across the F1 holder,
  then pull F1. Reverse the order to finish.
- **Reading:** log a ≥ 1 min average, with the HA 2-s current over the same
  minute.
- **Result:** zero = reading + I_TB1 + (other loads, §8.2 item 1).
- Once per regime if convenient.
- **Prediction:** I_TB1 ≈ 23–28 mA (§4).

**P-2: short the inputs at the INA228 terminal block.**

- **How:** leads off, VIN+ jumpered to VIN−, VBUS stays connected.
- **Expected:**
  - sd stays ~5 mA → the pickup is on the board or breakout.
  - sd → floor → the pickup is on the sense pair or shunt loop.
- It also gives today's chip-plus-board offset, to compare with the 0.9 µV
  from commissioning.

**P-3:** only after TB-1, TB-2 and P-2 name the path (§6.4).

---

## 6. SOC and accuracy updates

### 6.1 Keep from the two docs

Keep the V1.28 core. Nothing here overturns it:

- SOC from CHARGE with the anchor (turnover §5)
- review B2 (a)–(c)
- review B3: the provisional-anchor ladder
- O1 and O2
- the review §4–§5 budgets

**Datasheet checks of the review's claims** [S: DS]:

- **POR** at VS < 1.26 V typ (§7.4.2).
- **Reset values:** SHUNT_CAL 1000h, ADC_CONFIG FB68h, TEMP_LIMIT 7FFFh
  (§7.6.1.2, §7.6.1.3, §7.6.1.17).
- **Oscillator:** ±0.5 % at 25 °C, ±1 % over temperature.

One review budget row changes. The review's "0.88 mA noisy excess, if none
is real": the airtime model and the ESP temperature say it is real radio
current, which CHARGE should count.

### 6.2 New firmware items

1. **An in-situ offset term.**

   ```
   ah_net = (hw_charge_ah - anchor) - I_off_A * hours_since_anchor
   soc    = 100 + ah_net / ${validated_capacity_ah}f * 100
   ```

   - `I_off` is a substitution, 0.0 until P-1 measures it. Publish its value
     and source.
   - The anchor re-seed resets the hours. Apply the same term to the
     provisional anchor.
   - Publish Ah-below-full.

2. **Double the shunt integration time at the same cycle time.**
   - **Config:**
     `adc_time: {bus_voltage: 2074us, shunt_voltage: 4120us, temperature: 50us}`
     and `adc_averaging: 256`. ESPHome supports both [S]. The ADC_CONFIG
     layout was checked against the driver struct and FB68h.
   - **Arithmetic:**

     | | now | proposed | change |
     |---|---|---|---|
     | cycle | 128 × 3 × 4.12 ms = 1.582 s | 256 × (2.074 + 4.12 + 0.05) ms = 1.598 s | ≈ same |
     | shunt time per reading | 128 × 4.12 ms = 0.527 s | 256 × 4.12 ms = 1.055 s | × 2.00 |
     | bus time per reading | 0.527 s | 256 × 2.074 ms = 0.531 s | ≈ same |

   - **The noise table backs it** [S: DS Table 8-2, ADCRANGE 0]: 2074 µs ×
     256 = **19.7** noise-free bits, the same as 4120 µs × 128. The chip's
     own ENOB does not rise (4120 × 256 is also 19.7). The gain is against
     *external* white interference: sd × 1/√2.
     - noisy 18.1 → 12.8 mA
     - quiet 5.0 → 3.5 mA
     - hourly CHARGE 0.39 → 0.28 mA
   - **Assumption:** the table is labelled by the shunt ranges. That the bus
     channel scales the same way is [I]. TB-5 checks bus-voltage sd directly.
   - **Cost:** die temperature comes from 12.8 ms of conversion per reading.
     It is diagnostic only and averaged over 60 s.

3. **`max_current` 200 → 400 A.**
   - CURRENT is 20-bit two's complement with LSB = max_current / 2¹⁹ [S: DS
     Eq. 3, §7.6.1.8]. So it spans ±200 A.
   - **`i_max_plausible_a: 350` (line 339) can never trip,** at any of its
     five uses (lines 1347, 1369, 1396, 1413 and 2002).
     - An open Kelvin lead that drives the ADC toward ±163.84 mV (437 A)
       reads ≤ 200 A.
     - Above the range, MATHOF means "current and power data may be
       invalid" [S: DS DIAG_ALRT bit 9]. Whether CURRENT saturates or wraps
       is not stated [I].
   - **The coincident peak is out of range.** CHANGELOG 2026-08-27 records
     274–297 A at the DC bus.
   - **At 400 A:**
     - SHUNT_CAL = 13107.2 × 10⁶ × 400/2¹⁹ × 375 × 10⁻⁶ = **3750 (0x0EA6)**
       [S: DS Eq. 2]
     - That is distinct from the POR value 4096, so B2(a)'s readback still
       detects a reset. A POR would read 4096 / 3750 = 1.09× high.
     - LSB 0.763 mA, dithered by the chip's ~2 mA per-conversion noise.
   - **Review §9 becomes mandatory:** one substitution drives the lambda
     literal (lines 1676 and 1707) and `max_current`.

4. **Freshness predicate (B2c).** Add the now-reachable |I| test.

5. **RECON uncertainty.**
   - Lines 2346–2352 say "INA228 offset (~mAh) is negligible". Over 60 days
     it is not:
     - the datasheet's ±2.67 mA alone: 2.67 × 1,440 h = 3.8 Ah = 1.0 %
     - B1's gap: 15.3–20.1 × 1,440 = 22–29 Ah
   - Add σ_offset × hours to sigma.
   - U = offset + invisible drain + CE error, which is the lumped term SOC
     needs. After two agreeing brackets it can feed the
     `self_discharge_pct_per_month` hook (renamed "unseen drain").

6. **Re-zero triggers.** Re-zero after any shunt, lug, monitor or router
   move. §3.6 records 1–3 mA steps at each.

7. **Comment corrections.**

   | line | now says | should say |
   |---|---|---|
   | 79 | "Monitor ~100 mA" | consistent with the 3.3 V side; say so, and add the bank-side figure from P-1 |
   | 345 | "50 mA ≈ 60× step" | 50 mA = 131 CURRENT LSBs; the per-reading floor is 0.16 mA |
   | 1267–1270 | the `reset_on_boot` comment | under V1.28 the setting is load-bearing |

   Also wiring summary §5.2 ("noise floor ~5–10 mA"): that is interference.

### 6.3 Observability

- ENERGY idle rate as a live per-conversion noise gauge. The mean |I| per
  conversion ≈ (Wh/h) / V. The quiet state reads 0.46 W. With the
  interference gone, it should read ~|mean| × V ≈ 0.1 W.
- On-device 5-min sd.
- AP bandwidth.

### 6.4 Hardware, after the tests name the path

- **Input filter at the breakout terminal block**, in TI's form [S: DS
  §8.1.4]:
  - **10 Ω per leg.** TI's dV/dt protection value. Gain error
    20 / (92,000 + 20) = 0.022 % against R_DIFF = 92 kΩ [S: DS §6.5].
  - **0.1–1 µF ceramic differential.**
  - **A small C0G at the pins for 2.4 GHz** [I]. Add 100 pF–1 nF across
    VIN+/VIN− right at the pins; a 1 µF part is inductive there.
  - Match the legs.
- **If the ESP is confirmed:** move the antenna away from the breakout and
  pair, and/or set `output_power` to the lowest TB-2 value that keeps link
  margin. RSSI of −30 to −39 dBm leaves room.
- **The sense pair:** twist it right to the terminal, and keep the fan-out
  at the shunt short.
- **Optional standing zero:** fit a second, unmodified INA228 breakout
  (15 mΩ, 0x41) in series with BATT_RAW.
  - 25 mA × 15 mΩ = 0.375 mV; ±1 µV → ±0.07 mA [D].
  - Valid only while nothing else is on the bus. Decide after P-1.

### 6.5 Idle accuracy after each step

| state | idle SOC error | basis |
|---|---|---|
| today, SW ledger, quiet | 1.34 %/mo low against the measured drain | turnover |
| V1.28 as designed, if the B1 gap is an offset | 2.8–3.7 %/mo high | §4 |
| V1.28, if B1 closes with no offset | ≤ 0.49 %/mo (±1 µV) + wander + invisible drain | review §4, §3.6 |
| V1.28 + P-1 zero | ~0.1 %/mo + **±0.28 %/mo wander** + invisible drain | [D: ±0.5 mA DMM × 0.184; ±1.5 mA × 0.184] |
| + the §6.4 filter, if it removes the wander | ~0.1 %/mo + invisible drain | acceptance: §3.6 table flat across moves |
| + the §6.2 ADC timing | same mean; noise × 0.71 | §6.2 |

---

## 7. Corrections to existing records (R13)

1. **Report 08-26 §7.1.** The DTIM premise is wrong for this firmware. The
   datasheet puts the monitor at 23.5–27.4 mA; the reconciliation is open.
2. **Report 08-26 §7.5.** The temperature link is mainly the monitor's own
   heating.
3. **Report 08-26 §7.3.** The 08-04 step came with a +4 dB RSSI step and a
   noise-level change in the same hour. Thermal EMF is still possible. An
   RF-geometry term is now equally possible.
4. **Firmware.** The 350 A guard is unreachable at `max_current: 200 A`.
5. **Firmware.** The RECON "offset ~mAh" comment.
6. **Wiring summary §5.2.** The noise floor: the chip's is 0.16 mA per
   reading.
7. **Review §8.2 / Q1.** The third state is the lit OLED (Display Button
   history). Q1 is closed.
8. **Review §4 budget.** The 0.88 mA noisy excess is most likely real radio
   current.
9. **Turnover §4, candidates (a)/(b).** (a), the ESP's own radio, is
   favoured by three independent lines (§0.1). "Real current" is closed
   by §2.2.

---

## 8. Data

### 8.1 Received from Bill, 2026-09-25, and what each showed

| export | finding | section |
|---|---|---|
| Display Button (09-10 →) | the third state = the lit OLED | §3.4 |
| HW Energy / Net Charge (07-17 →) | per-conversion noise gauge; regime history; the zero steps | §3.3, §3.6 |
| WiFi Signal (07-28 →) | the router field at the monitor is 0.16–0.44 V/m; RSSI steps at physical events | §3.1, §3.6 |
| current, 2 s (09-24 14:16 → 09-25 02:16Z) | 11 h quiet since coexistence OFF; simultaneous sd for §3.3 | §0.1, §3.3 |
| ESP32 / INA228 / pack temperatures | the ESP runs warmer when noisy | §3.2 |

### 8.2 Still needed

**From Bill:**

1. **During storage:** is the charger's AC plugged in? What state is the
   inverter in? Is anything else on the busbars? This is needed to turn P-1
   into a zero.
2. **What happened at these times:**
   - 08-04 ~19–20Z (the rewire; what moved?)
   - 08-18 ~22Z (drain and noise changed, RSSI didn't)
   - 08-28 ~20Z (RSSI fell 3 dB)
   - 08-31 ~21Z (the rewire / INA228 power loss)

   Router moves, antenna, leads, monitor lid?
3. **Layout:**
   - antenna ↔ breakout, antenna ↔ sense pair, router ↔ monitor
   - sense-pair length and its untwisted ends
   - whether the TB1 leads run alongside the pair
   - a photo of the enclosure interior and one of the shunt end
4. **Commissioning Tier 2:** where the inputs were shorted, the sign of the
   0.9 µV, the sd while shorted, and whether Wi-Fi was on.
5. **Kelvin tap hardware:** the screw metal and the lug plating.

**Optional exports:**

6. **Display Button for July.** Confirms the July windows are OLED too.
7. **Battery current (2 s) for 09-10 → 09-24.** Repeats §3.3 across many
   noisy/quiet spells instead of one hour.

**Tests** (each needs Bill's go):

- TB-1 to TB-5, in one build
- P-1 and P-2

---

## 9. Suggested order

1. The answers in §8.2, items 1–2. They are free, and item 1 is needed for
   P-1.
2. The diagnostic build, TB-1 to TB-5, in the current quiet state. TB-1
   alone may settle both the source and B1.
3. P-1, the DMM reading. It sets `I_off`.
4. P-2, if the board-versus-leads question remains.
5. The R1 statement for V1.28, with §6.2 items 1–6 plus B2, B3, O1 and O2.
   Then turnover gates 2–6.
6. The filter/antenna fix. Acceptance:
   - TB-1-like sd near the floor with Wi-Fi *on*
   - a flat §3.6 table across a deliberate router move
