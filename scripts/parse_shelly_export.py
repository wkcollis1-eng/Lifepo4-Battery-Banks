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
    --force          : Append EVERY row (ignores duplicates & last-row cutoff)
    Header validation: Checks target CSV header before writing
    Enhanced --status: Shows first row, row count, file size + next export range

Usage:
    python parse_shelly_export.py --status
    python parse_shelly_export.py "export.csv" --dry-run
    python parse_shelly_export.py "export.csv" --force
    python parse_shelly_export.py --dir path/to/exports/
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
    return norm in {
        "min voltage", "max voltage",
        "min temperature", "max temperature",
        "min humidity", "max humidity",
        "humidity",
    }


# ── Header validation (new) ────────────────────────────────────────────────────
def validate_header(csv_path: pathlib.Path, expected: list[str]) -> bool:
    """Return True if header matches or file is empty/new."""
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return True
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            actual = next(csv.reader(f), None)
            if actual is None or actual == expected:
                return True
            print(f" WARNING: Header mismatch in {csv_path.name}")
            print(f"   Expected: {expected}")
            print(f"   Found:    {actual}")
            print("   Skipping this file to prevent data corruption.")
            return False
    except Exception as e:
        print(f" WARNING: Could not validate header of {csv_path.name} ({e})")
        return False


# ── Enhanced file info for --status (new) ──────────────────────────────────────
def get_file_info(csv_path: pathlib.Path) -> dict:
    """Return first_dt, last_dt, row_count, size_kb."""
    info = {"first": None, "last": None, "count": 0, "size_kb": 0.0}
    if not csv_path.exists():
        return info
    info["size_kb"] = round(csv_path.stat().st_size / 1024, 1)
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
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
            print(f"            next export: {next_hour.strftime('%d/%m/%Y %H:%M')} → now")
        else:
            print(f" {label:11} {'not found' if not path.exists() else 'empty'}: {path.name}")
    print()


# ── Core helpers ───────────────────────────────────────────────────────────────
def dt_to_row_key(dt: datetime.datetime) -> str:
    return f"{dt.strftime(OUTPUT_DATE_FMT)}|{dt.strftime(OUTPUT_TIME_FMT)}"


def parse_dt_key(date_str: str, time_str: str) -> str:
    return f"{date_str.strip()}|{time_str.strip()}"


def get_last_datetime(csv_path: pathlib.Path) -> datetime.datetime | None:
    if not csv_path.exists():
        return None
    last_row = None
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                last_row = row
        if not last_row:
            return None
        date_s = last_row.get("Date", "").strip()
        time_s = last_row.get("Time", "").strip()
        return datetime.datetime.strptime(f"{date_s} {time_s}", SHELLY_DATE_FMT)
    except Exception as e:
        print(f" WARNING: Could not read last row from {csv_path.name} ({e})")
        return None


def get_existing_keys(csv_path: pathlib.Path) -> set[str]:
    if not csv_path.exists():
        return set()
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            return {
                parse_dt_key(row.get("Date", ""), row.get("Time", ""))
                for row in csv.DictReader(f)
                if row.get("Date") and row.get("Time")
            }
    except Exception as e:
        print(f" WARNING: Could not read existing keys from {csv_path.name} ({e})")
        return set()


def count_skipped_duplicates(section_key: str, sections: dict, existing: set[str]) -> int:
    count = 0
    for dt_str in sections.get(section_key, {}):
        try:
            dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
            if dt_to_row_key(dt) in existing:
                count += 1
        except ValueError:
            pass
    return count


# ── Row filter (now supports --force) ──────────────────────────────────────────
def _filter(dt_str: str, existing: set[str], last_dt: datetime.datetime | None, force: bool) -> bool:
    if force:
        return True
    try:
        row_dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
    except ValueError:
        return False
    key = dt_to_row_key(row_dt)
    if key in existing or (last_dt and row_dt <= last_dt):
        return False
    return True


# ── Row builders ───────────────────────────────────────────────────────────────
def build_voltage_rows(sections: dict, existing: set[str], last_dt: datetime.datetime | None, force: bool) -> list[dict]:
    min_s = sections.get("min voltage", {})
    max_s = sections.get("max voltage", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, last_dt, force):
            continue
        if dt_str not in min_s or dt_str not in max_s:
            print(f" WARNING: {dt_str} missing Min or Max voltage — skipping")
            continue
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
        rows.append({
            "Date": dt.strftime(OUTPUT_DATE_FMT),
            "Time": dt.strftime(OUTPUT_TIME_FMT),
            "Min": round(min_s[dt_str], 4),
            "Max": round(max_s[dt_str], 4),
        })
    return rows


def build_temp_rows(sections: dict, existing: set[str], last_dt: datetime.datetime | None, force: bool) -> list[dict]:
    min_s = sections.get("min temperature", {})
    max_s = sections.get("max temperature", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, last_dt, force):
            continue
        if dt_str not in min_s or dt_str not in max_s:
            print(f" WARNING: {dt_str} missing Min or Max temp — skipping")
            continue
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
        rows.append({
            "Date": dt.strftime(OUTPUT_DATE_FMT),
            "Time": dt.strftime(OUTPUT_TIME_FMT),
            "Min": round(min_s[dt_str], 2),
            "Max": round(max_s[dt_str], 2),
        })
    return rows


def build_humidity_rows(sections: dict, existing: set[str], last_dt: datetime.datetime | None, force: bool) -> list[dict]:
    single = sections.get("humidity", {})
    if single:
        rows = []
        for dt_str in sorted(single.keys()):
            if not _filter(dt_str, existing, last_dt, force):
                continue
            dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
            rows.append({
                "Date": dt.strftime(OUTPUT_DATE_FMT),
                "Time": dt.strftime(OUTPUT_TIME_FMT),
                "Humidity": round(single[dt_str], 2),
            })
        return rows

    # Legacy min/max
    min_s = sections.get("min humidity", {})
    max_s = sections.get("max humidity", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, last_dt, force):
            continue
        vals = [v for v in (min_s.get(dt_str), max_s.get(dt_str)) if v is not None]
        if len(vals) == 1:
            print(f" WARNING: {dt_str} only has one humidity value — using it")
        if vals:
            dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
            rows.append({
                "Date": dt.strftime(OUTPUT_DATE_FMT),
                "Time": dt.strftime(OUTPUT_TIME_FMT),
                "Humidity": round(sum(vals) / len(vals), 2),
            })
    return rows


# ── CSV append with header validation ──────────────────────────────────────────
def append_rows(rows: list[dict], csv_path: pathlib.Path, header: list[str], dry_run: bool) -> int:
    if not rows:
        return 0
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if dry_run:
        for row in rows:
            vals = " ".join(f"{k}={row[k]}" for k in header if k not in ("Date", "Time"))
            print(f" DRY RUN {row['Date']} {row['Time']} {vals}")
        return len(rows)

    try:
        file_exists = csv_path.exists() and csv_path.stat().st_size > 0
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if not file_exists:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)
                vals = " ".join(f"{k}={row[k]}" for k in header if k not in ("Date", "Time"))
                print(f" Appended {row['Date']} {row['Time']} {vals}")
        return len(rows)
    except Exception as e:
        print(f" ERROR: Failed to write to {csv_path.name} — {e}")
        return 0


# ── Process one file (now with --force support) ────────────────────────────────
def process_file(path: pathlib.Path, dry_run: bool, force: bool) -> int:
    print(f"\nParsing: {path.name}")
    if force:
        print(" ⚠️  FORCE MODE: ALL rows will be appended (duplicates & cutoff ignored)")

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        print(f" ERROR: Cannot read export file {path.name} — {e}")
        return 0

    lines = [l.rstrip() for l in text.splitlines()]
    sections = parse_sections(lines)  # parse_sections is defined below
    if not sections:
        print(" ERROR: No sections detected.")
        return 0

    total_written = 0
    new_counts = {"voltage": 0, "temp": 0, "hum": 0}

    # Voltage
    if sections.get("min voltage") or sections.get("max voltage"):
        if not validate_header(VOLTAGE_CSV, VOLTAGE_HEADER):
            pass
        else:
            last_dt = None if force else get_last_datetime(VOLTAGE_CSV)
            existing = set() if force else get_existing_keys(VOLTAGE_CSV)
            if not force and last_dt:
                print(f" Voltage appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup = count_skipped_duplicates("min voltage", sections, existing) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate voltage row(s)")
            rows = build_voltage_rows(sections, existing, last_dt, force)
            written = append_rows(rows, VOLTAGE_CSV, VOLTAGE_HEADER, dry_run)
            total_written += written
            new_counts["voltage"] = written

    # Temperature
    if sections.get("min temperature") or sections.get("max temperature"):
        if not validate_header(TEMP_CSV, TEMP_HEADER):
            pass
        else:
            last_dt = None if force else get_last_datetime(TEMP_CSV)
            existing = set() if force else get_existing_keys(TEMP_CSV)
            if not force and last_dt:
                print(f" Temp appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup = count_skipped_duplicates("min temperature", sections, existing) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate temperature row(s)")
            rows = build_temp_rows(sections, existing, last_dt, force)
            written = append_rows(rows, TEMP_CSV, TEMP_HEADER, dry_run)
            total_written += written
            new_counts["temp"] = written

    # Humidity
    if (sections.get("humidity") or sections.get("min humidity") or sections.get("max humidity")):
        if not validate_header(HUMIDITY_CSV, HUMIDITY_HEADER):
            pass
        else:
            last_dt = None if force else get_last_datetime(HUMIDITY_CSV)
            existing = set() if force else get_existing_keys(HUMIDITY_CSV)
            if not force and last_dt:
                print(f" Humidity appending after: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup_key = "humidity" if sections.get("humidity") else "min humidity"
            dup = count_skipped_duplicates(dup_key, sections, existing) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate humidity row(s)")
            rows = build_humidity_rows(sections, existing, last_dt, force)
            written = append_rows(rows, HUMIDITY_CSV, HUMIDITY_HEADER, dry_run)
            total_written += written
            new_counts["hum"] = written

    print(f" → Voltage: {new_counts['voltage']} new | "
          f"Temp: {new_counts['temp']} new | "
          f"Hum: {new_counts['hum']} new")
    return total_written


def parse_sections(lines: list[str]) -> dict[str, dict[str, float]]:
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
            datetime.datetime.strptime(raw_ts, SHELLY_DATE_FMT)
            value = float(raw_val)
        except ValueError:
            skipped += 1
            continue
        result[current][raw_ts] = value
    if skipped:
        print(f" Skipped {skipped} unparseable line(s)")
    return result


# ── Main ───────────────────────────────────────────────────────────────────────
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
        print('Export the indicated date ranges from the Shelly app, then run:')
        print(' python parse_shelly_export.py "your_export.csv"')
        sys.exit(0)

    if args.dry_run:
        print("DRY RUN — nothing will be written\n")

    total = 0
    for path in input_files:
        total += process_file(path, args.dry_run, args.force)

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Done: "
          f"{total} row(s) {'would be ' if args.dry_run else ''}appended")


if __name__ == "__main__":
    main()
