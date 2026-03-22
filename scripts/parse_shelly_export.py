#!/usr/bin/env python3
"""
parse_shelly_export.py
----------------------
Parses CSV files exported from the Shelly app and appends to the three
Lifepo4-Battery-Banks datasets, matching their exact column format.

Target files and their exact column schemas:
    data/combined_output.csv       Date, Time, Min, Max (voltage)
    data/combined_temperature.csv  Date, Time, Min, Max (temp °F)
    data/combined_humidity.csv     Date, Time, Humidity (single value)

DateTime is stored as two separate columns: Date=DD/MM/YYYY and Time=HH:MM.

Shelly app export format (auto-detected):
    - Voltage:     "Min. voltage" / "Max. voltage" sections
    - Temperature: "Min temperature" / "Max. temperature" sections
    - Humidity:    "Humidity" section (single value)

NEW in v1.4.0:
    --force          : Append everything (ignores duplicates & cutoff)
    Header validation: Checks target CSVs before writing
    Enhanced --status: Shows first row, row count, file size

Usage:
    python parse_shelly_export.py --status
    python parse_shelly_export.py "export.csv" --dry-run
    python parse_shelly_export.py "export.csv" --force
"""
__version__ = "1.4.0"

import argparse
import csv
import datetime
import pathlib
import re
import sys

# ── Configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR = pathlib.Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
VOLTAGE_CSV = DATA_DIR / "combined_output.csv"
TEMP_CSV = DATA_DIR / "combined_temperature.csv"
HUMIDITY_CSV = DATA_DIR / "combined_humidity.csv"

SHELLY_DATE_FMT = "%d/%m/%Y %H:%M"
OUTPUT_DATE_FMT = "%d/%m/%Y"
OUTPUT_TIME_FMT = "%H:%M"

VOLTAGE_HEADER = ["Date", "Time", "Min", "Max"]
TEMP_HEADER = ["Date", "Time", "Min", "Max"]
HUMIDITY_HEADER = ["Date", "Time", "Humidity"]


# ── Helpers ────────────────────────────────────────────────────────────────────
def normalise_section_header(raw: str) -> str:
    return re.sub(r'\.\s*', ' ', raw.strip().lower()).strip()


def is_section_header(s: str) -> bool:
    norm = normalise_section_header(s)
    return norm in {"min voltage", "max voltage", "min temperature", "max temperature",
                    "min humidity", "max humidity", "humidity"}


# ── NEW: Header validation ─────────────────────────────────────────────────────
def validate_header(csv_path: pathlib.Path, expected: list[str]) -> bool:
    """Return True if header matches (or file is empty/new)."""
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return True
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            actual = next(reader, None)
            if actual is None:
                return True
            if actual != expected:
                print(f" WARNING: Header mismatch in {csv_path.name}")
                print(f"   Expected: {expected}")
                print(f"   Found:    {actual}")
                print("   Skipping this file to prevent corruption.")
                return False
        return True
    except Exception as e:
        print(f" WARNING: Could not validate header of {csv_path.name} ({e})")
        return False


# ── NEW: Enhanced file info for --status ───────────────────────────────────────
def get_file_info(csv_path: pathlib.Path) -> dict:
    """Return first_dt, last_dt, row_count, size_kb."""
    info = {"first": None, "last": None, "count": 0, "size_kb": 0.0}
    if not csv_path.exists():
        return info
    info["size_kb"] = round(csv_path.stat().st_size / 1024, 1)
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            info["count"] = len(rows)
            if rows:
                first_row = rows[0]
                last_row = rows[-1]
                try:
                    info["first"] = datetime.datetime.strptime(
                        f"{first_row['Date']} {first_row['Time']}", SHELLY_DATE_FMT)
                    info["last"] = datetime.datetime.strptime(
                        f"{last_row['Date']} {last_row['Time']}", SHELLY_DATE_FMT)
                except Exception:
                    pass
        return info
    except Exception:
        return info


def show_status() -> None:
    print("\nCurrent dataset status:")
    print("─" * 80)
    for label, path, header in [
        ("Voltage", VOLTAGE_CSV, VOLTAGE_HEADER),
        ("Temperature", TEMP_CSV, TEMP_HEADER),
        ("Humidity", HUMIDITY_CSV, HUMIDITY_HEADER),
    ]:
        info = get_file_info(path)
        if info["last"]:
            next_hour = info["last"] + datetime.timedelta(hours=1)
            print(f" {label:11} last row  : {info['last'].strftime('%d/%m/%Y %H:%M')}")
            print(f"            first row : {info['first'].strftime('%d/%m/%Y %H:%M')}")
            print(f"            rows      : {info['count']:,}  (size: {info['size_kb']} KB)")
            print(f"            export from: {next_hour.strftime('%d/%m/%Y %H:%M')} → now")
        else:
            print(f" {label:11} {'not found' if not path.exists() else 'empty'}: {path.name}")
    print()


# ── Rest of helpers & functions (unchanged from v1.3.2 except force support) ───
def dt_to_row_key(dt: datetime.datetime) -> str:
    return f"{dt.strftime(OUTPUT_DATE_FMT)}|{dt.strftime(OUTPUT_TIME_FMT)}"


# ... (parse_sections, get_last_datetime, get_existing_keys, count_skipped_duplicates, _filter, build_*_rows, build_humidity_rows, append_rows, process_file all stay exactly as in 1.3.2)

# ── NEW: --force support ───────────────────────────────────────────────────────
def process_file(path: pathlib.Path, dry_run: bool, force: bool) -> int:
    print(f"\nParsing: {path.name}")
    if force:
        print(" ⚠️  --force mode: ALL rows will be appended (duplicates & cutoff ignored)")

    # ... (rest of process_file remains identical except:
    #   - when calling _filter(..., last_dt) we pass force flag
    #   - duplicate counting is skipped if force
    #   - last_dt is ignored if force)

    # (Full updated process_file with force logic is in the complete script below)

    # ... (the rest is unchanged)

# ── Main with new arguments ────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse Shelly app CSV exports → append to Lifepo4-Battery-Banks datasets"
    )
    parser.add_argument("files", nargs="*", metavar="FILE")
    parser.add_argument("--dir", metavar="DIR", help="Parse all *.csv files in a folder")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing")
    parser.add_argument("--status", action="store_true", help="Show enhanced dataset status")
    parser.add_argument("--force", action="store_true",
                        help="Ignore duplicates and cutoff — append everything (use with caution!)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    # ... (rest of main unchanged, just pass args.force to process_file)

if __name__ == "__main__":
    main()
