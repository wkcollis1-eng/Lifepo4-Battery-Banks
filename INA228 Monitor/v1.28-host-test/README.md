# V1.28 host test

This test replays the V1.28 CORE lambdas on a PC. It is gate 3 of the
turnover's §10. The lambdas are the ones ESPHome generates, taken verbatim
from `main.cpp`. Only `stubs.h` and the wiring in `scenario.inc` belong to the
harness.

`stubs.h` includes a simulated INA228 register file. It models:

- SHUNT_CAL, ADC_CONFIG and TEMP_LIMIT;
- the CHARGE and ENERGY accumulators;
- a power-on reset;
- the ESPHome driver's setup writes.

## Run

You need a C++17 compiler plus ESPHome 2026.9.0. `g++` from WSL, MSYS2 or Git
Bash works, and so does `python -m ziglang c++` (`pip install ziglang`) on
Windows. On Windows, set `PYTHONUTF8=1` first: `harness.py` writes
`harness.cpp` in the default encoding, and `main.cpp` holds non-ASCII
characters.

1. Generate `main.cpp`.
   - Work in a temporary copy of `battery-bank-monitor.yaml`, with
     `secrets.yaml` beside it.
   - Delete the `api: encryption:` block from the copy. The noise library it
     pulls in needs the PlatformIO registry, and codegen does not need it.
   - Then run:

     ```
     esphome compile --only-generate _gentest.yaml
     ```

2. Build and run the harness from this folder:

   ```
   python make_replay.py
   python extract.py <build>/src/main.cpp .
   python harness.py <build>/src/main.cpp
   g++ -std=c++17 -Wall -Wextra -Wformat=2 -Wno-unused-variable -Wno-unused-parameter -O1 harness.cpp -o harness
   ./harness
   ```

**Expected:** `60 passed, 0 failed`, with 0 compiler errors and 0 warnings.
This was the result on 2026-09-25 after the review fixes, against ESPHome
2026.9.0 codegen (zig c++). It was 42 before them.

## Scenarios

| | what | checks |
|---|---|---|
| S1 | first V1.28 boot on the 09-25 13:30Z state | HW Net Charge and HW Energy continue across the 200 → 400 A LSB change; PWR_LIMIT 0x0960; config readback; provisional anchor from the ledger; no SOC step |
| S1b | the 09-25 HW Net Charge record: 404 rows, 6.9 h | SOC follows CHARGE; bracket Ah/Wh; mean net current −8.89 mA against the record's −8.8 |
| S2 | INA228 power-on reset while running | B2a detects it, publishes nothing, reboots; the boot bridges it; SOC is continuous |
| S2b | a chip that resets every minute for 3 h (review) | 3 reboots, then one per ≥ 30 min of uptime (8 in all, not 180); a `component.update` inside the 2 s delay does not count twice; the count clears after 1 h held |
| S3 | reset with nothing saved to bridge from | anchor invalidated; SOC carried from the last CHARGE SOC within 0.05 % |
| S4 | full charge that tapers to 6.5 A | O2 passes; session Ah; closure; clean anchor at 100 % |
| S4b | charger stopped mid-CV at 30 A | O2 refuses the anchor; SOC stays below 100 % |
| S5 | clean full → 20 d idle → full | CHARGE RECON U = 0 when the drain was seen; suggested offset 0 |
| S6 | CHARGE unreadable | ledger movement from the last CHARGE SOC after 180 s; back on recovery |
| S7 | ENERGY-rate noise gauge | 0.231 W reads quiet, 0.46 W reads noisy |
| S8 | manual anchor, Wi-Fi readback, every template | source "manual"; NONE and 11 dBm, and MIN_MODEM named when the driver reports it; all 18 templates run |
| S9 | LSB change with the chip unreadable at boot | anchors invalidated; SOC carries on |
| S4c | charger stopped mid-CV at 30 A, the one straddling reading 8 A (review) | O2 refuses: the straddling reading is never committed; 15 A control |
| S4d | straddle, charger off, charger back on at 30 A (review) | the straddling reading is dropped, not carried into the tail |
| S10 | reboot while HA time is not valid (review) | Hours Since Anchor runs on from the saved value plus uptime; no step beyond the 0.1 h save step when HA time returns; an anchor set without HA time keeps its hours through a reboot |
