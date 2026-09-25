"""Watch the battery-bank diag tests through Home Assistant, and press their buttons.

Written 2026-09-25 for the V1.27-diag2 run (diag-test-runsheet.md, turnover in
diag-test-turnover.md). Entities are resolved by friendly name on every start,
never from a guessed id (R5): the monitor's Restart button, for one, is
button.ina228_bring_up_restart.

usage (HA_URL and HA_TOKEN come from the environment):
  python diag_watch.py check        preflight; exit 1 unless ready to press a test
  python diag_watch.py watch        one stdout line per event, until killed
  python diag_watch.py press TB-4   press a test button; refuses while a test runs
  python diag_watch.py stop         press Diag Stop + Restore
  python diag_watch.py restart      press Restart (runsheet: only after CFGFAIL_TB5_RESTORED)
  python diag_watch.py selftest     prove each event fires, and stays silent when it should

watch keeps a per-entity cursor in ~/.cache/diag_watch/state.json, so a watcher
restarted after a kill or a Monitor re-arm resumes where the last one stopped:
nothing is lost and nothing is reported twice. Every event is also appended to
~/.cache/diag_watch/events.log.

Events (stdout, one line each):
  RESULT      every new Diag Result line (one per finished window)
  STATUS      Diag Status when a test ends, is skipped, refused or stopped, or a
              setting did not apply (done|SKIPPED|FAILED|NOT APPLIED|BUSY|Stopped)
  UNAVAILABLE / AVAILABLE   the monitor dropped off HA / came back (TB-1, reboot, crash)
  REBOOT      Uptime went down: any running test was aborted
  BANK        Bank State changed (the tests need IDLE)
  STALL       a test is running but nothing changed for 25 min
  ERROR / RECOVERED         3 polls in a row failed (HA down, network) / polling works again
"""

import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PREFIX = "Battery Bank Monitor "
SENSORS = {
    "result": "Diag Result",
    "status": "Diag Status",
    "uptime": "Uptime",
    "bank": "Bank State",
    "current": "Battery Current",
    "version": "ESPHome Version",
}
BUTTONS = {
    "TB-1": "Diag TB-1 Wi-Fi Off Test (30 min)",
    "TB-2": "Diag TB-2 TX Power Ladder (85 min)",
    "TB-3": "Diag TB-3 Averaging Ladder (27 min)",
    "TB-4": "Diag TB-4 OLED-Load Round (47 min)",
    "TB-5": "Diag TB-5 ADC Timing Preview (46 min)",
    "stop": "Diag Stop + Restore",
    "restart": "Restart",
}
PROD_HASH = "0x6b05d980"  # V1.27 production, flashed 2026-09-18 (CHANGELOG on H:)
RUNNING = re.compile(r"^TB-\d \d/\d")
ENDED = re.compile(r"done|SKIPPED|FAILED|NOT APPLIED|BUSY|Stopped")
DEAD = ("unavailable", "unknown", "", None)
# The longest healthy gap between two Diag changes is ~16 min [D: TB-2 step =
# 60 s settle + 15 min window, diag yaml]; 25 min leaves margin without hiding a hang.
STALL_S = 25 * 60
POLL_S = 30
DIR = Path.home() / ".cache" / "diag_watch"


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def hhmmss(t):
    return t.astimezone().strftime("%H:%M:%S")


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


class Watcher:
    """Turns HA history rows and a state snapshot into event lines. No I/O, so selftest can drive it."""

    def __init__(self, ids, st):
        self.ids = ids
        self.st = st
        st.setdefault("cursor", {})

    def process(self, hist, snap, now):
        ev, rows = [], []
        for role in ("result", "status"):
            eid = self.ids[role]
            cur = self.st["cursor"].get(eid)
            for r in hist.get(eid, []):
                if cur is None or ts(r["last_changed"]) > ts(cur):
                    rows.append(
                        (ts(r["last_changed"]), role, r["state"], r["last_changed"])
                    )
        for t, role, s, raw in sorted(rows, key=lambda x: x[0]):
            self.st["cursor"][self.ids[role]] = raw
            self.st["last_change"] = raw
            self.st["stalled"] = False
            if role == "result":
                if s not in DEAD:
                    ev.append(f"RESULT {hhmmss(t)} {s}")
            elif s in DEAD:
                if self.st.get("live", True):
                    ev.append(f"UNAVAILABLE {hhmmss(t)} Diag Status is {s or 'empty'}")
                self.st["live"] = False
            else:
                if not self.st.get("live", True):
                    ev.append(f"AVAILABLE {hhmmss(t)} {s}")
                self.st["live"] = True
                self.st["last_status"] = s
                if ENDED.search(s):
                    ev.append(f"STATUS {hhmmss(t)} {s}")
        up, prev = num(snap.get("uptime")), self.st.get("uptime")
        if up is not None:
            if prev is not None and up < prev - 5:
                ev.append(
                    f"REBOOT {hhmmss(now)} uptime {prev:.0f} s -> {up:.0f} s: any running test was aborted"
                )
            self.st["uptime"] = up
        b = snap.get("bank")
        if b not in DEAD and b != self.st.get("bank"):
            if self.st.get("bank") is not None:
                ev.append(f"BANK {hhmmss(now)} Bank State {self.st['bank']} -> {b}")
            self.st["bank"] = b
        last = self.st.get("last_change")
        if (
            RUNNING.match(self.st.get("last_status", ""))
            and last
            and (now - ts(last)).total_seconds() > STALL_S
            and not self.st.get("stalled")
        ):
            mins = (now - ts(last)).total_seconds() / 60
            ev.append(
                f"STALL {hhmmss(now)} no Diag change for {mins:.0f} min; last status: {self.st['last_status']}"
            )
            self.st["stalled"] = True
        return ev


# ---- HA I/O -------------------------------------------------------------------


def api(path, body=None):
    url, token = os.environ.get("HA_URL"), os.environ.get("HA_TOKEN")
    if not url or not token:
        print(
            "ERROR HA_URL and HA_TOKEN must both be set in the environment", flush=True
        )
        sys.exit(2)
    req = urllib.request.Request(
        url.rstrip("/") + path,
        data=None if body is None else json.dumps(body).encode(),
        method="GET" if body is None else "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode() or "null")


def resolve(states=None):
    """role -> entity_id for every sensor and button. Missing or duplicated names are errors."""
    states = api("/api/states") if states is None else states
    by_name = {}
    for e in states:
        by_name.setdefault(e["attributes"].get("friendly_name", ""), []).append(
            e["entity_id"]
        )
    ids, bad = {}, []
    for role, name in list(SENSORS.items()) + list(BUTTONS.items()):
        domain = "button" if role in BUTTONS else "sensor"
        hits = [i for i in by_name.get(PREFIX + name, []) if i.startswith(domain + ".")]
        if len(hits) == 1:
            ids[role] = hits[0]
        else:
            bad.append(f"'{PREFIX + name}': {len(hits)} {domain} entities")
    return ids, bad


def state(eid):
    return api(f"/api/states/{eid}")["state"]


def fetch_history(ids, since):
    q = urllib.parse.urlencode(
        {
            "filter_entity_id": f"{ids['result']},{ids['status']}",
            "significant_changes_only": "0",
        }
    )
    lists = api(f"/api/history/period/{urllib.parse.quote(since)}?{q}&no_attributes")
    return {rows[0]["entity_id"]: rows for rows in lists if rows}


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save(path, st):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1), encoding="utf-8")
    os.replace(tmp, path)


# ---- commands -----------------------------------------------------------------


def cmd_check():
    ids, bad = resolve()
    for m in bad:
        print(f"MISSING {m}")
    ok = not bad
    if "version" in ids:
        v = state(ids["version"])
        print(f"firmware: {v}")
        if PROD_HASH in v:
            print("NOT READY: production V1.27 is still flashed (diag2 not installed)")
            ok = False
    if "bank" in ids:
        b = state(ids["bank"])
        print(f"bank state: {b}")
        if b != "IDLE":
            print("NOT READY: the runsheet needs the bank idle")
            ok = False
    if "current" in ids:
        print(f"battery current: {state(ids['current'])} A")
    if "status" in ids:
        s = state(ids["status"])
        print(f"diag status: {s}")
        if RUNNING.match(s):
            print("NOT READY: a test is running")
            ok = False
    for role, eid in sorted(ids.items()):
        print(f"  {role:8} {eid}")
    print("READY" if ok else "NOT READY")
    return 0 if ok else 1


def cmd_press(role):
    ids, bad = resolve()
    if role not in ids:
        print(f"REFUSED: cannot resolve '{PREFIX + BUTTONS[role]}' ({'; '.join(bad)})")
        return 2
    before = state(ids["status"]) if "status" in ids else ""
    if role.startswith("TB-") and RUNNING.match(before):
        print(f"REFUSED: a test is running ({before})")
        return 2
    api("/api/services/button/press", {"entity_id": ids[role]})
    print(f"pressed {ids[role]} at {hhmmss(dt.datetime.now(dt.timezone.utc))}")
    if role == "restart":
        return 0
    want = f"{role} 1/" if role.startswith("TB-") else "Stopped"
    for _ in range(10):
        time.sleep(2)
        s = state(ids["status"])
        if (
            s.startswith(want)
            or s.startswith("BUSY")
            or "FAILED" in s
            or "SKIPPED" in s
        ):
            print(f"diag status: {s}")
            return 0 if s.startswith(want) else 1
    print(f"NO CONFIRMATION within 20 s; diag status still: {state(ids['status'])}")
    return 1


def cmd_watch(since=None):
    ids, bad = resolve()
    if "result" not in ids or "status" not in ids:
        print(f"ERROR cannot watch: {'; '.join(bad)}", flush=True)
        return 2
    DIR.mkdir(parents=True, exist_ok=True)
    spath, lpath = DIR / "state.json", DIR / "events.log"
    st = load(spath) or {}
    if st.get("ids") != ids or since:
        start = since or dt.datetime.now(dt.timezone.utc).isoformat()
        st = {
            "ids": ids,
            "cursor": {ids["result"]: start, ids["status"]: start},
            "last_change": start,
        }
        # seed it, or a watch started mid-test could never report STALL
        s = state(ids["status"])
        if s not in DEAD:
            st["last_status"] = s
    w = Watcher(ids, st)
    print(
        f"watching {ids['result']}, {ids['status']} from {min(st['cursor'].values())}",
        file=sys.stderr,
        flush=True,
    )
    fails = 0
    while True:
        try:
            hist = fetch_history(ids, min(st["cursor"].values()))
            snap = {"uptime": state(ids["uptime"]), "bank": state(ids["bank"])}
            ev = w.process(hist, snap, dt.datetime.now(dt.timezone.utc))
            if fails >= 3:
                ev.insert(
                    0,
                    f"RECOVERED {hhmmss(dt.datetime.now(dt.timezone.utc))} polling works again",
                )
            fails = 0
        except Exception as e:  # one failed poll must not kill the watch
            fails += 1
            ev = (
                [
                    f"ERROR {hhmmss(dt.datetime.now(dt.timezone.utc))} 3 polls failed in a row: {e!r}"
                ]
                if fails == 3
                else []
            )
        for line in ev:
            print(line, flush=True)
            with lpath.open("a", encoding="utf-8") as f:
                f.write(f"{dt.date.today().isoformat()} {line}\n")
        save(spath, st)
        time.sleep(POLL_S)


def selftest():
    t0 = dt.datetime(2026, 9, 25, 14, 0, tzinfo=dt.timezone.utc)

    def at(m):
        return (t0 + dt.timedelta(minutes=m)).isoformat()

    def rows(*pairs):
        return [{"state": s, "last_changed": at(m)} for m, s in pairs]

    ids = {"result": "sensor.r", "status": "sensor.s"}
    w = Watcher(
        ids, {"cursor": {"sensor.r": at(0), "sensor.s": at(0)}, "last_change": at(0)}
    )
    snap = {"uptime": "600", "bank": "IDLE"}
    fails = 0

    def expect(what, ev, kinds):
        nonlocal fails
        got = [e.split()[0] for e in ev]
        good = got == kinds
        fails += not good
        print(f"  {'ok  ' if good else 'FAIL'}  {what}: {got}")

    h = {
        "sensor.r": rows(
            (0, "OLD"), (5, "TB4_BASE_1 300s"), (10, "TB4_A_LIT_PAGE 300s")
        ),
        "sensor.s": rows((0, "x"), (5, "TB-4 2/9: a"), (10, "TB-4 3/9: b")),
    }
    expect(
        "two results in one poll fire; progress and pre-cursor rows silent",
        w.process(h, snap, t0),
        ["RESULT"] * 2,
    )
    expect("same rows again (re-arm overlap) are silent", w.process(h, snap, t0), [])
    h = {
        "sensor.r": [],
        "sensor.s": rows(
            (12, "TB-3 3/5: AVG 4 (ADC_CONFIG 0xFFFA) - NOT APPLIED"),
            (13, "TB-4 done - x"),
        ),
    }
    expect("NOT APPLIED and done fire", w.process(h, snap, t0), ["STATUS"] * 2)
    h = {
        "sensor.r": rows((20, "unavailable")),
        "sensor.s": rows(
            (19, "TB-1 2/3: off"),
            (20, "unavailable"),
            (21, "unavailable"),
            (31, "TB-1 3/3: on"),
        ),
    }
    expect(
        "drop and return fire once each; dead result silent",
        w.process(h, snap, t0),
        ["UNAVAILABLE", "AVAILABLE"],
    )
    expect(
        "uptime rising is silent",
        w.process({}, {"uptime": "700", "bank": "IDLE"}, t0),
        [],
    )
    expect(
        "uptime falling fires REBOOT",
        w.process({}, {"uptime": "12", "bank": "IDLE"}, t0),
        ["REBOOT"],
    )
    expect(
        "bank leaving IDLE fires",
        w.process({}, {"uptime": "20", "bank": "DISCHARGING"}, t0),
        ["BANK"],
    )
    now = t0 + dt.timedelta(minutes=31 + 26)
    expect(
        "running, no change for 26 min fires STALL",
        w.process({}, {"uptime": "30"}, now),
        ["STALL"],
    )
    expect("the same stall is reported once", w.process({}, {"uptime": "40"}, now), [])
    h = {"sensor.r": [], "sensor.s": rows((60, "TB-1 done"))}
    expect("test end fires", w.process(h, {"uptime": "50"}, now), ["STATUS"])
    later = t0 + dt.timedelta(minutes=200)
    expect("idle after a test never stalls", w.process({}, {"uptime": "60"}, later), [])
    print(f"{fails} failed -> {'SELFTEST FAILED' if fails else 'SELFTEST PASSED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["check"]:
        sys.exit(cmd_check())
    if a[:1] == ["watch"]:
        sys.exit(cmd_watch(a[1] if len(a) > 1 else None))
    if (
        a[:1] == ["press"]
        and len(a) == 2
        and a[1] in BUTTONS
        and a[1].startswith("TB-")
    ):
        sys.exit(cmd_press(a[1]))
    if a[:1] in (["stop"], ["restart"]):
        sys.exit(cmd_press(a[0]))
    if a[:1] == ["selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
