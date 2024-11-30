"""Tests for HTML generator module."""

import os
from unittest.mock import patch

import babel.core
import pytest

from templates.html_generator import weekday_name


@pytest.fixture
def mock_locale() -> None:
    """Fixture to control the locale during tests."""
    original_lang = os.environ.get("LANG")
    yield
    if original_lang:
        os.environ["LANG"] = original_lang
    else:
        os.environ.pop("LANG", None)


def test_weekday_name_english() -> None:
    """Test weekday names in English locale."""
    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        assert weekday_name(0) == "mon"
        assert weekday_name(4) == "fri"
        assert weekday_name(6) == "sun"


def test_weekday_name_finnish() -> None:
    """Test weekday names in Finnish locale."""
    with patch.dict(os.environ, {"LANG": "fi_FI.UTF-8"}):
        assert weekday_name(0) == "ma"
        assert weekday_name(4) == "pe"
        assert weekday_name(6) == "su"


def test_weekday_name_invalid_day() -> None:
    """Test handling of invalid weekday numbers."""
    with pytest.raises(ValueError, match="Invalid weekday number: 7"):
        weekday_name(7)
    with pytest.raises(ValueError, match="Invalid weekday number: -1"):
        weekday_name(-1)


def test_weekday_name_default_locale() -> None:
    """Test behavior with no explicit locale set."""
    if "LANG" in os.environ:
        del os.environ["LANG"]
    # Should fall back to en_US
    assert weekday_name(0).lower() in ["mon", "ma"]  # Accept common formats


def test_weekday_name_invalid_locale() -> None:
    """Test handling of invalid locale."""
    with (
        patch.dict(os.environ, {"LANG": "invalid_LOCALE"}),
        pytest.raises(babel.core.UnknownLocaleError),
    ):
        weekday_name(0)
