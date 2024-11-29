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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    return parser.parse_args()


def find_schedule_files(root_dir: str, weeks: int = 4) -> list[Path]:
    """Find all relevant YAML files from newest to oldest within time window."""
    root = Path(root_dir)
    today = datetime.now(tz=timezone.utc)
    cutoff = today - timedelta(weeks=weeks)

    files = []
    for year_dir in sorted(root.glob("[0-9][0-9][0-9][0-9]"), reverse=True):
        year = int(year_dir.name)
        for month_dir in sorted(year_dir.glob("[0-9][0-9]"), reverse=True):
            month = int(month_dir.name)
            for day_file in sorted(month_dir.glob("[0-9][0-9].yml"), reverse=True):
                day = int(day_file.stem)
                date = datetime(year, month, day, tzinfo=timezone.utc)
                if date > today:
                    continue
                if date < cutoff:
                    break
                files.append(day_file)
    return files


def load_schedule(file_path: Path) -> dict:
    """Load and parse a schedule YAML file."""
    yaml = YAML(typ="safe")
    with file_path.open() as f:
        return yaml.load(f)


def extract_programs(schedule: dict) -> list[tuple[str, datetime, str]]:
    """Extract program entries from schedule data."""
    programs = []
    for channel, content in schedule.get("data", {}).items():
        for prog in content.get("programmes", []):
            start_time = datetime.fromisoformat(prog["start_time"])
            series = prog.get("series", prog.get("title", ""))
            programs.append((series, start_time, channel))
    return programs


def analyze_recurring_programs(files: list[Path]) -> dict:
    """Analyze programs to find recurring patterns."""
    # Track occurrences of series+weekday+hour combinations
    occurrences = defaultdict(set)

    for file_path in files:
        schedule = load_schedule(file_path)
        programs = extract_programs(schedule)

        for series, start_time, channel in programs:
            weekday = start_time.weekday()
            # Round to nearest 5 minutes for tolerance
            hour = start_time.hour
            minute = (start_time.minute // 5) * 5

            key = (series, weekday, channel)
            occurrences[key].add((hour, minute))

    # Filter for programs occurring multiple times
    recurring = {}
    for (series, weekday, channel), times in occurrences.items():
        min_occurrences = 2
        if len(times) >= min_occurrences:  # Filter for recurring programs
            if series not in recurring:
                recurring[series] = defaultdict(set)
            recurring[series][channel].add((weekday, sorted(times)))

    return recurring


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

    files = find_schedule_files(args.directory)
    if not files:
        logger.warning("No schedule files found in the specified time window")
        return

    recurring = analyze_recurring_programs(files)

    # Log results
    for series in sorted(recurring.keys()):
        logger.info("\nSarja: %s", series)
        for channel, occurrences in recurring[series].items():
            logger.info("Kanava: %s", channel)
            for weekday, times in sorted(occurrences):
                logger.info("  %s:", weekday_name(weekday))
                for hour, minute in times:
                    logger.info("    %s", format_time(hour, minute))


if __name__ == "__main__":
    main()
