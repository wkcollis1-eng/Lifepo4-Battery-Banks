# Diag test build V1.27-diag2: run sheet

**Firmware:** `battery-bank-monitor-diag.yaml`. It is V1.27 plus test-only
additions, all tagged "DIAG".

**Why:** the noise and zero-offset tests in `docs/soc-noise-deep-dive.md` §5.

**What it changes:**

- CORE is unchanged: acquisition, watchdog, alarms, bank_state, SOC and
  runtime.
- Nothing new is persisted (NVS unchanged: 30 → 30 `restore_value: yes`).
- The diff against V1.27 changes only three version strings. Everything else
  is added.

## Validation status (read before installing)

| layer | result |
|---|---|
| Blast radius vs V1.27 | PASS: only the title, project version and boot-log version changed; no CR; NVS count unchanged |
| `esphome config` (ESPHome **2026.9.0**, your Device Builder version) | PASS: `Configuration is valid!` |
| Code generation | PASS: `Successfully generated source code`, run on a temp copy with API `encryption:` removed, because the sandbox could not reach the PlatformIO registry for its library |
| All 42 DIAG lambdas, from the generated C++, compiled with g++ against stubs of the 2026.9.0 / ESP-IDF 5.5 signatures | PASS: 0 errors (`-Wall -Wextra -Wformat=2`) |
| **Real `esphome compile` (`main.cpp.o`, 0 errors)** | **PASS on diag2, 2026-09-25**, ESPHome 2026.9.0 run from PowerShell: `Successfully compiled program.`, `main.cpp.obj` built with 0 errors. One warning, in the existing V1.27 watchdog log line (`%u` given a `long unsigned int`), not in DIAG code. RAM 36.6 %, flash 56.7 % [M: compile log]. The rows above were run on diag1. This compile repeats the config and codegen steps on diag2 with nothing removed. |
| Host test of the diag2 fixes | PASS: 24 checks, 0 failed. The ADC_CONFIG steps of TB-3 and TB-5 and the TB-1 last-window label are taken from the generated C++. They run against a simulated INA228 that can NACK a read, NACK a write, or ACK a write without latching it. The same test on diag1 fails 6 of 11 checks, so it can catch what diag2 fixes. |

**Device Builder's Install is the final gate.** It compiles before it flashes.

- If the compile shows any error, stop there and send the log. Nothing is
  flashed on a failed compile.
- The real compile has closed the ESP-IDF header risk (`esp_wifi.h` names and
  fields). What is still untested is the run on the device itself.

## Install

1. **Add the file in Device Builder** as a new config, using the same
   `secrets.yaml`. It has the same device name and address (10.0.0.247), so it
   updates the same device over the air.
2. **Install → Wirelessly.** Wait for the compile.
3. **After boot, check:**
   - `INA228 Reset Check` says kept power.
   - SOC and Battery Current look as before.
   - These new entities exist:
     - `Diag Status`
     - `Diag Result`
     - six `Diag Window …` sensors
     - `Diag 5-min Current Mean/SD`
     - `Diag Wi-Fi AP Info`
     - `Reset Reason`
     - six `Diag …` buttons (under Configuration)

## Run order

Run one test at a time; the buttons refuse while another test runs. Run with
the bank **idle**.

**Leave the router alone for the whole run.**

- Coexistence has been OFF since 09-24 (deep dive §3.5).
- A router reset turns 20/40 MHz coexistence back ON (deep dive §3.6). The
  noise regime then changes partway through a test, and its steps are no
  longer comparable. If that happens, note the time and re-run that test.
- Every test here runs in the quiet (coexistence OFF) regime. The v128 review
  (§6 T1, §12) asked for T1 in a noisy spell instead.
  - That does not matter for Q: CHARGE is unaffected by the noise.
  - It does matter for every sd reading.
  - A noisy-spell repeat means turning coexistence back on, and that is a
    separate decision.

| # | button | length | conditions |
|---|---|---|---|
| 1 | **Diag TB-4 OLED-Load Round** | 47 min | Nobody at the monitor. **Do not press the OLED button** (its 5-min sleep timer would cut the lit steps). |
| 2 | **Diag TB-1 Wi-Fi Off Test** | 30 min | HA shows the monitor unavailable for ~10 min in the middle. That is expected. |
| 3 | TB-4 twice more, spread over the day | 2 × 47 min | as #1 |
| 4 | **Diag TB-2 TX Power Ladder** | 85 min | — |
| 5 | **Diag TB-3 Averaging Ladder** | 27 min | — |
| 6 | **Diag TB-5 ADC Timing Preview** | 46 min | — |

Total ≈ 6.5 h. `Diag Status` shows the current step. Each finished window
publishes one line to `Diag Result`.

## Reading `Diag Result`

Example. The numbers are illustrative, not a measurement:

```
TB4_B_BLACK 300s n=150 mean=-8.05 sd=1.98 sk=0.03 ek=0.40 pos=0.0% min=-14.1 max=-2.3 sd1m=1.61/2.44 Q=-8.12mA E=0.2210W Vsd=0.090mV
```

| field | meaning |
|---|---|
| label | test and step |
| 300s | window length |
| n | 2-s samples in the window |
| mean, sd, sk, ek | mean, sd, skew and excess kurtosis of the 2-s current, in mA |
| pos | share of readings > 0 (physically impossible at idle) |
| min, max | extremes, in mA |
| sd1m | lowest / highest 1-minute sd |
| Q | mean current from the INA228 CHARGE register, noise-immune; it counts even with Wi-Fi off |
| E | ENERGY rate, the per-conversion noise gauge |
| Vsd | bus-voltage sd, in mV |

**Labels that flag a problem (new in diag2).** Leave these windows out of the
analysis.

| label or status | meaning |
|---|---|
| `CFGFAIL_` in front of a TB-3 or TB-5 label | the ADC_CONFIG write for that window was not confirmed by reading it back, so the window may have run at the wrong setting. A readback that itself fails also sets it, so a flagged window may in fact have been fine. |
| `TB1_ON_AFTER_NOAPI` in place of `TB1_WIFI_ON_AFTER` | the API had not reconnected by the end of the 5-min wait, so the "radio on again" window may have run partly with the radio off |
| `Diag Status` "TB-3 SKIPPED" or "TB-5 SKIPPED" | reading ADC_CONFIG failed at the start. Nothing was changed and no windows ran. Press the button again. |
| `CFGFAIL_TB5_RESTORED` in `Diag Result`, or `Diag Status` "ADC_CONFIG restore NOT APPLIED" | TB-5's inline restore to production failed. The test retries it when it finishes, but it does not read that retry back, and "TB-5 done" appears either way. **After TB-5 ends, press `Restart`.** ESPHome rewrites ADC_CONFIG at boot, and the INA228's charge count is kept (`reset_on_boot: false`). |

## What each result would mean

**TB-4. Today's base is sd ≈ 5.0 mA, E ≈ 0.45 W.** The lit windows in
September gave sd ≈ 2 mA, E ≈ 0.23 W.

| step | "low" = sd ≤ 3 mA and E ≤ 0.25 W | "not low" |
|---|---|---|
| A_LIT_PAGE | reproduces the September lit windows without a person present | presence, not the display, did it |
| B_BLACK | **the panel-on state suppresses the noise.** A black frame is a burn-in-free stopgap. | the pixel load matters |
| C_WHITE | expected low under either explanation | — |
| D_LOOP_1MS (extra CPU load, panel off) | **the load level drives it** (buck-regulator mechanism) | weak evidence that the panel itself does it: (d) may add too little load (below) |

Step (d) uses a 1 ms loop interval, not a full CPU spin. A 0 ms interval
would starve the idle task and risk a watchdog reset. So (d) adds only part
of the OLED's ~8–9 mA. A null result is weaker evidence than a positive one.
The P-5 resistor test (deep dive §5.2) is the clean load test.

To see how much load (d) actually added, compare D_LOOP_1MS's Q with the Q
of the TB4_BASE windows on either side of it.

**TB-1.**

| window | reading | meaning |
|---|---|---|
| TB1_WIFI_OFF | sd → ~0.2–0.3 mA | the ESP (radio or its load) causes the noise |
| TB1_WIFI_OFF | sd ~5 mA | **not a conclusion on its own.** Turning the radio off also changes the buck's load. The deep dive (§4) can't predict which way that moves the noise under mechanism A. Read it together with TB-4. |
| TB1_WIFI_OFF | **Q > 0 (predicted +7 to +15 mA)** | **proves an in-situ offset** (SOC gap, deep dive §4), with no assumptions. With the bank idle, the monitor runs from the busbars and nothing charges them, so the true current is a discharge. |
| TB1_WIFI_OFF | **−4.8 < Q ≤ 0 mA** | **offset likely, not proven.** The −4.8 mA bound comes from the ESP's radio-off current (C3 datasheet Table 5-8) being converted through the buck's efficiency. Both steps are [I] for this board. |
| TB1_WIFI_OFF | Q steps by only a few mA from the ON windows | the ESP draws far less than its datasheet |
| ON windows | Q ≈ −8 mA | today's reading |

A gross gain error is already ruled out. Commissioning measured the charger's
AC→DC efficiency at 95.7 % ± 2.5 % [M: 1586 Wh DC ÷ 1657 Wh AC, Kill-A-Watt,
Commissioning Report]. A Q that disagrees with the draw therefore points to
an offset, not a scale error.

**TB-2.** sd against TX power:

| pattern | meaning |
|---|---|
| × 0.25 at 8.5 dBm (−12 dB from 20.5 dBm) [D: 10^(−12/20) = 0.251] | radiated from the ESP |
| ≈ × 0.5 | via the ESP's load |
| flat | external |

- **The TX max in `Diag Status` is read back from the Wi-Fi driver.** It is
  the setting, not what the antenna radiates.
- **The C3 may cap TX power by data rate** [I: not checked against the
  datasheet]. If so, the top steps would radiate the same, and a radiated
  source would drop by less than × 0.25. It could then be misread as "via the
  ESP's load".
  - This [I] is falsified if sd falls at each of the first steps
    (20.5 → 17 → 14 dBm).

**TB-3.**

- **AVG 1:** sd is the per-conversion σ. Compare it with ~42 mA from ENERGY.
- **Kurtosis (ek) ≫ 0:** the error is impulsive.
- **sd × √AVG constant across steps:** white, independent per conversion.

**TB-5.**

- **Expected:** TB5_FDC5 sd ≈ 0.71 × TB5_BASE, with Vsd within ~±20 % of
  base.
- **If so:** the §6.2 ADC timing can go into V1.28.

## Safety

- **CORE runs normally throughout:** SOC, alarms, OLED, LED.
- **Wi-Fi off (TB-1)** re-enables itself after 10 min. A failsafe re-enables
  it at 15 min regardless, and any reboot brings it back.
  - **For those ~10 min, HA cannot reach the monitor.** `Diag Stop + Restore`
    does nothing, and battery alarms do not reach HA.
  - The only ways back are the 10-min timer, the 15-min failsafe or a power
    cycle.
  - Run TB-1 only when an outage is unlikely.
- **`Diag Stop + Restore`** stops the running test and restores ADC_CONFIG,
  TX power, the loop interval and the panel.
- **A reboot also restores everything.** ESPHome rewrites the INA228 ADC
  config at boot, and TX power and the loop interval return to their
  defaults.
- **During TB-3 and TB-5** the 2-s current that CORE sees is noisier or
  differently averaged, for 5–15 min at a time.
  - The SW ledger books at most ~2 mAh over the whole TB-3 ladder.
  - CHARGE is per conversion and unaffected.
- **If an outage starts mid-test,** press `Diag Stop + Restore`, except in
  TB-1's radio-off window, where it cannot arrive (above). The tests do not
  affect CORE, but the results would be meaningless under load.
- **The OLED button's page cycle** now includes a "DIAG test page". That is
  harmless.

## Export afterwards

Export these for the whole test period:

1. `Diag Result` (text): the main output
2. `Diag Window Mean`, `SD`, `Positive`, `1-min SD Min`, `CHARGE Mean` and
   `ENERGY Rate`
3. `Diag Status`, `Diag Wi-Fi AP Info` and `Reset Reason`
4. `Diag 5-min Current Mean` and `SD`
5. `Battery Current` (2 s), `HW Energy` and `HW Net Charge`

## Afterwards

Re-install V1.27 (`battery-bank-monitor.yaml`). The Diag entities go
unavailable; delete them in HA if you like.
