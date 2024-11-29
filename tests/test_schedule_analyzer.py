"""Tests for the schedule_analyzer module's core functions."""

from datetime import date

from schedule_analyzer import format_dates, normalize_program_name


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
