# Battery-bank SOC V1.28: review and data validation (handoff)

Written 2026-09-24, after session 49c33aa0's turnover. This reviews
`docs/soc-accuracy-turnover.md` against firmware **V1.27**
(`esphome/battery-bank-monitor.yaml`, master, 2,705 lines, read 2026-09-24)
and two Home Assistant history exports. **Nothing is built.** V1.28 still waits
on Bill's go (R12). Line numbers are V1.27's.

Evidence tags follow the turnover:

- **[M]** measured, here in the exported HA history.
- **[D]** derived, with the chain shown.
- **[S]** source document.
- **[I]** inference, not yet checked.

---

## 0. Summary

The core design is right. Computing SOC from the INA228 CHARGE register is the
correct fix for a drain that sits below the SW ledger's ±50 mA deadband, and
the exported data support it (§2, §7). The proposal is **not ready for the R1
statement.** Four things come first:

1. **B1.** Close the monitor energy balance. The arithmetic does not yet
   support "the shunt sees the monitor", and V1.28 depends on it. One
   measurement settles it (§3).
2. **B2.** V1.28 promotes the V1.23/25/26 HW path from OBSERVABILITY to
   CORE. It needs a CORE-grade pass: a runtime reset check, retiring the
   one-time migration branch, and a freshness predicate (§3).
3. **B3.** Replace the SW-ledger fallback with a provisional-anchor ladder.
   That freezes the error at its current size instead of letting it grow (§3).
4. **Budgets.** Rewrite the §5 accuracy budget, which omits the large terms
   (§4 here), and add an outage budget (§5 here).

New from the data (§8):

- The noisy/quiet switch has a **~25 min hysteresis floor** that matches the
  802.11n 20/40 coexistence timer.
- A **third, quieter state** appeared three times, together with a +3 mA
  step in drain.

Proposed edits to the turnover are in §10. Open questions for Bill are in §11.

---

## 1. Sources and method

- **Firmware:** V1.27 at master, fetched 2026-09-24. Every line reference in
  the turnover lands where it says it does.
- **INA228 datasheet:** TI SLYS021A (Jan 2021, rev. May 2022). The turnover
  cites the right document.
- **Exports** [M]:
  - `history.csv` is `sensor.battery_bank_monitor_battery_current`,
    609,384 rows.
  - `history__1_.csv` is `sensor.battery_bank_monitor_battery_voltage`,
    168,720 rows.
  - Both hold hourly long-term-statistics means from 2026-08-25 17:00Z to
    09-10 08:00Z, then raw states from 09-10 08:12Z to 09-24 ~16:19Z.
  - Each file has 28 `unavailable` rows. They line up with the reboots
    (09-22 20:06:53, 09-24 10:49:33 EDT), the router power-downs, and the
    coexistence change (09-24 11:14:40 EDT).
  - Current is stored at full precision on a 0.3815 mA grid. Voltage is
    recorded on change, in 195 µV steps.
- **Regime classification:**
  - 5-min blocks with ≥100 samples; a block is noisy if its sd > 9 mA.
  - The block-sd histogram is bimodal and empty between 8 and 10 mA.
  - The result is insensitive to the threshold: 8, 9 and 10 mA give 415, 413
    and 412 noisy blocks in the turnover window [M].
- **Spell durations:** 1-min sd, the same 9 mA threshold, and a 3-min centred
  median to suppress flicker. Runs ≥5 min are counted.
- **Integration:** left rectangle on the raw timestamps. Gaps >10 s are not
  bridged. Hourly means count as 1 h each.
- The analysis scripts were session-local, as with turnover gate 3. Re-run
  them from the exports.

---

## 2. What holds up

- **The CHARGE averaging premise is quantitatively confirmed.** Each CURRENT
  sample is one 1.58 s conversion cycle, so one hour of CHARGE averages
  3600 / 1.58 = 2,278 cycles. For zero-mean white contamination the hourly sd
  should be 18.11 / √2278 = 18.11 / 47.7 = 0.38 mA. The turnover measured
  0.39 mA [D from turnover M].
- **The samples are white at 2 s.**
  - Lag-1 autocorrelation is −0.003 (noisy) and −0.002 (quiet).
  - The sd of noisy-state block means follows the white-noise prediction out
    to 5 min: 2.77 vs 2.75 mA at 1 min, 1.27 vs 1.23 mA at 5 min [M].
- **The turnover's regime statistics reproduce** [M]:

  | | turnover | this export |
  |---|---|---|
  | noisy mean / sd | −8.28 / 18.11 mA | −8.27 / 18.01 mA |
  | noisy blocks / n | 411 / 61,017 | 413 / 61,396 |
  | quiet mean / sd | −7.22 / 5.44 mA | −7.22 / 5.49 mA |
  | quiet blocks / n | 608 / 89,254 | 618 / 90,715 |

- **The turnover's arithmetic checks.**
  - 1 µV / 375 µΩ = 2.67 mA.
  - 2.67 mA × 1,680 h = 4.49 Ah = 1.13 %.
  - 13.1 / 397 = 3.3 %.
  - Welch t = 0.88 / √(0.39²/37 + 0.31²/37) = 0.88 / 0.082 = 10.7.
  - Staleness 80 × 60 / 3600 / 397 = 0.336 %.
  - Budget rows 1.34, 0.49, 0.16 and 0.0025 %/mo.
- **These decisions are right:**
  - not seeding the anchor from the 96.7 % estimate;
  - catching NAN → `runtime_hours` 0.0 h (line 1590);
  - keeping the WiFi-off test build separate from V1.28;
  - leaving the SW integrators and the 09-18 prediction rows alone.

---

## 3. Blocking before R1

### B1. The monitor energy balance does not close

V1.28 assumes the shunt sees the monitor's own draw. A rough check says it
should see more than it does:

1. `power_save_mode: none` (line 554) keeps the ESP32-C3 receiver on
   continuously.
2. The receive current is 84 mA at 3.3 V [S, secondary: a third-party
   reproduction of Espressif's "Current Consumption Depending on RF Modes"
   table. Confirm against Espressif's datasheet].
3. 84 mA × 3.3 V = 277 mW.
4. Through the D24V7F3 at an assumed 85 % efficiency [I, not verified at this
   load], that is 277 / 0.85 = 326 mW in.
5. At 13.26 V, 326 mW / 13.26 V = 24.6 mA from the bank. That is before the
   OLED, INA228 (640 µA typ at 3.3 V [S: SLYS021A §6.5]) and LED.
6. The shunt sees 7.3–8.2 mA in total [M]. The header (line ~80) says
   "Monitor ~100 mA". If that is the 3.3 V-side figure, it agrees with the
   estimate and makes the gap sharper.

Either the radio is not in continuous receive, in which case correct the
header and the survival-sleep note, or part of the monitor's supply returns on
the battery side of the shunt. §8 records bypass as impossible by
construction. The arithmetic does not support that yet.

If it is bypass, V1.28 inherits an unseen drain of 25 mA × 730 h = 18.3 Ah/mo,
which is 4.6 %/mo. That is larger than every other budget term combined, and
invisible to both ledgers.

**To close it** (either one is enough):

- Have the T1 build publish the **mean** current as well as the sd (§6). If
  the monitor is on the shunt, the drain must fall when the radio is off.
- Take one DMM reading in series with TB1 BATT_RAW. It is physical work, so
  Bill chooses how (R14).

§8.2 (the third state) may settle this for free.

### B2. V1.28 moves OBSERVABILITY code into CORE

The header promises the HW counters "never feed back into CORE", and
V1.23/25/26 were reviewed under that promise. V1.28 makes `hw_charge_ah`, the
bridge and the reset check the source of the displayed SOC and runtime.
"Keep as is" is the right code decision but the wrong review status. The code
needs a CORE-grade pass, and the header's isolation statement must change. The
pass finds three gaps.

**(a) The reset detector runs only at boot.**

The INA228 breakout is socketed. A VS contact glitch can reset it without
resetting the ESP [I]. POR asserts when VS falls below 1.26 V typ
[S: SLYS021A §7.4.2 p18]. After a POR:

- SHUNT_CAL returns to its reset value 1000h = 4096 [S: §7.6.1.3 p24].
- The firmware's SHUNT_CAL is 13107.2×10⁶ × (200 / 2¹⁹) × 375×10⁻⁶ = 1875
  [D: §8.1.2 eq. 2]. Every current-derived value then reads
  4096 / 1875 = **2.18× high**.
- ADC_CONFIG reverts to FB68h: 1052 µs conversions, no averaging
  [S: §7.6.1.2 p22].
- CHARGE restarts from 0.
- **Nothing trips.** The watchdog watches bus voltage, which needs no
  calibration.

This hazard predates V1.28; it already hits the SW ledger. V1.28 makes it
SOC-critical. Fix it in the `hw_charge_ah` lambda:

1. Before reading CHARGE, read back SHUNT_CAL (0x02) and the TEMP_LIMIT
   sentinel (0x10). That is two 2-byte reads per minute. Read SHUNT_CAL on
   the running device once and use that value, rather than hard-coding 1875
   (0x0753).
2. On a mismatch, return `{}` **before** updating `hw_charge_saved_ah`.
   Otherwise that poll saves `raw_new + old_offset`, and the bridge later
   restores a wrong value.
3. Publish the event and call `App.safe_reboot()`. The existing boot path then
   bridges.

Do not read DIAG_ALRT in this check. The ALERT-latch ownership comment
(~lines 396–402) still applies.

**(b) Retire the "first boot on sentinel firmware" branch** (lines ~461–468).

Its 0.5 Ah threshold assumes the check runs within ~3 s of power-up (header:
350 A × 3 s = 0.29 Ah). A reset caught by a 60 s poll during an 80 A charge,
counting at 2.18×, reaches 80 × 2.18 × 60 / 3600 = **2.9 Ah** [D]. The boot
check would read that as "no reset" and skip the bridge.

The branch was a one-time migration path. Replace it with a persisted
`sentinel_established` flag. Once the flag is set, a missing sentinel always
means a reset.

**(c) Add a freshness predicate.**

A failed CHARGE read returns `{}`, so `hw_charge_ah` keeps its last state and
a CHARGE-based SOC freezes silently. The source sensor should declare CHARGE
valid only when all three hold:

- the last good read was within ~3 polls;
- the anchor is finite;
- this boot's reset check passed.

### B3. Freeze the error with a provisional anchor, not the SW ledger

The turnover's fallback continues the SW ledger. In the quiet state that
ledger books 0 % of the drain, so its error keeps growing at 1.34 %/mo until
the next full charge.

Instead, while `hw_charge_anchor_ah` is NAN but CHARGE is valid, seed a
**provisional** anchor that makes the CHARGE-based SOC equal the ledger's SOC
at that instant:

```
A_p = hw_now − (soc_sw − 100) / 100 × ${validated_capacity_ah}
check: 100 + (hw_now − A_p) / C × 100 = 100 + (soc_sw − 100) = soc_sw   ✓
```

What this gives:

- No step at the V1.28 boot.
- The error is frozen at what the ledger had already accumulated instead of
  growing.
- The turnover's optional carry-forward after an unbridged reset becomes the
  same mechanism, so there is one code path instead of two.

This does not violate turnover decision 2, because nothing is baked in
silently:

- The source text sensor names the state, e.g.
  `INA228 CHARGE, provisional anchor (reads high by ledger error to <date>)`.
- Only an absorption-confirmed full charge promotes the anchor.
- Keep the provisional anchor in its **own global**, so `hw_charge_anchor_ah`,
  `cycle_integration_delta`, CYCLE CONFIRM and the 09-18 prediction rows are
  untouched.

The degradation ladder, decided at design time:

1. CHARGE with a confirmed anchor.
2. CHARGE with a provisional anchor.
3. SW ledger, only when CHARGE itself is invalid (B2c).
4. Never NAN.

The source sensor should also report where the anchor came from. Under V1.28
the "Mark as Fully Charged" button (2672–2673) sets CORE SOC to 100 % in one
HA tap, with no record that it was not a real full charge. Label it
`anchor: manual`.

---

## 4. Accuracy budget, idle month (replaces the turnover §5 table)

Conversion used throughout: **1 mA for a month = 0.184 %/mo**
[D: 1 mA × 730 h = 0.73 Ah; 0.73 / 397 = 0.184 %].

| term | size | basis |
|---|---|---|
| SW ledger today, quiet state (for comparison) | 1.34 %/mo low | [D] turnover; unchanged |
| INA228 offset, uncorrected | ≤ 0.49 %/mo | [D] 2.67 mA; ±1 µV max, TCT > 280 µs [S: §6.5 p5] |
| **invisible drain** (cell self-discharge + BMS, inside the batteries) | **unknown**; 0.184 %/mo per mA | hook at 0; RECON measures it at the next clean full→full bracket |
| **monitor supply, if it bypasses the shunt** | **~4.6 %/mo** | [D] B1 |
| **contamination DC, quiet state** | **unbounded until T1/T2** | [M] §7: the quiet state is contaminated too |
| noisy-state excess (0.88 mA), if none is real | ≤ 0.16 %/mo, only while noisy | [D] turnover; a *relative* bound between states |
| thermal EMF at shunt / Kelvin-lead junctions | 0.49 %/mo per µV | not in any INA228 spec; a T2 short at the pins cannot see it |
| offset drift (matters once T2 subtracts an offset) | ≤ 0.005 %/mo per °C | [D] 10 nV/°C max [S: §6.5 p5] → 0.027 mA/°C |
| time base (oscillator) | ≤ 0.007 %/mo at idle | [S: §6.5 p5, §7.3.6 p16] ±0.5 % at 25 °C, ±1 % over temperature, and it clocks the charge count; 0.5 % × 1.34 %/mo |
| bridge, per bridged INA228 reset, **under load** | 0.25 % at 30 A; 0.67 % at 80 A | [D] V1.26 header: 10 mAh + ~2 min of flow; 80 × 120 / 3600 = 2.67 Ah |
| slow hour-scale component | ~0.01 mA equivalent if zero-mean | [M/D] §7: 0.32 mA / √730 |
| symmetric noise | averages out | [M] §2 |

**The turnover §2 estimate is one-sided.** The ±1.1 % on "~96.7 %" covers only
the INA228 offset. Seventy days of invisible drain push the true SOC lower,
never higher, so 96.7 % is closer to an upper bound than a centre.

**Capacity.** 397 Ah dates from Oct 2025 (line 290). Publish Ah-below-full,
which does not depend on capacity, alongside %, and use
`${validated_capacity_ah}f` in the formula, not a literal `397.0`.

---

## 5. Outage budget: the §6 unattended moment

The turnover budget is for an idle month. During an outage, different terms
dominate.

**O1. Coulombic efficiency accumulates.**

- CHARGE books every Ah in at 100 %.
- At the firmware's own `recon_coul_eff` of 0.99, 1 Ah per 100 Ah recharged
  is booked but not stored. That reads 1 / 397 = 0.25 % optimistic per
  100 Ah [D].
- The outage load model swings the bank about 50 points a day (53 % low →
  103 % end of day), roughly 200 Ah. So ~2 Ah, or **~0.5 %/day optimistic**,
  compounding until an anchor fires [D].
- Gain errors (shunt tolerance, oscillator) scale with depth of discharge but
  cancel over a full cycle. CE does not cancel.

**Decision for R1:** either apply `recon_coul_eff` to positive CHARGE
increments (conservative, but it depends on an assumed η), or publish
Ah-in-since-anchor so the uncertainty is visible. Optimistic is the wrong
direction for this system.

**O2. The anchor can fire on a truncated charge.**

- `absorption_reached` needs only 60 s at ≥ `full_charge_v_min` (14.2 V per
  the line-2527 comment) with I > 0.
- The anchor fires on the `is_charging` release (I < 0.05 A for 60 s,
  lines 2228–2260) if absorption was reached and I ≥ −1 A.
- Outage sequence: the generator stops mid-CV, then more than 60 s passes
  near 0 A before the loads move to the inverter. Result: **100 % is anchored
  on an incomplete charge**, in exactly the outage cycle.

V1.28 makes the anchor the single source of truth, so add a **taper
criterion**: record the charge current over the last CV samples before the
stop, and anchor only if it had tapered below a threshold. Pick the threshold
from LiTime completion logs; the CV absorption telemetry already exists.
Otherwise log a partial session.

---

## 6. Tests and adjacent items

**T1 (WiFi-off build).**

1. Publish the **mean** current, not only the sd. This answers B1.
2. Run it in a noisy spell. With coexistence ON, spells are noisy 77 % of the
   time (§8.1).
3. Read the result against three outcomes, not two:

| sd with WiFi off | reading |
|---|---|
| ≈ 0.2 mA | the monitor's radio explains everything |
| ≈ 5 mA | the radio explains the regime switch; something else explains the quiet residual |
| ≈ 18 mA | the leads |

If the radio is implicated, one more split remains: radiated coupling versus
conduction through the shared 3V3 rail. The INA228's supply rejection is
specified only at DC, ±0.5 µV/V max [S: §6.5 p5].

**T2 (shorted input).**

- Run it in the noisy regime.
- A short at the INA228 pins includes board and radio pickup and excludes
  lead pickup.
- A short at the shunt end of the leads includes lead pickup and excludes the
  shunt-body thermocouples.
- Neither sees thermal EMF at the shunt body.
- The offset drift bound means a correction made at one temperature holds to
  ~0.027 mA/°C.

**Turnover §8 alias item.** It is correct only in its narrow form. Whiteness
at 2 s rules out a beat with the poll. It does not rule out fast periodic
interference aliased by the INA228's own sub-sampling (128 shunt conversions
per cycle, spaced 3 × 4.12 ms = 12.36 ms apart), which would also look white
at 2 s. This does not affect V1.28.

**Scope.** V1.28 fixes SOC only. The CURRENT channel stays contaminated, and
runtime, the ±50 mA state thresholds and Ri all use it. Bill's stated goal
("full accuracy of the INA228") needs a monitor-side fix. If T1 points at the
leads, TI recommends a differential RC filter at the inputs: series R of
≤100 Ω with a 0.1–1 µF ceramic capacitor [S: §8.1.4 p34]. Keep R low, because
the gain error ≈ 2R / (R_DIFF + 2R) with R_DIFF = 92 kΩ [S: §6.5 p5]:

| R per leg | gain error | other effects |
|---|---|---|
| 100 Ω | 200 / 92,200 = 0.22 %, ~4× the chip's 0.05 % gain spec | |
| 10 Ω | 20 / 92,020 = 0.022 % | corner 1 / (2π × 20 Ω × 1 µF) ≈ 8 kHz; bias-current offset ≤ 2.5 nA × 10 Ω = 25 nV ≈ 0.07 mA |

Also twist the Kelvin pair.

**Turnover §9 (reboots).** ESPHome's `debug:` component offers a
`reset_reason` text sensor and a `min_free` heap sensor intended for leak
detection [S: esphome.io/components/debug; confirm in the 2026.9.0 source,
R6]. A slow leak is a plausible cause of spaced reboots, and heap is the slow
variable to telemeter. A zero-component alternative is to call
`esp_reset_reason()` in `on_boot` and publish it the same way as
`ina228_reset_check`. Correlate both reboot times with the ROUTER CHANGE
record.

---

## 7. Data validation: results

**Confirms**

- **The quiet state is contamination, not load.** 8.69 % of quiet samples
  read > 0 mA (charging direction) with no charger connected. The Gaussian
  prediction is 9.42 %. Skew is 0.012 [M]. The turnover's §4 symmetry
  argument therefore applies to the quiet state too.
- **The noisy distribution** has skew 0.016. 6.10 % of samples are above
  +20 mA against a Gaussian 5.83 %, with excess kurtosis 1.37 [M].
- **The INA228 floor is never reached.** No 5-min block in 14 days has
  sd < 2.2 mA [M].
- **The slow component is real.** The 1-h block-mean sd exceeds the
  white-noise prediction [M/D]:
  - quiet: √(0.349² − 0.142²) = 0.32 mA (50 blocks);
  - noisy: √(0.436² − 0.354²) = 0.25 mA (221 blocks).

  The quiet figure matches the 0.29 mA derived from the turnover's CHARGE
  numbers.
- **The turnover's 6-day extension holds.** From the V1.27 build
  (09-18 20:19Z) to 09-24 15:20Z [M]:
  - 138.8 h (5.78 d), mean drain 7.96 mA;
  - 1.105 Ah drained, 0.057 Ah booked, **1.048 Ah unbooked** (turnover:
    6 d × 7.6 mA = 1.09 Ah).

  12.0 + 1.05 = 13.05 Ah, and 13.05 / 397 = 3.29 %. The ~96.7 % estimate
  stands.
- **No charge or discharge event in 30 days** [M]:
  - hourly current −5.5 to −9.7 mA (08-25 → 09-10);
  - maximum voltage 13.3008 V, never near 14.2 V.

  The anchor is correctly NAN. O1/O2 cannot be tested from these files.

**Corrects**

- **Noise floor** (a correction to my review). The stored current sits on the
  CURRENT_LSB grid (200 / 2¹⁹ = 0.3815 mA), not on the 0.83 mA ADC step.
  - Floor ≈ √(0.16² + (0.3815/√12)²) = √(0.0256 + 0.0121) ≈ **0.19 mA** [D].
  - The 0.16 mA rms comes from 19.7-bit noise-free ENOB at 4120 µs × 128
    [S: Table 8-2 p33], taking p-p ≈ 6.6σ [I].
  - Quiet is therefore ≈ 28× the floor and noisy ≈ 93×, not 15–25×.
  - The line-345 comment ("~0.83 mA step, 50 mA ≈ 60× step") has the same
    issue: 50 mA is 131 CURRENT_LSBs.
- **SW-ledger booking** (a correction to the turnover §3).
  - The net booked share in the noisy state is **10.0 %**
    [M: 0.997 mA booked out − 0.166 mA booked in = 0.831 mA, of 8.27 mA].
  - The turnover's 11–12 % counts only the discharge side. Excursions past
    +50 mA are booked as charge in (`charge_current`, line 1397).
  - The share depends heavily on noise amplitude: from 09-10 to 09-18 it was
    **2.6 %** [M].
- **CHARGE time base** (tempers my review's "validated" claim).
  - For the 08-31 20:50Z → 09-18 20:00Z segment, the samples integrate to
    **3.718 Ah** over 430.5 h, a mean of 8.64 mA [M].
  - Unbooked is 3.48–3.62 Ah, depending on the booked share assumed for the
    hourly-only part (2.6–10 %).
  - The V1.26 header's CHARGE figure is 3.72 Ah unbooked. So CHARGE counted
    0.10–0.24 Ah more, i.e. 0.23–0.57 mA, or about 2.6–6.6 % [D].
  - The turnover's 37-h windows agreed to ~1 %; this segment does not.
  - The segment's exact end time is also uncertain.
  - Idle impact is ≤ 0.57 × 0.184 ≈ 0.1 %/mo, so the budget does not move.
  - **Action:** export `sensor.battery_bank_monitor_hw_net_charge_ina228` for
    08-31 → 09-18 and compare directly.

**Cannot test from these files**

- B1: no interval with the radio off. §8.2 may help.
- O1 and O2: no charging.
- T1 and T2.
- Invisible drain: needs RECON at the next full charge.

---

## 8. New findings

### 8.1 The regime switch runs on a ~25 min hysteresis timer

Over 09-10 → 09-24 there were **101 switches**, and the current was noisy
**77 %** of the time before coexistence went off [M]. The two states have
different dwell-time shapes [M, 1-min classification]:

| spell length (min) | 5–9 | 10–14 | 15–19 | 20–24 | **25–29** | 30–34 | 35–39 | 40–44 | 45–49 | 50–54 | 55–59 | 60+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| quiet spells | 3 | 0 | 1 | 3 | **24** | 3 | 4 | 4 | 3 | 1 | 3 | 10 |
| noisy spells | 4 | 9 | 6 | 1 | 4 | 5 | 4 | 2 | 4 | 2 | 4 | 54 |

- **Quiet spells have a floor.** There are 37 quiet spells of 15–40 min, with
  a median of 27 and an IQR of 25–29. Only two are shorter than 24 min (17
  and 21).
- **Noisy spells have no floor**, including nine of 10–14 min.

A dwell time with a hard floor is what a protocol timer looks like, and 802.11n
20/40 BSS coexistence has exactly this shape:

- A single trigger event forces the BSS from 20/40 MHz down to 20 MHz.
  Reverting requires several consecutive scan intervals with no trigger
  [S: IEEE 802.11-07/1975, LB97 20/40 coexistence, Broadcom].
- Implementations use a trigger-scan interval of 300 s [S: openwrt
  mtk-wifi-gpl `include/dot11n_ht.h`] and a transition delay factor of 5
  [S: Ralink RT5370 SoftAP v2.6.0.0 release notes].
- 5 × 300 s = 1,500 s = **25 min** [D].
- 25–30 min in practice = 25 min plus the wait for the next scan [I].

Caveats: an early 802.11n draft used 1,800 s and 4 [S: 11-07/1975], and the
R6400's own values are unconfirmed [I].

Implications:

- **Which state is which.** The natural quiet spells are almost certainly the
  router's **20 MHz fallback**. Coexistence OFF is also quiet, yet the link
  runs at 40 MHz (150 Mbps, turnover §8). So **channel width is not the
  mechanism**, and the turnover's §8 entry stands. The noisy condition is
  **40 MHz with coexistence active** [I].
- **The stopgap has a mechanism.** The turnover counts the coexistence test as
  n=1, confounded with the radio restart. The 37 natural spells carrying the
  hysteresis signature largely resolve that.
- **Prediction to register in CHANGELOG now** (it scores itself): with
  "Enable 20/40 MHz Coexistence" OFF, there will be no noisy spell (5-min
  sd > 9 mA) and no 20–30 min quiet interludes until a router reset.
- **Time of day** [M, descriptive only]: 86 % of 5-min blocks from 00:00 to
  04:59 EDT are noisy, against 61 %, 65 % and 64 % at 10:00, 15:00 and
  17:00 EDT. That fits daytime triggers from neighbouring networks [I].
- **It does not pick the coupling path.** There is no 300 s periodicity in the
  noise power. Folded on 300 s in 10-s phase bins, noisy runs 214–236 mA² and
  quiet runs 35–38 mA² [M]. So the noise is not scan bursts; it is continuous
  for as long as the state lasts. T1 is still the test that decides (a) versus
  (b).

### 8.2 A third, quieter state with a +3 mA drain step

Three windows sit below the quiet state [M]:

| window (EDT) | 1-min sd | mean |
|---|---|---|
| 09-11 14:23–14:26 | 1.8–2.1 mA | −10.1 to −10.8 mA |
| 09-18 12:03–12:06 | 1.8–2.1 mA | −9.9 to −11.1 mA |
| 09-22 14:17–14:26 | 1.7–2.9 mA | −9.3 to −11.1 mA |

- This is the lowest noise in the record, though still ~10× the 0.19 mA
  floor.
- The drain rises ≈ **+3.2 mA** at the same time: ≈ −10.4 mA against the
  quiet −7.2 mA.
- The 09-22 window starts ~6 min after the router came back from its
  14:06–14:11 power-down, so Bill was likely in the basement.

Something on the monitor changed its own draw by ~3 mA at the moment the
noise dropped. If it was the monitor's own load (for example the OLED page
button), then **the shunt saw the monitor's load step, which is direct
evidence against the bypass hypothesis in B1**. Whatever lowered the noise
from ~5.5 to ~2 mA is also a lead on the coupling path. See §11 Q1.

### 8.3 Idle OCV is a free trace of the slow variable

The daily median bus voltage falls smoothly from 13.3008 V (08-25) to
13.2934 V (09-24) [M]:

- −7.4 mV over 30 d = −0.25 mV/day;
- easing from 0.26 to 0.23 mV/day between the two halves [D].

It cannot be converted to SOC without this bank's OCV–SOC curve. It does not
depend on capacity, though, and a change in slope would flag a change in
*total* drain, including drain the shunt cannot see. A daily idle-OCV slope
sensor is cheap observability.

Voltage noise does not track the regime (5-min sd 0.071 vs 0.067 mV) [M].
That is expected: 18 mA × 375 µΩ = 6.75 µV at the shunt, far below the 195 µV
bus step. The voltage channel therefore cannot discriminate the coupling
paths.

---

## 9. Minor items

- Drive CURRENT_LSB in the `hw_charge_ah` lambda (`3.814697265625e-4`, which
  "MUST track max_current") and the `max_current` in the ina2xx block from
  one substitution. It is CORE scaling now.
- The `reset_on_boot: false` comment says the accumulators do not affect
  primary SOC. Under V1.28 the setting is load-bearing; say so.
- The clamp at 100 % hides charge above the anchor, e.g. a charger restart on
  a full bank (≤ ~1 Ah per the recon note, ≈ 0.25 %). Ratchet the SOC anchor
  up whenever `hw` exceeds it.
- The "Manual SOC anchor" comment sits above the Ri-reset button, not above
  "Mark as Fully Charged".
- The header says "reviewed against ESPHome 2026.5.x". The deployed version
  is 2026.9.0.
- NVS: 30 `restore_value` globals now, and V1.28 adds 2–3. Count them per the
  validation skill.
- Gate 2 notes that the secrets were exposed and not rotated. The V1.28 flash
  is the natural moment to rotate them.
- Staleness (turnover decision 3): agreed. Drive the SOC from `hw_charge_ah`'s
  `on_value`.

---

## 10. Proposed edits to `soc-accuracy-turnover.md`

- **§2**
  - Mark the ±1.1 % as offset-only. Invisible drain since 07-16 is
    one-sided, so 96.7 % leans toward an upper bound.
  - Note that the data reproduce the 6-day extension: 1.048 Ah unbooked.
- **§3**
  - Change "11–12 %" to "≈10 % net (12 % discharge side, less 2 % booked as
    charge in); amplitude-dependent, 2.6 % for 09-10 → 09-18."
  - Add: the quiet state is contamination too; 8.69 % of quiet samples read
    > 0 mA.
- **§4**
  - Add the §8.1 hysteresis evidence to the coexistence item, which is no
    longer just n=1.
  - Add the prediction row.
  - Add the third state (§8.2).
- **§5**
  - Decision 1: replace it with the B3 ladder.
  - "Keep as is": keep the code, re-review it as CORE, and add B2 (a)–(c).
  - Replace the budget table with §4 here and add the §5 outage budget.
  - Add O1 (CE decision) and O2 (taper criterion).
  - Use `${validated_capacity_ah}f` in the formula.
- **§6:** name the outage terms (O1, O2) that the unattended moment exposes.
- **§7**
  - T1: publish the mean; use the three-outcome reading guide.
  - T2: run it in the noisy regime, with both short locations.
- **§8**
  - Alias item: narrow form only.
  - Channel-width item: stands, with the §8.1 refinement (quiet occurs at both
    20 and 40 MHz).
  - Bypass item: mark "pending one measurement (B1)".
- **§9:** add `min_free`, or `esp_reset_reason()` via the reset-check pattern.
- **§10 gate 3 (host replay):** add synthetic cases:
  - NAN anchor at boot → provisional anchor;
  - mid-run POR (SHUNT_CAL = 1000h, sentinel = 7FFFh, CHARGE restarting at
    2.18×) → no save, reboot, bridge;
  - stale CHARGE read;
  - truncated-CV stop;
  - charger restart on a full bank (ratchet);
  - manual button.
- **§11:** add these exports and this document as evidence.

---

## 11. Open questions for Bill

1. What was happening at the monitor at 09-11 14:23, 09-18 12:03 and
   09-22 14:17 EDT (OLED page button, standing near the leads, anything
   else)? This may close B1 for free.
2. B1: does the monitor's supply return land on the load side or the battery
   side of the shunt? Or take the one DMM reading (R14).
3. There is an earlier ~2.4 mA INA228 offset figure for this monitor. Was it
   measured or derived? If measured, T2 may already be done.
4. O1: apply `recon_coul_eff` to positive CHARGE increments, or publish
   Ah-in-since-anchor?
5. O2: what tail-current threshold do the LiTime completion logs support?
6. Optional: can the R6400 show its OBSS scan interval or transition delay?
7. What is the exact end time of the V1.26 header's 3.72 Ah segment? Please
   export HW Net Charge (INA228) history for 08-31 → 09-18.

---

## 12. Suggested order

1. Export the HW Net Charge history (free). It closes the 18-day CHARGE vs
   samples gap.
2. Answer Q1 (free). It may close B1.
3. Register the coexistence prediction row in CHANGELOG now.
4. Run the T1 build (mean + sd) during a noisy spell. Coexistence ON is set by
   Bill (R12).
5. Write the R1 statement for V1.28 incorporating B2, B3, O1, O2 and the
   rewritten budgets. Then run gates 2–6 as the turnover lists them.

This file is uncommitted. Commit it separately, and only when Bill asks.
