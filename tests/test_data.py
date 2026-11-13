"""Check cleaning against the small examples supplied in the assignment."""

from pathlib import Path

import pandas as pd
import pytest

from tennis_career.data import _read_birth_date, _clean_matches, _read_matches

_FIXTURES = Path(__file__).parent / "fixtures"


def _rows(filename):
    return _read_matches((_FIXTURES / filename).read_text(), "morematchmx")


def test_female_birthdays():
    rows = _rows("female_player.js")
    frame = _clean_matches(rows, pd.Timestamp("1981-09-26"), "Serena Williams")
    first = frame.iloc[0]
    assert len(frame) == 3
    assert first["opponent"] == "Anne Miller"
    assert first["result"] == "L"
    assert first["player_age"] == pytest.approx(5147 / 365.25)
    assert first["opponent_age"] == pytest.approx(6858 / 365.25)
    assert first["age_difference"] == pytest.approx(-1711 / 365.25)


def test_male_decimal_ages():
    rows = _rows("male_player.js")
    frame = _clean_matches(rows, pd.Timestamp("1986-06-03"), "Rafael Nadal")
    assert frame["result"].tolist() == ["L", "L", "W"]
    assert frame.iloc[0]["opponent_age"] == pytest.approx(22.264202601)
    assert frame.iloc[2]["age_difference"] == pytest.approx(
        frame.iloc[2]["player_age"] - 18.7597535934)


def test_overlap_keeps_profile_record_without_changing_input():
    rows = _rows("male_player.js")
    current = rows[0].copy()
    current[16] = "19790101"
    frame = _clean_matches(rows + [current], pd.Timestamp("1986-06-03"), "Nadal")
    assert len(frame) == 3
    assert frame.iloc[0]["opponent_age"] != 22.264202601
    assert rows[0][16] == "22.264202601"


@pytest.mark.parametrize("value", ["", "unknown", "-1", "inf", "29990101"])
def test_unknown_opponent_age_is_retained_and_warned(value):
    rows = _rows("female_player.js")
    rows[0][16] = value
    with pytest.warns(UserWarning, match="missing"):
        frame = _clean_matches(rows, pd.Timestamp("1981-09-26"), "Serena")
    assert len(frame) == 3
    assert pd.isna(frame.iloc[0]["age_difference"])


def test_match_before_birth_is_rejected():
    rows = _rows("female_player.js")
    with pytest.raises(ValueError, match="earlier than"):
        _clean_matches(rows, pd.Timestamp("2000-01-01"), "Serena")


@pytest.mark.parametrize("index,value", [(0, "bad_date"), (4, "unknown")])
def test_invalid_date_or_result(index, value):
    rows = _rows("female_player.js")
    rows[0][index] = value
    with pytest.raises(ValueError, match="invalid date or win/loss"):
        _clean_matches(rows, pd.Timestamp("1981-09-26"), "Serena")


@pytest.mark.parametrize("text", ["", "var morematchmx=nope;",
                                 "var morematchmx={};", "var morematchmx=[1];"])
def test_invalid_js(text):
    with pytest.raises(ValueError):
        _read_matches(text, "morematchmx")


def test_parser_does_not_execute_javascript():
    text = 'var morematchmx=[]; throw new Error("not executed");'
    assert _read_matches(text, "morematchmx") == []


def test_metadata_and_empty_matches():
    assert _read_birth_date("var dob=19810926;") == pd.Timestamp("1981-09-26")
    with pytest.raises(ValueError, match="birth date"):
        _read_birth_date("no metadata")
    with pytest.raises(ValueError, match="No career matches"):
        _clean_matches([], pd.Timestamp("1981-09-26"), "Serena")
