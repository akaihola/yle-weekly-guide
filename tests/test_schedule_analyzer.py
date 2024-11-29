"""Tests for the schedule_analyzer module's date formatting functions."""

from datetime import date

from schedule_analyzer import format_dates


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
    assert format_dates(dates) == "1/8/22.12."


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
    assert format_dates(dates) == "30.11. - 7/21.12."


def test_format_dates_empty() -> None:
    """Test formatting an empty set of dates."""
    assert format_dates(set()) == ""
