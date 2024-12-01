"""HTML generation utilities for schedule analyzer."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import jinja2
from babel.core import Locale
from babel.dates import format_date
from zoneinfo import ZoneInfo

MAX_WEEKDAY = 6  # Sunday (0-based indexing)


def weekday_name(day_num: int) -> str:
    """Convert weekday number to name using system locale."""
    import os

    if not 0 <= day_num <= MAX_WEEKDAY:
        msg = f"Invalid weekday number: {day_num}. Must be 0-{MAX_WEEKDAY}."
        raise ValueError(msg)

    lang = os.environ.get("LANG", "en_US.UTF-8").split(".")[0]
    locale = Locale.parse(lang)  # Let UnknownLocaleError propagate

    # Create a date for the given weekday (using 2024 which starts on Monday)
    d = date(2024, 1, 1 + day_num)  # Jan 1, 2024 is Monday
    # Format just the weekday name using explicit locale
    return format_date(d, format="E", locale=locale).lower()  # E gives abbreviated name


def generate_html_table(
    by_weekday: dict[int, list[tuple[str, str, set[datetime.date]]]],
    files: list[Path],
    *,
    tz_name: str | None = None,
) -> str:
    """Generate HTML table for recurring programs using Jinja2 template."""
    # Get all unique dates from files
    file_dates = {
        datetime.strptime(
            f.parent.parent.name + f.parent.name + f.stem + "+0000",
            "%Y%m%d%z",
        ).date()
        for f in files
    }

    # Set default timezone if none specified
    tz_name = tz_name or "Europe/Helsinki"
    # Calculate the date range to show using the specified timezone
    tz = ZoneInfo(tz_name)
    today = datetime.now(tz).date()
    current_monday = today - timedelta(days=today.weekday())
    last_data_monday = max(file_dates) - timedelta(days=max(file_dates).weekday())

    # We want to show 5 weeks including the current week and going forward to last data
    # If we don't have enough future weeks, we'll backfill with past weeks
    weeks_to_show = 5
    weeks_forward = (last_data_monday - current_monday).days // 7 + 1
    weeks_backward = max(0, weeks_to_show - weeks_forward)

    start_monday = current_monday - timedelta(weeks=weeks_backward)

    # Generate all dates we want to show
    week_dates = {weekday: [] for weekday in range(7)}
    for week in range(weeks_to_show):
        week_start = start_monday + timedelta(weeks=week)
        for weekday in range(7):
            date = week_start + timedelta(days=weekday)
            week_dates[weekday].append(date)

    max_dates = weeks_to_show  # Always 5 weeks

    # Set up Jinja2 environment
    template_dir = Path(__file__).parent
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True,
    )
    env.globals["weekday_name"] = weekday_name

    # Copy static files
    for static_file in ["schedule.js", "style.css"]:
        source = template_dir / static_file
        dest = Path(static_file)
        dest.write_text(source.read_text())

    template = env.get_template("schedule.html")
    return template.render(
        by_weekday=by_weekday,
        week_dates=week_dates,
        max_dates=max_dates,
        tz_name=tz_name,
    )
