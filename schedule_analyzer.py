#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ruamel-yaml",
# ]
# ///
"""TV/Radio schedule analyzer for finding recurring programs."""

from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


def setup_logging(*, debug: bool = False) -> None:
    """Configure logging with optional debug level."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments

    """
    parser = argparse.ArgumentParser(
        description="Analyze recurring programs from schedule YAML files",
    )
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="Root directory containing YYYY/MM/DD.yml schedule files",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "html"],
        default="text",
        help="Output format (text or html)",
    )
    return parser.parse_args()


def find_schedule_files(root_dir: str, weeks: int = 4) -> list[Path]:
    """Find all relevant YAML files from newest to oldest within time window."""
    root = Path(root_dir)
    logger.debug("Searching in: %s", root)

    log_directory_contents(root)

    files = []
    logger.debug("Looking for year directories matching: [0-9][0-9][0-9][0-9]")
    year_dirs = sorted(root.glob("[0-9][0-9][0-9][0-9]"), reverse=True)
    for year_dir in year_dirs:
        year = int(year_dir.name)
        logger.debug("Found year directory: %s", year_dir.name)

        logger.debug(
            "Looking for month directories in %s matching: [0-9][0-9]",
            year_dir.name,
        )
        month_dirs = sorted(year_dir.glob("[0-9][0-9]"), reverse=True)
        for month_dir in month_dirs:
            month = int(month_dir.name)
            logger.debug("Found month directory: %s/%s", year_dir.name, month_dir.name)

            log_directory_contents(month_dir)

            logger.debug(
                "Looking for day files in %s/%s matching: [0-9][0-9].yaml",
                year_dir.name,
                month_dir.name,
            )
            day_files = sorted(month_dir.glob("[0-9][0-9].yaml"), reverse=True)
            for day_file in day_files:
                day = int(day_file.stem)
                date = datetime(year, month, day, tzinfo=timezone.utc)
                if not files:  # First file found
                    latest_date = date
                    cutoff = min(
                        datetime.now(tz=timezone.utc),
                        latest_date - timedelta(weeks=weeks),
                    )
                    logger.debug(
                        "Date range: %s to %s",
                        cutoff.date(),
                        latest_date.date(),
                    )
                elif date < cutoff:
                    logger.debug("Reached cutoff date: %s", date.date())
                    break
                logger.debug("Found schedule file: %s", day_file)
                files.append(day_file)
    return files


def load_schedule(file_path: Path) -> dict:
    """Load and parse a schedule YAML file."""
    yaml = YAML(typ="safe")
    with file_path.open() as f:
        return yaml.load(f)


def normalize_program_name(name: str) -> str:
    """Normalize program names with custom rules."""
    if name == "Yle Uutiset ja sää":
        return "Yle Uutiset"
    return name


def extract_programs(schedule: dict) -> list[tuple[str, datetime]]:
    """Extract program entries from schedule data."""
    programs = []
    content = next(iter(schedule.get("data", {}).values()))
    for prog in content.get("programmes", []):
        start_time = datetime.fromisoformat(prog["start_time"])
        series = normalize_program_name(prog.get("series", prog.get("title", "")))
        programs.append((series, start_time))
    return programs


def analyze_recurring_programs(
    files: list[Path],
) -> list[tuple[int, int, int, str, set[datetime.date]]]:
    """Analyze programs to find recurring patterns.

    Returns:
        List of tuples (weekday, hour, minute, series) for recurring programs

    The function tracks occurrences of series+weekday combinations with their time
    ranges
    in a dictionary where:
    - Keys are (series, weekday) tuples
    - Values are lists of ((earliest_time, latest_time), set(dates)) tuples

    """
    occurrences = defaultdict(list)
    tolerance = timedelta(minutes=13)

    for file_path in files:
        schedule = load_schedule(file_path)
        programs = extract_programs(schedule)

        logger.debug("Processing file: %s", file_path)
        for series, start_time in programs:
            logger.debug("  Found program: %s at %s", series, start_time)
            weekday = start_time.weekday()

            # Create a datetime with just time components for comparison
            time_only = start_time.replace(year=2000, month=1, day=1)
            key = (series, weekday)

            # Try to find matching time slot
            matched = False
            for (earliest, latest), dates in occurrences[key]:
                if earliest - tolerance <= time_only <= latest + tolerance:
                    # Update time range if needed
                    new_earliest = min(earliest, time_only)
                    new_latest = max(latest, time_only)
                    # Replace tuple with updated range
                    idx = occurrences[key].index(((earliest, latest), dates))
                    dates.add(start_time.date())
                    occurrences[key][idx] = ((new_earliest, new_latest), dates)
                    dates.add(start_time.date())
                    matched = True
                    break

            if not matched:
                # Create new time slot
                occurrences[key].append(((time_only, time_only), {start_time.date()}))

    # Filter for programs occurring multiple times
    recurring = []
    min_occurrences = 2
    for (series, weekday), time_slots in occurrences.items():
        for (earliest, latest), dates in time_slots:
            if len(dates) >= min_occurrences:
                # Use the average time for display
                avg_time = earliest + (latest - earliest) / 2
                logger.debug(
                    "Analyzing series '%s' on %s at %s "
                    "(range: %s-%s) with %d occurrences",
                    series,
                    weekday_name(weekday),
                    avg_time.strftime("%H:%M"),
                    earliest.strftime("%H:%M"),
                    latest.strftime("%H:%M"),
                    len(dates),
                )
                recurring.append(
                    (weekday, avg_time.hour, avg_time.minute, series, dates),
                )

    # Sort by time then weekday
    recurring.sort()
    return recurring


def log_directory_contents(directory: Path, prefix: str = "") -> None:
    """Log the contents of a directory with optional prefix for context."""
    logger.debug("%sDirectory contents:", prefix)
    for item in directory.iterdir():
        logger.debug(
            "%s  %s %s",
            prefix,
            "DIR " if item.is_dir() else "FILE",
            item.name,
        )


def weekday_name(day_num: int) -> str:
    """Convert weekday number to name."""
    days = [
        "Maanantai",
        "Tiistai",
        "Keskiviikko",
        "Torstai",
        "Perjantai",
        "Lauantai",
        "Sunnuntai",
    ]
    return days[day_num]


def format_time(hour: int, minute: int) -> str:
    """Format time as HH:MM."""
    return f"{hour:02d}:{minute:02d}"


def format_dates(dates: set[datetime.date]) -> str:
    """Format a set of dates intelligently as ranges or lists.

    Examples:
        (1/8/22.12.) - Same month, non-sequential
        (1-22.12.) - Same month, sequential
        (30.11.-14.12.) - Multi-month range
        (30.11., 7/14/21.12.) - Multi-month with non-sequential dates
        (5-19.12., 2.1.) - Sequential range followed by non-sequential date

    """
    sorted_dates = sorted(dates)
    if not sorted_dates:
        return ""

    weekly_interval = 7  # Days between weekly recurring programs

    # Split dates into sequential groups
    sequences = []
    current_seq = [sorted_dates[0]]

    for prev, curr in zip(sorted_dates, sorted_dates[1:]):
        if (curr - prev).days == weekly_interval:
            current_seq.append(curr)
        else:
            sequences.append(current_seq)
            current_seq = [curr]
    sequences.append(current_seq)

    # Format each sequence
    formatted_parts = []
    for sequence in sequences:
        if len(sequence) == 1:
            d = sequence[0]
            formatted_parts.append(f"{d.day}.{d.month}.")
        else:
            start, end = sequence[0], sequence[-1]
            if start.month == end.month:
                formatted_parts.append(f"{start.day}-{end.day}.{start.month}.")
            else:
                formatted_parts.append(
                    f"{start.day}.{start.month}.-{end.day}.{end.month}.",
                )

    return ", ".join(formatted_parts)


def count_weekday_occurrences(files: list[Path], weekday: int) -> int:
    """Count how many times a weekday occurs in the analyzed files."""
    dates = {
        datetime.strptime(
            f.parent.parent.name + f.parent.name + f.stem,
            "%Y%m%d",
        )
        .replace(tzinfo=timezone.utc)
        .date()
        for f in files
    }
    return sum(1 for date in dates if date.weekday() == weekday)


def generate_html_table(
    by_weekday: dict[int, list[tuple[str, str, set[datetime.date]]]],
    files: list[Path],
) -> str:
    """Generate HTML table for recurring programs."""
    html = [
        "<html><head><style>",
        "table { border-collapse: collapse; }",
        "th, td { border: 1px solid black; padding: 4px; }",
        "th { background-color: #f0f0f0; }",
        "</style></head><body>",
        "<table>",
    ]

    # Get all unique dates from files
    all_dates = sorted(
        {
            datetime.strptime(
                f.parent.parent.name + f.parent.name + f.stem,
                "%Y%m%d",
            )
            .replace(tzinfo=timezone.utc)
            .date()
            for f in files
        },
    )

    for weekday in range(7):
        if weekday in by_weekday:
            # Header row with weekday and dates
            week_dates = [d for d in all_dates if d.weekday() == weekday]
            html.append("<tr>")
            html.append(f"<th colspan='2'>{weekday_name(weekday)}</th>")
            html.extend([f"<th>{date.day}.{date.month}.</th>" for date in week_dates])
            html.append("</tr>")

            # Program rows - each program gets its own row
            for time_str, name, prog_dates in sorted(by_weekday[weekday]):
                html.append("<tr>")
                html.append(f"<td>{time_str}</td>")
                html.append(f"<td>{name}</td>")

                # Add markers for dates when program occurs
                for date in week_dates:
                    marker = "X" if date in prog_dates else ""
                    html.append(f"<td>{marker}</td>")
                html.append("</tr>")

    html.append("</table></body></html>")
    return "\n".join(html)


def main() -> None:
    """Analyze schedule files and report recurring programs."""
    args = parse_args()
    setup_logging(debug=args.debug)

    files = find_schedule_files(args.directory)
    if not files:
        logger.warning("No schedule files found in the specified time window")
        return

    recurring = analyze_recurring_programs(files)

    if args.format == "html":
        # For HTML, keep programs separate
        by_weekday = defaultdict(list)
        for weekday, hour, minute, series, dates in recurring:
            time_str = format_time(hour, minute)
            # Store program info as (time, name, dates) tuple
            by_weekday[weekday].append((time_str, series, dates))
        html_output = generate_html_table(by_weekday, files)
        sys.stdout.write(html_output + "\n")
    else:
        # For text output, group by weekday and time
        by_weekday_time = defaultdict(lambda: defaultdict(list))
        for weekday, hour, minute, series, dates in recurring:
            time_str = format_time(hour, minute)
            expected_occurrences = count_weekday_occurrences(files, weekday)
            if len(dates) < expected_occurrences:
                series_with_dates = f"{series} ({format_dates(dates)})"
                by_weekday_time[weekday][time_str].append(series_with_dates)
            else:
                by_weekday_time[weekday][time_str].append(series)

        # Text output
        for weekday in range(7):
            if weekday in by_weekday_time:
                logger.info("%s:", weekday_name(weekday))
                for time_str, series_list in sorted(by_weekday_time[weekday].items()):
                    logger.info("  %s: %s", time_str, " / ".join(sorted(series_list)))


if __name__ == "__main__":
    main()
