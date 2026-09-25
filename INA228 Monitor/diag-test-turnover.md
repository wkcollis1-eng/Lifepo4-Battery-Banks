# Diag test turnover - V1.27-diag2 (written 2026-09-25)

For the Claude Code session that runs `diag-test-runsheet.md` and reports each
result as it arrives. The runsheet is the procedure and the reading of every
label; this file only says how to drive it. Do not copy its tables here (R10).

## State at handover

- **diag2 is NOT flashed** [M: ESPHome Version sensor, 2026-09-25 09:25 and
  09:34, config hash `0x6b05d980` = production V1.27; no Diag entities in HA].
  Bill installs `H:/esphome/battery-bank-monitor-diag.yaml` from Device Builder.
  Nothing is pressed until `diag_watch.py check` prints `READY`.
- Firmware commit `6d69f66`, runsheet commit `900042c`.
- `diag_watch.py` verification, 2026-09-25:
  - Self-test: 11/11 PASS.
  - Fault injection: 7 of 7 injected faults caught; the clean copy stays green.
  - Live: history fetch, the cursor boundary, and a kill + re-arm, all against
    the Uptime sensor. The re-arm lost no row and repeated none.
  - **`press` has never run live.** The auto-mode classifier denied even a
    press that would have refused [Modify Shared Resources]. The first press
    needs Bill's go-ahead in the session; how he grants it is his call.

## Fallback to production V1.27

Installing diag2 overwrites the add-on's production build, because both yamls
use the same `device_name`. A verified V1.27 build is kept at
`C:\Users\wkcol\esphome\fallback\battery-bank-monitor-V1.27-0x6b05d980\`.
- Its config hash matches the running monitor [M: build log vs the ESPHome
  Version sensor, 2026-09-25].
- The folder's README gives the restore paths, in order. None of them is Claude's
  to run (see Authority).

## Authority (R12)

Bill's 2026-09-25 request covers these three actions, and only these:

- Pressing the Diag test buttons in runsheet order.
- **Diag Stop + Restore.**
- **Restart**, only under the runsheet's `CFGFAIL_TB5_RESTORED` rule.

Anything else, ask first. That includes:

- flashing,
- sending notifications,
- the router,
- HA restarts,
- reinstalling V1.27,
- deleting the H: diag copy.

## Ask Bill before the first press (R14: stop until answered)

Log any unanswered question in `H:/open_questions.yaml`. The questions:

1. Is diag2 installed, and is Device Builder finished with it?
2. TB-4: will nobody be at the monitor, and nobody press the OLED button?
3. Will the router be left alone for the whole run? That is 5.5 h of test time
   plus gaps [D: 30+85+27+3x47+46 = 329 min, from the button labels].
4. TB-1 takes the monitor off Wi-Fi for 10 min. In that window Stop + Restore
   and battery alarms cannot reach HA. Is that acceptable now?
5. How far apart should the three TB-4 runs be?

## Run it

Set `HA_URL=http://10.0.0.210:8123`. `HA_TOKEN` is already in the environment;
never write it into a file. Run all of the following in `INA228 Monitor/`.

1. `python diag_watch.py check` before every press. It needs `READY`.
2. **Start the watcher once, before the first press, with the Monitor tool.**
   - Command: `python -u diag_watch.py watch`
   - Set `timeout_ms` to 1800000, which is the cap.
   - When it expires, re-arm the same command. The cursor in
     `~/.cache/diag_watch/state.json` resumes exactly where it stopped.
   - Delete that file before the first watch of a NEW run, or the watcher
     replays everything since the old cursor.
3. `python diag_watch.py press TB-n` for each test.
   - It refuses while a test runs.
   - It confirms `TB-n 1/...` within 20 s.
   - `stop` presses Stop + Restore; `restart` presses Restart.

## Each event

| event | do |
|---|---|
| `RESULT` | Quote the raw line. Give the runsheet's reading of that label, and go no further than it does. Tag figures (R15). |
| `STATUS ... done` | Summarise that test's windows in a few lines. Append them to `diag-test-results.md`. Update the R20 checkpoint. Then the next test, in order and at Bill's spacing. |
| `STATUS` with SKIPPED, FAILED or NOT APPLIED | Look it up in "Labels that flag a problem". That window is not evidence. |
| `STATUS BUSY` | The press went into a running test. `press` should prevent this, so report it. |
| `UNAVAILABLE` / `AVAILABLE` | Expected only in TB-1 2/3, which lasts 10 min. Anywhere else it is a fault; report it. |
| `REBOOT` | The running test was aborted. Report it. Do not re-press without Bill. |
| `BANK` | The bank left IDLE. Run `stop`, then report. |
| `STALL` or `ERROR` | Report it. Press nothing and ask Bill. |

Leave `CFGFAIL_*` and `TB1_ON_AFTER_NOAPI` windows out of every conclusion
(runsheet, "Labels that flag a problem"). If `CFGFAIL_TB5_RESTORED` appeared,
run `restart` once TB-5 is done.

## Record

Append to `diag-test-results.md`, creating it on the first result:

- every RESULT line verbatim, with its time,
- the per-test summary.

The watcher also logs every event to `~/.cache/diag_watch/events.log`.

## After the last test

1. Do the runsheet's end-of-run exports.
2. Bill reinstalls V1.27 from Device Builder.
3. Ask before deleting the H: diag copy. Device Builder commits the deletion on
   sight, the same way it committed the add (`6b60914`).
