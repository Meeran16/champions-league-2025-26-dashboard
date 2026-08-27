from __future__ import annotations

from difflib import SequenceMatcher
import re
import unicodedata
import pandas as pd


TEAM_ALIASES = {
    "psg": "Paris Saint-Germain",
    "paris": "Paris Saint-Germain",
    "paris saint germain": "Paris Saint-Germain",
    "bayern": "Bayern Munich",
    "bayern munich": "Bayern Munich",
    "real": "Real Madrid",
    "real madrid": "Real Madrid",
    "atleti": "Atletico Madrid",
    "atletico": "Atletico Madrid",
    "atletico madrid": "Atletico Madrid",
    "spurs": "Tottenham Hotspur",
    "tottenham": "Tottenham Hotspur",
    "newcastle": "Newcastle United",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_phrase(haystack: str, needle: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack) is not None


def resolve_teams(question: str, team_names: list[str]) -> list[str]:
    q = normalize(question)
    found: list[tuple[int, str]] = []

    # Exact canonical names first.
    for team in sorted(team_names, key=len, reverse=True):
        n = normalize(team)
        match = re.search(rf"(?<!\w){re.escape(n)}(?!\w)", q)
        if match:
            found.append((match.start(), team))

    # Aliases only if they do not duplicate a canonical match.
    for alias, canonical in TEAM_ALIASES.items():
        if canonical not in team_names:
            continue
        match = re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", q)
        if match and canonical not in [team for _, team in found]:
            found.append((match.start(), canonical))

    found.sort(key=lambda x: x[0])
    return [team for _, team in found]


def resolve_players(question: str, players: pd.DataFrame) -> list[str]:
    q = normalize(question)
    names = players["player"].dropna().astype(str).drop_duplicates().tolist()
    found: list[tuple[int, str]] = []

    for name in sorted(names, key=len, reverse=True):
        normalized = normalize(name)
        match = re.search(rf"(?<!\w){re.escape(normalized)}(?!\w)", q)
        if match:
            found.append((match.start(), name))
            continue

        parts = normalized.split()
        if len(parts) >= 2:
            surname = parts[-1]
            # Require a reasonably distinctive surname to avoid noisy matching.
            if len(surname) >= 5:
                match = re.search(rf"(?<!\w){re.escape(surname)}(?!\w)", q)
                if match:
                    found.append((match.start(), name))

    # De-duplicate while preserving mention order.
    result: list[str] = []
    for _, name in sorted(found, key=lambda x: x[0]):
        if name not in result:
            result.append(name)
    return result


def closest_team(token: str, team_names: list[str], threshold: float = 0.78) -> str | None:
    target = normalize(token)
    scored = [
        (SequenceMatcher(None, target, normalize(team)).ratio(), team)
        for team in team_names
    ]
    score, team = max(scored, default=(0.0, None))
    return team if score >= threshold else None
