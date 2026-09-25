# Battery-bank SOC: noise root cause and INA228 accuracy (deep dive)

Written 2026-09-25. This reviews `docs/soc-accuracy-turnover.md` (the
**turnover**) and `docs/soc-v128-review.md` (the **review**) against:

- firmware **V1.27**, `INA228 Monitor/battery-bank-monitor.yaml` (2,705
  lines). Line numbers below are this copy's. They match the ones both docs
  cite.
- the wiring summary (Rev 1.10) and the commissioning report
- the 2026-08-26 report
- the INA228 data in `data/`

**Nothing is built.** V1.28 still waits on Bill's go (R12). Physical work is
Bill's call (R14).

Evidence tags follow the review:

- **[M]** measured
- **[D]** derived, with the chain shown
- **[S]** source document
- **[I]** inference, not yet checked

**What this session could and could not reach.**

- **Blocked** by the sandbox's network policy: TI, Espressif, Pololu and
  Mouser.
  - INA228 datasheet figures are carried over from the review, with its
    SLYS021A citations.
  - ESP32-C3 and D24V7F3 figures are **[I]** and are given as ranges.
- **Read:**
  - ESPHome source: GitHub `dev`, 2026.10.0-dev, commit `4a2f17b`. The device
    runs 2026.9.0. The code paths cited here are long-standing.
  - Adafruit's INA228 breakout design files: GitHub `Adafruit-INA228-PCB`.

---

## 0. Answers

### 0.1 The noise source

- **The noise is not current.** Two independent arguments show it (§2):
  - it reads positive when nothing on the bus can charge the bank
  - its skew is about 100× too small for any train of discharge pulses

  The monitor's own Wi-Fi bursts, sampled through the shunt, add at most
  ~0.35 mA of scatter [D].
- **It is an error voltage generated inside the measurement.** It is 2–7 µV
  rms after 128× averaging. It enters at inputs that have **no filtering
  between the field wiring and the silicon.**
  - Adafruit's schematic runs VIN+ and VIN− from the terminal block straight
    to the INA228 [S].
  - The only other part on those nets was the 15 mΩ shunt, which has been
    removed.
- **The most probable source is the monitor's own ESP32-C3 transmitting**,
  not the router [D from M, with I]. One model covers both regimes and the
  0.88 mA drain difference: noise variance ∝ the ESP's transmit airtime
  (§3.2). It needs:
  - ~0.1–0.16 % airtime in the quiet state
  - ~1.2–1.8 % airtime in the noisy state

  In this model the router's 20/40 coexistence setting changes *how much
  airtime the ESP needs*. It does not change the coupling path.

  **This stays [I] until TB-1 and TB-2 (§5) run.** Both are firmware-only.
  They can run now, in the quiet state, with no router change.
- **The "third state" is not new.** The July commissioning data has three
  windows like it (§3.4). The `Display Button` history in HA may explain all
  six windows at no cost.

### 0.2 SOC and accuracy

- **The largest SOC term is the unmeasured zero, not the noise.**
  - The firmware turns Wi-Fi power save off. `power_save_mode: none`
    (line 554) becomes `WIFI_PS_NONE` [S: ESPHome source], so the receiver
    never sleeps.
  - A monitor run that way should draw **~17–28 mA** from the bank [I, §4].
    The shunt reads **7.3–8.2 mA** [M].
  - The 08-26 report closed that gap by assuming a DTIM power-save draw. The
    firmware never uses that mode.
- **If the gap is an in-situ offset**, V1.28 inherits **1.6–3.8 %/mo**
  unchanged. The true SOC today would then be **~88–93 %, not ~96.7 %**
  [D, conditional; §4].
- **How to settle it:**
  - One DMM reading settles it (P-1).
  - TB-1 gives a partial answer for free. With the radio off, a reading above
    zero can only be an offset.
- **V1.28's core design stands.** Integrating the CHARGE register removes the
  deadband term. Once CHARGE integrates the noise, the noise costs SOC nothing.
  Under the airtime model, the regime-dependent part of the mean is real radio
  current, which CHARGE should count.
- **New firmware items** (§6.2), beyond the review:
  - an explicit in-situ offset term
  - 2× shunt integration time at the same cycle time
  - `max_current` 200 → 400 A. The 350 A plausibility guard can never trip
    today.
  - an honest RECON uncertainty

### 0.3 Data needed

See §8. Five items are free HA exports. Four are questions for Bill.

---

## 1. Signatures any explanation must meet

| # | Signature | Source |
|---|---|---|
| S1 | Noisy: mean −8.28 mA, sd 18.11 mA. Quiet: −7.22 / 5.44 mA | [M] turnover §3; reproduced in review §2 |
| S2 | White at 2 s (lag-1 −0.003 / −0.002). Block means scale as white noise out to 5 min | [M] review §2 |
| S3 | Symmetric: skew 0.016 noisy, 0.012 quiet. 6.1–6.2 % of noisy samples > +20 mA; 8.69 % of quiet samples > 0 mA | [M] turnover §4, review §7 |
| S4 | Hourly CHARGE scatter 0.39 mA, which is the white-noise prediction 18.11 / √2278 | [M/D] review §2 |
| S5 | The regime follows the router (coexistence, power-downs). Quiet spells have a ~25 min floor | [M] turnover §4, review §8.1 |
| S6 | Noisy draws 0.88 mA more (Welch t = 10.7) | [M] turnover §3 |
| S7 | Third state: sd ~2 mA with ~+3.2 mA more drain (09-11, 09-18, 09-22) | [M] review §8.2 |
| S8 | Never at the chip floor (~0.2 mA). No 5-min block below 2.2 mA in 14 d | [M/D] review §7 |
| S9 | July, from the 2-s export in this repo: idle sd 7.2–7.8 mA; skew 0.02–0.20; lag-1 ≤ 0.02; 17.5–19 % of samples > 0 mA | [M] this review, `data/ina228 Amperage.csv` |
| S10 | ENERGY rises 1.124 Wh/h at idle. The true idle power is ~0.1 W | [M] V1.27 R13 note, lines 1003–1007 |
| S11 | 2026-08-04 rewire: drain and scatter both stepped within the same hour (§3.5) | [M] this review, `ina228_hourly_*.csv` |

---

## 2. Why the noise is not current

### 2.1 Sign

At idle, nothing on the bus charges the bank:

- the inverter is off
- the charger's state during storage is question 6 in §8

Every consumer, the monitor included, returns through the shunt as
discharge. A true reading can never be positive. Yet 8.69 % of quiet
samples (September) and 17.5–19 % of idle samples (July) are positive [M].
**Those readings are error.**

A charger trickling current would be real charge current. But a trickle is
DC, and it cannot produce zero-mean scatter.

### 2.2 Shape

Suppose the "noise" were real current pulses in the discharge direction:
Wi-Fi TX bursts, CPU bursts, the LED. The INA228 samples the shunt in 4.12 ms
windows. Each reading's scatter would then come from how many pulses land in
those windows.

For Poisson or clustered arrivals and any positive pulse sizes *a*, the
statistics of one reading follow:

```
N pulses per reading ~ Poisson(mu)
mean contribution  m    = mu * E[a]
variance                = mu * E[a^2]
skew                    = E[a^3] / (E[a^2]^1.5 * sqrt(mu))
skew / (sd / m)         = E[a^3] * E[a] / E[a^2]^2  >= 1   (Cauchy-Schwarz)
```

So **skew ≥ sd / m**. The pulses cannot contribute more than the whole mean,
so *m* ≤ |mean|:

| | sd | m ≤ | skew must be ≥ | measured skew |
|---|---|---|---|---|
| noisy | 18.11 mA | 8.28 mA | 2.19 | 0.016 |
| quiet | 5.44 mA | 7.22 mA | 0.75 | 0.012 |

Both miss by two orders of magnitude. The distribution is what a zero-mean
error looks like, not what sampled pulses look like.

### 2.3 Size

Take the airtime model of §3.2. The ESP's extra TX in the noisy state is
~1.5 % airtime, in pulses of ~63 mA at the bank.

1. For 0.2–1 ms frames, the pulse rate is 0.015 / d = 15–75 per second.
2. Each reading has 0.527 s of shunt time, so it catches N = 8–40 pulses.
3. Each pulse moves a reading by 63 mA × d / 0.527 s = 0.024–0.12 mA.
4. The scatter is (per-pulse shift) × √N = **0.15–0.34 mA** [D].

Real radio current shows up in the mean, not in the noise.

---

## 3. Where the error enters

### 3.1 The input is wide open

- **No filter on the inputs.** On the Adafruit breakout, net VIN+ is IC1,
  X1-3, R1, SJ1 and JP2-7. Net VIN− is IC1, X1-1, R1 and JP2-6. There is no
  capacitor or series resistor on either [S: `Adafruit INA228 I2C Power
  Monitor.sch`, parsed this session]. R1, the 15 mΩ shunt, was removed.
- **TI's recommended differential RC is absent** [S: SLYS021A §8.1.4, via
  review §6].
- **The sense pair** is 22 AWG, twisted, unshielded. Its length and its
  untwisted fan-out at each end are not recorded (§8, item 7).
- **The XIAO's U.FL antenna** is inside the same enclosure, on the wall or
  lid (wiring summary §8.2 step 6). Its distance to the breakout is not
  recorded.

**Field at the INA228** [D, with the distances I]. Using
E = √(30 × P × G) / d:

| source | assumed power, gain, distance | field |
|---|---|---|
| ESP32-C3 | 20 dBm (0.1 W), 2 dBi (G 1.6), 0.1 m | √4.8 / 0.1 = 22 V/m |
| router | 25 dBm EIRP (0.32 W), 2 m | √9.5 / 2 = 1.5 V/m |

Power density scales as E², so the ESP's field is ~200× the router's per
unit of airtime. The distances are guesses; §8 item 7 asks for them.

### 3.2 One model fits both regimes: noise variance ∝ the ESP's TX airtime

**Assumption.** Each ESP transmit burst adds an independent error at the
INA228 input. The coupling may be radiated or conducted.

**Consequences:**

- noise variance ∝ airtime *T*
- extra real drain = ΔT × ΔI_b, where ΔI_b is one burst's current at the bank

**Arithmetic:**

1. Variance ratio: 18.11² / 5.44² = 328.0 / 29.6 = **11.08** [D from M].
2. Burst current at the bank:
   ΔI_b = (TX − RX current at 3.3 V) × 3.3 V / (η × 13.30 V).
   - For 200 mA and η = 0.90: 660 / 11.97 = 55 mA.
   - For 250 mA and η = 0.80: 825 / 10.64 = 78 mA.
   - Range **55–78 mA** [I: ESP32-C3 TX/RX currents and D24V7F3 efficiency
     not re-read].
3. ΔT = 0.88 mA / (55–78 mA) = 1.60–1.13 %.
4. T_quiet = ΔT / (11.08 − 1) = **0.16–0.11 %**.
5. T_noisy = 11.08 × T_quiet = **1.8–1.2 %**.

These airtimes are small, and the right order for a node that sends a few
small frames per second [I]. The 802.11 mechanism that makes the ESP need
~10× more airtime with 40 MHz + coexistence ON is still open. Candidates
[I]:

- legacy-rate protection frames
- retries
- rate fallback

The monitor-side quantity, airtime, is testable directly.

**What the model predicts:**

- **Wi-Fi off:** sd falls to the chip floor (~0.2–0.3 mA) in either regime,
  and the mean moves positive by the radio's share of the draw (§4).
- **Lower TX power:** sd falls.
  - **Radiated:** variance ∝ TX power, so going from 20 to 8.5 dBm gives
    sd × 10^(−11.5/20) = **× 0.27**.
  - **Conducted** through the ESP's supply current: about **× 0.5**. TX
    current falls less than TX power [I].
  - **Router as the source:** no change.

**What would break it.** If sd is unchanged with Wi-Fi off, the source is
outside the monitor: the router's RF on the leads (turnover §4 (b)).

### 3.3 The ENERGY register suggests the error is correlated across conversions

[D, with assumptions stated]

- **The assumption.** Per the V1.24 comment (lines 1360–1365), the POWER
  register rectifies each raw conversion before averaging. ENERGY integrates
  POWER. So its idle rate measures the mean |error| of a *single* 4.12 ms
  conversion.
- **Per-conversion error from ENERGY:**
  1. Mean |I| per conversion = 1.124 W / 13.30 V = 84.5 mA.
  2. For a Gaussian, σ = 84.5 / √(2/π) = **~106 mA**.
- **Per-conversion error from the averaged readings,** if conversions were
  independent: σ = sd_avg × √128.
  - The R13 window (24.8 h to 09-18 19:48Z) falls inside the 09-10 → 09-18
    period. That period's ledger booking share was 2.6 % (review §7). A 2.6 %
    share corresponds to sd_avg ≈ 14–16 mA, taking the period's noise level
    for the window's:
    - A Gaussian model gives 15.7 mA.
    - The measured tails are heavier (excess kurtosis 1.37), which pulls the
      figure lower.
  - That gives σ = **160–180 mA**.
- **Comparison.** The averaged readings carry (160–180 / 106)² ≈ **2.3–2.9×**
  more variance than independent conversions would give. The error is
  positively correlated over tens to hundreds of milliseconds: it has power
  below ~40 Hz.
- **What that means.** Bursty packet traffic fits this. Broadband RF sampled
  independently at each conversion does not.

TB-3 (§5) measures this directly.

### 3.4 The third state existed in July too

From the 2-s export in this repo (UTC), idle 5-min blocks:

| window (UTC) | sd | mean | context |
|---|---|---|---|
| 07-15 16:20–16:30 | 3.1–4.6 mA | −11.8 / −12.7 mA | commissioning |
| 07-15 16:30–16:50 | 2.26 mA (1.8–2.5) | −7.7 to −8.3 mA | commissioning |
| 07-16 11:35–11:40 | 1.81 mA | −12.07 mA | before the heater test |
| 07-16 20:00–20:05 | 1.98 mA | −9.08 mA | 10 min after the first anchor (19:50Z), which Bill verified |

The surrounding idle blocks sit at 7–8 mA sd and about −6 to −7 mA.

All three low-noise windows fall at moments of operator activity [I, from
the commissioning timeline]:

- 07-15 16:30Z: day-1 bring-up, when the export starts at 15:45Z
- 07-16 11:35Z: the end of the 70 W overnight leg, whose event file ends
  11:40Z
- 07-16 20:00Z: just after the first anchor

Two rows (07-15 16:20Z and 07-16 11:35Z) sit ~5 mA more negative than the
surrounding idle blocks. That is the same kind of drain step as review §8.2.

- **Free check.** `Display Button` (line 2066) is a named, non-internal
  entity, so HA recorded every press. Check its history against these three
  windows and the review's three September windows.
- **TB-4 (§5)** lights the OLED remotely with nobody present. That separates
  "OLED lit" from "someone standing at the monitor".

### 3.5 The 2026-08-04 rewire changed the noise too

In the hourly file (range-based sd = (max − min) / 6.6 at n ≈ 1,770 per
hour; crude, so only ratios are used):

- **Across the step, in the same hour:**
  - drain −5.5 → −9.1 mA (17Z → 19Z)
  - hourly sd estimate 10.6 → 15.1 mA
- **Segment means:**
  - sd estimate 10.4 → 13.3 mA (**+28 %**)
  - drain −6.23 → −8.28 mA

The report puts the drain step down to a thermal-EMF shift at the re-landed
joints (report §7.3). The airtime model cannot produce that step from the
sd change:

1. The model's scale: quiet 29.6 mA² ↔ 0.14 % airtime.
2. The observed rise, 13.3² − 10.4² = 68 mA², is ≈ 0.32 % airtime.
3. At 63 mA per burst, 0.32 % gives ~0.2 mA, not 2.9 mA [D].

So the report's offset explanation of the drain step survives. The rewire
also changed the pickup geometry.

**Consequence for SOC.** The in-situ zero moves when the shunt connections
are disturbed. Re-zero after any lug work (§6.2).

---

## 4. The energy balance (review B1), sharpened

**Firmware.** `power_save_mode: none` (line 554). ESPHome maps NONE to
`WIFI_PS_NONE`, and the C++ default is also NONE [S:
`wifi_component_esp_idf.cpp`, `wifi_apply_power_save_()`]. The receiver
stays on.

**Expected monitor draw at the bank** [I for the ESP and the buck]:

- **3.3 V side**, total ≈ **61–91 mA**:
  - ESP32-C3 with the receiver on: 60–90 mA. The review cites 84 mA from a
    secondary copy of Espressif's table; not re-read here.
  - INA228: 0.64 mA typical [S, via review].
  - Breakout power LED: ~0.13 mA [D: (3.3 − ~2.0 V) / 10 kΩ; S: Adafruit
    schematic, R7 = 10 kΩ, D1].
  - Status LED: 0.6 mA average (line 756).
- **Bank side**, I = 3.3 V × I₃V₃ / (η × 13.30 V) with η = 0.80–0.90:
  - 61 mA → 201 / 11.97 = 16.8 mA
  - 91 mA → 300 / 10.64 = 28.2 mA
  - → **16.8–28.2 mA**
- **Measured:** 7.3–8.2 mA [M, turnover §3].
- **Gap: 8.6–20.9 mA**, which is **3.2–7.8 µV** at 375 µΩ [D].

**The 08-26 report's reconciliation.** Report §7.1 reconciled 7.4 mA with "a
XIAO ESP32-C3 holding a Wi-Fi association in DTIM power-save draws ~25 mA".

- The arithmetic holds: 25 × 3.3 / 0.87 / 13.35 = 7.1 mA.
- The premise does not describe this firmware.
- The header's "Monitor ~100 mA" (line 79) may be the 3.3 V-side figure, and
  roughly right.

**Which one is right is open.** The report's R13 note ("an [I] wearing an
[M]'s clothes") may itself need an R13 correction.

**Three explanations remain:**

1. The ESP draws far less than its datasheet with power save off. [I,
   unlikely]
2. An in-situ offset of +3–8 µV in the sense path: thermal EMF, a DC part of
   the RF error, or the board. The reading is less negative than the truth.
3. Current on the battery side of the shunt. Bill rules out a bypass by
   construction. A charger trickling current would be real charge current,
   and harmless to SOC.

**SOC consequence if (2) holds:**

- **Rate.** 1 mA for a month = 0.73 Ah = 0.184 % of 397 Ah. So V1.28 would
  read high by 8.6–20.9 × 0.184 = **1.6–3.8 %/mo**.
- **Since the 07-16 anchor** (1,686 h to 09-25 02:00Z):
  1. 8.6 × 1,686 = 14.5 Ah = 3.7 %
  2. 20.9 × 1,686 = 35.2 Ah = 8.9 %
  3. Both come on top of the turnover's 3.3 %, so the true SOC is **~88–93 %**.

**The drain–temperature correlation cannot separate these.** Report §7.5
regresses drain on die temperature alone. Splitting die temperature into
ambient (pack) and the monitor's own heating (die − pack) gives, hourly and
idle-only [M, this review]:

| segment | hours | pack coef (mA/°F) | die − pack coef (mA/°F) | r² |
|---|---|---|---|---|
| pre-rewire, 07-20 → 08-04 18Z | 373 | −0.54 ± 0.07 | −1.57 ± 0.21 | 0.19 |
| post-rewire, 08-04 19Z → 08-26 | 517 | −0.66 ± 0.03 | −6.83 ± 0.22 | 0.76 |

- **Most of the post-rewire correlation is with the monitor's own heating,
  not with ambient.** The die − pack coefficient changed 4× at the rewire,
  so it is not a usable temperature coefficient. Do not compensate SOC with
  it.
- **The ambient coefficient**, −0.54 to −0.66 mA/°F:
  1. × 1.8 = −0.97 to −1.19 mA/°C
  2. × 375 µΩ = **0.36–0.45 µV/°C**
  3. That is 36–45× the INA228's offset-drift maximum of 10 nV/°C [S, via
     review].
  4. If it is real, it is in the wiring, not the chip.

**How to settle it:**

- **P-1 (DMM):** the one clean way.
- **TB-1 (radio off):** partial.
  - The ESP with its radio off still draws ~21–26 mA at 3.3 V [I]. That is
    ≈ 6–8 mA at the bank.
  - A reading above zero is then certainly offset. A reading above about
    −6 mA is very likely offset.
  - The step size measures the radio's share of the draw directly.
- **RECON at the next full charge:** lumps offset and invisible (BMS) drain
  together. It cannot separate them.

---

## 5. Tests

### 5.1 One diagnostic build (firmware only, controlled at runtime from HA)

**When to run it.** Run it now, in the quiet state. No router change is
needed: the quiet state (5.44 mA) sits ~25× above the ~0.2 mA floor, so it
discriminates as well as the noisy state. Repeat in a noisy spell only if the
quiet results are ambiguous.

**Scope.** Keep it separate from V1.28, as turnover §7 requires. No SOC logic
changes. The build gate is `esp-firmware-validation` (turnover §10, gate 4).

**TB-1: Wi-Fi off, 10 min.**

- **How:** `wifi.disable` → 10 min → `wifi.enable`. On the device, keep n,
  mean, sd, min and max of the 2-s current, plus ΔCHARGE/Δt. Publish them on
  reconnect.
- **Expected:**
  - ESP, radiated or conducted: sd → 0.2–0.3 mA. The mean steps positive by
    the radio's draw (§4).
  - Router or other external source: sd unchanged.

**TB-2: TX-power ladder.**

- **How:** a template `number` calls `esp_wifi_set_max_tx_power(dBm × 4)`.
  Step 20.5 → 17 → 14 → 11 → 8.5 dBm, 15 min each. Data stays live in HA.
- **Expected:**
  - ESP, radiated: sd ∝ 10^(ΔdBm / 20), i.e. × 0.27 at −11.5 dB.
  - ESP, conducted: ≈ × 0.5 [I].
  - Router or other external source: flat.

**TB-3: averaging ladder.**

- **How:** a `select` writes ADC_CONFIG AVG ∈ {1, 4, 16, 64, 128, 256, 1024},
  5 min each.
- **Expected:**
  - sd ∝ 1/√N if the error is white per conversion.
  - A slower fall at small N if the error is correlated; §3.3 predicts this.
  - AVG 1 gives the per-conversion σ directly. Compare it with the ~106 mA
    from ENERGY.

**TB-4: OLED lit remotely, 5 min, nobody present, three times.**

- **Expected:**
  - If the 2 mA state follows the OLED, the monitor itself modulates the
    error.
  - If not, the low-noise windows were a person at the monitor, which points
    to radiated coupling geometry.

**TB-5: preview the production ADC setting of §6.2.**

- **How:** VBUSCT 2074, VSHCT 4120, VTCT 50, AVG 256. ADC_CONFIG = 0xFDC5.
- **Expected:** sd × 0.71 if the error is white.

**Passive additions, no test window needed:**

- a 5-min on-device current sd and mean, so the regime shows directly in HA
- the AP's bandwidth or secondary channel from `esp_wifi_sta_get_ap_info()`,
  read every 60 s
  - This logs HT20/HT40 against the regime and tests the review's §8.1 claim
    that the quiet state is the 20 MHz fallback.
  - [I] whether the field tracks the AP's live HT operation.
- the reset reason (review §6)

**Notes:**

- **The mean readings answer B1 in part.** TB-1 and TB-2 both give them (§4).
- **TX-power range.** 8.5–20.5 dB is ESPHome's validated `output_power` range
  [S: `wifi/__init__.py`]. This YAML sets no `output_power`, so ESPHome
  re-applies nothing on reconnect (`wifi_component.cpp` checks `isnan`). The
  test script must restore the value at the end; a reboot also restores the
  default.
- **TB-3 changes the samples CORE sees, while it runs.** At AVG 1 the 2-s
  samples scatter ~60–200 mA. The SW ledger books both tails, so the net
  booked is small: ≤ 0.6 mAh per 5-min step, ~2 mAh for the whole ladder
  [D: Gaussian model]. CHARGE is unaffected in the mean.
- **TB-3 and the ALERT limits.** Limits are evaluated on the averaged result
  (SLOWALERT = 1, line 516). At AVG 1 that is one conversion. It stays far
  from ±250 A and 12.2 V.

### 5.2 Physical tests (Bill's call, R14)

**P-1: DMM in series with TB1 BATT_RAW.**

- **Avoiding a reboot:** clip the DMM, on a mA range, across the F1 fuse
  holder, then pull F1. Reverse the order to finish.
- **Reading:** log a DMM average of at least 1 min, and note the minute. Take
  the HA 2-s current over the same minute.
- **Result:** in-situ zero = reading − (−I_TB1 − other loads). Other loads
  are known only once §8 item 6 is answered.
- This single reading gives both B1 and the V1.28 offset term. Once in each
  regime is better, if convenient.

**P-2: short the inputs at the INA228 terminal block.**

- **How:** lift the leads and jumper VIN+ to VIN−. VBUS stays connected. Run
  it in the current state.
- **Expected:**
  - sd stays ~5 mA → the pickup is on the board or breakout (the ESP is next
    door).
  - sd falls to the floor → the pickup is on the sense pair or the shunt
    loop.
- It also gives today's chip-plus-board offset, to compare with the 0.9 µV
  measured at commissioning.

**P-3:** only after TB-1, TB-2 and P-2 have named the path. See §6.4.

---

## 6. SOC and accuracy updates

### 6.1 Keep from the two docs

Keep the V1.28 core. Nothing here overturns it:

- SOC from the CHARGE register with the anchor (turnover §5)
- review B2 (a)–(c): the CORE-grade pass
- review B3: the provisional-anchor ladder
- O1 (coulombic efficiency) and O2 (taper)
- the rewritten idle and outage budgets (review §4–§5)

One budget row changes. The review's "noisy-state excess (0.88 mA), if none
is real, ≤ 0.16 %/mo": under §3.2, the 0.88 mA is real radio current, and
CHARGE should count it. The TB-1 mean step confirms or refutes this.

### 6.2 New firmware items

1. **An in-situ offset term.**
   - The reading = truth + I_off, so CHARGE carries I_off × t. Correct for it:

     ```
     ah_net = (hw_charge_ah - anchor) - I_off_A * hours_since_anchor
     soc    = 100 + ah_net / ${validated_capacity_ah}f * 100
     ```

   - Give `I_off` a substitution that defaults to 0.0 until P-1 measures it.
     Publish its value and source.
   - The anchor re-seed resets the hours. Apply the same term to the
     provisional anchor.
   - Publish Ah-below-full (review §4).

2. **Double the shunt integration time at the same cycle time.**
   - **Config:**
     `adc_time: {bus_voltage: 2074us, shunt_voltage: 4120us, temperature: 50us}`
     and `adc_averaging: 256`. ESPHome supports per-channel times and 256
     [S: `ina2xx_base/__init__.py`]. The ADC_CONFIG bit layout was checked
     against the driver's struct and the POR value FB68h.
   - **Arithmetic:**

     | | now | proposed | change |
     |---|---|---|---|
     | cycle | 128 × 3 × 4.12 ms = 1.582 s | 256 × (2.074 + 4.12 + 0.05) ms = 1.598 s | ≈ same |
     | shunt time per reading | 128 × 4.12 ms = 0.527 s | 256 × 4.12 ms = 1.055 s | × 2.00 |
     | bus time per reading | 0.527 s | 256 × 2.074 ms = 0.531 s | ≈ same |

   - **Effect** [D]: white-noise sd × 1/√2.
     - noisy 18.1 → 12.8 mA
     - quiet 5.44 → 3.85 mA
     - hourly CHARGE 0.39 → 0.28 mA
   - The 2-s poll still reads a fresh result every time, because 1.598 s is
     under 2 s.
   - **Costs:**
     - Die temperature comes from 12.8 ms of conversion per reading instead of
       527 ms. It is diagnostic only, and throttle-averaged over 60 s.
     - The bus channel at 2074 µs × 256 should match 4120 µs × 128 *if* noise
       ∝ 1/√(total time) [I]. Check TI's noise-versus-conversion-time table
       before adopting.
   - TB-5 previews this setting.

3. **`max_current` 200 → 400 A.**
   - CURRENT is a 20-bit two's-complement value with LSB = max_current / 2¹⁹
     [S: ESPHome `read_current_a_`, `configure_shunt_`]. It therefore tops
     out at ±200 A.
   - **So `i_max_plausible_a: 350` (line 339) can never trip.** That holds at
     all five uses (lines 1347, 1369, 1396, 1413 and 2002).
     - Line 336 describes the guard as catching an "ADC saturated/Kelvin
       open" fault.
     - An open Kelvin lead drives the ADC toward ±163.84 mV (437 A). The
       register would still read ≤ 200 A, and the ledgers would integrate it.
   - **The coincident peak exceeds the register's range.** The CHANGELOG
     2026-08-27 records 274–297 A at the DC bus. Whether the chip saturates
     there or sets MATHOF with invalid data is [I, datasheet].
   - **At 400 A:**
     - LSB = 0.763 mA
     - SHUNT_CAL = 13107.2 × 10⁶ × 400/2¹⁹ × 375 × 10⁻⁶ = **3750 (0x0EA6)**
     - That is still distinct from the POR value 4096, so review B2(a)'s
       readback check still works. A POR would read 4096 / 3750 = 1.09× high.
     - The chip's own per-conversion noise, ~2 mA [D: 0.19 mA × √128], dithers
       a 0.76 mA LSB, so CHARGE loses nothing [I].
   - **This makes review §9 mandatory.** Drive the CURRENT_LSB literal in the
     HW lambdas (lines 1676, 1707) and `max_current` from one substitution.

4. **Freshness predicate (review B2c).** The |I| plausibility test becomes
   reachable under item 3. Add it.

5. **RECON uncertainty.**
   - The comment at lines 2346–2352 says "INA228 offset (~mAh) is negligible".
     Over a 60-day bracket it is not:
     - The datasheet's ±2.67 mA maximum alone is 2.67 × 1,440 h = 3.8 Ah, or
       1.0 %.
     - B1's possible gap is 8.6–20.9 mA × 1,440 h = 12.4–30.1 Ah.
   - Add σ_offset × hours to sigma.
   - Label U as what it is: offset + invisible drain + CE error. That lumped
     term is exactly what SOC needs. Once two long brackets agree, U can feed
     the `self_discharge_pct_per_month` hook, renamed to mean "unseen drain".

6. **Re-zero triggers.**
   - After any shunt or lug work: the 08-04 step was ~2.9 mA [M, report].
   - Seasonally, if the ambient coefficient is real: 0.54–0.66 mA/°F × a 10 °F
     swing = 5.4–6.6 mA [D].

7. **Comment corrections.**

   | line | now says | should say |
   |---|---|---|
   | 79 | "Monitor ~100 mA" | state which side (3.3 V or bank); replace with P-1's number |
   | 345 | "50 mA ≈ 60× step" | 50 mA = 131 CURRENT LSBs; the per-reading chip floor is ~0.2 mA, not 0.83 |
   | 1267–1270 | the `reset_on_boot` comment | under V1.28 the setting is load-bearing (review §9) |

   Also, wiring summary §5.2 says "practical noise floor ~5–10 mA". That is
   the interference, not the chip.

### 6.3 Observability

- On-device 5-min current sd and mean.
- AP bandwidth (§5.1).
- ENERGY idle rate as a live per-conversion noise gauge. [D: E|I_conv| =
  (Wh/h) / V]

### 6.4 Hardware, after the tests name the path

- **An input filter at the breakout terminal block**, in TI's form:
  - ≤ 10 Ω per leg
  - 0.1–1 µF differential
  - gain error 0.022 % at 10 Ω (review §6 table)
  - plus a small C0G, 100 pF–1 nF, directly across VIN+/VIN− at the pins for
    2.4 GHz, where a 1 µF part is already inductive [I]
  - Match the two legs.
- **If the ESP radiates it:**
  - Move the antenna away from the breakout and the pair.
  - Or set `output_power` to the lowest value that TB-2 shows still keeps
    link margin.
- **The sense pair:** twist it right up to the terminal, and keep the
  untwisted fan-out at the shunt short.
- **Optional, for a standing in-situ zero:** fit a second, unmodified INA228
  breakout (15 mΩ on board, at 0x41) in series with BATT_RAW. It reads the
  monitor's own draw:
  - 25 mA × 15 mΩ = 0.375 mV
  - its ±1 µV offset is then ±0.07 mA [D]
  - With the bank otherwise idle, main zero = reading + I_monitor.
  - This is valid only when nothing else is on the bus. Decide after P-1.

### 6.5 Idle accuracy after each step

| state | idle SOC error | basis |
|---|---|---|
| today, SW ledger, quiet state | 1.34 %/mo low against the measured drain | turnover |
| V1.28 as designed, if the B1 gap is an offset | 1.6–3.8 %/mo high | §4 |
| V1.28, if B1 closes with no offset | ≤ 0.49 %/mo (datasheet offset) + invisible drain | review §4 |
| V1.28 + in-situ zero from P-1 | ~0.1 %/mo + zero drift + invisible drain | [D: ±0.5 mA DMM-limited × 0.184] |
| + the §6.2 ADC timing | same mean; noise × 0.71 | §6.2 |

Invisible drain (BMS and cell self-discharge) remains in every row. RECON
brackets it.

---

## 7. Corrections to existing records (R13)

1. **Report 08-26, §7.1.** The DTIM power-save premise does not match the
   firmware (`WIFI_PS_NONE`). The monitor-draw reconciliation is open, not
   closed. Its R13 note may itself be backwards.
2. **Report 08-26, §7.5.** The drain–temperature link is mostly the monitor's
   own heating (die − pack) after the rewire. It is not an ambient
   coefficient (§4 table).
3. **Firmware.** The 350 A plausibility guard is unreachable with
   `max_current: 200 A` (§6.2 item 3).
4. **Firmware.** The RECON sigma comment ("offset ~mAh negligible") is wrong
   by three orders of magnitude over a 60-day bracket (§6.2 item 5).
5. **Wiring summary §5.2.** The "noise floor ~5–10 mA" is interference. The
   chip's floor is ~0.2 mA per reading.
6. **Turnover §4, candidates (a) and (b).**
   - (a), the ESP's own radio, is now quantitatively consistent with S1 and
     S6 (§3.2).
   - "Real current" is closed by §2.2, not only by the sign argument.
7. **Review §8.2, the third state.** The same state appears three times in
   the July commissioning data (§3.4).

---

## 8. Data I need to validate this

### 8.1 Free: HA history exports (pass `end_time`)

1. **`binary_sensor.battery_bank_monitor_display_button`** for all of July,
   and 09-10 → now. Checks the six low-noise windows (§3.4) and closes review
   Q1 without asking anyone.
2. **`sensor.battery_bank_monitor_hw_energy_ina228`** and
   **`..._hw_net_charge_ina228`**, from the V1.23 flash to now.
   - The ENERGY idle rate by regime tests §3.3.
   - CHARGE closes review Q7.
3. **`sensor.battery_bank_monitor_wifi_signal`** (RSSI), 09-10 → now. Does
   RSSI step with the regime?
4. **Battery current (2 s), 09-24 11:14 EDT → now.**
   - Scores the review's §8.1 prediction: no noisy spell while coexistence is
     OFF.
   - Gives a clean quiet baseline for TB-1.
5. **INA228 die temperature, pack temperature and ESP32 internal
   temperature**, 09-10 → now. Repeats the §4 temperature split within a
   single regime.

### 8.2 From Bill

6. **During storage:**
   - Is the LiTime charger's AC plugged in?
   - What state is the inverter in: soft-off with DC live, or the DC breaker
     open?
   - Is anything else on the busbars?
7. **Layout:**
   - distance from the U.FL antenna to the INA228 breakout
   - distance from the antenna to the sense pair
   - distance from the router to the monitor
   - sense-pair length, and the untwisted length at each end
   - whether the TB1 power leads run alongside the pair
   - a photo of the enclosure interior and one of the shunt end
8. **Commissioning Tier 2** (review Q3):
   - Where were the inputs shorted: at the pins or at the terminal block?
   - What sign did the 0.9 µV have?
   - What was the sd with the inputs shorted?
   - Was the XIAO powered and on Wi-Fi at the time?
9. **Kelvin tap hardware:** the screw metal and the lug plating. This bears
   on the thermal-EMF question.

### 8.3 Tests (each needs Bill's go)

- TB-1 to TB-5, in one build (§5.1)
- P-1 and P-2 (§5.2)

---

## 9. Suggested order

1. Items 1–5 (free exports) and answers 6–9.
2. The diagnostic build, TB-1 to TB-5, in one flash. Run it in the current
   quiet state.
3. P-1, the DMM reading. It can be done any time, and has the highest value
   for SOC.
4. P-2, if TB-1 implicates the ESP and the board-versus-leads question
   remains.
5. The R1 statement for V1.28, with §6.2 items 1–6 plus the review's B2, B3,
   O1 and O2. Then turnover gates 2–6.
6. The hardware fix for the named path. Re-run TB-1 as the acceptance test.
