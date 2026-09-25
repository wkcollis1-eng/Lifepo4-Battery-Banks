# Diag test results - V1.27-diag2 (run of 2026-09-25)

Procedure and the reading of every label: `diag-test-runsheet.md`. How the run
is driven: `diag-test-turnover.md`. This file holds the raw `Diag Result`
lines, verbatim, and a short summary per test.

## Run conditions

- Firmware: diag2, config hash `0xbecf144a` [M: ESPHome Version sensor].
  READY at 14:11:02 UTC. INA228 Reset Check: kept power. Reset Reason:
  software via esp_restart (the OTA reboot).
- Diag Wi-Fi AP Info at boot: `ch 8, 2nd none, sta bw HT40, 11bgn, tx max 20.00 dBm` [M].
- Bank IDLE at the first press.
- Order (Bill, 2026-09-25, a change from the runsheet so the TB-4 runs spread
  out): TB-4, TB-1, TB-4, TB-2, TB-4, TB-3, TB-5, 1 min after each "done".
  Buttons pressed by Claude with `diag_watch.py press`.
- Bill: nobody near the monitor during TB-4, router left as is for the run,
  TB-1 Wi-Fi-off window accepted (open_questions.yaml, 2026-09-25).
- Times are EDT, as printed by the watcher.

## 1. TB-4 run 1 - pressed 10:11:42

```
RESULT 10:17:02 TB4_BASE_1 300s n=150 mean=-8.94 sd=5.86 sk=-0.33 ek=1.29 pos=4.0% min=-29.0 max=9.9 sd1m=5.15/7.13 Q=-9.13mA E=0.4844W Vsd=0.087mV
RESULT 10:22:22 TB4_A_LIT_PAGE 300s n=150 mean=-10.46 sd=2.58 sk=-0.54 ek=3.09 pos=0.0% min=-21.4 max=-1.5 sd1m=2.00/3.06 Q=-10.42mA E=0.2595W Vsd=0.094mV
RESULT 10:27:42 TB4_BASE_2 300s n=150 mean=-8.17 sd=5.30 sk=-0.16 ek=-0.08 pos=4.0% min=-23.7 max=3.8 sd1m=4.92/6.09 Q=-8.11mA E=0.4809W Vsd=0.079mV
RESULT 10:33:02 TB4_B_BLACK 300s n=150 mean=-9.67 sd=5.44 sk=-0.45 ek=2.20 pos=3.3% min=-29.4 max=8.0 sd1m=3.56/7.08 Q=-9.92mA E=0.4326W Vsd=0.097mV
RESULT 10:38:22 TB4_BASE_3 300s n=150 mean=-8.70 sd=5.45 sk=0.12 ek=0.59 pos=6.0% min=-23.7 max=9.5 sd1m=4.64/6.33 Q=-8.72mA E=0.4728W Vsd=0.096mV
RESULT 10:43:42 TB4_C_WHITE 300s n=150 mean=-10.15 sd=1.72 sk=-0.13 ek=-0.05 pos=0.0% min=-14.9 max=-5.7 sd1m=1.65/1.85 Q=-10.14mA E=0.2229W Vsd=0.094mV
RESULT 10:49:02 TB4_BASE_4 300s n=150 mean=-7.62 sd=5.03 sk=0.26 ek=-0.38 pos=8.0% min=-18.3 max=6.1 sd1m=4.22/5.92 Q=-8.13mA E=0.4708W Vsd=0.085mV
RESULT 10:54:22 TB4_D_LOOP_1MS 300s n=150 mean=-6.42 sd=6.51 sk=0.31 ek=-0.15 pos=16.0% min=-21.7 max=11.1 sd1m=5.92/7.71 Q=-6.37mA E=0.6266W Vsd=0.094mV
RESULT 10:59:42 TB4_BASE_5 300s n=150 mean=-8.09 sd=5.58 sk=0.26 ek=0.30 pos=7.3% min=-24.8 max=9.9 sd1m=5.09/6.40 Q=-8.24mA E=0.4718W Vsd=0.093mV
STATUS 10:59:42 TB-4 done - panel off, loop interval restored
```

**Run 1 summary** (n=150 2-s samples per window; runsheet "low" = sd <= 3 mA AND E <= 0.25 W):

| step | sd mA | E W | runsheet reading | Q mA | Q vs mean of bracketing bases [D] |
|---|---|---|---|---|---|
| bases 1-5 | 5.03-5.86 | 0.471-0.484 | reference | -8.11 to -9.13 | spread 1.02 mA [D] |
| A_LIT_PAGE | 2.58 | 0.2595 | not low: sd passes, E 0.0095 W over | -10.42 | -1.80 |
| B_BLACK | 5.44 | 0.4326 | not low: "the pixel load matters" | -9.92 | -1.51 |
| C_WHITE | 1.72 | 0.2229 | low: expected under either explanation | -10.14 | -1.72 |
| D_LOOP_1MS | 6.51 | 0.6266 | not low: "weak evidence that the panel itself does it" | -6.37 | **+1.82** |

- Every figure is [M] from the RESULT lines above except the last column, which is
  [D]: step Q minus the mean of the base windows either side of it.
- D's Q went the wrong way. The runsheet reads D's null on the assumption that the
  loop ADDS load; here the 2-s mean (-6.42) and CHARGE (-6.37) both show 1.82 mA
  LESS drain than the bracketing bases. Not interpreted here; see runs 2 and 3.
- Black and white frames differ in noise (sd 5.44 vs 1.72) but their Q deltas
  differ by 0.21 mA [D], inside the 1.02 mA base-to-base Q spread, so this run
  cannot resolve a pixel-current difference.
- n = 1 run of 3. The deep dive's TB-4(b) criterion is 3 out of 3; nothing here
  is a conclusion yet.

## 2. TB-1 - pressed 11:00:48

```
RESULT 11:10:48 TB1_WIFI_ON_BEFORE 600s n=300 mean=-8.74 sd=5.08 sk=0.31 ek=0.35 pos=5.0% min=-21.7 max=7.2 sd1m=3.77/5.99 Q=-8.62mA E=0.4767W Vsd=0.093mV
UNAVAILABLE 11:12:51 Diag Status is unavailable
AVAILABLE 11:20:59 TB-1 2/3: Wi-Fi OFF 10 min - HA shows unavailable; results arrive after reconnect
RESULT 11:20:59 TB1_WIFI_OFF 600s n=300 mean=-6.54 sd=8.16 sk=0.12 ek=0.10 pos=20.7% min=-28.2 max=18.3 sd1m=6.71/10.09 Q=-6.38mA E=0.9886W Vsd=0.106mV
RESULT 11:31:14 TB1_WIFI_ON_AFTER 600s n=300 mean=-8.88 sd=4.71 sk=0.13 ek=0.05 pos=3.7% min=-21.0 max=5.3 sd1m=3.06/5.95 Q=-8.79mA E=0.4751W Vsd=0.089mV
STATUS 11:31:14 TB-1 done
```

**TB-1 summary** (n=300 2-s samples per window; figures are [M] from the RESULT lines above unless tagged [D]):

| window | sd mA | E W | Q mA | runsheet reading |
|---|---|---|---|---|
| WIFI_ON_BEFORE | 5.08 | 0.4767 | -8.62 | ON window, Q ~ -8 mA: today's reading |
| WIFI_OFF | 8.16 | 0.9886 | -6.38 | Q below -4.8: neither offset row applies |
| WIFI_ON_AFTER | 4.71 | 0.4751 | -8.79 | ON window, Q ~ -8 mA: today's reading |

- The two ON windows agree: Q 0.17 mA apart, E 0.0016 W apart [D]. The control held.
  ON_AFTER is labelled WIFI_ON_AFTER, not ON_AFTER_NOAPI, so it counts.
- Q step, Wi-Fi off: +2.33 mA [D: -6.38 - mean(-8.62, -8.79)]. A step of a few mA is the
  runsheet's "the ESP draws far less than its datasheet".
- Noise ROSE with the radio off: sd 8.16 against 5.08 / 4.71, and E 0.9886 W against
  0.4767 / 0.4751. The runsheet has no row for a rise. Its rows are sd ~0.2-0.3 mA (the
  ESP causes the noise) and sd ~5 mA (not a conclusion alone, read with TB-4). Reported,
  not read.
- HA marked the monitor unavailable at 11:12:51, about 2 min after Wi-Fi went off [D],
  and available at 11:20:59. All three results arrived. None was lost across the outage.
- [I], not a conclusion: in the two highest-noise windows so far (WIFI_OFF sd 8.16,
  TB-4 D_LOOP_1MS sd 6.51), and only in those, Q moved toward zero. If the added noise
  is not zero-mean, part of the +2.33 mA is noise rather than ESP draw, and the "far less
  than its datasheet" reading is weaker. Falsified by a high-noise window in TB-2 or in
  TB-4 runs 2-3 whose Q does not move.

## 3. TB-4 run 2 - pressed 11:32:15

```
RESULT 11:37:35 TB4_BASE_1 300s n=150 mean=-8.62 sd=4.94 sk=0.39 ek=0.39 pos=4.0% min=-20.6 max=8.8 sd1m=4.71/5.07 Q=-8.71mA E=0.4421W Vsd=0.045mV
RESULT 11:42:55 TB4_A_LIT_PAGE 300s n=150 mean=-10.17 sd=2.74 sk=1.79 ek=8.42 pos=0.7% min=-16.0 max=6.1 sd1m=1.70/4.11 Q=-10.23mA E=0.2588W Vsd=0.073mV
RESULT 11:48:15 TB4_BASE_2 300s n=150 mean=-8.34 sd=5.27 sk=-0.22 ek=0.27 pos=6.0% min=-26.3 max=3.8 sd1m=4.38/6.22 Q=-8.63mA E=0.4661W Vsd=0.047mV
RESULT 11:53:35 TB4_B_BLACK 300s n=150 mean=-9.73 sd=5.40 sk=0.15 ek=1.64 pos=4.0% min=-24.8 max=9.2 sd1m=3.94/6.32 Q=-10.20mA E=0.4283W Vsd=0.061mV
RESULT 11:58:55 TB4_BASE_3 300s n=150 mean=-8.75 sd=5.47 sk=-0.09 ek=0.45 pos=5.3% min=-24.4 max=6.9 sd1m=4.07/6.17 Q=-8.85mA E=0.4672W Vsd=0.058mV
RESULT 12:04:15 TB4_C_WHITE 300s n=150 mean=-10.04 sd=1.86 sk=-0.47 ek=0.18 pos=0.0% min=-16.0 max=-6.1 sd1m=1.41/2.22 Q=-10.14mA E=0.2222W Vsd=0.057mV
RESULT 12:09:35 TB4_BASE_4 300s n=150 mean=-8.65 sd=4.29 sk=-0.32 ek=0.11 pos=0.7% min=-20.6 max=3.1 sd1m=3.97/4.66 Q=-8.29mA E=0.4456W Vsd=0.084mV
RESULT 12:14:55 TB4_D_LOOP_1MS 300s n=150 mean=-6.59 sd=6.13 sk=0.16 ek=0.51 pos=12.0% min=-26.3 max=9.2 sd1m=5.35/6.67 Q=-6.93mA E=0.6086W Vsd=0.076mV
RESULT 12:20:15 TB4_BASE_5 300s n=150 mean=-8.12 sd=4.88 sk=0.25 ek=0.30 pos=4.0% min=-22.1 max=6.9 sd1m=4.26/6.04 Q=-8.43mA E=0.4324W Vsd=0.089mV
STATUS 12:20:15 TB-4 done - panel off, loop interval restored
```

**Run 2 summary** (n=150 2-s samples per window; runsheet "low" = sd <= 3 mA AND E <= 0.25 W):

| step | sd mA | E W | runsheet reading | Q mA | Q vs mean of bracketing bases [D] | run 1 [D] |
|---|---|---|---|---|---|---|
| bases 1-5 | 4.29-5.47 | 0.432-0.467 | reference | -8.29 to -8.85 | spread 0.56 mA [D] | spread 1.02 |
| A_LIT_PAGE | 2.74 | 0.2588 | not low: sd passes, E 0.0088 W over | -10.23 | -1.56 | -1.80 |
| B_BLACK | 5.40 | 0.4283 | not low: "the pixel load matters" | -10.20 | -1.46 | -1.51 |
| C_WHITE | 1.86 | 0.2222 | low: expected under either explanation | -10.14 | -1.57 | -1.72 |
| D_LOOP_1MS | 6.13 | 0.6086 | not low: "weak evidence that the panel itself does it" | -6.93 | **+1.43** | +1.82 |

- Every step read the same way under the runsheet in run 2 as in run 1. That is 2 of the 3
  runs the TB-4(b) criterion asks for, so nothing here is a conclusion yet.
- D's Q went the wrong way again: 1.43 mA LESS drain than its bases [D], against the
  runsheet's assumption that the loop adds load.
- The black and white Q deltas differ by 0.11 mA [D], inside this run's 0.56 mA base Q
  spread. As in run 1, this run cannot resolve a pixel-current difference.
- Base E (0.432-0.467 W) and Vsd (0.045-0.089 mV) sit below run 1's (0.471-0.484 W,
  0.079-0.096 mV) [M]. The runsheet gives no reading for a base-to-base shift. Reported, not read.
- A_LIT_PAGE had sk 1.79 / ek 8.42 (run 1: sk -0.54 / ek 3.09) [M]. The runsheet reads ek
  only in TB-3. Reported, not read.
- [I] (see TB-1): D_LOOP_1MS is the third high-noise window whose Q moved toward zero.
  It is consistent with the flag, not a test of it.

## 4. TB-2 - pressed 12:21:16

```
RESULT 12:37:16 TB2_TX_20.00dBm 900s n=450 mean=-8.18 sd=5.15 sk=0.20 ek=0.10 pos=6.2% min=-23.3 max=6.9 sd1m=4.10/6.00 Q=-8.26mA E=0.4490W Vsd=0.089mV
RESULT 12:53:16 TB2_TX_17.00dBm 900s n=450 mean=-9.05 sd=4.13 sk=0.81 ek=1.98 pos=2.9% min=-21.0 max=11.4 sd1m=3.04/5.83 Q=-9.22mA E=0.3468W Vsd=0.097mV
RESULT 13:09:16 TB2_TX_14.00dBm 900s n=450 mean=-10.27 sd=2.10 sk=0.30 ek=1.23 pos=0.0% min=-16.8 max=0.0 sd1m=1.64/2.75 Q=-10.27mA E=0.2386W Vsd=0.096mV
RESULT 13:25:16 TB2_TX_11.00dBm 900s n=450 mean=-10.42 sd=1.84 sk=0.18 ek=0.55 pos=0.0% min=-16.0 max=-3.1 sd1m=1.41/2.34 Q=-10.47mA E=0.2309W Vsd=0.098mV
RESULT 13:41:16 TB2_TX_8.50dBm 900s n=450 mean=-10.82 sd=1.81 sk=0.01 ek=-0.30 pos=0.0% min=-16.4 max=-5.7 sd1m=1.58/2.20 Q=-10.84mA E=0.2313W Vsd=0.095mV
STATUS 13:41:16 TB-2 done - TX power restored
```

**TB-2 summary** (n=450 2-s samples per 15-min window; figures [M] from the RESULT lines above unless tagged):

| TX max (read back) | sd mA | E W | Q mA |
|---|---|---|---|
| 20.00 dBm | 5.15 | 0.4490 | -8.26 |
| 17.00 dBm | 4.13 | 0.3468 | -9.22 |
| 14.00 dBm | 2.10 | 0.2386 | -10.27 |
| 11.00 dBm | 1.84 | 0.2309 | -10.47 |
| 8.50 dBm | 1.81 | 0.2313 | -10.84 |

- The first step asked for 20.5 dBm, and the driver read back 20.00. No step reported SET FAILED.
- The runsheet's side test ("the C3 may cap TX power by data rate" [I]) is falsified by its
  own criterion: sd fell at each of the first steps, 20 -> 17 -> 14 dBm.
- **The runsheet's reading at 8.5 dBm matches none of its rows.** The sd ratio is 0.351 [D:
  1.81 / 5.15]. Its 95 % CI is 0.320-0.386 [D: log-ratio of two sample sds, SE 0.047, n=450
  each, assuming independent normal samples].
  - x0.25 (radiated) is outside the CI, z=+7.2. The same holds for x0.266 [D: 10^(-11.5/20)],
    re-anchored to the 20.00 dBm actually set: z=+5.9.
  - "About x0.5" (via the ESP's load) is outside, z=-7.5.
  - "Flat" (external) is outside, z=-22.2.
  - The independence assumption is unchecked. With an effective n of 45 (n/10), the CI is
    0.262-0.471 and both rows remain outside it (z=+2.3, -2.4).
- The fall is not a single scaling. sd dropped 3.05 mA between 20 and 14 dBm, then 0.29 mA
  between 14 and 8.5 dBm [D]. It levels off near 1.8 mA, close to TB-4's white-frame windows
  (1.72, 1.86). The runsheet's three rows each assume one scaling. Reported, not read.
- Q went from -8.26 to -10.84 mA across the ladder, 2.58 mA MORE drain at LOWER TX power [D].
  [I], not a conclusion: less TX power should not add load, so this Q shift is unlikely to be
  current drawn by the ESP. It supports the TB-1 flag that Q moves with the noise. Falsified
  by a TX-power-only change that moves Q with sd held level.

## 5. TB-4 run 3 - pressed 13:42:17

```
RESULT 13:47:38 TB4_BASE_1 300s n=150 mean=-8.86 sd=5.34 sk=0.72 ek=2.60 pos=4.0% min=-21.0 max=14.9 sd1m=3.74/6.23 Q=-9.17mA E=0.4589W Vsd=0.097mV
RESULT 13:52:58 TB4_A_LIT_PAGE 300s n=150 mean=-10.76 sd=2.66 sk=0.62 ek=3.24 pos=0.7% min=-20.6 max=0.4 sd1m=1.77/3.66 Q=-10.82mA E=0.2541W Vsd=0.057mV
RESULT 13:58:18 TB4_BASE_2 300s n=150 mean=-8.48 sd=5.06 sk=0.06 ek=0.47 pos=5.3% min=-24.8 max=5.3 sd1m=4.97/5.25 Q=-8.70mA E=0.4536W Vsd=0.093mV
RESULT 14:03:38 TB4_B_BLACK 300s n=150 mean=-10.07 sd=5.78 sk=-0.08 ek=2.70 pos=5.3% min=-34.3 max=11.4 sd1m=5.24/6.28 Q=-9.94mA E=0.4251W Vsd=0.091mV
RESULT 14:08:58 TB4_BASE_3 300s n=150 mean=-8.71 sd=5.10 sk=-0.13 ek=1.19 pos=6.7% min=-28.6 max=5.3 sd1m=3.89/6.06 Q=-9.30mA E=0.4615W Vsd=0.096mV
RESULT 14:14:18 TB4_C_WHITE 300s n=150 mean=-10.57 sd=2.01 sk=0.16 ek=-0.34 pos=0.0% min=-15.3 max=-5.3 sd1m=1.73/2.24 Q=-10.52mA E=0.2258W Vsd=0.098mV
RESULT 14:19:38 TB4_BASE_4 300s n=150 mean=-9.14 sd=5.66 sk=0.21 ek=0.84 pos=5.3% min=-24.0 max=8.4 sd1m=5.07/6.26 Q=-8.83mA E=0.4672W Vsd=0.067mV
RESULT 14:24:58 TB4_D_LOOP_1MS 300s n=150 mean=-7.15 sd=6.80 sk=0.35 ek=4.68 pos=11.3% min=-38.5 max=23.3 sd1m=4.92/8.22 Q=-6.88mA E=0.6036W Vsd=0.090mV
RESULT 14:30:18 TB4_BASE_5 300s n=150 mean=-8.41 sd=6.32 sk=-0.28 ek=1.36 pos=7.3% min=-30.9 max=9.9 sd1m=5.42/7.76 Q=-8.65mA E=0.4736W Vsd=0.084mV
STATUS 14:30:18 TB-4 done - panel off, loop interval restored
```

**Run 3 summary** (n=150 per window). Bases: sd 5.06-6.32, E 0.454-0.474 W, Q -8.65 to -9.30
(spread 0.65 mA [D]). Every step read the same way under the runsheet as in runs 1 and 2.

**TB-4, all three runs** (Q column: step Q minus the mean of its bracketing bases [D], run 1 / 2 / 3):

| step | runsheet reading, runs 1 / 2 / 3 | sd mA | E W | Q vs bases mA [D] |
|---|---|---|---|---|
| A_LIT_PAGE | not low x3; each time on E alone (over by 0.0095 / 0.0088 / 0.0041 W) | 2.58 / 2.74 / 2.66 | 0.2595 / 0.2588 / 0.2541 | -1.80 / -1.56 / -1.89 |
| B_BLACK | not low x3: "the pixel load matters" | 5.44 / 5.40 / 5.78 | 0.4326 / 0.4283 / 0.4251 | -1.51 / -1.46 / -0.94 |
| C_WHITE | low x3: expected under either explanation | 1.72 / 1.86 / 2.01 | 0.2229 / 0.2222 / 0.2258 | -1.72 / -1.57 / -1.45 |
| D_LOOP_1MS | not low x3: "weak evidence that the panel itself does it" | 6.51 / 6.13 / 6.80 | 0.6266 / 0.6086 / 0.6036 | +1.82 / +1.43 / +1.86 |

- 3 of 3 runs agree at every step, which meets the TB-4(b) criterion of 3 out of 3. The
  runsheet's readings are the ones in the second column; this file adds none of its own.
- A_LIT_PAGE never met "low", and each time E alone was over, by under 0.01 W.
- D_LOOP_1MS showed LESS drain than its bases in all three runs, +1.43 to +1.86 mA [D].
  The runsheet assumes the loop adds load. Not interpreted here.
- The black frame kept base-level noise (sd 5.40-5.78) yet sat 0.94-1.51 mA below its bases
  in Q [D]. So the panel shifts Q even with the noise unchanged. This undercuts a 13:09 note
  in chat that the panel Q deltas might be only noise (R13: that note was wrong to omit B_BLACK).

## 6. TB-3 - pressed 14:31:19, STOPPED on BANK

```
STATUS 14:31:19 TB-3 1/5: AVG 1 (ADC_CONFIG 0xFFF8)   [read back by `press`]
BANK 14:31:28 Bank State IDLE -> DISCHARGING           [watcher poll; HA history: 18:31:23 UTC]
STATUS 14:31:33 Stopped - all test settings restored   [`stop` pressed 14:31:32]
BANK 14:31:58 Bank State DISCHARGING -> IDLE           [watcher poll; HA history: 18:31:33 UTC]
```

- Bank current during AVG 1, 2-s HA samples 14:31:21-14:31:31 [M, n=6]: -103.0, +6.5,
  +120.5, -52.3, +10.7, +19.8 mA. Before and after it sat at about -10 mA. The swing runs both
  ways, so it is the AVG 1 noise, not a discharge. Two samples crossed the firmware's -0.05 A
  discharge threshold [S: battery-bank-monitor-diag.yaml, discharge_threshold_a].
- Side effects [M: HA history]: the lifetime, this-cycle and outage-event Ah/Wh counters
  integrated during the 10 s of DISCHARGING, sub-mAh changes. No HA automation, script or
  package reads bank state, discharge flags or outage counters [M: grep of H: automations.yaml,
  scripts.yaml, configuration.yaml, packages/].
- No TB-3 window completed. Nothing here is TB-3 evidence.
- Blocked on Bill (open_questions.yaml, 2026-09-25): re-press TB-3 with the BANK rule relaxed
  for TB-3, or skip to TB-5.

## 7. TB-3 (second press) - pressed 15:08:53

Bill, 2026-09-25: "continue with tb-3 and tb-5". During TB-3 only, a BANK change does not stop
the test. A guard presses Stop + Restore if |bank current| > 1 A. The guard was tested before the press:
it tripped at 8 mA against a 1 mA limit (dry run) and stayed silent at 1 A.

```
STATUS 15:08:53 TB-3 1/5: AVG 1 (ADC_CONFIG 0xFFF8)   [read back by `press`]
BANK 15:10:31 Bank State IDLE -> CHARGING               [watcher; first of many - state flips
     IDLE/CHARGING/DISCHARGING every 5-25 s under AVG 1 (HA history 19:09:43-19:10:38 UTC).
     |I| 2-s samples 19:09:30-19:10:40 UTC [M, n=34]: min -0.189 A, max +0.096 A, mean -0.011 A.
     Watcher re-armed 15:11 with BANK lines filtered for the rest of TB-3; guard enforces the rule]
RESULT 15:14:04 TB3_AVG_1 300s n=150 mean=-19.86 sd=64.30 sk=-1.66 ek=4.77 pos=37.3% min=-331.5 max=119.8 sd1m=49.59/74.50 Q=-8.70mA E=0.4785W Vsd=0.505mV
RESULT 15:19:14 TB3_AVG_4 300s n=150 mean=-2.47 sd=44.47 sk=0.22 ek=1.58 pos=41.3% min=-133.1 max=153.0 sd1m=37.59/51.40 Q=-8.93mA E=0.4797W Vsd=0.259mV
RESULT 15:24:24 TB3_AVG_16 300s n=150 mean=-6.18 sd=27.00 sk=-0.24 ek=3.20 pos=30.0% min=-122.5 max=92.7 sd1m=20.20/34.75 Q=-8.34mA E=0.4792W Vsd=0.141mV
RESULT 15:29:34 TB3_AVG_64 300s n=150 mean=-9.94 sd=5.91 sk=-0.49 ek=1.69 pos=4.7% min=-31.3 max=5.3 sd1m=4.64/7.33 Q=-8.66mA E=0.4709W Vsd=0.088mV
RESULT 15:34:44 TB3_AVG_128 300s n=150 mean=-8.67 sd=6.30 sk=0.22 ek=0.25 pos=9.3% min=-24.0 max=8.4 sd1m=5.05/7.21 Q=-8.72mA E=0.4822W Vsd=0.083mV
STATUS 15:34:44 TB-3 done - ADC_CONFIG restored
```

**TB-3 summary** (n=150 2-s samples per window; figures [M] from the RESULT lines above unless tagged).
No window carried CFGFAIL_, so every AVG write was confirmed by readback.

| AVG | sd mA | sd x sqrt(AVG) [D] | +/-1 SE [D] | ek | E W | Q mA | bank-state changes [M: HA history] |
|---|---|---|---|---|---|---|---|
| 1 | 64.30 | 64.30 | 6.84 | 4.77 | 0.4785 | -8.70 | 27 |
| 4 | 44.47 | 88.94 | 6.88 | 1.58 | 0.4797 | -8.93 | 29 |
| 16 | 27.00 | 108.00 | 10.07 | 3.20 | 0.4792 | -8.34 | 10 |
| 64 | 5.91 | 47.28 | 3.71 | 1.69 | 0.4709 | -8.66 | 0 |
| 128 | 6.30 | 71.28 | 4.38 | 0.25 | 0.4822 | -8.72 | 0 |

SE of sd is kurtosis-corrected: sd/2 x sqrt(2/(n-1) + ek/n). Bank-state changes are counted between
consecutive RESULT times, so each count includes that step's 10-s settle.

- **AVG 1 ("sd is the per-conversion sigma; compare it with ~42 mA from ENERGY"):** sd 64.30 is
  22.3 mA above ~42, z=+3.26 [D]. The ~42 is treated as exact, because the runsheet gives no
  uncertainty for it. The runsheet says to compare, but not what a gap means, so this file adds nothing.
- **"ek >> 0: the error is impulsive":** at AVG 1, ek 4.77, z=+12.1 [D: normal-theory SE 0.394, n=150].
  The runsheet sets no number for ">>". The row's reading fits AVG 1.
- **"sd x sqrt(AVG) constant across steps: white, independent per conversion":** not constant.
  chi2 = 55.2 on 4 df against a common value (weighted mean 64.76) [D], p < 0.001.
  - So the row's reading does not apply. The runsheet has no row for the non-constant case, so the
    pattern is reported, not read: it rose over AVG 1 -> 4 -> 16, then fell at 64.
  - From AVG 64 to 128, sd went 5.91 -> 6.30. White noise would give 4.18 [D: 5.91 / sqrt 2], z=+5.48.
- **AVG 128 is the firmware's normal setting** [S: battery-bank-monitor-diag.yaml:1800,
  `adc_averaging: 128`]. That window (sd 6.30, E 0.4822 W) sits inside today's TB-4 base
  range (sd 4.29-6.32, E 0.432-0.484 W) [M].
- **Q stayed at -8.34 to -8.93 mA at every step** [M], inside the base range. This matches the
  runsheet's "CHARGE is per conversion and unaffected".
  - TB-3 therefore does not test the [I] that Q tracks noise (see TB-1). AVG does not reach
    CHARGE [S: runsheet Safety], so a flat Q is what both readings predict.
- **Bank state changed 66 times during TB-3** [M: HA history], all of it in the AVG 1, 4 and 16
  windows. None happened at 64 or 128, or after "done".
  - Guard peak |I| was 253.3 mA [M: about one poll every 3 s, 15:09-15:34]. The guard never tripped
    and ended on its own at "TB-3 done".
  - The runsheet puts the SW ledger's booking at most ~2 mAh over the ladder [S: runsheet Safety].
    Not checked here.

## 8. TB-5 - pressed 15:35:59

```
STATUS 15:35:59 TB-5 1/3: base ADC config, 15 min   [read back by `press`]
RESULT 15:51:00 TB5_BASE 900s n=450 mean=-8.87 sd=5.32 sk=0.09 ek=-0.01 pos=3.8% min=-22.9 max=7.6 sd1m=4.11/6.36 Q=-8.96mA E=0.4610W Vsd=0.090mV
RESULT 16:06:11 TB5_FDC5 900s n=450 mean=-8.96 sd=3.91 sk=0.17 ek=1.19 pos=1.8% min=-22.1 max=7.2 sd1m=3.03/4.84 Q=-8.96mA E=0.4615W Vsd=0.098mV
     [FDC5/BASE sd 0.735, CI95 0.662-0.817 [D: log-ratio, kurtosis-corrected SE, n=450 each]; vs 0.71 z=+0.64,
      vs 1.0 z=-5.74. Lag-1 autocorrelation from HA's 2-s history [M, n=439/441]: BASE -0.012, FDC5 -0.096,
      so the independence assumption holds at lag 1 (AR1 n_eff CI 0.666-0.811). Vsd +8.9 % vs base [D],
      inside +/-20 %. Both runsheet conditions met -> its reading: "the 6.2 ADC timing can go into V1.28".]
RESULT 16:21:21 TB5_RESTORED 900s n=450 mean=-8.88 sd=5.92 sk=0.27 ek=0.77 pos=8.0% min=-30.1 max=10.7 sd1m=4.67/7.12 Q=-8.83mA E=0.4963W Vsd=0.081mV
STATUS 16:21:21 TB-5 done
```

**TB-5 summary** (n=450 2-s samples per 15-min window; figures [M] from the RESULT lines above unless tagged):

| window | sd mA | E W | Vsd mV | Q mA |
|---|---|---|---|---|
| TB5_BASE | 5.32 | 0.4610 | 0.090 | -8.96 |
| TB5_FDC5 | 3.91 | 0.4615 | 0.098 | -8.96 |
| TB5_RESTORED | 5.92 | 0.4963 | 0.081 | -8.83 |

- **Runsheet expectation met on both counts.**
  - FDC5/BASE sd is 0.735, CI95 0.662-0.817 [D]: against 0.71, z=+0.64; against 1.0, z=-5.74.
  - Lag-1 autocorrelation was -0.012 and -0.096 [M: HA 2-s history, n=439/441], so the samples
    can be treated as independent here. That is the assumption TB-2's CI had to leave unchecked.
  - Vsd rose 8.9 % against base [D], inside +/-20 %.
  - The runsheet's reading: "the 6.2 ADC timing can go into V1.28".
- **The restore was confirmed.** The last window is labelled TB5_RESTORED, not CFGFAIL_TB5_RESTORED,
  so no `restart` was needed.
  - Its sd of 5.92 is back inside today's TB-4 base range of 4.29-6.32 [M].
  - Its E of 0.4963 W sits 0.012 W above the top of that range (0.484) [D]. Reported, not read.
- **Bank state stayed IDLE throughout TB-5** [M: HA history 19:35:59-20:21:21 UTC]. The watcher
  reported no REBOOT, STALL or ERROR.

## End-of-run exports (runsheet "Export afterwards")

`diag2-export-2026-09-25/`: one CSV per entity (entity_id, state, last_changed_utc) for
13:30-20:25 UTC, which covers the flash through TB-5 done. All 15 entities in runsheet items 1-5 are
there, with the entity ids resolved from HA's live states by friendly name.

- **HA records only changes.** A 2-s sample that repeats the previous value is not a row.
  - Battery Current has 11,713 rows. The period holds about 12,360 two-second slots [D: 24,720 s / 2],
    and TB-1's 8-min outage accounts for some of the gap.
- **Diag Result holds 43 result rows, and 0 of them carry CFGFAIL_.** The set of labels matches
  this file's 43 RESULT lines one for one.
  - Its other two rows are `unknown` at the flash (14:10:41 UTC) and `unavailable` in TB-1 (15:12:51 UTC).
  - The first TB-3 press (section 6) produced no result, as recorded there.
- Battery Current is stored gzipped (`.csv.gz`, byte-identical after decompression) to fit the
  repo's 500 KB pre-commit limit on new files.

## After the run

- **Bill reinstalled V1.27 from Device Builder.** The monitor reported ESPHome 2026.9.0, config hash
  0x6b05d980, built 2026-09-25 16:29:02, uptime 63 s [M: HA, 16:30]. The diag2 build was 0xbecf144a.
- **The installed file matches the repo.** H:/esphome/battery-bank-monitor.yaml is byte-identical to
  this repo's battery-bank-monitor.yaml once line endings are normalised (H: LF, checkout CRLF) [M].
