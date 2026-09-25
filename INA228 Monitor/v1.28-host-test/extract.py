"""Extract generated lambdas from main.cpp; emit a stub-typed compile unit.

Usage: python3 extract.py main.cpp out_dir
Writes: lambdas.json (all lambdas with context), check.cpp (V1.28-touched lambdas).
"""

import json
import re
import sys

MAIN, OUT = sys.argv[1], sys.argv[2]
src = open(MAIN, encoding="utf-8").read()
lines = src.split("\n")

# id -> generated type (from the static pointer declarations)
decl = {}
for m in re.finditer(r"^static (.+?) \*const ([A-Za-z_0-9]+) = ", src, re.M):
    decl[m.group(2)] = m.group(1)


def match_brace(s, i):
    """s[i] == '{'; return index just past the matching '}' (skips strings, chars, comments)."""
    depth = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "/" and s.startswith("//", i):
            i = s.index("\n", i)
            continue
        if c == "/" and s.startswith("/*", i):
            i = s.index("*/", i) + 2
            continue
        if c == '"':
            i += 1
            while s[i] != '"':
                i += 2 if s[i] == "\\" else 1
            i += 1
            continue
        if c == "'":
            i += 1
            while s[i] != "'":
                i += 2 if s[i] == "\\" else 1
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced")


lams = []
covered_to = -1
for m in re.finditer(r"\[\]\(([^)]*)\) -> ([^{]+?) \{", src):
    start = m.start()
    line_start = src.rfind("\n", 0, start) + 1
    if src[line_start:start].lstrip().startswith("//"):
        continue  # YAML echo in a comment
    if start < covered_to:
        continue  # nested helper lambda: part of its parent
    end = match_brace(src, m.end() - 1)
    covered_to = end
    line_no = src.count("\n", 0, start) + 1
    ctx = lines[line_no - 1].strip()
    lams.append(
        {
            "line": line_no,
            "ctx": ctx,
            "params": m.group(1),
            "ret": m.group(2).strip(),
            "text": src[start:end],
        }
    )

json.dump(lams, open(f"{OUT}/lambdas.json", "w"), indent=1)

MARK = [
    "brk_",
    "soc_anchor",
    "hw_lsb_a",
    "ina_expect",
    "esp_wifi_get",
    "absorb_tail",
    "soc_unclamped",
    "last_session",
    "ina_noise",
    "soc_source",
    "fb_active",
    "hw_prov_anchor",
    "sentinel_established",
    "hw_energy_raw_wh",
    "hw_last_good_ms",
    "anchor_epoch",
    "hours_since_anchor",
    "last_closure_ah",
    "last_offset_suggest_ma",
    "ina228_config_readback",
    "wifi_ps_readback",
    "wifi_txp_readback",
    "sess_in_start",
    "ina_reset",
    "524288",
    "soc_ledger",
    "last_recommended_sd_rate",
    "last_unseen_drain_ah",
    "hw_charge_anchor_ah",
    "hw_charge_ah",
    "hw_energy_wh",
    "soc_estimate",
    "ah_charged_cycle",
    "ah_discharged_cycle",
]
sel = [lam for lam in lams if any(k in lam["text"] for k in MARK)]
print(f"{len(lams)} lambdas in main.cpp; {len(sel)} touch V1.28 ids")

used = set()
for lam in sel:
    for tok in re.findall(r"\b([a-z_][a-z_0-9]*)->", lam["text"]):
        if tok in decl:
            used.add(tok)
    for tok in re.findall(r"\b([a-z_][a-z_0-9]*)\b", lam["text"]):
        if tok in decl:
            used.add(tok)

json.dump(
    {
        "decl": {k: decl[k] for k in sorted(used)},
        "sel_lines": [lam["line"] for lam in sel],
    },
    open(f"{OUT}/used.json", "w"),
    indent=1,
)
print("ids used:", len(used))
