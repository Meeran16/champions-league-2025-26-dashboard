from __future__ import annotations

import re
import pandas as pd

from src.ai.entities import normalize, resolve_players, resolve_teams


POSITION_KEYWORDS = {
    "forward": "Forward",
    "forwards": "Forward",
    "striker": "Forward",
    "strikers": "Forward",
    "midfielder": "Midfielder",
    "midfielders": "Midfielder",
    "midfield": "Midfielder",
    "defender": "Defender",
    "defenders": "Defender",
    "defence": "Defender",
    "defense": "Defender",
    "goalkeeper": "Goalkeeper",
    "goalkeepers": "Goalkeeper",
    "keeper": "Goalkeeper",
    "keepers": "Goalkeeper",
}


def detect_position(question: str) -> str | None:
    q = normalize(question)
    for token, position in POSITION_KEYWORDS.items():
        if re.search(rf"(?<!\w){re.escape(token)}(?!\w)", q):
            return position
    return None


def route_question(
    question: str,
    data: dict[str, pd.DataFrame],
) -> dict[str, object]:
    q = normalize(question)
    team_names = data["team_summary"]["team_name"].dropna().astype(str).tolist()
    teams = resolve_teams(question, team_names)
    players = resolve_players(question, data["player_rankings"])
    position = detect_position(question)

    # Most specific comparisons first.
    if len(players) >= 2 and any(k in q for k in ["compare", "versus", " vs ", "rank above", "better"]):
        return {"intent": "compare_players", "players": players[:2]}

    if len(teams) >= 2 and any(k in q for k in ["compare", "versus", " vs ", "better"]):
        return {"intent": "compare_teams", "teams": teams[:2]}

    if "possession" in q and any(k in q for k in ["weak", "poor", "worse", "low points", "bad results"]):
        return {"intent": "high_possession_weak_results"}

    if "possession" in q and any(k in q for k in ["lower possession", "low possession", "despite lower", "efficient"]):
        return {"intent": "efficient_low_possession"}

    if "away" in q and any(k in q for k in ["best", "strongest", "top", "better"]):
        return {"intent": "best_away_teams"}

    if "home" in q and any(k in q for k in ["best", "strongest", "top", "better"]):
        return {"intent": "best_home_teams"}

    if "final" in q and any(k in q for k in ["what happened", "result", "score", "final", "won", "winner"]):
        return {"intent": "final_match"}

    if players:
        if len(players) >= 2 and ("why" in q or "above" in q):
            return {"intent": "compare_players", "players": players[:2]}
        if any(k in q for k in ["profile", "why", "rank", "score", "lpi", "show"]):
            return {"intent": "player_profile", "player": players[0]}

    if position and any(k in q for k in ["highest", "top", "best", "rank", "ranking"]):
        return {"intent": "top_players", "position": position}

    if teams:
        team = teams[0]
        if "form" in q or "last five" in q or "last 5" in q:
            return {"intent": "team_form", "team": team}
        if any(k in q for k in ["matches", "match history", "results", "fixtures"]):
            return {"intent": "team_match_history", "team": team}
        if any(k in q for k in ["profile", "why", "perform", "performance", "show", "stats", "statistics"]):
            return {"intent": "team_profile", "team": team}

    if any(k in q for k in ["scored the most", "most goals", "top scoring", "highest scoring team", "scoring teams"]):
        return {"intent": "top_scoring_teams"}

    if "stage" in q and any(k in q for k in ["highest scoring", "most goals per match", "scoring rate"]):
        return {"intent": "stage_scoring"}

    if any(k in q for k in ["finished first", "league table", "standings", "who was first", "who finished first"]):
        return {"intent": "league_table"}

    if any(k in q for k in ["tournament summary", "competition summary", "how many teams", "how many matches", "how many goals"]):
        return {"intent": "tournament_summary"}

    # Friendly defaults when one entity is clearly mentioned.
    if teams:
        return {"intent": "team_profile", "team": teams[0]}
    if players:
        return {"intent": "player_profile", "player": players[0]}

    return {"intent": "unsupported"}
