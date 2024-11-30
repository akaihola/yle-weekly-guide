"""HTML generation utilities for schedule analyzer."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import jinja2
from babel.core import Locale
from babel.dates import format_date

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
) -> str:
    """Generate HTML table for recurring programs using Jinja2 template."""
    # Get all unique dates from files and include today
    today = datetime.now(timezone.utc).date()
    all_dates = sorted(
        {
            datetime.strptime(
                f.parent.parent.name + f.parent.name + f.stem + "+0000",
                "%Y%m%d%z",
            ).date()
            for f in files
        }
        | {today},
    )

    # Group dates by week and weekday for template
    week_dates = defaultdict(lambda: defaultdict(list))
    for current_date in all_dates:
        monday = current_date - timedelta(days=current_date.weekday())
        week_dates[monday][current_date.weekday()].append(current_date)

    # Convert to format expected by template
    first_date = min(all_dates)
    week_dates = {
        weekday: (
            [None] * (1 if weekday < first_date.weekday() else 0)
            + [
                date
                for monday in sorted(week_dates.keys())
                for date in week_dates[monday].get(weekday, [])
            ]
        )
        for weekday in range(7)
    }

    max_dates = max(len(dates) for dates in week_dates.values())

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
    )
