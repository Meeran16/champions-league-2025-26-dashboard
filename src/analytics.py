\
from __future__ import annotations
import pandas as pd

def team_matches(matches: pd.DataFrame, team: str) -> pd.DataFrame:
    mask = (matches["home_team"] == team) | (matches["away_team"] == team)
    return matches.loc[mask].sort_values(["date", "match_id"]).copy()

def result_for_team(row: pd.Series, team: str) -> str:
    is_home = row["home_team"] == team
    gf = row["home_goals"] if is_home else row["away_goals"]
    ga = row["away_goals"] if is_home else row["home_goals"]
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"

def display_score(row: pd.Series) -> str:
    score = f"{int(row['home_goals'])}–{int(row['away_goals'])}"
    if int(row.get("penalty_shootout", 0) or 0) == 1:
        ph, pa = row.get("penalty_home"), row.get("penalty_away")
        if pd.notna(ph) and pd.notna(pa):
            score += f" ({int(ph)}–{int(pa)} pens)"
    elif int(row.get("extra_time", 0) or 0) == 1:
        score += " AET"
    return score

def player_signal_columns(df: pd.DataFrame) -> list[str]:
    preferred = [c for c in df.columns if c.startswith("points_")]
    goalkeeper = [
        c for c in ["save_points", "cs_count_points", "cs_rate_points", "clean_sheet_signal"]
        if c in df.columns
    ]
    return preferred + goalkeeper

def clean_signal_name(column: str) -> str:
    if column.startswith("points_"):
        return column[len("points_"):].replace("_", " ").title()
    mapping = {
        "save_points": "Saves leaderboard",
        "cs_count_points": "Clean-sheet count",
        "cs_rate_points": "Clean-sheet rate",
        "clean_sheet_signal": "Clean-sheet signal",
    }
    return mapping.get(column, column.replace("_", " ").title())


