# Battery-bank SOC accuracy — turnover

Written 2026-09-24 ~11:50 EDT, end of session 49c33aa0. Firmware on the device:
**V1.27**. Nothing for V1.28 is built. Tracked as `docs/pending.md` P21.

Line numbers below are **V1.27's** (`esphome/battery-bank-monitor.yaml`, 2,705
lines); they move on the next edit. Evidence is referenced, not copied (R10):
see §10 for where each record lives.

---

## 1. The goal, in Bill's words

> "want to know what is the root cause of the noise. want the full accuracy of
> the ina228, not contaminated by the noise."

> "If it holds, the permanent fix still belongs in the monitor."

"It" is the router stopgap in §4. The fix he means is firmware (V1.28, §5).

## 2. Where it stands

- `sensor.battery_bank_monitor_state_of_charge` reads **99.96 %** [M, live API
  2026-09-24 15:20 UTC]. Estimated true SOC is **~96.7 % ±1.1 %** [D: 12.0 Ah
  unbooked by 09-18 (V1.27 header note (f), line ~163) + 6 d × ~7.6 mA = ~13.1 Ah;
  13.1 / 397 Ah = 3.3 % low. The ±1.1 % is the INA228 offset maximum, 1 µV
  [S: TI SLYS021A p1] / 375 µΩ = 2.67 mA, over 1,680 h since the 07-16 anchor].
- **Cause of the error:** SOC comes from a software ledger with a ±50 mA
  deadband. The bank's standing drain is 7.3–8.2 mA [M, §3], below the deadband,
  so the ledger misses most or all of it.
- **The noise** is contamination, and it switches between two states. The
  switch is in the router's operating mode. **How the noise gets into the
  INA228 reading is still unknown** (§4).
- **The fix proposed:** V1.28 computes SOC from the INA228 CHARGE register.
  That register has no deadband and averages the noise out. The design does not
  depend on how the noise couples in. **It is waiting on Bill's go (R12).**
- **The anchor** `hw_charge_anchor_ah` is **NAN**, because there has been no
  full charge since V1.27. `Cycle Integration Delta (SW-HW)` is therefore
  `unknown` [M, live API 15:20 UTC]. The next full charge seeds it. That is the
  pre-test top-up in the CHANGELOG 2026-09-18 prediction rows.

**Read this before anything else.** The router stopgap in §4 (coexistence OFF)
puts the monitor in the **quiet** state. In the quiet state the ledger books 0 %
of the drain [D, §3]. That is the "SOC stuck at 100 %" Bill first reported. The
stopgap cleans up the current trace and **freezes the SOC display.** Only V1.28
fixes both.

## 3. Measurements

Window: 09-20 20:00 to 09-24 10:00 EDT. Current samples are polled every 2 s
from HA history (pass `end_time`; see `docs/off-host-access.md`). The regimes
were split in 5-min blocks.

| | noisy regime | quiet regime |
|---|---|---|
| current samples | n=61,017 in 411 blocks [M] | n=89,254 in 608 blocks [M] |
| current mean / sd | −8.28 / 18.11 mA [M] | −7.22 / 5.44 mA [M] |
| drain from the CHARGE register, hourly | 8.18 mA, sd 0.39, n=37 h [M] | 7.30 mA, sd 0.31, n=37 h [M] |
| share of that drain the SW ledger books | 11–12 % [D] | 0 % [D] |

- The two drains differ by **0.88 mA**, Welch t=10.7 on n=37/37 h [M]. The
  monitor draws more in the noisy regime. That extra is either real current
  (its own radio working harder) or a small non-zero mean in the noise.
- **The CHARGE register already averages the noise away** [M]. Per sample the
  noisy sd is 18.11 mA. The register's hourly drain values scatter by only
  0.39 mA sd. This is the measured basis for V1.28.
- Why noise helps the ledger: excursions past −50 mA get booked, which is why
  the noisy regime books 11–12 % [D]. A noisy trace makes the SOC drift down
  slowly, in the right direction but far too little. **"The SOC reads correctly
  when it is noisy" is false.**

## 4. The noise: what is known

- **It is contamination, not current.** It is symmetric: skew 0.02, and 6.2 % of
  noisy samples exceed +20 mA in the charge direction with no charger connected
  [M]. A real load cannot produce that.
- **It has two stable states.** 24 switches, holds of 1–11 h and once 41.7 h
  [M]. Within each state the noise is white [M], so it is not an alias or beat
  against the 2 s poll.
- **The switch is in the router.** These flipped the regime:
  - the router power-downs on 09-22 and 09-24
  - "Enable 20/40 MHz Coexistence" set to OFF on the basement R6400 at
    **11:14:40 EDT 09-24**. Quiet followed at once: sd 5.33 mA, n=346,
    11:14:41–11:27 [M].

  That coexistence result is **n=1**. Applying the setting also restarts the
  radio, so the setting and the restart are confounded.

  One event did **not** flip it: the monitor's own reboot at 10:49:37 [M, §9].
- **Stopgap in force:** coexistence OFF. A router reset puts it back ON, because
  it is "enabled by default" [S: NETGEAR KB 30228, updated 2025-07-07, covers
  R6400/R6400v2]. If the noise comes back, check that box first.
- **Still unknown: how the noise gets into the reading.** Two candidates:
  - (a) the monitor's own ESP32-C3 radio; it draws 0.88 mA more when noisy [M, §3]
  - (b) the router's RF picked up on the INA228 sense leads

  §7 test 1 tells them apart.

## 5. V1.28 design (proposed, NOT built)

**What it does.** Compute SOC from `hw_charge_ah`, the CHARGE register (0x0A)
plus the V1.26 bridge offset, lines 1659–1684, relative to the anchor:

    soc = 100 + (hw_charge_ah - hw_charge_anchor_ah) / 397.0 * 100  (clamp 0..100)

Sign: positive HW net means charge in. CYCLE CONFIRM already uses
`hw_now - hw_anchor` that way (lines 2311–2312). Keep the `self_discharge_ah`
hook (inert at 0), because the shunt cannot see intrinsic self-discharge.

**Keep as is:**
- anchor seeding at a full charge (line 2323)
- anchor seeding on the manual "Mark as Fully Charged" button (2672–2673)
- the V1.25/V1.26 power-on-reset detection, bridge and invalidation in
  `on_boot` (410–488)

The anchor global is `restore_value` (~981). CHARGE keeps counting through an
ESP-only reboot or an OTA flash. On 09-22 ~20:07 and 09-24 10:49 the INA228
kept power [M: `INA228 Reset Check` after each boot].

**Decisions the builder must make and state (R1):**

1. **What happens while the anchor is NAN.** That is now, and again after any
   INA228 power loss that could not be bridged. **Do not publish NAN.**
   `runtime_hours` returns **0.0 h** on a NAN SOC (line 1590). The OLED shows
   `SOC: --` (line 640) and drops the "stop@20%" line (683–684). An overnight
   outage is exactly when those are read.

   Recommended: fall back to the SW ledger, and publish a text sensor naming
   the source (`INA228 CHARGE` / `SW ledger - reads high`) so the fallback is
   never silent (R8).

   There is no step at the switchover. The first full charge seeds the anchor
   in the same branch that resets the SW integrators (2392–2393), so both read
   100 %.

   Optional: after an INA228 power loss that could not be bridged, carry the
   last CHARGE-based SOC forward from a persisted global. Then the display does
   not jump by the unbooked drain.
2. **Do not seed the anchor from the ~96.7 % estimate.** It is [D] with ±1.1 %.
   Seeding from it bakes that in with no way to tell later. The next full
   charge seeds it for real.
3. **Staleness.** `hw_charge_ah` polls every 60 s and `soc_estimate` every 30 s.
   At 80 A the lag is up to 0.34 % [D: 80 A × 60 s / 3600 / 397 Ah]. That is lag
   only; it does not accumulate. To remove it, drive the SOC from
   `hw_charge_ah`'s `on_value`, as `cycle_integration_delta` already is
   (line 1689).
4. **Version strings.** Bump the header, the project version and the boot log
   (line 380). V1.20–V1.24 were missed (header note (h)).

**Accuracy budget**, per month from anchor to anchor:

| term | size | basis |
|---|---|---|
| SW ledger today, quiet state (for comparison) | 1.34 %/mo low | [D: 7.3 mA × 730 h / 397 Ah] |
| INA228 offset, not corrected | ≤ 0.49 %/mo | [D: 2.67 mA × 730 h / 397 Ah; 1 µV max, S: TI SLYS021A p1] |
| the 0.88 mA noisy-state excess, if none of it is real current | ≤ 0.16 %/mo, and only while noisy | [D: 0.88 mA × 730 h / 397 Ah] |
| bridge quantisation, per bridged INA228 reset | ≤ 0.0025 % | [D: 10 mAh save step / 397 Ah] |
| symmetric noise | averages out | [M: hourly sd 0.39 mA against a per-sample 18.11 mA, §3] |

Capacity is `validated_capacity_ah: "397.0"`, "measured Oct 2025" (line 290). A
capacity error scales every figure above. It is not re-measured here.

## 6. Unattended moment for V1.28

An overnight outage. The bank is discharging and nobody is watching. The SOC
and `Runtime Remaining` on the OLED and in HA must show the CHARGE-based value,
or say plainly that they are the fallback. Never NAN, never 0.0 h. The design
must also survive, with no human involved:
- an ESP reboot mid-outage (CHARGE and the anchor persist)
- an INA228 power loss (bridged, or the fallback is announced)

## 7. Tests proposed (each awaits Bill's go)

1. **WiFi-off test build**, kept separate from V1.28 so each change can be
   judged alone.
   - **How:** a template button runs `wifi.disable`, waits 10 min, then runs
     `wifi.enable`. During the window the device computes the current's sd
     itself and publishes it on reconnect. `wifi.disable` and `wifi.enable`
     exist in 2026.9.0, and `enable_on_boot` defaults to true, so a reboot
     mid-test brings WiFi back [S: ESPHome 2026.9.0 source, read this session].
   - **When:** during a noisy spell. That means coexistence back ON, which Bill
     sets on the router (R12).
   - **Reading the result:**
     - sd falls to about 5 mA with WiFi off: the path is the monitor's own
       radio.
     - sd stays about 18 mA: the path is the router's RF on the leads.
     - Whether the noise returns when coexistence goes back ON is the n=2 for
       the setting.
2. **Shorted-input offset test.** This is physical work, so Bill decides how
   (R14). It measures the actual INA228 offset against the ≤ 2.67 mA maximum.
   With that number V1.28 can subtract the offset instead of carrying
   ±0.49 %/mo.
3. **CHANGELOG 2026-09-18 prediction rows** (RECON rate; CYCLE CONFIRM
   +4 to +13 mA × cycle hours; V1.27 reset check). These score themselves at
   the next full charge. Score them where they stand. Do not re-register them
   for V1.28 unless its change touches what they measure. The ledger, RECON and
   CYCLE CONFIRM read the SW integrators, and V1.28 should leave those alone.

## 8. Disproven — do not reopen

Each item is recorded with its evidence in `open_questions.yaml` (entries dated
2026-09-20..24).
- **Router distance or geometry.** The regime did not track it (Fisher test,
  n.s.).
- **Some of the monitor's current bypasses the shunt.** Bill: impossible, by
  construction.
- **A constant source (router RF, the ESP radio) as the whole cause.** A
  constant cannot make two states or a 41.7 h quiet spell (Bill). A constant
  can still be the coupling path once the state is set, and that is §4 (a)/(b).
- **Alias or beat against the poll.** The noise is white within each regime.
- **A slow WiFi link.** It is 150 Mbps in the noisy state.
- **Channel width (20 vs 40 MHz via coexistence).** It is 150 Mbps in the quiet
  state too, with coexistence off (Bill, 11:27). R13, recorded in the last
  entry.
- **"The SOC reads right when noisy."** It books 11–12 % of the drain [D, §3].
- **The 10:49:33 event was a WiFi drop.** It was a monitor reboot (§9). R13,
  recorded in the last entry.

## 9. Found along the way: unexplained reboots

The ESP rebooted on its own at **09-22 ~20:07 EDT** and at **09-24 10:49:37
EDT**, 139,324 s apart [M: `sensor.battery_bank_monitor_uptime`, 2.16 s at
14:49:39 UTC].
- No new firmware (build 09-18 16:19).
- `reboot_timeout: 0s` on both `wifi` and `api` rules out those timeouts [D,
  from config].
- The INA228 kept power both times, and the second reboot did not flip the
  noise regime [M].

The cause is unknown. A reset-reason text sensor would name the next one.
ESPHome's `debug:` component offers one; confirm it against the 2026.9.0
source before relying on it (R6). It is cheap to add in V1.28.

## 10. Gates for V1.28, once Bill says go

1. R1 statement.
2. R2: copy `esphome/` into `C:\sandbox`, secrets included. Never print
   `secrets.yaml`, because those credentials were exposed and not rotated.
3. Replay recorded current and CHARGE through the new SOC lambda on the host,
   as V1.25's Ri change was replayed. Pull the data fresh with `end_time`,
   because the old scratchpad JSON is session-local.
4. `esp-firmware-validation`, run **from PowerShell**: config → codegen →
   `g++ -Wall` lambda check → real compile, with **0 errors in `main.cpp.obj`**.
   Git Bash false-passes with exit 0. Use an ESPHome that matches the Device
   Builder add-on: read `update.esphome_device_builder_update` first (it was
   2026.9.0).
5. Write a CHANGELOG prediction row before flashing. Bill installs via Device
   Builder > Install.
6. Observe after the flash:
   - `INA228 Reset Check` = kept power
   - the source sensor reads `SW ledger` (the anchor is still NAN)
   - the SOC does not step
   - then, at the first full charge, the source reads `INA228 CHARGE`

## 11. Where the evidence lives

- `open_questions.yaml`: the 2026-09-20..24 entries. They cover router placement,
  settings, link rate, the dated **ROUTER CHANGE** record, and the R13
  corrections.
- `CHANGELOG.md`: the prediction rows dated 2026-09-18 and the V1.25–V1.27
  entries.
- Firmware header notes V1.25–V1.27: lines ~86–175.
- Session transcript `49c33aa0-e197-4241-af71-f13371e294f0.jsonl` (Claude Code
  project `C--Users-wkcol`), and its R20 checkpoint in `~/.claude/checkpoints/`.
- **Uncommitted at writing:** `open_questions.yaml`, `docs/off-host-access.md`
  (the history `end_time` note), `docs/pending.md` (P21), and this file. Commit
  them separately, and only when Bill asks.
