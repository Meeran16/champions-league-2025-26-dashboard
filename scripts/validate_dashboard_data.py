\
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "derived"

REQUIRED = [
    "tournament_summary.csv",
    "matches.csv",
    "league_table.csv",
    "team_summary.csv",
    "home_away_summary.csv",
    "rolling_form.csv",
    "stage_summary.csv",
    "player_rankings.csv",
]

def main() -> None:
    missing = [name for name in REQUIRED if not (DATA / name).exists()]
    if missing:
        raise RuntimeError("Missing dashboard files: " + ", ".join(missing))

    summary = pd.read_csv(DATA / "tournament_summary.csv")
    matches = pd.read_csv(DATA / "matches.csv")
    league = pd.read_csv(DATA / "league_table.csv")
    players = pd.read_csv(DATA / "player_rankings.csv")

    row = summary.iloc[0]
    assert int(row["teams"]) == 36, f"Expected 36 teams, got {row['teams']}"
    assert int(row["matches"]) == 189, f"Expected 189 matches, got {row['matches']}"
    assert int(row["league_phase_matches"]) == 144, (
        f"Expected 144 league-phase matches, got {row['league_phase_matches']}"
    )
    assert len(matches) == 189, f"matches.csv has {len(matches)} rows"
    assert len(league) == 36, f"league_table.csv has {len(league)} rows"
    assert league["position"].nunique() == 36, "League positions are not unique"

    expected_positions = {"Forward", "Midfielder", "Defender", "Goalkeeper"}
    found_positions = set(players["position_group"].dropna().unique())
    missing_positions = expected_positions - found_positions
    assert not missing_positions, f"Missing player positions: {sorted(missing_positions)}"

    for position in expected_positions:
        group = players[players["position_group"] == position]
        assert (group["rank"] == 1).any(), f"No rank-1 player for {position}"
        assert group["performance_score"].between(0, 100).all(), (
            f"Player score outside 0-100 for {position}"
        )

    print("Dashboard data validation passed:")
    print(f"  teams: {int(row['teams'])}")
    print(f"  matches: {int(row['matches'])}")
    print(f"  league-phase matches: {int(row['league_phase_matches'])}")
    print(f"  league-table rows: {len(league)}")
    print(f"  player ranking rows: {len(players)}")
    print("  player positions: Forward, Midfielder, Defender, Goalkeeper")

if __name__ == "__main__":
    main()


