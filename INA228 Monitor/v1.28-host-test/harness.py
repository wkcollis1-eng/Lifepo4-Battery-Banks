"""Build harness.cpp: the V1.28-touched lambdas, verbatim from main.cpp, against stubs.h."""

import json
import re
import sys

MAIN = sys.argv[1]
src = open(MAIN, encoding="utf-8").read()
L = json.load(open("lambdas.json"))
used = json.load(open("used.json"))["decl"]
sel_lines = set(json.load(open("used.json"))["sel_lines"])
sel = [lam for lam in L if lam["line"] in sel_lines]
used.update(
    {
        "cycle_integration_delta": "template_::TemplateSensor",
        "soc_ledger_sensor": "template_::TemplateSensor",
        "is_charging": "template_::TemplateBinarySensor",
    }
)

# initial values of globals: new(NAME) globals::...<T>(INIT);
init = {}
for m in re.finditer(
    r"new\(([a-z_0-9]+)\) globals::(?:Restoring)?GlobalsComponent<([^>]+)>\((.*?)\);",
    src,
):
    init[m.group(1)] = (m.group(2), m.group(3))

out = [
    '#include "stubs.h"',
    "namespace font { struct Font {}; }",
    "namespace display { struct Display {",
    "  void print(int, int, font::Font *, const char *) {}",
    "  __attribute__((format(printf, 5, 6))) void printf(int, int, font::Font *, const char *, ...) {}",
    "}; }",
]
kind = {}
for name, typ in sorted(used.items()):
    if typ.startswith("globals::"):
        t, iv = init.get(name, (re.search(r"<(.+)>", typ).group(1), "{}"))
        iv = iv if iv else "{}"
        out.append(
            f"static G<{t}> {name}_{{{iv}}}; static G<{t}> *const {name} = &{name}_;"
        )
        kind[name] = "global"
    elif typ in (
        "template_::TemplateSensor",
        "integration::IntegrationSensor",
        "sensor::Sensor",
        "dallas_temp::DallasTemperatureSensor",
        "wifi_signal::WiFiSignalSensor",
    ):
        out.append(f"static Sensor {name}_; static Sensor *const {name} = &{name}_;")
        kind[name] = "sensor"
    elif typ == "template_::TemplateTextSensor":
        out.append(
            f"static TextSensor {name}_; static TextSensor *const {name} = &{name}_;"
        )
        kind[name] = "text"
    elif typ in ("template_::TemplateBinarySensor", "gpio::GPIOBinarySensor"):
        out.append(
            f"static BinarySensor {name}_; static BinarySensor *const {name} = &{name}_;"
        )
        kind[name] = "binary"
    elif typ.startswith("script::QueueingScript<float, int, bool>"):
        out.append(f"static Script3 {name}_; static Script3 *const {name} = &{name}_;")
    elif typ.startswith("script::"):
        out.append(f"static Script0 {name}_; static Script0 *const {name} = &{name}_;")
    elif typ == "homeassistant::HomeassistantTime":
        out.append(f"static HATime {name}_; static HATime *const {name} = &{name}_;")
    elif typ == "i2c::IDFI2CBus":
        out.append(f"static Bus {name}_; static Bus *const {name} = &{name}_;")
    elif typ == "font::Font":
        out.append(
            f"static font::Font {name}_; static font::Font *const {name} = &{name}_;"
        )
    else:
        out.append(f"// (not stubbed: {name} : {typ})")

names = {}
for lam in sel:
    nm = f"L_{lam['line']}"
    out.append(f"// ---- main.cpp:{lam['line']}  {lam['ctx'][:90]}")
    out.append(f"static auto {nm} = {lam['text']};")
    names[lam["line"]] = (nm, lam)

# role macros for the scenario, found by content
ROLES = {
    "BOOT": lambda lam: '"INA228 ALERT armed:' in lam["text"],
    "HWC_T": lambda lam: lam["ctx"].startswith("hw_charge_ah->set_template"),
    "HWC_OV": lambda lam: "brk_loaded->value() = true" in lam["text"],
    "HWE_T": lambda lam: lam["ctx"].startswith("hw_energy_wh->set_template"),
    "HWE_OV": lambda lam: "static float p_wh" in lam["text"],
    "SOC_T": lambda lam: lam["ctx"].startswith("soc_estimate->set_template"),
    "LEDGER_T": lambda lam: lam["ctx"].startswith("soc_ledger_sensor->set_template"),
    "CID_T": lambda lam: lam["ctx"].startswith("cycle_integration_delta->set_template"),
    "ANCHOR_SET": lambda lam: "float anchor_ah, int src, bool clean" in lam["params"],
    "CHG_PRESS": lambda lam: "Charge session started" in lam["text"],
    "CHG_SESS": lambda lam: "Charge session (INA228 CHARGE" in lam["text"],
    "CHG_COND": lambda lam: "REFUSED (O2)" in lam["text"],
    "CHG_THEN": lambda lam: "ANCHOR CLOSURE" in lam["text"],
    "CHG_ELSE": lambda lam: (
        "Charge session ended (no full-charge anchor)" in lam["text"]
    ),
    "TAIL_5S": lambda lam: "absorb_tail_pending_a->value() = i" in lam["text"],
    "MANUAL": lambda lam: "MANUAL ANCHOR" in lam["text"],
    "WIFI_RB": lambda lam: "esp_wifi_get_ps" in lam["text"],
    "MEANNET": lambda lam: (
        "brk_in_ah->value() - brk_out_ah->value()) / h" in lam["text"]
    ),
}
for role, pred in ROLES.items():
    hits = [names[lam["line"]][0] for lam in sel if pred(lam)]
    if len(hits) != 1:
        sys.exit(f"role {role}: {len(hits)} matches")
    out.append(f"#define {role} {hits[0]}")

# every template lambda (for the smoke run)
tmpl = [
    names[lam["line"]][0]
    for lam in sel
    if "->set_template" in lam["ctx"] and lam["ret"] == "std::optional<float>"
]
out.append(
    "static std::vector<std::function<std::optional<float>()>> ALL_TEMPLATES = {"
    + ", ".join(tmpl)
    + "};"
)
trans = [n for n, t in used.items() if t.startswith("globals::GlobalsComponent<")]
tsens = [
    n for n, t in used.items() if t in ("template_::TemplateSensor", "sensor::Sensor")
]
out.append("static void reset_transients() {")
for n in sorted(trans):
    out.append(f"  {n}_.v = {n}_.init;")
for n in sorted(tsens):
    out.append(f"  {n}_.state = NAN; {n}_.has = false;")
out.append("}")
out.append('#include "scenario.inc"')
open("harness.cpp", "w").write("\n".join(out) + "\n")
print(f"harness.cpp: {len(sel)} lambdas, {len(tmpl)} templates")
