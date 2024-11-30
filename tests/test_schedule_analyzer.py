"""Tests for the schedule_analyzer module's core functions."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import mock_open, patch

from schedule_analyzer import (
    analyze_recurring_programs,
    format_dates,
    normalize_program_name,
)

# Constants for test assertions
DAILY_NEWS_HOUR = 18
WEEKLY_SHOW_HOUR = 20
WEEKLY_SHOW_MINUTE = 30
FLEXIBLE_SHOW_HOUR = 19
FLEXIBLE_SHOW_MINUTE = 5
WEEKDAYS_COUNT = 3
WEEKLY_OCCURRENCES = 3
FLEXIBLE_OCCURRENCES = 2

if TYPE_CHECKING:
    import pytest


def create_mock_schedule(programs: list[tuple[str, datetime]]) -> dict:
    """Create a mock schedule dictionary from program list."""
    return {
        "data": {
            "channel": {
                "programmes": [
                    {
                        "series": name,
                        "start_time": time.isoformat(),
                    }
                    for name, time in programs
                ],
            },
        },
    }


def test_analyze_recurring_daily_program() -> None:
    """Test identifying a program that occurs daily at the same time."""
    mock_files = [
        Path("2024/01/01.yaml"),
        Path("2024/01/02.yaml"),
        Path("2024/01/03.yaml"),
    ]

    base_time = datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc)
    daily_program = "Daily News"

    schedules = [
        create_mock_schedule([(daily_program, base_time + timedelta(days=i))])
        for i in range(3)
    ]

    # Create a mock that only intercepts our YAML files
    real_open = open

    def selective_mock_open(*args: tuple[Any, ...], **kwargs: Any) -> Any:
        if str(args[0]).endswith(".yaml"):
            return mock_open()(*args, **kwargs)
        return real_open(*args, **kwargs)

    with patch("builtins.open", selective_mock_open), patch(
        "schedule_analyzer.load_schedule",
    ) as mock_load:
        mock_load.side_effect = schedules
        result = analyze_recurring_programs(mock_files, min_occurrences=1)

    # Should find program occurring at 18:00 on each day
    assert len(result) == WEEKDAYS_COUNT  # One entry per weekday
    for _weekday, hour, minute, name, dates in result:
        assert hour == DAILY_NEWS_HOUR
        assert minute == 0
        assert name == daily_program
        assert len(dates) == 1  # One occurrence per weekday


def test_analyze_recurring_weekly_program() -> None:
    """Test identifying a program that occurs weekly."""
    mock_files = [
        Path("2024/01/01.yaml"),  # Monday
        Path("2024/01/08.yaml"),  # Next Monday
        Path("2024/01/15.yaml"),  # Next Monday
    ]

    base_time = datetime(2024, 1, 1, 20, 30, tzinfo=timezone.utc)
    weekly_program = "Monday Show"

    schedules = [
        create_mock_schedule([(weekly_program, base_time + timedelta(days=7 * i))])
        for i in range(3)
    ]

    # Create a mock that only intercepts our YAML files
    real_open = open

    def selective_mock_open(*args: tuple[Any, ...], **kwargs: Any) -> Any:
        if str(args[0]).endswith(".yaml"):
            return mock_open()(*args, **kwargs)
        return real_open(*args, **kwargs)

    with patch("builtins.open", selective_mock_open), patch(
        "schedule_analyzer.load_schedule",
    ) as mock_load:
        mock_load.side_effect = schedules
        result = analyze_recurring_programs(mock_files)

    assert len(result) == 1  # One entry for Monday
    weekday, hour, minute, name, dates = result[0]
    assert weekday == 0  # Monday
    assert hour == WEEKLY_SHOW_HOUR
    assert minute == WEEKLY_SHOW_MINUTE
    assert name == weekly_program
    assert len(dates) == WEEKLY_OCCURRENCES  # Three Mondays


def test_analyze_time_variation_tolerance() -> None:
    """Test that programs with slight time variations are grouped together."""
    mock_files = [
        Path("2024/01/01.yaml"),
        Path("2024/01/08.yaml"),
    ]

    base_time = datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc)
    program = "Flexible Time Show"

    # Second occurrence is 10 minutes later (within tolerance)
    schedules = [
        create_mock_schedule([(program, base_time)]),
        create_mock_schedule([(program, base_time + timedelta(days=7, minutes=10))]),
    ]

    # Create a mock that only intercepts our YAML files
    real_open = open

    def selective_mock_open(*args: tuple[Any, ...], **kwargs: Any) -> Any:
        if str(args[0]).endswith(".yaml"):
            return mock_open()(*args, **kwargs)
        return real_open(*args, **kwargs)

    with patch("builtins.open", selective_mock_open), patch(
        "schedule_analyzer.load_schedule",
    ) as mock_load:
        mock_load.side_effect = schedules
        result = analyze_recurring_programs(mock_files)

    assert len(result) == 1
    weekday, hour, minute, name, dates = result[0]
    assert hour == FLEXIBLE_SHOW_HOUR
    assert minute == FLEXIBLE_SHOW_MINUTE  # Average of 19:00 and 19:10
    assert len(dates) == FLEXIBLE_OCCURRENCES


def test_format_dates_same_month_sequence() -> None:
    """Test formatting dates that are sequential within the same month."""
    dates = {
        date(2023, 12, 1),
        date(2023, 12, 8),
        date(2023, 12, 15),
        date(2023, 12, 22),
    }
    assert format_dates(dates) == "1-22.12."


def test_format_dates_same_month_non_sequence() -> None:
    """Test formatting dates that are non-sequential within the same month."""
    dates = {
        date(2023, 12, 1),
        date(2023, 12, 8),
        date(2023, 12, 22),
    }
    assert format_dates(dates) == "1-8.12., 22.12."


def test_format_dates_multi_month_sequence() -> None:
    """Test formatting dates that are sequential across multiple months."""
    dates = {
        date(2023, 11, 30),
        date(2023, 12, 7),
        date(2023, 12, 14),
        date(2023, 12, 21),
    }
    assert format_dates(dates) == "30.11.-21.12."


def test_format_dates_multi_month_mixed() -> None:
    """Test formatting dates that are non-sequential across multiple months."""
    dates = {
        date(2023, 11, 30),
        date(2023, 12, 7),
        date(2023, 12, 21),  # Skip 14th to make non-sequential
    }
    assert format_dates(dates) == "30.11.-7.12., 21.12."


def test_format_dates_empty() -> None:
    """Test formatting an empty set of dates."""
    assert format_dates(set()) == ""


def test_format_dates_sequence_with_gap() -> None:
    """Test formatting dates with a sequence followed by a non-sequential date."""
    dates = {
        date(2023, 12, 5),
        date(2023, 12, 12),
        date(2023, 12, 19),
        date(2024, 1, 2),
    }
    assert format_dates(dates) == "5-19.12., 2.1."


def test_normalize_program_name_uutiset_ja_saa() -> None:
    """Test normalizing 'Yle Uutiset ja sää' to 'Yle Uutiset'."""
    assert normalize_program_name("Yle Uutiset ja sää") == "Yle Uutiset"


def test_normalize_program_name_regular() -> None:
    """Test that regular program names are returned unchanged."""
    name = "Kauniit ja rohkeat"
    assert normalize_program_name(name) == name


def test_normalize_program_name_empty() -> None:
    """Test normalizing an empty string."""
    assert normalize_program_name("") == ""


def test_normalize_program_name_whitespace() -> None:
    """Test normalizing strings with extra whitespace."""
    assert normalize_program_name("  Yle Uutiset ja sää  ") == "Yle Uutiset"


def test_weekday_names_finnish(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test weekday names in Finnish."""
    from templates.html_generator import weekday_name

    monkeypatch.setenv("LANG", "fi_FI.UTF-8")

    expected = [
        "ma",
        "ti",
        "ke",
        "to",
        "pe",
        "la",
        "su",
    ]

    for i, exp in enumerate(expected):
        assert weekday_name(i).lower() == exp


def test_weekday_names_english(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test weekday names in English."""
    from templates.html_generator import weekday_name

    monkeypatch.setenv("LANG", "en_US.UTF-8")

    expected = [
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    ]

    for i, exp in enumerate(expected):
        assert weekday_name(i).lower() == exp


def test_weekday_names_swedish(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test weekday names in Swedish."""
    from templates.html_generator import weekday_name

    monkeypatch.setenv("LANG", "sv_SE.UTF-8")

    expected = ["mån", "tis", "ons", "tors", "fre", "lör", "sön"]

    for i, exp in enumerate(expected):
        assert weekday_name(i).lower() == exp
