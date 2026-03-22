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

Shelly app export format (one metric per file, auto-detected):
    - Voltage:     file contains "Min. voltage" / "Max. voltage" sections
    - Temperature: file contains "Min temperature" / "Max. temperature" sections
    - Humidity:    file contains "Humidity" section (single value)

Changes in v1.5.0:
    - FIXED: normalise_section_header() now removes dots before collapsing
      whitespace, so "Max. voltage" and "Max. temperature" are correctly
      detected (previously produced double-spaces that missed the lookup set)
    - FIXED: dead `if not validate_header(...): pass` blocks replaced with
      explicit else branches that log the skip reason
    - FIXED: DATA_DIR.mkdir() moved inside the non-dry-run branch so --dry-run
      no longer creates directories as a side effect
    - FIXED: get_file_info() now strips whitespace from Date/Time fields
      before parsing, matching the behaviour of get_last_datetime()
    - FIXED: show_status() next-export range now substitutes the real current
      datetime instead of printing the literal string "now"
    - FIXED: --force + --dry-run no longer prints the misleading
      "ALL rows will be appended" warning (nothing is written in dry-run)
    - IMPROVED: duplicate detection relies solely on get_existing_keys();
      get_last_datetime() is retained only for the informational "appending
      after" log line, not as a filter gate — this correctly handles gaps
      and out-of-order rows in the target CSVs

Usage:
    python parse_shelly_export.py --status
    python parse_shelly_export.py "export.csv" --dry-run
    python parse_shelly_export.py "export.csv" --force
    python parse_shelly_export.py --dir path/to/exports/
"""
__version__ = "1.5.0"

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
    """
    Normalise a Shelly section header to a canonical lookup key.

    Shelly exports are inconsistent: some headers have trailing dots
    ("Min. voltage", "Max. temperature"), others don't ("Min temperature",
    "Humidity"). Replacing dots with a space (the previous approach) produced
    double-spaces when a dot was already followed by a space, causing those
    headers to silently miss the lookup set.

    This version removes dots entirely, then collapses any resulting runs of
    whitespace to a single space, giving a clean single-spaced key regardless
    of the source punctuation.
    """
    s = re.sub(r'\.', '', raw.strip().lower())
    return re.sub(r'\s+', ' ', s).strip()


def is_section_header(s: str) -> bool:
    norm = normalise_section_header(s)
    return norm in {
        "min voltage", "max voltage",
        "min temperature", "max temperature",
        "min humidity", "max humidity",
        "humidity",
    }


# ── Header validation ──────────────────────────────────────────────────────────
def validate_header(csv_path: pathlib.Path, expected: list[str]) -> bool:
    """Return True if the target CSV header matches expected, or file is new/empty."""
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


# ── File info for --status ─────────────────────────────────────────────────────
def get_file_info(csv_path: pathlib.Path) -> dict:
    """Return first_dt, last_dt, row_count, size_kb for --status display."""
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
                    # Strip whitespace before parsing — guards against trailing
                    # spaces that silently return None in the original version.
                    info["first"] = datetime.datetime.strptime(
                        f"{first_row['Date'].strip()} {first_row['Time'].strip()}",
                        SHELLY_DATE_FMT,
                    )
                    info["last"] = datetime.datetime.strptime(
                        f"{last_row['Date'].strip()} {last_row['Time'].strip()}",
                        SHELLY_DATE_FMT,
                    )
                except Exception:
                    pass
        return info
    except Exception:
        return info


def show_status() -> None:
    now = datetime.datetime.now()
    print("\nCurrent dataset status:")
    print("─" * 80)
    for label, path, _header in [
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
            print(f"            next export: {next_hour.strftime('%d/%m/%Y %H:%M')} → "
                  f"{now.strftime('%d/%m/%Y %H:%M')}")
        else:
            print(f" {label:11} {'not found' if not path.exists() else 'empty'}: {path.name}")
    print()


# ── Core helpers ───────────────────────────────────────────────────────────────
def dt_to_row_key(dt: datetime.datetime) -> str:
    return f"{dt.strftime(OUTPUT_DATE_FMT)}|{dt.strftime(OUTPUT_TIME_FMT)}"


def parse_dt_key(date_str: str, time_str: str) -> str:
    return f"{date_str.strip()}|{time_str.strip()}"


def get_last_datetime(csv_path: pathlib.Path) -> datetime.datetime | None:
    """Read the last row's datetime — used only for the informational log line."""
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
    """
    Build a set of all Date|Time keys already in the target CSV.

    This is the sole duplicate-detection mechanism. Using the full key set
    (rather than a simple last-row cutoff) correctly handles gaps and any
    out-of-order rows that may exist in the target file.
    """
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


def count_skipped_duplicates(
    section_keys: list[str], sections: dict, existing: set[str]
) -> int:
    """
    Count rows across one or more section keys that are already in existing.

    Accepts a list of section keys so voltage/temperature callers can check
    both min and max together, avoiding an under-count when only one side
    is present.
    """
    seen: set[str] = set()
    count = 0
    for key in section_keys:
        for dt_str in sections.get(key, {}):
            if dt_str in seen:
                continue
            seen.add(dt_str)
            try:
                dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
                if dt_to_row_key(dt) in existing:
                    count += 1
            except ValueError:
                pass
    return count


# ── Row filter ─────────────────────────────────────────────────────────────────
def _filter(dt_str: str, existing: set[str], force: bool) -> bool:
    """
    Return True if this row should be included in the output.

    In normal mode: include only rows whose key is not already in existing.
    In force mode: include everything unconditionally.

    Note: the last_dt cutoff from v1.4.0 has been removed. The existing-keys
    set is the correct and complete duplicate check — a cutoff based solely on
    the last row fails silently when the target CSV has gaps.
    """
    if force:
        return True
    try:
        dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
    except ValueError:
        return False
    return dt_to_row_key(dt) not in existing


# ── Row builders ───────────────────────────────────────────────────────────────
def build_voltage_rows(
    sections: dict, existing: set[str], force: bool
) -> list[dict]:
    min_s = sections.get("min voltage", {})
    max_s = sections.get("max voltage", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, force):
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


def build_temp_rows(
    sections: dict, existing: set[str], force: bool
) -> list[dict]:
    min_s = sections.get("min temperature", {})
    max_s = sections.get("max temperature", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, force):
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


def build_humidity_rows(
    sections: dict, existing: set[str], force: bool
) -> list[dict]:
    single = sections.get("humidity", {})
    if single:
        rows = []
        for dt_str in sorted(single.keys()):
            if not _filter(dt_str, existing, force):
                continue
            dt = datetime.datetime.strptime(dt_str, SHELLY_DATE_FMT)
            rows.append({
                "Date": dt.strftime(OUTPUT_DATE_FMT),
                "Time": dt.strftime(OUTPUT_TIME_FMT),
                "Humidity": round(single[dt_str], 2),
            })
        return rows

    # Legacy min/max humidity fallback
    min_s = sections.get("min humidity", {})
    max_s = sections.get("max humidity", {})
    rows = []
    for dt_str in sorted(set(min_s) | set(max_s)):
        if not _filter(dt_str, existing, force):
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


# ── CSV append ─────────────────────────────────────────────────────────────────
def append_rows(
    rows: list[dict],
    csv_path: pathlib.Path,
    header: list[str],
    dry_run: bool,
) -> int:
    if not rows:
        return 0

    if dry_run:
        for row in rows:
            vals = " ".join(f"{k}={row[k]}" for k in header if k not in ("Date", "Time"))
            print(f" DRY RUN {row['Date']} {row['Time']} {vals}")
        return len(rows)

    # Only create the data directory when actually writing.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

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


# ── Process one export file ────────────────────────────────────────────────────
def process_file(path: pathlib.Path, dry_run: bool, force: bool) -> int:
    print(f"\nParsing: {path.name}")
    if force and not dry_run:
        print(" ⚠️  FORCE MODE: ALL rows will be appended (duplicates ignored)")

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        print(f" ERROR: Cannot read export file {path.name} — {e}")
        return 0

    lines = [line.rstrip() for line in text.splitlines()]
    sections = parse_sections(lines)
    if not sections:
        print(" ERROR: No sections detected.")
        return 0

    total_written = 0
    new_counts = {"voltage": 0, "temp": 0, "hum": 0}

    # ── Voltage ────────────────────────────────────────────────────────────────
    if sections.get("min voltage") or sections.get("max voltage"):
        if not validate_header(VOLTAGE_CSV, VOLTAGE_HEADER):
            print(f" SKIPPED voltage — header mismatch in {VOLTAGE_CSV.name}")
        else:
            existing = set() if force else get_existing_keys(VOLTAGE_CSV)
            last_dt = get_last_datetime(VOLTAGE_CSV)
            if last_dt:
                print(f" Voltage last recorded: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup = count_skipped_duplicates(
                ["min voltage", "max voltage"], sections, existing
            ) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate voltage row(s)")
            rows = build_voltage_rows(sections, existing, force)
            written = append_rows(rows, VOLTAGE_CSV, VOLTAGE_HEADER, dry_run)
            total_written += written
            new_counts["voltage"] = written

    # ── Temperature ───────────────────────────────────────────────────────────
    if sections.get("min temperature") or sections.get("max temperature"):
        if not validate_header(TEMP_CSV, TEMP_HEADER):
            print(f" SKIPPED temperature — header mismatch in {TEMP_CSV.name}")
        else:
            existing = set() if force else get_existing_keys(TEMP_CSV)
            last_dt = get_last_datetime(TEMP_CSV)
            if last_dt:
                print(f" Temperature last recorded: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup = count_skipped_duplicates(
                ["min temperature", "max temperature"], sections, existing
            ) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate temperature row(s)")
            rows = build_temp_rows(sections, existing, force)
            written = append_rows(rows, TEMP_CSV, TEMP_HEADER, dry_run)
            total_written += written
            new_counts["temp"] = written

    # ── Humidity ──────────────────────────────────────────────────────────────
    if sections.get("humidity") or sections.get("min humidity") or sections.get("max humidity"):
        if not validate_header(HUMIDITY_CSV, HUMIDITY_HEADER):
            print(f" SKIPPED humidity — header mismatch in {HUMIDITY_CSV.name}")
        else:
            existing = set() if force else get_existing_keys(HUMIDITY_CSV)
            last_dt = get_last_datetime(HUMIDITY_CSV)
            if last_dt:
                print(f" Humidity last recorded: {last_dt.strftime('%d/%m/%Y %H:%M')}")
            dup_keys = (
                ["humidity"] if sections.get("humidity")
                else ["min humidity", "max humidity"]
            )
            dup = count_skipped_duplicates(dup_keys, sections, existing) if not force else 0
            if dup:
                print(f" Skipped {dup} duplicate humidity row(s)")
            rows = build_humidity_rows(sections, existing, force)
            written = append_rows(rows, HUMIDITY_CSV, HUMIDITY_HEADER, dry_run)
            total_written += written
            new_counts["hum"] = written

    print(f" → Voltage: {new_counts['voltage']} new | "
          f"Temp: {new_counts['temp']} new | "
          f"Hum: {new_counts['hum']} new")
    return total_written


# ── Section parser ─────────────────────────────────────────────────────────────
def parse_sections(lines: list[str]) -> dict[str, dict[str, float]]:
    """
    Walk the lines of a Shelly export and collect timestamped values per section.

    Section detection uses normalise_section_header() which strips dots and
    collapses whitespace, so "Min. voltage", "Max. temperature", "Humidity",
    etc. all resolve to clean single-spaced keys.
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

        # Skip blank lines, lines before any section, and column-header rows
        # ("Time, V", "Time, °F", "Time, %", etc.)
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
    parser.add_argument("--status", action="store_true", help="Show dataset status and next export range")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore duplicates — append all rows (use with caution)",
    )
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
        print("Export the indicated date ranges from the Shelly app, then run:")
        print('  python parse_shelly_export.py "your_export.csv"')
        print("Or for a folder of exports:")
        print('  python parse_shelly_export.py --dir path/to/exports/')
        sys.exit(0)

    if args.dry_run:
        print("DRY RUN — nothing will be written\n")

    total = 0
    for path in input_files:
        total += process_file(path, args.dry_run, args.force)

    print(
        f"\n{'DRY RUN — ' if args.dry_run else ''}Done: "
        f"{total} row(s) {'would be ' if args.dry_run else ''}appended"
    )


if __name__ == "__main__":
    main()
