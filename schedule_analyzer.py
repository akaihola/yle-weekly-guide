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
    return parser.parse_args()


def find_schedule_files(root_dir: str, weeks: int = 4) -> list[Path]:
    """Find all relevant YAML files from newest to oldest within time window."""
    root = Path(root_dir)
    today = datetime.now(tz=timezone.utc)
    cutoff = today - timedelta(weeks=weeks)

    logger.debug("Searching in: %s", root)
    logger.debug("Date range: %s to %s", cutoff.date(), today.date())

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
                if date > today:
                    logger.debug("Skipping future date: %s", date.date())
                    continue
                if date < cutoff:
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


def extract_programs(schedule: dict) -> list[tuple[str, datetime]]:
    """Extract program entries from schedule data."""
    programs = []
    content = next(iter(schedule.get("data", {}).values()))
    for prog in content.get("programmes", []):
        start_time = datetime.fromisoformat(prog["start_time"])
        series = prog.get("series", prog.get("title", ""))
        programs.append((series, start_time))
    return programs


def analyze_recurring_programs(files: list[Path]) -> dict:
    """Analyze programs to find recurring patterns."""
    # Track occurrences of series+weekday+hour combinations
    occurrences = defaultdict(set)

    for file_path in files:
        schedule = load_schedule(file_path)
        programs = extract_programs(schedule)

        for series, start_time in programs:
            weekday = start_time.weekday()
            # Round to nearest 5 minutes for tolerance
            hour = start_time.hour
            minute = (start_time.minute // 5) * 5

            key = (series, weekday)
            occurrences[key].add((hour, minute))

    # Filter for programs occurring multiple times
    recurring = defaultdict(set)
    for (series, weekday), times in occurrences.items():
        min_occurrences = 2
        if len(times) >= min_occurrences:  # Filter for recurring programs
            recurring[series].add((weekday, tuple(sorted(times))))

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


def main() -> None:
    """Analyze schedule files and report recurring programs."""
    args = parse_args()
    setup_logging(debug=args.debug)

    files = find_schedule_files(args.directory)
    if not files:
        logger.warning("No schedule files found in the specified time window")
        return

    recurring = analyze_recurring_programs(files)

    # Log results
    for series in sorted(recurring.keys()):
        logger.info("\nSarja: %s", series)
        for weekday, times in sorted(recurring[series]):
            logger.info("  %s:", weekday_name(weekday))
            for hour, minute in times:
                logger.info("    %s", format_time(hour, minute))


if __name__ == "__main__":
    main()
