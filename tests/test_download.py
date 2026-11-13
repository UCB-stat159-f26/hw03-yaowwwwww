"""Exercise the public retrieval API using mocked HTTP responses only."""

import json
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

from tennis_career import get_career_matches
from tennis_career.data import _download

_FIXTURES = Path(__file__).parent / "fixtures"


def _response(text, status=200):
    response = requests.Response()
    response.status_code = status
    response._content = text.encode()
    return response


def _player_responses(tour="W", archive=True):
    female = tour == "W"
    name = "Serena Williams" if female else "Rafael Nadal"
    filename = "female_player.js" if female else "male_player.js"
    dob = "19810926" if female else "19860603"
    source = (_FIXTURES / filename).read_text()
    player = {"name": name, "tour": tour,
              "url": "https://www.tennisabstract.com/?p=" + name.replace(" ", "")}
    profile = f"var dob={dob};\n" + source.replace("morematchmx", "matchmx")
    responses = [_response(json.dumps([player])), _response(profile)]
    responses.append(_response(source) if archive else _response("", 404))
    return responses


@pytest.mark.parametrize("name", ["serena williams", "Serena Williams",
                                 "SerenaWilliams"])
def test_name_variants_and_provenance(monkeypatch, name):
    download = Mock(side_effect=_player_responses())
    monkeypatch.setattr(requests, "get", download)
    frame = get_career_matches(name)
    assert len(frame) == 3  # Profile/archive overlap is removed.
    assert frame["player_name"].unique().tolist() == ["Serena Williams"]
    assert frame["match_date"].is_monotonic_increasing
    assert len(frame.attrs["source_urls"]) == 2
    assert pd.Timestamp(frame.attrs["retrieved_at"]).tzinfo is not None
    assert download.call_args_list[0].args[0].endswith("q=serena%20williams")
    assert all(call.kwargs["timeout"] == 30 for call in download.call_args_list)


def test_atp_uses_classic_profile_and_handles_missing_archive(monkeypatch):
    download = Mock(side_effect=_player_responses(tour="M", archive=False))
    monkeypatch.setattr(requests, "get", download)
    frame = get_career_matches("Rafael Nadal")
    assert len(frame) == 3
    assert frame.iloc[0]["opponent_age"] == pytest.approx(22.264202601)
    assert download.call_args_list[1].args[0].endswith(
        "/cgi-bin/player-classic.cgi?p=RafaelNadal")
    assert len(frame.attrs["source_urls"]) == 1


@pytest.mark.parametrize("name", [None, "", "123"])
def test_invalid_name_never_downloads(name):
    with pytest.raises(ValueError, match="full player name"):
        get_career_matches(name)


def test_unknown_player(monkeypatch):
    monkeypatch.setattr(requests, "get", Mock(return_value=_response("[]")))
    with pytest.raises(ValueError, match="Player not found.*GastonSanchez"):
        get_career_matches("GastonSanchez")


def test_invalid_search_response(monkeypatch):
    monkeypatch.setattr(requests, "get", Mock(return_value=_response("<html>")))
    with pytest.raises(ValueError, match="invalid player-search"):
        get_career_matches("Serena Williams")


@pytest.mark.parametrize("status,optional", [(404, False), (500, True)])
def test_http_errors_are_not_silently_ignored(monkeypatch, status, optional):
    monkeypatch.setattr(requests, "get", Mock(return_value=_response("", status)))
    with pytest.raises(RuntimeError, match="Could not download"):
        _download("https://example.invalid/data", optional=optional)


def test_connection_timeout(monkeypatch):
    monkeypatch.setattr(requests, "get", Mock(side_effect=requests.Timeout))
    with pytest.raises(RuntimeError, match="Could not download"):
        get_career_matches("Serena Williams")
