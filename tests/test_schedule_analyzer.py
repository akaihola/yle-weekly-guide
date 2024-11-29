"""Tests for the schedule_analyzer module's core functions."""

from datetime import date

from babel import Locale

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


def test_weekday_name_monday() -> None:
    """Test Monday (0) converts to weekday name in current locale."""
    from templates.html_generator import weekday_name

    # Get expected name from babel using current locale
    locale = Locale.parse("fi_FI")  # Explicitly parse the locale
    expected = locale.days["format"]["wide"][0]  # Monday is 0
    assert weekday_name(0).lower() == expected.lower()


def test_weekday_name_sunday() -> None:
    """Test Sunday (6) converts to weekday name in current locale."""
    from templates.html_generator import weekday_name

    locale = Locale.default()
    expected = locale.days["format"]["wide"][6]  # Sunday is 6
    assert weekday_name(6).lower() == expected.lower()


def test_weekday_name_all_days() -> None:
    """Test all weekday numbers map to unique localized names."""
    from datetime import date

    from babel.dates import format_date

    from templates.html_generator import weekday_name

    # Generate expected names the same way as weekday_name()
    expected = [
        format_date(date(2024, 1, 1 + i), format="EEEE", locale=Locale.default())
        for i in range(7)
    ]
    actual = [weekday_name(i) for i in range(7)]
    assert [name.lower() for name in actual] == [name.lower() for name in expected]
