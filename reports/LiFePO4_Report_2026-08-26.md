# LiFePO4 Battery Bank: Technical Report — INA228 Era

**Data through:** August 26, 2026
**Published:** August 26, 2026
**Version:** 2026-08-26
**DOI:** [10.5281/zenodo.14538065](https://doi.org/10.5281/zenodo.14538065)

---

## Abstract

This report covers the first 41 days of the INA228 instrumentation era and closes
the gap between the April 5, 2026 report and today. The Shelly Plus Uni voltage
watchdog was retired on July 16, 2026 and replaced by a purpose-built monitor —
an INA228 20-bit current/voltage front end on a 375 µΩ shunt, polled every 2 s —
that measures current directly for the first time in this study.

**Key result: the quiescent drain that every prior report could only infer is now
measured — and it turns out to be the instrument itself.** The bank draws
**7.4 mA ± 2.4 mA** time-weighted over 41 quiescent days (−7.2 Ah, 1.8% of the
validated 397 Ah, ≡ 1.4 %/month) [M]. With the Shelly and the DROK panel meter
both retired and the inverter off, the INA228 monitor — powered from the busbars,
so its return runs through the shunt — is the only load on the bus. 7.4 mA at
13.35 V is 99 mW, which is what a Wi-Fi-associated XIAO ESP32-C3 behind an 87%
buck should draw [D]. **The bank's own external parasitic load is effectively
nil**, and the firmware header's "Monitor ~100 mA" is 14× high. The study's stated
"highest-value next step" — a direct bus-current measurement to collapse the
SOC/endurance uncertainty in the flat-OCV region — is complete.

The quoted uncertainty is not statistical. The 41-day mean is tight; its accuracy
is bounded by this INA228's commissioning-measured 0.9 µV ≡ 2.4 mA shunt offset,
which is the larger term and which no amount of averaging reduces.

**Second result: the bank returns to its own baseline after ten months.** With the
two instruments cross-calibrated over their 817-sample overlap, the November 2025
stasis baseline of 13.270 V (Shelly) restates as **13.301 V** on the INA228 scale.
The INA228 reads **13.3005 V** on the final day of this window — a difference
smaller than the cross-calibration uncertainty. Between those dates the bank sat
through a 95-day storage stasis at zero measurable drift, a full 110.7 Ah
discharge campaign, and a complete recharge.

**Third result, and the one that needs action: the firmware's coulomb ledger
cannot see the drain it is meant to track.** Over 31.96 continuous days the INA228's
own hardware CHARGE register accumulated −5.8222 Ah and an independent
integration of the published 2 s series returned −5.8019 Ah (0.35% apart), while
the firmware's software ledger recorded **−0.0149 Ah — 0.26% of the charge the
same chip moved**. The ±0.05 A integration deadband is 6.7× larger than the drain
it is excluding. State of charge consequently reads 99.996% when the coulomb
truth is ≈98.2%, and the error grows at ≈1.4 %SOC/month of storage with nothing
on the dashboard to indicate it. See §6.

**What this report does NOT establish: true self-discharge.** The shunt measures
charge crossing the terminals; self-discharge happens inside the cells and does
not. That measurement is scheduled — discharge below 80% SOC, then charge, and
reconcile the full→full cycle — and §6 is its prerequisite: run it with the
present deadband and the monitor's own 0.177 Ah/day will be booked as
self-discharge, an artefact of ≈1.3 %/month that would land inside the published
LFP range and read as a confirmation. See §7.7.

**Status: STASIS — every criterion passes, most of them by one to two orders of
magnitude.** The old thresholds were written for a 10 mV instrument and no longer
discriminate; §5.3 proposes replacements.

> **Provenance tags** used throughout, per the project's evidence convention:
> **[M]** measured (carries n, window, source series) · **[S]** spec (document +
> section) · **[D]** derived (arithmetic on [M]/[S], formula shown) ·
> **[I]** inferred (a model not yet tested; carries its falsifying observation).

---

## Executive Summary

1. **Direct measurement, 41 days, 1.79 M samples — and the load is the monitor.**
   7.4 ± 2.4 mA time-weighted; regime means 5.9–8.8 mA [M]. With the Shelly and
   DROK meter retired and the inverter off, the INA228 monitor is the only thing
   on the busbars, and at 99 mW the measurement matches what its parts list
   predicts [D]. Endurance is **≈15 months to 80% SOC** on the validated 397 Ah
   — but that is the endurance *of the instrument*, since the instrument is the
   entire load (§7.6).
2. **The 2026-08-04 step is an instrument offset shift, not a load change.** The
   drain stepped 5.90 → 8.78 mA inside one hour. The operator's account of that
   window: the bank was **rewired to eliminate stacked lugs**, with nothing added
   or removed. Nothing was available to consume +50% more — the monitor is the
   only load, it did not reboot (32 days continuous uptime spans the date), and
   the firmware did not change. What did change is joints in the shunt's own
   current path. The step is +2.88 mA ≡ **1.08 µV** at this shunt, the same order
   as its 0.9 µV commissioning offset (§7.3).
3. **The coulomb ledger is blind below 50 mA** (§6). Three independent
   accountants over the same ~32 days: silicon −5.8222 Ah, independent
   integration −5.8019 Ah, firmware −0.0149 Ah.
4. **The detector designed to catch exactly this has never run.** The firmware
   publishes a `Cycle Integration Delta (SW−HW)` sensor whose whole purpose is to
   surface software-versus-hardware divergence. It returns NaN until a full-charge
   anchor seeds its snapshot, and no anchor has fired since the sensor was added.
   It has no series in InfluxDB at all.
5. **Post-charge relaxation resolved for the first time.** A two-exponential fit
   over 55,691 minute means gives τ₁ = 2.16 h, τ₂ = 3.12 d, asymptote
   13.3042 V, residual sd 5.6 mV [M]. Practical rest-to-OCV time is ≈13 days,
   not the ≈30 minutes that applies after a *load* step.
6. **The noise floor fell 2.7 decades.** Within-day voltage standard deviation
   went from 60.25 mV on day 1 to **0.131 mV** on day 41 — below the INA228's own
   195.3 µV bus LSB, as expected for a dithered quantised signal [M].
7. **The Apr 5 → Jul 14 gap is closed.** 95 days of Shelly daily minima (Apr 1 –
   Jul 4) show drift of **+0.0074 ± 0.0655 mV/day, p = 0.91** — indistinguishable
   from zero over a full quarter [M].
8. **Cycle-2 coulombic efficiency is still not available.** Only one full-charge
   anchor has ever fired (2026-07-16). `last_coulombic_efficiency` has read the
   commissioning value 95.78% — an accounting floor, not a measurement —
   unchanged for 41 days, and `cv_absorption_time` is likewise frozen at
   16.82 min. Both need a second full charge.
9. **True self-discharge remains unmeasured, and §6 is in its way.** The shunt
   sees only charge crossing the terminals. The scheduled measurement — discharge
   below 80% SOC, then charge, then reconcile — will misattribute the monitor's
   0.177 Ah/day to the cells unless the coulomb deadband is fixed first (§7.7).

---

## 1. Instrument Transition

### 1.1 What changed

| | Shelly Plus Uni (retired 2026-07-16) | INA228 monitor (from 2026-07-14) |
| :--- | :--- | :--- |
| Measures | Bus voltage only | Bus voltage **and** current |
| Voltage resolution | 10 mV quantisation | 195.3 µV LSB, σ ≈ 0.10 mV intra-minute |
| Current | — | 375 µΩ shunt, ±163.84 mV range, 0.83 mA LSB |
| Cadence | ~2 min at retirement (was ~6 s) | 2 s, continuous |
| Accumulators | none | firmware Ah/Wh **and** the chip's own 40-bit CHARGE/ENERGY registers |
| Protection | none | 4 firmware alarms + 5 latched hardware limits on a dedicated ALERT pin |

Full build, defect and acceptance history is in
[`INA228 Monitor/Battery-Bank-Monitor-Commissioning-Report.md`](../INA228%20Monitor/Battery-Bank-Monitor-Commissioning-Report.md).
This report does not repeat it; it covers what the instrument has measured since.

### 1.2 Cross-calibration — putting both instruments on one scale

The two overlapped from the INA228's first bus reading (2026-07-14 23:38 UTC) to
the Shelly's retirement (2026-07-16 23:50 UTC). Every Shelly sample is paired
with the INA228's 60 s trailing mean at that instant; the paired set ships as
[`data/ina228/shelly_ina228_crosscheck.csv`](../data/ina228/shelly_ina228_crosscheck.csv).

| Subset | n | Shelly − INA228 | sd | 95% CI of the mean |
| :--- | ---: | ---: | ---: | :--- |
| All paired samples | 817 | −26.95 mV | 33.06 | [−29.22, −24.68] |
| **Bank idle and voltage still** | **148** | **−30.64 mV** | **7.84** | **[−31.91, −29.37]** |
| Under load, I < −5 A | 323 | −25.51 mV | 7.66 | [−26.35, −24.67] |

The quiescent subset is gated on **both** a quiet bank (|I| < 0.5 A) **and** a
still voltage (|dV/dt| < 1 mV/min). Without the second gate the spread inflates
from 7.84 mV to 33.06 mV: matching a 2-minute, 10 mV-quantised instrument against
a 2-second one during post-charge relaxation measures the relaxation, not the
offset. That is the ungated row above, and it is why it is not the row used.

![Shelly minus INA228](../figures/fig_shelly_ina228_offset.png)
*Figure 1 — Paired offset distributions. The idle and loaded subsets sit ~5 mV
apart, consistent with different sense-tap IR paths rather than a scale error.*

> **[M] Adopted offset: Shelly reads 30.6 mV low, 95% CI ±1.3 mV, n = 148.**
> **Limits:** the two subsets disagree by 5.1 mV and the ungated estimate by
> 3.7 mV, so the *usable* uncertainty when restating a Shelly-era figure is
> **±3 mV**, not ±1.3 mV. The overlap is 2 days at one temperature and one SOC;
> it does not establish temperature or SOC dependence of the offset, and it can
> never be extended — the Shelly is retired.

### 1.3 What the offset buys

Applying it to the Shelly-era anchors makes ten months of data directly
comparable:

| Shelly-era figure | As published | On the INA228 scale [D] |
| :--- | ---: | ---: |
| Nov 4, 2025 stasis baseline | 13.270 V | **13.301 V** |
| Repo "measured stasis OCV" | 13.262 V | 13.293 V |
| Apr 5, 2026 report, day-42 stasis | 13.251 V | 13.282 V |
| Feb 2026 pre-charge baseline | 13.225 V | 13.256 V |
| **INA228 measured, 2026-08-26** | — | **13.3005 V** |

The bank's rested plateau today is within **0.5 mV** of its November 2025
baseline restated on the same scale — well inside the ±3 mV cross-calibration
uncertainty, so the honest statement is **indistinguishable from the November
baseline**, not "0.5 mV above it".

![Ten-month timeline](../figures/fig_ina228_ten_month_timeline.png)
*Figure 2 — Ten months on one scale. The Shelly trace is the daily level (mean of
hourly midpoints through Mar 31; daily minimum Apr 1 – Jul 16 — the two
statistics are identical once the bank is in stasis, as Mar 27–31 shows
directly, where the hourly Min and Max are the same 10 mV code). Winter sat
30–40 mV below the November baseline; the July recharge returned the bank to it.*

---

## 2. Data Coverage

### 2.1 INA228 record

| Series | Samples | Window (UTC) | Cadence |
| :--- | ---: | :--- | :--- |
| Battery current | 1,790,710 | 2026-07-14 00:28 → 2026-08-26 19:45 | 2.00 s median |
| Battery power | 1,790,710 | same | 2.00 s median |
| Bus voltage | 502,956 | 2026-07-14 23:37 → 2026-08-26 19:45 | 2.08 s median |
| Pack temperature | 13,188 | same | 60 s |
| INA228 die temperature | 37,276 | same | 60 s |
| HW CHARGE register | 58,042 | 2026-07-17 12:30 → 2026-08-26 19:44 | 60 s |

Integrated coverage over the 42.19-day window is **99.93%**. Every gap longer
than 15 minutes falls inside the 2026-07-14/15 bring-up:

| Gap start (UTC) | Gap end | Duration | Cause |
| :--- | :--- | ---: | :--- |
| 2026-07-14 01:31 | 2026-07-14 22:02 | 20.52 h | bench bring-up, device off |
| 2026-07-14 22:05 | 2026-07-14 23:11 | 1.10 h | bring-up |
| 2026-07-15 00:27 | 2026-07-15 15:45 | 15.31 h | bring-up |

**From 2026-07-15 15:45 UTC to the end of the window there is no gap longer than
15 minutes** — 42.2 days of continuous 2-second telemetry. All analysis in §3–§6
uses that continuous span.

### 2.2 Bridging the April → July gap

The April 5 report ended at 2026-04-02. The INA228 record begins 2026-07-14.
Shelly daily-minimum exports covering 2026-04-01 → 2026-07-16 now ship as
[`data/shelly_daily_min_2026-04-01_2026-07-16.csv`](../data/shelly_daily_min_2026-04-01_2026-07-16.csv)
(107 rows), and the final Shelly high-frequency file (2026-06-17 → 2026-07-16,
8,343 rows, gzipped) is added to `data/high_freq_voltage/`. **The published record is now
continuous from 2025-10-29 to 2026-08-26 — 301 days.**

### 2.3 Published datasets

The raw 2 s series is ~130 MB and is not versioned. Four tiers ship instead:

| File | Rows | Contents |
| :--- | ---: | :--- |
| `data/ina228/ina228_hourly_*.csv` | 1,052 | hourly V/I/P min/mean/max, Ah, Wh, temps, coverage |
| `data/ina228/ina228_daily_*.csv` | 44 | same, daily |
| `data/ina228/stasis_ma60_*.csv.gz` | 55,691 | 1-minute MA-60s voltage means, stasis window |
| `data/ina228/coulomb_ledger_hourly.csv` | 968 | the three-way ledger of §6 |
| `data/ina228/shelly_ina228_crosscheck.csv` | 817 | the paired cross-calibration of §1.2 |
| `data/ina228/events/*.csv[.gz]` | 32,486 | **full 2 s resolution**, four event windows |

`scripts/ina228_export.py` rebuilds all of them from InfluxDB over any window;
`scripts/ina228_analysis.py` reproduces every figure and number in this report
from the published files alone, with no host access.

> **Three files ship gzipped** — `stasis_ma60_*.csv.gz`, the 70 W overnight
> event, and the final Shelly HF file — because plain they exceed the
> repository's 500 KB pre-commit gate. They are compressed, not downsampled, so
> no sample is lost; `pd.read_csv` handles the extension with no extra argument.

> **Note on reading the event files.** Home Assistant writes to InfluxDB on state
> change, not on a sample clock, so a series that stops writing has stopped
> *changing*. Bus voltage quantised to the 195.3 µV LSB genuinely holds for
> minutes under a steady load. The export therefore matches voltage and power to
> the current timestamps **backward** (last known value), which is the correct
> reconstruction; a nearest-match within a tolerance leaves 59% of the overnight
> leg NaN and would be read as missing data that does not exist.

---

## 3. Charge Characterisation

One charge event falls in this window: the LiTime 12 V / 14.6 V / 80 A charger,
2026-07-16 18:13 → 19:50 UTC, which set the study's first full-charge anchor.

| Metric | Value | Basis |
| :--- | ---: | :--- |
| Duration | 97.7 min (105.0 min window) | [M] |
| Charge delivered | **+115.375 Ah / +1585.80 Wh** | [M] left-rectangle, 2 s |
| CC current | 78.6 A mean, 79.30 A peak | [M] = 98.3% of nameplate |
| CV entry | 14.20 V at t ≈ 80 min | [M] |
| Peak voltage | **14.5842 V** | [M] = spec 14.6 V − 16 mV |
| Taper cutoff | 6.48 A ≈ C/77 | [M] |
| C-rate | 0.157 C | [D] 78.6 A ÷ 500 Ah nameplate |
| Pack ΔT | +2.7 °F | [M] DS18B20 |
| BOVL margin | 216 mV below the 14.80 V hardware limit | [D] |

![Charge profile](../figures/fig_ina228_charge_profile.png)
*Figure 3 — CC/CV profile at 2 s resolution. The oscillation above 14.4 V in both
panels is BMS balancing: 10.7 min of activity, 183 mV pk-pk, 8 reversals, the
~80–90 s cycle documented in the Shelly-era study and now countable.*

The independent integration here (+115.375 Ah) reproduces the firmware's own
accumulator (115.448 Ah) to **0.06%**, which is the integration-method agreement
that matters when both are seeing current well above the deadband. §6 is about
what happens when they are not.

**Charger AC→DC efficiency of 95.7% ± 2.5%** is carried forward from
commissioning [M, Kill-A-Watt, 112-min window] and is not re-measured here.

---

## 4. Discharge Characterisation

Three discharge legs fall in this window, all part of the commissioning campaign.
No unplanned outage has occurred since 2026-07-16.

| Leg | Duration | Ah | Wh | Mean I | Peak I | Vmin | Sag |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 70 W overnight | 937.7 min | 76.137 | 1009.58 | 4.87 A | 5.56 A | 13.2498 V | 1.2% |
| ~1 kW heater | 15.4 min | 19.458 | 252.84 | 75.67 A | 81.75 A | 12.9615 V | 2.7% |
| Inverter nameplate | 11.6 min | 15.053 | 195.36 | 77.53 A | 130.11 A | 12.8340 V | 3.6% |
| **Campaign total** | | **110.65** | **1457.78** | | | | |

110.65 Ah is **27.9%** of the validated 397 Ah [D]. The campaign minimum SOC was
**72.17%** — the bank never approached the knee.

![Discharge legs](../figures/fig_ina228_discharge_legs.png)
*Figure 4 — Bus voltage under three load levels, all on the same y-scale. Even at
inverter nameplate (0.26 C) the trace stays 434 mV clear of the 12.40 V warning
threshold. The step-recovery-step structure in panels 2 and 3 is the two
inverter-overload trips.*

**Alarm margins actually observed:**

| Threshold | Setting | Worst approach | Margin |
| :--- | ---: | ---: | ---: |
| Voltage Warning | 12.40 V | 12.834 V | 434 mV |
| Critical / BUVL (hardware) | 12.20 V | 12.834 V | 634 mV |
| Emergency | 11.80 V | 12.834 V | > 1 V |
| SUVL (hardware) | −250 A | −130.1 A recorded | 48% |
| Overvoltage / BOVL (hardware) | 14.80 V | 14.584 V | 216 mV |

> **[M] Limit — the 130.1 A is the instrument's number, not the world's.** The
> INA228 averages 128 conversions over 1.58 s, so it under-reports sub-2 s
> transients by design. The Kill-A-Watt max-hold on the same event implies
> ≈146 A instantaneous. **The 130.1 A is a lower bound on peak current, and the
> SUVL margin computed from it is an upper bound on the true margin.** The
> hardware SUVL comparator runs per-conversion and is the actual fast-transient
> guard; it did not fire, which bounds the true peak below 250 A.

---

## 5. Stasis Assessment

### 5.1 Post-charge relaxation

From the charger-stop edge the bank relaxed from 13.9945 V (day-0 mean) to
13.3005 V (day-41 mean). Fitting V(t) = V∞ + A₁e^(−t/τ₁) + A₂e^(−t/τ₂) over
55,691 one-minute MA-60s means:

| Parameter | Value |
| :--- | ---: |
| V∞ | 13.3042 V |
| A₁ / τ₁ (surface charge) | +0.1699 V / **2.16 h** |
| A₂ / τ₂ (bulk diffusion) | +0.6105 V / **3.12 d** |
| Residual sd, full span | 5.58 mV |
| 95% of relaxation complete | t ≈ 9.4 d [D] = 3τ₂ |
| 99% complete | t ≈ 14.4 d [D] |

![Relaxation](../figures/fig_ina228_relaxation.png)
*Figure 5 — Relaxation and fit residual. The residual falls below 1 mV around day
28 and then grows back to ≈4 mV by day 41: the two exponentials are fully decayed
there, and what remains is a slow linear decline the model does not contain. That
decline is the real coulombic loss of §5.2 — the residual growth is a feature of
the fit, not a defect in it.*

> **[M] Limits.** τ₂ = 3.12 d is fitted over 41 days at one temperature
> (68.0–70.5 °F pack) at one SOC (≈100%) after one charge profile. It should not
> be extrapolated to cold storage or to relaxation from partial SOC. It is also a
> different quantity from the commissioning report's post-**load** relaxation
> (τ₆₃ ≈ 7.1 min): surface-charge decay after a CV charge and polarisation decay
> after a current step are not the same process, and their time constants differ
> by three orders of magnitude.

### 5.2 Drift, now resolvable

| Window | Drift | r² | se | p |
| :--- | ---: | ---: | ---: | ---: |
| Last 3 days | −0.3330 mV/day | 0.990 | 0.0335 | 0.064 |
| Last 5 days | −0.3038 mV/day | 0.992 | 0.0156 | 3.0 × 10⁻⁴ |
| **Last 7 days** | **−0.3031 mV/day** | **0.997** | **0.0079** | **2.2 × 10⁻⁷** |
| Last 14 days | −0.3581 mV/day | 0.995 | 0.0074 | 4.3 × 10⁻¹⁵ |
| Last 30 days | −0.5524 mV/day | 0.939 | 0.0266 | 1.6 × 10⁻¹⁸ |

Every prior report in this series reached the same conclusion — "drift is
indistinguishable from zero" — because a 10 mV instrument could not resolve
0.3 mV/day. **It is not zero.** At 0.008 mV/day standard error the 7-day slope is
38 σ from zero. The longer windows are steeper because they still contain the
tail of relaxation; the 5- and 7-day figures agree to 0.001 mV/day and are the
stasis rate.

**Two paths to the loss rate, and what their comparison is worth** [D]:

| Path | Method | Result | What it measures |
| :--- | :--- | ---: | :--- |
| Voltage | −0.3031 mV/day ÷ 6.0 mV/%SOC plateau slope | −1.54 %SOC/month | **total** SOC decline |
| Coulomb | −7.2 Ah / 39.97 d ÷ 397 Ah | −1.38 %SOC/month | charge **crossing the shunt** |

The two are consistent, and this is the first time in the study that the
electrochemistry and the charge ledger could be compared at all — one instrument
now measures both.

> **[M] What the agreement does NOT establish — corrected 2026-08-26.** An
> earlier draft read the 11% gap as bounding true self-discharge, since the
> difference between "total decline" and "charge out through the terminals" is
> what stayed inside the cells. It does not bound it usefully, for two reasons
> that each dominate the gap:
>
> 1. **The voltage path is contaminated.** §7.4 shows the relaxation tail still
>    contributes more mV/day than the drain does over much of this window
>    (τ₂ ≈ 3.3 d, and the window starts at day 13). The −0.3031 mV/day figure is
>    the *late* rate, but the comparison spans earlier days too.
> 2. **The plateau slope is extrapolated.** 6.0 mV/%SOC was measured between two
>    rested OCV points at 75.9% and 80.8% SOC and is applied here at ≈98%, where
>    the curve is steeper — biasing the voltage path high, which is the direction
>    of the observed gap.
>
> Read the table as *the two paths are consistent*, nothing more. Self-discharge
> is addressed in §7.7, where it is stated as unmeasured.
>
> **Falsifying observation:** a rested OCV point taken near 98% SOC that puts the
> local plateau slope outside 5.4–6.6 mV/% would break the consistency claim.

### 5.3 Stasis criteria — the old thresholds no longer discriminate

| Criterion | Threshold (2026-04 protocol) | Measured | Status | Headroom |
| :--- | :--- | ---: | :--- | ---: |
| MA drift rate, 3-day | < 5 mV/day | −0.333 mV/day | **PASS** | 15× |
| Voltage range, 3-day window | < 60 mV | 0.59 mV | **PASS** | 102× |
| Noise vs pre-charge baseline | < +10% | −99.8% | **PASS** | — |
| Days since charge | > 14 | 41 | **PASS** | 2.9× |

**Status: STASIS.** All four pass — but three of them pass by more than an order
of magnitude, which means they are no longer measuring anything. A criterion that
cannot fail on a healthy system cannot flag an unhealthy one either.

**Proposed INA228-era criteria**, scaled to the new instrument's noise floor
(0.131 mV within-day sd) rather than to the Shelly's 10 mV quantisation:

| Criterion | Proposed threshold | Current value | Basis |
| :--- | :--- | ---: | :--- |
| Drift rate, 7-day OLS | \|slope\| < 0.6 mV/day | 0.303 | 2× the observed stasis rate |
| Within-day voltage sd | < 0.5 mV | 0.131 | ≈2.5 × the bus LSB |
| Daily voltage range | < 2 mV | 0.59 | 10 × the LSB |
| Days since charge | > 15 | 41 | 99% relaxation, from §5.1 |
| **Quiescent drain** | **< 12 mA** | **7.49** | new — no voltage-only analogue |
| **Ledger divergence \|SW−HW\|** | **< 0.5 Ah/month** | **5.81 Ah unbooked** | new — see §6 |

These are proposals, not adopted thresholds: each is derived from a single
41-day window at one season and one SOC, and should be revisited after a winter
window and a second charge cycle.

![Noise floor](../figures/fig_ina228_noise_floor.png)
*Figure 6 — Within-day voltage sd, log scale. Day 1: 60.25 mV. Day 41: 0.131 mV
— below the 195.3 µV bus LSB, which is expected: the sd of a dithered quantised
signal can sit below one code.*

### 5.4 The 95-day storage stasis, April – July 2026

The newly published bridge data covers the period between the last report and the
instrument change. Over **95 consecutive days** (2026-04-01 → 2026-07-04, before
the July 5 charge), the Shelly daily minimum:

| Metric | Value |
| :--- | ---: |
| Mean | 13.2366 V |
| sd | 17.42 mV |
| Range | 13.11 – 13.27 V |
| **OLS drift** | **+0.0074 mV/day, se 0.0655, r² 0.000, p = 0.910** |

Drift over a full quarter is indistinguishable from zero at n = 95 [M]. Combined
with the 42-day stasis in the April report, the bank held stasis continuously
from mid-February to early July 2026 — **≈140 days** — with no charging.

> **[M] Limits.** These are daily *minima* from a 10 mV-quantised instrument, so
> the resolution floor is ±0.07 mV/day on the slope — the measurement cannot
> distinguish true zero from the −0.3 mV/day the INA228 now resolves. The correct
> reading is "**below the Shelly's detection limit**," which is exactly what the
> INA228 data proves: the drift was always there and the old instrument could
> never have seen it.

---

## 6. The Coulomb Ledger Cannot See the Drain

### 6.1 What was measured

Over the 31.96 continuous days since the last reboot (2026-07-25 20:00 UTC → 2026-08-26
20:00 UTC — no reboot, uptime confirmed at 2,766,270 s), three independent
accountants tracked the same current:

| Accountant | Method | Net charge | Equivalent |
| :--- | :--- | ---: | ---: |
| INA228 CHARGE register | 40-bit accumulator in silicon, every 1.58 s conversion, read raw over I²C once a minute | **−5.8222 Ah** | −7.582 mA |
| Independent integration | left-rectangle over the published 2 s series, 10 s stale guard, **no deadband** | **−5.8019 Ah** | −7.555 mA |
| Firmware coulomb ledger | `ah_charged_this_cycle` − `ah_discharged_this_cycle`, **±0.05 A deadband** | **−0.0149 Ah** | −0.019 mA |

- Silicon vs independent integration: **0.0203 Ah apart (0.35%)** — pure
  integration-method error, exactly the term the design intended to bound.
- Firmware vs either: the firmware books **0.26%** of the charge that moved.
- **Unbooked at the end of the window: 5.807 Ah = 1.46 %SOC**, growing at
  ≈1.4 %SOC per month of storage.

![Coulomb ledger](../figures/fig_ina228_coulomb_ledger.png)
*Figure 7 — Two lines descend together; one stays flat at zero. The slope change
near day 10 is the 2026-08-04 step of §7.*

### 6.2 Why

`discharge_current` — the internal sensor that feeds Ah integration — returns 0.0
whenever `i > discharge_threshold_a`, and `discharge_threshold_a` is −0.05 A:

```yaml
discharge_threshold_a:    "-0.05"  # A; I < this → discharging
charge_threshold_a:       "0.05"   # A; I > this → charging
```

The measured drain is 7.5 mA. **The deadband is 6.7× larger than the current it
is excluding**, so the quiescent drain is not attenuated by the ledger — it is
invisible to it. The same deadband zeroes `self_discharge_ah_this_cycle`
(reads 0.0000 Ah for 41 days) and `self_discharge_equivalent_current` (0.0 A).

The 50 mA figure is not arbitrary: firmware V1.2 lowered it from 1 A specifically
to improve SOC fidelity, and 50 mA is a sound choice for rejecting shunt noise
during *operation*. It was chosen before anyone knew the storage drain was
7.5 mA, because until this instrument existed nobody could measure it.

### 6.3 The consequence

State of charge is coulomb-counted and anchored at full charge. With the drain
unbooked, **SOC reads 99.996% while the coulomb truth is ≈98.2%** [D: 100 − 7.188
Ah / 397 Ah]. The error is one-directional (SOC always optimistic) and accumulates
without limit during storage:

| Storage duration | True SOC | Displayed SOC | Error |
| ---: | ---: | ---: | ---: |
| 1 month | 98.6% | ~100.0% | 1.4% |
| 6 months | 91.7% | ~100.0% | 8.3% |
| 12 months | 83.4% | ~100.0% | 16.6% |
| 22 months | 69.7% | ~100.0% | 30.3% |

[D: linear extrapolation of the measured 1.38 %SOC/month.] For a bank whose
design brief is *"designed for no help coming"* and whose operating model is
*"the operator reads SOC and shuts the bank at ~20%"*, a silently optimistic SOC
during long storage is the failure mode that matters most: it is exactly the
number the operator would consult before an outage.

### 6.4 The detector that has never run

The firmware already contains the right check. `Cycle Integration Delta (SW−HW)`
computes the software net minus the hardware net since the last anchor —
precisely the divergence in §6.1. Its comment names the purpose exactly:

> *"Divergence = software integration error (deadband + cadence), the term under
> the CE calculation."*

It returns NaN until an anchor seeds `hw_charge_anchor_ah`, and the hardware
accumulators were added in V1.23 — **after** the only anchor this system has ever
recorded (2026-07-16). The sensor has therefore never published a value, has no
InfluxDB series, and appears on the dashboard as a blank. A check that has never
run is not a check; it is a blank space that looks like a clean result.

### 6.5 Recommended remedies

Ordered by how much they buy per unit of risk. None is applied here — this report
recommends; it does not change firmware.

1. **Publish the divergence unconditionally.** Seed `hw_charge_anchor_ah` at boot
   from the current register value when no anchor snapshot exists, so the sensor
   reports from the first minute instead of waiting for an anchor. This is the
   R8 fix — it converts "never looked" into "looked, found nothing," and it is
   the only item here that costs nothing and risks nothing.
2. **Integrate the quiescent term separately.** Keep the ±50 mA deadband on the
   operational ledger — it earns its place there — and add a low-current
   integrator with a ±2 mA deadband (above the measured 0.9 µV ≡ 2.4 mA
   offset floor from commissioning Tier 2) whose output feeds SOC. Two
   integrators with disjoint bands, not a widened single one.
3. **Or read the hardware accumulator as the SOC source of record** and keep the
   software ledger as the cross-check, inverting the current relationship. The
   register is continuous, deadband-free, and 40 bits wide (±58,000 Ah); the
   0.35% agreement above is the evidence it can carry that role. The cost is that
   the register resets on reboot, so this needs the persisted-anchor treatment
   the outage counters already got in V1.20.
4. **Add the ledger-divergence criterion to the stasis protocol** (§5.3), so the
   next occurrence is caught by the report rather than by a one-off analysis.

> **Not attempted here, and why:** any of 1–3 is a firmware change on a live
> backup system, and the project's validation gate for firmware is
> config → codegen → standalone lambda compile → full `esphome compile` to a
> linked binary with zero errors, in a sandbox, before flash. That gate belongs
> to whoever flashes the change.

---

## 7. The Quiescent Drain: What It Is, and the 2026-08-04 Step

### 7.1 The load inventory, from the operator

Attribution of a current is a fact about wiring, not something recoverable from
the current itself. Asked directly, the operator's answer (2026-08-26):

| On the bank | Status |
| :--- | :--- |
| Shelly Plus Uni | **retired** |
| DROK panel meter | **retired** |
| Giandel 1500 W inverter | connected, **off** |
| INA228 monitor | **powered from the busbars** |

That last line is the one that matters. In the low-side topology the shunt sits
in the negative cable between battery− and the negative busbar, so anything fed
from the busbars returns *through* the shunt. **The monitor's own consumption is
inside the measurement, not outside it** — and with everything else retired or
off, the monitor is the only load on the bus.

> **[M] The measured drain is the monitor.** 7.4 mA at 13.35 V = **99 mW**.
> For scale, a XIAO ESP32-C3 holding a Wi-Fi association in DTIM power-save
> draws ~25 mA at 3.3 V, which through the Pololu D24V7F3 at ~87% is **7.1 mA**
> at bus voltage [D]. The measurement and the parts list agree without fitting
> anything.
>
> **The bank's own external parasitic load is therefore effectively nil.** What
> the earlier reports called "parasitic draw" was the Shelly and the DROK meter,
> and both are gone. What remains is the instrument watching the bank.

**This also corrects a firmware figure from [I] to [M].** The header of
`battery-bank-monitor.yaml` reasons about survival sleep from "Monitor ~100 mA =
8% of inverter standby; buys ~1 day." Measured, it is **7.4 mA — the assumption
is 14× high** [M]. Survival sleep is even less necessary than that note argued,
and the 100 mA figure should be replaced at its site rather than left to be
re-quoted.

> **How this nearly went wrong, recorded per R13.** Before asking, the arithmetic
> pointed the other way: "commissioning says the monitor draws ~100 mA, the total
> is 7.4 mA, therefore the monitor must sit upstream of the shunt." Both premises
> were fine and the logic was valid; the ~100 mA was an **[I] wearing an [M]'s
> clothes**, and the conclusion was backwards. The question cost the operator one
> line and would otherwise have become a published claim about wiring that nobody
> had looked at.

### 7.2 What was measured, by regime

![Parasitic drain](../figures/fig_ina228_parasitic.png)
*Figure 8 — Daily time-weighted quiescent drain. The step on 2026-08-04 coincides
with a documented rewire of the bank's lugs; §7.3 is about what that means.*

| Segment | Window | Duration | Mean drain | At 13.35 V |
| :--- | :--- | ---: | ---: | ---: |
| Post-charge settling | Jul 17 – Jul 27 | 11.0 d | 6.94 mA | 93 mW |
| **Pre-rewire** | **Jul 29 – Aug 4 14:40 ET** | **6.8 d** | **5.90 mA** | **79 mW** |
| **Post-rewire** | **Aug 5 – Aug 18** | **14.0 d** | **8.78 mA** | **117 mW** |
| Late | Aug 19 – Aug 26 | 7.8 d | 7.36 mA | 98 mW |
| **Whole window** | **Jul 16 – Aug 26** | **40.9 d** | **7.38 mA** | **99 mW** |

> **[M] Precision, honestly stated.** The commissioning Tier-2 qualification
> measured this INA228's shunt-channel offset at 0.9 µV ≡ **2.4 mA** at 375 µΩ.
> Quoting a drain to three significant figures on an instrument with a ±2.4 mA
> offset is false precision. **The defensible statement is 7.4 mA ± 2.4 mA**, and
> the regime-to-regime spread of 5.9–8.8 mA sits entirely inside that band. The
> 41-day *mean* is statistically tight; its *accuracy* is bounded by the offset,
> and the offset is the larger term. Shunt calibration against a clamp at ~115 A
> (§8.2 item 5) is what would tighten it.

### 7.3 The 2026-08-04 step is an offset shift, not a load

The drain stepped from 5.90 mA to 8.78 mA inside one hour on 2026-08-04, between
14:00 and 15:00 ET. The operator's account of that window: **the bank was
rewired to eliminate stacked lugs. No load was added or removed.**

That decides it on physical grounds, and the arithmetic is corroborating rather
than load-bearing:

| Evidence | Reading |
| :--- | :--- |
| Nothing was added to the bus | A real +50% rise in load has nothing to come from — the monitor is the only consumer, and it did not change |
| No reboot | Uptime is 32 days continuous and spans 2026-08-04, so the monitor's own duty cycle did not restart |
| No firmware change | Same binary before and after |
| Joints in the shunt's current path were unbolted and re-landed | The one thing that demonstrably changed |
| **Step size in shunt terms** | **+2.88 mA × 375 µΩ = 1.08 µV** — the same order as the 0.9 µV offset measured at commissioning with the inputs shorted |

Unbolting and re-seating dissimilar-metal joints shifts thermal EMF by about
this much. **Conclusion: instrument offset shift.** The 1.08 µV figure is not
independent evidence — it is what any 2.88 mA step converts to at this shunt —
but it establishes that the observed step is *within reach* of the mechanism the
operator's account supplies, which a step ten times larger would not have been.

**Consequence for the headline:** the 41-day mean straddles two different zeros.
The pre-rewire and post-rewire segments are each internally consistent, and the
post-rewire regime is the one that describes the bank as it is now wired. Neither
is "the" answer to better than the ±2.4 mA offset band, which is why §7.2 quotes
the drain to two significant figures.

### 7.4 Two tests that did NOT settle it, recorded so nobody re-runs them

Per R13, the failed approaches are written down where they were tried.

**1. The data-feed "blip" is not diagnostic.** The operator suggested that moving
the INA228 off a lug should show as a short dropout. There are two on Aug 4 —
36.1 s at 14:43:29 ET and 39.7 s at 14:48:45 ET — sitting right at the step. But
there are **82 gaps longer than 20 s across the 41-day window**, roughly two a
day, from Wi-Fi dropouts, and the usual length is 25–27 s. The Aug 4 pair is
slightly longer than typical and nothing more. Suggestive, not evidence.

**2. The voltage record cannot settle it, and the obvious test is confounded.**
The clean discriminator looks compelling: a real +50% load must make the bank's
voltage fall ~50% faster, while a shunt-offset shift leaves the voltage
untouched. Run naively it returns the opposite of the load hypothesis — but that
result is worthless, because **2026-08-04 is day 19 post-charge, and at
τ₂ ≈ 3.3 d the relaxation tail still contributes more mV/day there than the
drain does.** Fitting the two exponentials and a broken linear term jointly does
not rescue it: the break sits inside the exponential's tail, the terms are
collinear, and the fit returns a **positive** pre-step slope — physically
impossible for a bank in storage, and a clear sign of a degenerate fit rather
than a finding.

> **No clean pre-step window exists**, so this test cannot be done
> retrospectively at all. It is stated here in full because it is exactly the
> analysis a reader would think to run, and it does not work. A *future* load
> change would be cleanly separable, now that relaxation is spent.

**Still worth doing:** short the INA228 inputs and re-measure the offset at
operating die temperature (§8.2 item 5). Its role has changed — it is no longer
the tie-breaker but a **confirmation and a new post-rewire zero**, and it starts
the offset-vs-age trend that a shunt-based instrument needs anyway.

### 7.5 Temperature is a real covariate, but not the explanation here

Quiescent drain does correlate with die temperature across the post-settling
record: **−1.311 mA/°F, r = −0.753, r² = 0.568, p = 3.1 × 10⁻¹²⁵, n = 678 hourly
means** [M]. Within the post-step segment alone the sensitivity is −0.875 mA/°F,
so the +0.68 °F across the Aug 4 boundary accounts for only −0.59 mA of the
−2.88 mA step.

That residual was the original puzzle. It is now explained by §7.3, and the
temperature correlation is better read as a property of the *instrument* than of
the bank: a shunt-and-ADC chain with a temperature-dependent offset will produce
exactly this, and the ±2.4 mA offset band covers the whole observed range.

> **Deliberately not claimed.** A joint regression of drain on both die and pack
> temperature returns R² = 0.86 with coefficients of −6.34 and +5.57 mA/°F —
> large, opposite, and physically meaningless. Die and pack temperature are
> collinear over this record and the fit is absorbing that, not measuring two
> effects. It is reported only so that nobody re-derives it and believes it.

### 7.6 Endurance, restated

Both columns use the **validated 397 Ah**, so the only thing that changes between
them is the measured drain:

| Quantity | Prior estimate (12.5 mA) | Measured (7.4 mA) | Change |
| :--- | ---: | ---: | ---: |
| Drain | 0.300 Ah/day | **0.177 Ah/day** | −41% |
| Time to 80% SOC from full | 8.7 months | **≈15 months** | +69% |
| Time to 50% SOC from full | 21.7 months | **≈37 months** | +69% |
| Time to the 20% operator floor | 34.8 months | **≈59 months** (4.9 yr) | +69% |

[D: 397 Ah × ΔSOC ÷ (drain × 24 h).]

> **[M] Limits — and the right way to read these.** At 7.4 ± 2.4 mA the endurance
> band is roughly **11–22 months** to 80% SOC, not a point value; the uncertainty
> is dominated by the shunt offset, not by the statistics. More importantly,
> **this is the endurance of the instrument, not of the bank.** The monitor is
> the entire load. Power it from something other than the bank, or implement the
> survival sleep the firmware header contemplates, and storage endurance is
> limited by true self-discharge instead — which, as §7.7 sets out, has not yet
> been measured.

> **Reconciling with the README's "~11+ months to 80% SOC."** That figure is
> 12.5 mA applied to the **500 Ah nameplate** (100 Ah ÷ 0.300 Ah/day = 333 d =
> 10.9 months), not to the 397 Ah the discharge test validated. Mixing capacity
> bases across reports is a bookkeeping hazard; everything here uses 397 Ah, and
> the README is corrected to match.

### 7.7 What this is NOT: self-discharge remains unmeasured

**The shunt measures charge that leaves through the terminals. Self-discharge
happens inside the cells and does not cross the shunt.** No quantity in this
report is a measurement of it, and the operator's assessment is the correct one:
true self-discharge has not been calculated yet.

Two claims in earlier drafts of this report were weaker than they read, and are
withdrawn here:

1. **"Two independent loss paths agree to 11%" does not bound self-discharge.**
   The coulomb path measures external drain; the voltage path measures total SOC
   decline, so their *difference* is the self-discharge candidate. But §7.4
   showed the voltage path over this window is dominated by the relaxation tail,
   and the 6.0 mV/%SOC plateau slope was measured at 76–81% SOC and applied at
   ≈98%. The difference is not resolvable against those two uncertainties.
2. **"Self-discharge ~0%" is inherited, not re-established.** It comes from the
   Shelly-era 92-day study, on an instrument that could not resolve 0.3 mV/day.
   Nothing in the INA228 record confirms or refutes it.

**The measurement the operator has scheduled is the right one**, and it is the
designated next step: reach stasis (done), discharge the bank below 80% SOC,
then charge it. A full→full cycle with a known depth of discharge lets the
firmware's V1.10 reconciliation compute the unaccounted charge

    U = recon_coul_eff × Ah_in − Ah_out

which is the self-discharge, separated from the external drain the shunt already
sees.

> ### ⚠ Prerequisite: the deadband must be fixed *before* that cycle runs
>
> §6 showed the firmware's coulomb ledger cannot see the 7.4 mA drain — it books
> 0.26% of it. Run the reconciliation with that deadband in place and `Ah_out`
> will be short by the monitor's entire contribution, so **U will absorb the
> monitor and report it as self-discharge.**
>
> The size of the error is not subtle [D]: at 0.177 Ah/day, a 60-day storage leg
> contributes **10.6 Ah = 2.7% of 397 Ah**, which would present as a
> self-discharge rate of ≈1.3 %/month against a true value plausibly near zero.
> The published LFP figure is ~2–3 %/month at rest, so the artefact lands
> squarely inside the range that would look like a *confirmation*.
>
> Fixing the ledger (§6.5 item 1 or 2) is therefore not housekeeping — it is a
> precondition for the self-discharge number being meaningful at all.

## 8. Open Items

### 8.1 Questions for the operator — answered 2026-08-26

These were facts about the physical installation, not derivable from the data at
any price. Both were put to the operator and both are now closed; the answers are
what §7.1 and §7.3 are built on.

| # | Question | Answer | What it unblocked |
| ---: | :--- | :--- | :--- |
| Q1 | What is on the busbars, load side of the shunt — and does the monitor's supply land on the busbars or the battery posts? | Shelly **retired**; DROK meter **retired**; inverter **connected but off**; monitor **powered from the busbars** | Attribution of the drain. The monitor's return runs through the shunt, so the 7.4 mA **is** the monitor (§7.1) |
| Q2 | Did anything change at the bank on 2026-08-04 ≈ 2:30 PM ET, or ≈ 2026-08-19? | The bank was **rewired to eliminate stacked lugs**; no load added or removed | The step is an **instrument offset shift**, not a load change (§7.3) |

> **Worth recording: Q1's answer was the opposite of the standing inference.**
> From "commissioning says the monitor draws ~100 mA" and "the total is 7.4 mA"
> it followed that the monitor must sit upstream of the shunt. Valid logic, bad
> premise — the ~100 mA was an untested estimate, and the real figure is 14×
> lower. One question to the operator replaced an inference that was about to
> become a published claim about wiring nobody had looked at.

### 8.2 Measurements still outstanding

| # | Item | Status |
| ---: | :--- | :--- |
| 1 | **Cycle-2 coulombic efficiency** | Still blocked. Only one anchor has ever fired; `last_coulombic_efficiency` has read 95.78% — the commissioning accounting floor — unchanged for 41 days. Needs a second full charge. |
| 2 | **CV absorption-time trend** | Frozen at the single baseline 16.82 min for the same reason. The trend is the early capacity-fade indicator, and it has one point. |
| 3 | **Apparent Ri, V1.21 sample** | Still n = 2, both commissioning samples (2.185 and 1.818 mΩ), both below the 2.63 mΩ ohmic floor and both to be struck. No qualifying rest→load step has occurred since. Needs a 45 s load hold within ±15%. |
| 4 | **Definitive inverter efficiency** | Unchanged at the provisional 87–94%. Needs the single-steady-load protocol of the commissioning report §8.1. |
| 5 | **Shunt calibration against a clamp at ~115 A** | Not done. Would take the DROK's ±1% tolerance to ~0.1% of reference. Now the binding constraint on the drain figure: the ±2.4 mA offset, not the statistics, is what makes it 7.4 ± 2.4 rather than 7.38. |
| 6 | **Short-input offset re-measurement at operating die temperature** | Not done. Post-rewire zero for the shunt channel, confirmation of §7.3, and the first point of an offset-vs-age trend. |
| 7 | **True self-discharge** | Not measured, and not measurable from this record — see §7.7. Scheduled: discharge below 80% SOC, then charge, then reconcile the full→full cycle. **Blocked on the §6 deadband fix**, without which the monitor's 0.177 Ah/day is booked as self-discharge. |

Items 1–3 all reduce to one action: **run a full charge.** A single LiTime cycle
would fire the anchor, produce the first valid CE sample, add the second
absorption-time point, and re-seed the SW−HW divergence detector of §6.4.

Item 7 needs that same cycle **preceded by a discharge below 80% SOC** — the
operator's scheduled sequence — and **preceded in turn by the §6 deadband fix**,
without which its answer is wrong by the monitor's entire contribution. The
correct order is therefore: fix the ledger → discharge below 80% → charge to
anchor → reconcile.

### 8.3 Repository and configuration observations

- **The archived firmware and the deployed copy have diverged.** The device is
  running code at V1.23 or later — it publishes `HW Net Charge (INA228)`, which
  first exists in V1.23. The repository's
  `INA228 Monitor/battery-bank-monitor.yaml` contains V1.20–V1.24 code but its
  header and changelog still read V1.19. The copy at
  `H:/esphome/ina228-bringup.yaml` contains **no V1.20+ code at all**. This is
  commissioning housekeeping item 6 ("reconcile the working tree so the archived
  YAML is the compiled YAML") still open, and now three ways instead of two.
  Recommend: bring the header and changelog up to the code, and reconcile or
  retire the H: copy.
- **Bank entities are now in InfluxDB with infinite retention**, closing
  commissioning housekeeping item 7. This report is the first to be built on
  that: the 41-day 2 s record it rests on outlived the HA recorder's 14-day purge
  by construction.

---

## 9. Updated Key Metrics

| Metric | Apr 5, 2026 | Aug 26, 2026 | Change |
| :--- | ---: | ---: | :--- |
| Published record | Oct 29 2025 – Apr 2 2026 (158 d) | Oct 29 2025 – Aug 26 2026 (301 d) | +143 days |
| Instrument | Shelly Plus Uni | INA228 + 375 µΩ shunt | replaced 2026-07-16 |
| Voltage resolution | 10 mV | 0.195 mV | 51× |
| Current measurement | none | 2 s, 0.83 mA LSB | new |
| Samples this window | 758,338 (HF, cumulative) | 1,790,710 (current, 43.8 d span) | — |
| Within-day voltage sd | 6.72 mV (MA-60 window) | **0.131 mV** | 51× lower |
| Stasis drift rate | −0.19 mV/day (5-day, at noise floor) | **−0.3031 mV/day** (7-day, 38 σ) | now resolvable |
| Quiescent drain | 12.5 mA [bench meter] | **7.4 ± 2.4 mA [M, 41 d]** | measured; it is the monitor |
| Bank's own external load | not separated | **effectively nil** | Shelly + DROK retired |
| Endurance to 80% SOC, on 397 Ah | 8.7 months | **≈15 months** (band 11–22) | +69% |
| True self-discharge | ~0% [inherited, Shelly era] | **not measured** | needs the §7.7 cycle |
| Rested plateau voltage | 13.251 V (Shelly) | 13.3005 V (INA228) | = Nov 2025 baseline |
| Full-charge cycles | — | 1 | first anchor 2026-07-16 |
| Coulombic efficiency | — | 95.78% (floor, not a measurement) | needs cycle 2 |

---

## 10. Conclusions

1. **The study's headline open question is closed, and the answer relocates the
   load.** The quiescent drain is 7.4 ± 2.4 mA [M, 41 days, 1.79 M samples,
   99.93% coverage], not the 12.5 mA estimated on the bench or the 13–20 mA
   inferred from drift. With the Shelly and DROK meter retired and the inverter
   off, **that current is the monitor itself** — 99 mW, matching what its parts
   list predicts — and the bank's own external parasitic load is effectively nil.
   Storage endurance to the 20% operator floor is ≈59 months in the present
   configuration, which is a statement about how long the *instrument* can watch
   the bank, not about the bank.

2. **Stasis is confirmed, and for the first time the drift inside it is
   resolvable.** −0.3031 mV/day over the last 7 days, se 0.0079, p = 2.2 × 10⁻⁷.
   Prior reports could only say "indistinguishable from zero," which was a
   statement about the Shelly, not about the bank.

3. **The two loss paths are consistent, but their difference does not measure
   self-discharge.** Voltage gives −1.54 %SOC/month via the OCV plateau slope and
   coulomb gives −1.38 %SOC/month. Both uncertainties — relaxation contamination
   of the voltage path, and extrapolating a 76–81% SOC plateau slope to ≈98% —
   are larger than the gap between them, so **true self-discharge remains
   unmeasured** (§7.7). The scheduled full→full reconciliation is the measurement,
   and §6's deadband is its prerequisite.

4. **The bank returns to its own baseline after ten months and a full cycle.**
   13.3005 V measured against a November 2025 baseline of 13.301 V restated on
   the same scale — a difference below the ±3 mV cross-calibration uncertainty.
   Architectural immunity, as this study has argued it, now has a
   cross-instrument, cross-cycle, ten-month datapoint.

5. **The instrument is better than the firmware's use of it.** The INA228 and an
   independent integration agree to 0.35% on 32 days of quiescent charge, while
   the firmware's own ledger books 0.26% of it. That is not an instrument
   limitation; it is a ±50 mA deadband chosen before the drain it excludes could
   be measured. **SOC is silently optimistic during storage at ≈1.4 %/month, and
   the detector designed to catch that has never published a value.**

6. **The 2026-08-04 step resolved to the instrument, on physical grounds.** The
   drain stepped 5.90 → 8.78 mA inside one hour. The operator's account: the bank
   was rewired that afternoon to eliminate stacked lugs, with no load added or
   removed. Nothing on the bus could consume 50% more — the monitor is the only
   load, it did not reboot, and the firmware did not change — while joints in the
   shunt's own current path were unbolted and re-landed. At 375 µΩ the step is
   1.08 µV, the same order as this chip's 0.9 µV commissioning offset (§7.3).

   Two analyses that looked decisive and were not are recorded in §7.4: the
   data-feed "blip" is indistinguishable from the 82 routine Wi-Fi dropouts in the
   window, and the voltage record cannot separate a load step from an offset step
   at day 19 post-charge, because the relaxation tail dominates there. **A
   question to the operator settled in one line what the data could not settle at
   all** — which is the general lesson of this section.

---

## 11. Recommendations

### 11.1 Completed this update

| Item | Status |
| :--- | :--- |
| Publish the INA228-era datasets with a reproducible export path | Done — `scripts/ina228_export.py`, four data tiers, pinned cutoff |
| Cross-calibrate the two instruments over their overlap | Done — §1.2, n = 148 gated pairs |
| Close the Apr 5 → Jul 14 gap in the published record | Done — 107 daily minima + the final Shelly HF file |
| Direct measurement of quiescent drain | Done — §7, the study's stated next step |
| **Attribute that drain to a load** | Done — §7.1, from the operator; it is the monitor |
| **Resolve the 2026-08-04 step** | Done — §7.3, instrument offset shift after a documented rewire |
| Charge and discharge characterisation at 2 s resolution | Done — §3, §4 |
| Stasis assessment on the new instrument | Done — §5 |
| Reproducible analysis from published files only | Done — `scripts/ina228_analysis.py` |

### 11.2 Next steps

The first four are one ordered sequence, not four independent items. Running them
out of order produces a self-discharge number that is wrong by the monitor's
entire contribution (§7.7).

| Priority | Action | Why now |
| :--- | :--- | :--- |
| **1** | **Fix the coulomb ledger** — seed `hw_charge_anchor_ah` at boot so the SW−HW divergence sensor publishes, then either add a low-current integrator (±2 mA band) or make the hardware register the SOC source of record | §6.5. **Prerequisite for step 3.** The seeding half costs nothing and risks nothing; it turns a permanently blank sensor into a reading |
| **2** | **Discharge the bank below 80% SOC** | The operator's scheduled sequence. Also gives the first cycle with a known DoD since commissioning |
| **3** | **Charge to a full anchor, then reconcile** | One action closes four items: CE cycle 2, absorption-time point 2, the re-seeded divergence detector, **and the first true self-discharge measurement** — provided step 1 ran first |
| **4** | Short-input offset re-measurement at operating die temperature | Post-rewire zero for the shunt channel; confirms §7.3 and starts the offset-vs-age trend |
| 5 | Shunt calibration against a clamp at ~115 A | Takes ±1% to ~0.1%. This is now the binding constraint on the drain figure — ±2.4 mA of offset, not statistics, is why §7.2 quotes two significant figures |
| 6 | Replace the "Monitor ~100 mA" assumption in the firmware header with the measured 7.4 mA | §7.1. It is 14× high and it is the basis of the survival-sleep argument |
| 7 | Reconcile the three firmware copies (§8.3) | F1-recurrence guard; the archived YAML should be the compiled YAML |
| 8 | Re-run this report after a winter window | Every limit in §5 and §7 is stated at 68–70 °F |

---

## Appendix A: Revision History

| Version | Date | Changes |
| :--- | :--- | :--- |
| **2026-08-26** | **Aug 26, 2026** | **INA228 era. Direct parasitic measurement; instrument cross-calibration; coulomb-ledger deadband finding; Apr–Jul gap closed; stasis criteria proposed for the new noise floor** |
| 2026-04-05 | Apr 5, 2026 | 30-day extension; stasis confirmed at day 42; HF gap and sampling-rate change documented |
| 2026-03-06 | Mar 6, 2026 | Extended post-charge analysis to day 12; stasis assessment; MA-60 comparison |
| 2026-03-01 | Mar 1, 2026 | Charge event analysis; parasitic loss quantification; self-discharge finding |
| 2026-01-31 | Feb 1, 2026 | Extended to 94+ days; abstract; temperature analysis |
| 2025-12-26 | Dec 27, 2025 | High-frequency data; Eco Mode analysis |
| 2025-11-22 | Nov 23, 2025 | Initial stasis monitoring report |
| 2025-10-29 | Oct 30, 2025 | Original discharge test report |

---

## Appendix B: Data Files Used

| File | Rows | Window | Used in |
| :--- | ---: | :--- | :--- |
| `data/ina228/ina228_daily_2026-07-13_2026-08-26.csv` | 44 | Jul 14 – Aug 26 | §2, §5, §7 |
| `data/ina228/ina228_hourly_2026-07-13_2026-08-26.csv` | 1,052 | Jul 14 – Aug 26 | §7 |
| `data/ina228/stasis_ma60_2026-07-16_2026-08-26.csv.gz` | 55,691 | Jul 16 – Aug 26 | §5.1, §5.2 |
| `data/ina228/coulomb_ledger_hourly.csv` | 968 | Jul 17 – Aug 26 | §6 |
| `data/ina228/shelly_ina228_crosscheck.csv` | 817 | Jul 14 – Jul 16 | §1.2, §1.3 |
| `data/ina228/events/charge_2026-07-16_litime_80A.csv` | 3,103 | Jul 16 18:10–19:55 | §3 |
| `data/ina228/events/discharge_2026-07-15_70W_overnight.csv.gz` | 28,084 | Jul 15 19:50 – Jul 16 11:40 | §4 |
| `data/ina228/events/discharge_2026-07-16_1kW_heater.csv` | 702 | Jul 16 14:18–14:42 | §4 |
| `data/ina228/events/discharge_2026-07-16_inverter_trip.csv` | 597 | Jul 16 17:38–17:58 | §4 |
| `data/shelly_daily_min_2026-04-01_2026-07-16.csv` | 107 | Apr 1 – Jul 16 | §2.2, §5.4 |
| `data/high_freq_voltage/voltage_data_2026-06-17_to_2026-07-16.csv.gz` | 8,343 | Jun 17 – Jul 16 | §1.2 |
| `data/Shelly Voltage.csv` | 1,089 | Jul 15 – Jul 16 | §1.2 |
| `data/combined_output.csv` | 3,636 | Oct 29 2025 – Mar 31 2026 | §1.3 |

**Source of record:** InfluxDB 1.x on the Home Assistant host, database
`"Home Assistant"`, retention `autogen` / infinite. Every figure and number above
is reproduced by `python scripts/ina228_analysis.py` from the files in this
table, with no host access required.

---

**Repository:** <https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks>
**DOI:** 10.5281/zenodo.14538065
**License:** CC BY 4.0 (data) / MIT (code)
