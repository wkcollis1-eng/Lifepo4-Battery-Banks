#!/usr/bin/env python3
"""
parse_shelly_export.py
----------------------
Parses CSV files exported from the Shelly app and appends to the three
Lifepo4-Battery-Banks datasets, matching their exact column format.

Target files and their exact column schemas:
    data/combined_output.csv        Date, Time, Min, Max     (voltage)
    data/combined_temperature.csv   Date, Time, Min, Max     (temp °F)
    data/combined_humidity.csv      Date, Time, Humidity     (single value)

DateTime is stored as two separate columns: Date=DD/MM/YYYY and Time=HH:MM
This matches the existing CSV format exactly.

Shelly app export format (auto-detected):
    - Voltage:     "Min. voltage" / "Max. voltage" sections
    - Temperature: "Min temperature" / "Max. temperature" sections (dot inconsistent)
    - Humidity:    "Min. humidity" / "Max. humidity" sections

HUMIDITY NOTE:
    combined_humidity.csv stores a single value. When the Shelly export contains
    both Min and Max humidity, they are averaged to produce one value.

TEMPERATURE NOTE:
    combined_temperature.csv stores values in °F. If the export unit is °C
    (detected from the Time header row), values are converted to °F automatically.

BACKFILL:
    On first run, use --status to see the last timestamp in each file and the
    exact date range to request from the Shelly app.

Usage:
    python parse_shelly_export.py --status
    python parse_shelly_export.py "export.csv" --dry-run
    python parse_shelly_export.py "export.csv"
    python parse_shelly_export.py --dir path/to/exports/
"""

import argparse
import csv
import datetime
import pathlib
import re
import sys

# ── Configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR   = pathlib.Path(__file__).parent
DATA_DIR     = SCRIPT_DIR.parent / "data"

VOLTAGE_CSV  = DATA_DIR / "combined_output.csv"
TEMP_CSV     = DATA_DIR / "combined_temperature.csv"
HUMIDITY_CSV = DATA_DIR / "combined_humidity.csv"

# Date/time formats
SHELLY_DATE_FMT = "%d/%m/%Y %H:%M"   # Shelly export: "21/03/2026 08:00"
OUTPUT_DATE_FMT = "%d/%m/%Y"          # CSV Date column: "21/03/2026"
OUTPUT_TIME_FMT = "%H:%M"             # CSV Time column: "08:00"

# Column headers — must match existing files exactly
VOLTAGE_HEADER  = ["Date", "Time", "Min", "Max"]
TEMP_HEADER     = ["Date", "Time", "Min", "Max"]
HUMIDITY_HEADER = ["Date", "Time", "Humidity"]


# ── Helpers ────────────────────────────────────────────────────────────────────
def normalise_section_header(raw: str) -> str:
    """Strip optional trailing dot: 'Max. voltage' → 'max voltage'."""
    return re.sub(r'\.\s*', ' ', raw.strip().lower()).strip()


def is_section_header(s: str) -> bool:
    return normalise_section_header(s) in {
        "min voltage", "max voltage",
        "min temperature", "max temperature",
        "min humidity", "max humidity",
    }


def detect_export_type(lines: list[str]) -> str:
    for line in lines:
        c = normalise_section_header(line.strip())
        if c in ("min voltage", "max voltage"):
            return "voltage"
        if c in ("min temperature", "max temperature",
                 "min humidity", "max humidity"):
            return "temphum"
    return "unknown"


def detect_temp_unit(lines: list[str]) -> str:
    """Return 'F' or 'C' from the Time header row after a temperature section."""
    in_temp = False
    for line in lines:
        s = line.strip().lower()
        c = normalise_section_header(s)
        if c in ("min temperature", "max temperature"):
            in_temp = True
            continue
        if in_temp and s.startswith("time"):
            return "C" if ("°c" in s or ", c" in s) else "F"
    return "F"


def f_to_c(f: float) -> float:
    return round((f - 32) * 5 / 9, 2)


def c_to_f(c: float) -> float:
    return round(c * 9 / 5 + 32, 2)


def dt_to_row_key(dt: datetime.datetime) -> str:
    """Canonical dedup key matching what's stored in the CSV: 'DD/MM/YYYY|HH:MM'."""
    return f"{dt.strftime(OUTPUT_DATE_FMT)}|{dt.strftime(OUTPUT_TIME_FMT)}"


def parse_dt_key(date_str: str, time_str: str) -> str:
    """Build dedup key from existing CSV row."""
    return f"{date_str.strip()}|{time_str.strip()}"


# ── Last-row reader ────────────────────────────────────────────────────────────
def get_last_datetime(csv_path: pathlib.Path) -> datetime.datetime | None:
    """Return the last datetime from a target CSV (reads Date + Time columns)."""
    if not csv_path.exists():
        return None
    last_row = None
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            last_row = row
    if not last_row:
        return None
    try:
        date_s = last_row.get("Date", "").strip()
        time_s = last_row.get("Time", "").strip()
        return datetime.datetime.strptime(f"{date_s} {time_s}", SHELLY_DATE_FMT)
    except (ValueError, KeyError):
        return None


def get_existing_keys(csv_path: pathlib.Path) -> set[str]:
    """Return all Date|Time dedup keys already in the CSV."""
    if not csv_path.exists():
        return set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        return {
            parse_dt_key(row.get("Date", ""), row.get("Time", ""))
            for row in csv.DictReader(f)
        }


def show_status() -> None:
    """Print last timestamp and recommended Shelly export range for each file."""
    print("\nCurrent dataset status:")
    print("─" * 65)
    for label, path in [
        ("Voltage     ", VOLTAGE_CSV),
        ("Temperature ", TEMP_CSV),
        ("Humidity    ", HUMIDITY_CSV),
    ]:
        last = get_last_datetime(path)
        if last:
            next_hour = last + datetime.timedelta(hours=1)
            now = datetime.datetime.now()
            print(f"  {label}  last row : {last.strftime('%d/%m/%Y %H:%M')}")
            print(f"               export from Shelly app: "
                  f"{next_hour.strftime('%d/%m/%Y %H:%M')} → "
                  f"{now.strftime('%d/%m/%Y %H:%M')}")
        else:
            print(f"  {label}  {'not found' if not path.exists() else 'empty or unreadable'}: {path.name}")
    print()


# ── Shelly section parser ──────────────────────────────────────────────────────
def parse_sections(lines: list[str]) -> dict[str, dict[str, float]]:
    """
    Parse all Min/Max data sections from a Shelly export.
    Returns: { "canonical section name": { "DD/MM/YYYY HH:MM": float } }
    """
    result: dict[str, dict] = {}
    current = None
    skipped = 0

    for line in lines:
        s = line.strip()
        low = s.lower()

        if is_section_header(low):
            current = normalise_section_header(low)
            result.setdefault(current, {})
            continue

        if current is None or not s or low.startswith("time"):
            continue

        parts = s.split(",")
        if len(parts) != 2:
            skipped += 1
            continue

        raw_ts, raw_val = parts[0].strip(), parts[1].strip()
        try:
            datetime.datetime.strptime(raw_ts, SHELLY_DATE_FMT)  # validate
            value = float(raw_val)
        except ValueError:
            skipped += 1
            continue

        result[current][raw_ts] = value

    if skipped:
        print(f"    Skipped {skipped} unparseable line(s)")

    return result


# ── Row builders ───────────────────────────────────────────────────────────────
def _filter(dt_str: str, existing: set[str],
            last_dt: datetime.datetime | None) -> bool:
    """Return True if this row should be included (not duplicate, not before cutoff)."""
    try:
        row_dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
    except ValueError:
        return False
    key = dt_to_row_key(row_dt)
    if key in existing:
        return False
    if last_dt and row_dt <= last_dt:
        return False
    return True


def build_voltage_rows(sections: dict, existing: set[str],
                       last_dt: datetime.datetime | None) -> list[dict]:
    min_s = sections.get("min voltage", {})
    max_s = sections.get("max voltage", {})
    rows  = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, last_dt):
            continue
        if dt_str not in min_s or dt_str not in max_s:
            print(f"    WARNING: {dt_str} missing {'Min' if dt_str not in min_s else 'Max'} — skipping")
            continue
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
        rows.append({
            "Date": dt.strftime(OUTPUT_DATE_FMT),
            "Time": dt.strftime(OUTPUT_TIME_FMT),
            "Min":  round(min_s[dt_str], 4),
            "Max":  round(max_s[dt_str], 4),
        })
    return rows


def build_temp_rows(sections: dict, temp_unit: str, existing: set[str],
                    last_dt: datetime.datetime | None) -> list[dict]:
    min_s = sections.get("min temperature", {})
    max_s = sections.get("max temperature", {})
    rows  = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, last_dt):
            continue
        if dt_str not in min_s or dt_str not in max_s:
            print(f"    WARNING: {dt_str} missing {'Min' if dt_str not in min_s else 'Max'} temp — skipping")
            continue
        raw_min, raw_max = min_s[dt_str], max_s[dt_str]
        # Normalise to °F to match combined_temperature.csv
        tmin = round(raw_min, 2) if temp_unit == "F" else c_to_f(raw_min)
        tmax = round(raw_max, 2) if temp_unit == "F" else c_to_f(raw_max)
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
        rows.append({
            "Date": dt.strftime(OUTPUT_DATE_FMT),
            "Time": dt.strftime(OUTPUT_TIME_FMT),
            "Min":  tmin,
            "Max":  tmax,
        })
    return rows


def build_humidity_rows(sections: dict, existing: set[str],
                        last_dt: datetime.datetime | None) -> list[dict]:
    min_s = sections.get("min humidity", {})
    max_s = sections.get("max humidity", {})
    rows  = []
    all_times = sorted(set(min_s) | set(max_s))
    for dt_str in all_times:
        if not _filter(dt_str, existing, last_dt):
            continue
        vals = [v for k, v in [(dt_str, min_s.get(dt_str)),
                                (dt_str, max_s.get(dt_str))] if v is not None]
        if not vals:
            continue
        humidity = round(sum(vals) / len(vals), 2)
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
        rows.append({
            "Date":     dt.strftime(OUTPUT_DATE_FMT),
            "Time":     dt.strftime(OUTPUT_TIME_FMT),
            "Humidity": humidity,
        })
    return rows


# ── CSV append ─────────────────────────────────────────────────────────────────
def append_rows(rows: list[dict], csv_path: pathlib.Path,
                header: list[str], dry_run: bool) -> int:
    if not rows:
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    if dry_run:
        for row in rows:
            vals = "  ".join(f"{k}={row[k]}" for k in header
                             if k not in ("Date", "Time"))
            print(f"    DRY RUN  {row['Date']} {row['Time']}  {vals}")
        return len(rows)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
            vals = "  ".join(f"{k}={row[k]}" for k in header
                             if k not in ("Date", "Time"))
            print(f"    Appended {row['Date']} {row['Time']}  {vals}")

    return len(rows)


# ── Process one file ───────────────────────────────────────────────────────────
def process_file(path: pathlib.Path, dry_run: bool) -> int:
    print(f"\nParsing: {path.name}")

    text  = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = [l.rstrip() for l in text.splitlines()]

    export_type = detect_export_type(lines)
    if export_type == "unknown":
        print("  ERROR: Cannot detect export type (voltage or temp/humidity).",
              file=sys.stderr)
        return 0
    print(f"  Detected type: {export_type}")

    sections = parse_sections(lines)
    total_written = 0

    if export_type == "voltage":
        last_dt  = get_last_datetime(VOLTAGE_CSV)
        existing = get_existing_keys(VOLTAGE_CSV)
        if last_dt:
            print(f"  Appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
        rows = build_voltage_rows(sections, existing, last_dt)
        dup  = sum(1 for dt_str in sections.get("min voltage", {})
                   if not _filter(dt_str, existing, last_dt)
                   and dt_to_row_key(datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)) in existing)
        if dup:
            print(f"  Skipped {dup} duplicate row(s)")
        total_written += append_rows(rows, VOLTAGE_CSV, VOLTAGE_HEADER, dry_run)

    else:  # temphum
        temp_unit = detect_temp_unit(lines)
        print(f"  Temperature unit: °{temp_unit}")

        has_temp = bool(sections.get("min temperature") or sections.get("max temperature"))
        has_hum  = bool(sections.get("min humidity")    or sections.get("max humidity"))

        if has_temp:
            last_dt  = get_last_datetime(TEMP_CSV)
            existing = get_existing_keys(TEMP_CSV)
            if last_dt:
                print(f"  Temp appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            rows = build_temp_rows(sections, temp_unit, existing, last_dt)
            total_written += append_rows(rows, TEMP_CSV, TEMP_HEADER, dry_run)

        if has_hum:
            last_dt  = get_last_datetime(HUMIDITY_CSV)
            existing = get_existing_keys(HUMIDITY_CSV)
            if last_dt:
                print(f"  Humidity appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            rows = build_humidity_rows(sections, existing, last_dt)
            total_written += append_rows(rows, HUMIDITY_CSV, HUMIDITY_HEADER, dry_run)

        if not has_temp and not has_hum:
            print("  No temperature or humidity data found in file.")

    return total_written


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse Shelly app CSV exports → append to Lifepo4-Battery-Banks datasets"
    )
    parser.add_argument("files", nargs="*", metavar="FILE")
    parser.add_argument("--dir",     metavar="DIR",
                        help="Parse all *.csv files in a folder")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview output without writing anything")
    parser.add_argument("--status",  action="store_true",
                        help="Show last timestamp in each dataset")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    input_files: list[pathlib.Path] = []

    if args.dir:
        d = pathlib.Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: --dir '{args.dir}' is not a directory.", file=sys.stderr)
            sys.exit(1)
        input_files = sorted(d.glob("*.csv"))
        print(f"Found {len(input_files)} CSV file(s) in {d}")

    for f in args.files:
        p = pathlib.Path(f)
        if not p.exists():
            print(f"ERROR: File not found: {f}", file=sys.stderr)
            sys.exit(1)
        input_files.append(p)

    if not input_files:
        print("No files specified. Showing dataset status:\n")
        show_status()
        print("Export the indicated date ranges from the Shelly app, then run:")
        print("  python parse_shelly_export.py \"your_export.csv\"")
        sys.exit(0)

    if args.dry_run:
        print("DRY RUN — nothing will be written\n")

    total = 0
    for path in input_files:
        total += process_file(path, args.dry_run)

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Done: "
          f"{total} row(s) {'would be ' if args.dry_run else ''}appended")


if __name__ == "__main__":
    main()
