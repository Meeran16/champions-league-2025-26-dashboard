\
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "derived"

REQUIRED_FILES = {
    "summary": "tournament_summary.csv",
    "matches": "matches.csv",
    "league_table": "league_table.csv",
    "team_summary": "team_summary.csv",
    "home_away": "home_away_summary.csv",
    "rolling_form": "rolling_form.csv",
    "stage_summary": "stage_summary.csv",
    "player_rankings": "player_rankings.csv",
}

def data_ready() -> bool:
    return all((DATA_DIR / f).exists() for f in REQUIRED_FILES.values())

def missing_files() -> list[str]:
    return [f for f in REQUIRED_FILES.values() if not (DATA_DIR / f).exists()]

def load_csv(name: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    if name not in REQUIRED_FILES:
        raise KeyError(f"Unknown dataset: {name}")
    path = DATA_DIR / REQUIRED_FILES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dashboard dataset: {path}. "
            "Run 'python scripts/export_dashboard_data.py' first."
        )
    return pd.read_csv(path, parse_dates=parse_dates)

def load_all() -> dict[str, pd.DataFrame]:
    return {
        "summary": load_csv("summary"),
        "matches": load_csv("matches", parse_dates=["date"]),
        "league_table": load_csv("league_table"),
        "team_summary": load_csv("team_summary"),
        "home_away": load_csv("home_away"),
        "rolling_form": load_csv("rolling_form", parse_dates=["date"]),
        "stage_summary": load_csv("stage_summary"),
        "player_rankings": load_csv("player_rankings"),
    }


