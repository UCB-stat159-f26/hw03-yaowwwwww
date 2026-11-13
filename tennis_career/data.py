"""Download matches, then clean them without executing JavaScript."""

import json
import re
import unicodedata
import warnings
from urllib.parse import parse_qs, quote, urlparse

import pandas as pd
import requests

_BASE_URL = "https://www.tennisabstract.com"
_DAYS_PER_YEAR = 365.25
_FIELDS = {0: "match_date", 1: "tournament", 2: "surface", 4: "result",
           8: "round", 11: "opponent", 16: "opponent_age_raw"}
_MATCH_KEY = ["match_date", "tournament", "round", "opponent"]


def _download(url, optional=False):
    """Allow a missing archive, but report connection and server failures."""
    try:
        response = requests.get(url, timeout=30)
        if optional and response.status_code == 404:
            return ""
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(f"Could not download Tennis Abstract data: {url}") from error
    return response.text


def _normalize_name(name):
    """Compare names without case, accents, spaces or punctuation."""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", name)


def _find_player(player_name):
    """Use the site's search to find one exact full-name match."""
    if not isinstance(player_name, str) or not _normalize_name(player_name):
        raise ValueError("Enter a full player name, such as 'Serena Williams'.")
    query = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", player_name)
    query = " ".join(query.split()).lower()
    source = _download(f"{_BASE_URL}/cgi-bin/search.cgi?q={quote(query)}")
    try:
        results = json.loads(source)
        matches = [item for item in results
                   if _normalize_name(item["name"]) == _normalize_name(player_name)]
    except (ValueError, TypeError, KeyError) as error:
        message = "Tennis Abstract returned invalid player-search data."
        raise ValueError(message) from error
    if len(matches) != 1:
        raise ValueError(f"Player not found or ambiguous: {player_name!r}.")
    return matches[0]


def _get_profile(player):
    """ATP classic pages are newer than the standalone ATP profile JS."""
    player_id = parse_qs(urlparse(player["url"]).query)["p"][0]
    slug = player_id.split("/")[-1].replace("-", "")
    if player["tour"] == "W":
        url = f"{_BASE_URL}/jsmatches/{quote(slug)}.js"
    else:
        url = f"{_BASE_URL}/cgi-bin/player-classic.cgi?p={quote(slug)}"
    return slug, url, _download(url)


def _read_matches(source, variable):
    """Read a JSON array assignment and reject malformed match rows."""
    pattern = r"\bvar\s+" + re.escape(variable) + r"\s*=\s*"
    match = re.search(pattern, source)
    if match is None:
        raise ValueError(f"Missing {variable} in Tennis Abstract data.")
    try:
        rows, _ = json.JSONDecoder().raw_decode(source[match.end():])
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid {variable} array.") from error
    if not isinstance(rows, list):
        raise ValueError(f"Expected a list of match rows in {variable}.")
    if any(not isinstance(row, list) or len(row) < 17 for row in rows):
        raise ValueError(f"Incomplete match row in {variable}.")
    return rows


def _read_birth_date(source):
    """Extract the player's birth date from profile metadata."""
    match = re.search(r"\bvar\s+dob\s*=\s*['\"]?(\d{8})", source)
    if match is None:
        raise ValueError("Player birth date is missing from the profile.")
    return pd.to_datetime(match[1], format="%Y%m%d", errors="raise")


def _prepare_matches(rows):
    """Select needed columns and remove overlap before calculating ages."""
    if not rows:
        raise ValueError("No career matches are available for this player.")
    selected = [[row[index] for index in _FIELDS] for row in rows]
    frame = pd.DataFrame(selected, columns=_FIELDS.values())
    frame["match_date"] = pd.to_datetime(
        frame["match_date"], format="%Y%m%d", errors="coerce")
    if frame["match_date"].isna().any() or not frame["result"].isin(["W", "L"]).all():
        raise ValueError("Match data has an invalid date or win/loss result.")
    return frame.drop_duplicates(_MATCH_KEY, keep="last").copy()


def _get_opponent_ages(values, dates):
    """WTA uses birth dates; ATP archives may already contain ages."""
    values = values.astype(str)
    is_birthday = values.str.fullmatch(r"\d{8}")
    ages = pd.to_numeric(values.where(~is_birthday), errors="coerce")
    birthdays = pd.to_datetime(
        values.where(is_birthday), format="%Y%m%d", errors="coerce")
    ages = ages.where(~is_birthday, (dates - birthdays).dt.days / _DAYS_PER_YEAR)
    return ages.where(ages.ge(0)).replace(float("inf"), float("nan"))


def _clean_matches(rows, birth_date, player_name):
    """Return a tidy table; keep unknown opponent ages as missing values."""
    frame = _prepare_matches(rows)
    if frame["match_date"].lt(birth_date).any():
        raise ValueError("A match date is earlier than the player's birth date.")
    frame["player_age"] = (frame["match_date"] - birth_date).dt.days / _DAYS_PER_YEAR
    frame["opponent_age"] = _get_opponent_ages(
        frame.pop("opponent_age_raw"), frame["match_date"])
    frame["age_difference"] = frame["player_age"] - frame["opponent_age"]
    frame["player_name"] = player_name
    if frame["opponent_age"].isna().any():
        message = "Some opponent ages are missing; those matches cannot be plotted."
        warnings.warn(message, UserWarning, stacklevel=2)
    return frame.sort_values("match_date", kind="stable").reset_index(drop=True)


def get_career_matches(player_name):
    """Return a player's singles matches as a pandas DataFrame.

    Accept full names with spaces or CamelCase. Invalid names raise ValueError;
    failed downloads raise RuntimeError. Unknown opponent ages are missing.
    """
    player = _find_player(player_name)
    slug, profile_url, profile = _get_profile(player)
    archive_url = f"{_BASE_URL}/jsmatches/{quote(slug)}Career.js"
    archive = _download(archive_url, optional=True)
    rows = _read_matches(archive, "morematchmx") if archive else []
    rows += _read_matches(profile, "matchmx")
    frame = _clean_matches(rows, _read_birth_date(profile), player["name"])
    frame.attrs["source_urls"] = [profile_url] + ([archive_url] if archive else [])
    frame.attrs["retrieved_at"] = pd.Timestamp.now(tz="UTC").isoformat()
    return frame
