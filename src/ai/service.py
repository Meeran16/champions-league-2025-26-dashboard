from __future__ import annotations

import pandas as pd

from src.ai.models import EvidenceResult
from src.ai.router import route_question
from src.ai import tools


SUPPORTED_EXAMPLES = [
    "Who finished first in the league phase?",
    "Which team scored the most?",
    "Compare Arsenal and Bayern Munich.",
    "Show PSG's form.",
    "Who had the best away record?",
    "Which teams had high possession but weak results?",
    "Which teams were efficient despite lower possession?",
    "Who is the highest-ranked forward?",
    "Why does Kylian Mbappe rank above Harry Kane?",
    "Compare Thibaut Courtois and David Raya.",
    "What happened in the final?",
]


def analyze_question(
    question: str,
    data: dict[str, pd.DataFrame],
) -> EvidenceResult:
    route = route_question(question, data)
    intent = route["intent"]

    if intent == "tournament_summary":
        return tools.tournament_summary(question, data)
    if intent == "league_table":
        return tools.league_table(question, data)
    if intent == "stage_scoring":
        return tools.stage_scoring(question, data)
    if intent == "top_scoring_teams":
        return tools.top_scoring_teams(question, data)
    if intent == "team_profile":
        return tools.team_profile(question, data, str(route["team"]))
    if intent == "compare_teams":
        teams = route["teams"]
        return tools.compare_teams(question, data, str(teams[0]), str(teams[1]))
    if intent == "team_form":
        return tools.team_form(question, data, str(route["team"]))
    if intent == "team_match_history":
        return tools.team_match_history(question, data, str(route["team"]))
    if intent == "best_away_teams":
        return tools.home_away_leaders(question, data, "Away")
    if intent == "best_home_teams":
        return tools.home_away_leaders(question, data, "Home")
    if intent == "high_possession_weak_results":
        return tools.high_possession_weak_results(question, data)
    if intent == "efficient_low_possession":
        return tools.efficient_low_possession(question, data)
    if intent == "top_players":
        return tools.top_players(question, data, str(route["position"]))
    if intent == "player_profile":
        return tools.player_profile(question, data, str(route["player"]))
    if intent == "compare_players":
        players = route["players"]
        return tools.compare_players(question, data, str(players[0]), str(players[1]))
    if intent == "final_match":
        return tools.final_match(question, data)

    return EvidenceResult(
        question=question,
        intent="unsupported",
        title="Question not yet supported",
        answer=(
            "The grounding layer could not map this question to an approved analytics function. "
            "No statistics were guessed."
        ),
        facts=[],
        scope="No analytical result generated.",
        caveats=[
            "This first version intentionally prefers a safe unsupported response over arbitrary SQL or invented statistics."
        ],
        followups=SUPPORTED_EXAMPLES[:5],
    )
