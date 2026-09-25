# Diag test build V1.27-diag1: run sheet

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
| **Real `esphome compile` (`main.cpp.o`, 0 errors)** | **NOT RUN.** The sandbox's network policy denied `api.registry.platformio.org`. |

**Device Builder's Install is the final gate.** It compiles before it flashes.

- If the compile shows any error, stop there and send the log. Nothing is
  flashed on a failed compile.
- The residual risk is in ESP-IDF header details the stubs cannot check:
  `esp_wifi.h` names and fields.

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

## What each result would mean

**TB-4. Today's base is sd ≈ 5.0 mA, E ≈ 0.45 W.** The lit windows in
September gave sd ≈ 2 mA, E ≈ 0.23 W.

| step | "low" = sd ≤ 3 mA and E ≤ 0.25 W | "not low" |
|---|---|---|
| A_LIT_PAGE | reproduces the September lit windows without a person present | presence, not the display, did it |
| B_BLACK | **the panel-on state suppresses the noise.** A black frame is a burn-in-free stopgap. | the pixel load matters |
| C_WHITE | expected low under either explanation | — |
| D_LOOP_1MS (extra CPU load, panel off) | **the load level drives it** (buck-regulator mechanism) | the panel itself does it |

Step (d) uses a 1 ms loop interval, not a full CPU spin. A 0 ms interval
would starve the idle task and risk a watchdog reset. So (d) adds only part
of the OLED's ~8–9 mA. A null result is weaker evidence than a positive one.
The P-5 resistor test (deep dive §5.2) is the clean load test.

**TB-1.**

| window | reading | meaning |
|---|---|---|
| TB1_WIFI_OFF | sd → ~0.2–0.3 mA | the ESP (radio or its load) causes the noise |
| TB1_WIFI_OFF | sd ~5 mA | the source is external |
| TB1_WIFI_OFF | **Q above −4.8 mA, especially positive (predicted +7 to +15 mA)** | **proves an in-situ offset** (SOC gap, deep dive §4). With the radio off, the true draw is 4.8–9.1 mA of discharge |
| TB1_WIFI_OFF | Q steps by only a few mA from the ON windows | the ESP draws far less than its datasheet |
| ON windows | Q ≈ −8 mA | today's reading |

**TB-2.** sd against TX power:

| pattern | meaning |
|---|---|
| × 0.27 at 8.5 dBm | radiated from the ESP |
| ≈ × 0.5 | via the ESP's load |
| flat | external |

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
- **`Diag Stop + Restore`** stops the running test and restores ADC_CONFIG,
  TX power, the loop interval and the panel.
- **A reboot also restores everything.** ESPHome rewrites the INA228 ADC
  config at boot, and TX power and the loop interval return to their
  defaults.
- **During TB-3 and TB-5** the 2-s current that CORE sees is noisier or
  differently averaged, for 5–15 min at a time.
  - The SW ledger books at most ~2 mAh over the whole TB-3 ladder.
  - CHARGE is per conversion and unaffected.
- **If an outage starts mid-test,** press `Diag Stop + Restore`. The tests do
  not affect CORE, but the results would be meaningless under load.
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
