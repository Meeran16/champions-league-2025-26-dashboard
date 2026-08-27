from __future__ import annotations

from typing import Any
import pandas as pd

from src.ai.models import EvidenceResult
from src.analytics import display_score, player_signal_columns


FULL_SCOPE = "Complete competition: 189 matches across league phase and knockout stages."
LEAGUE_SCOPE = "League phase: 144 matches. Detailed possession and shooting statistics are available only for this phase."
PLAYER_SCOPE = "Player LPI: locally preserved published leaderboard candidates. This is a project-defined index, not an official UEFA award."


def _records(df: pd.DataFrame, columns: list[str] | None = None, limit: int = 12) -> list[dict[str, Any]]:
    frame = df.copy()
    if columns is not None:
        frame = frame[[c for c in columns if c in frame.columns]]
    frame = frame.head(limit)
    frame = frame.where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


def _fmt(value: Any, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def tournament_summary(question: str, data: dict[str, pd.DataFrame]) -> EvidenceResult:
    s = data["summary"].iloc[0]
    return EvidenceResult(
        question=question,
        intent="tournament_summary",
        title="Tournament summary",
        answer=(
            f"The 2025/26 competition contains {int(s['teams'])} teams, "
            f"{int(s['matches'])} matches and {int(s['goals'])} goals, "
            f"an average of {float(s['goals_per_match']):.2f} goals per match."
        ),
        facts=[
            {"label": "Teams", "value": str(int(s["teams"]))},
            {"label": "Matches", "value": str(int(s["matches"]))},
            {"label": "Goals", "value": str(int(s["goals"]))},
            {"label": "Goals / match", "value": f"{float(s['goals_per_match']):.2f}"},
        ],
        scope=FULL_SCOPE,
        followups=[
            "Who finished first in the league phase?",
            "Which stage had the highest scoring rate?",
            "Which team scored the most?",
        ],
    )


def league_table(question: str, data: dict[str, pd.DataFrame], limit: int = 10) -> EvidenceResult:
    table = data["league_table"].sort_values("position").copy()
    leader = table.iloc[0]
    return EvidenceResult(
        question=question,
        intent="league_table",
        title="League-phase standings",
        answer=(
            f"{leader['team_name']} finished first in the reconstructed league-phase table "
            f"with {int(leader['points'])} points and a goal difference of "
            f"{int(leader['goal_difference']):+d}."
        ),
        facts=[
            {"label": "Leader", "value": str(leader["team_name"])},
            {"label": "Points", "value": str(int(leader["points"]))},
            {"label": "Wins", "value": str(int(leader["wins"]))},
            {"label": "Goal difference", "value": f"{int(leader['goal_difference']):+d}"},
        ],
        table=_records(
            table,
            ["position", "team_name", "played", "wins", "draws", "losses", "goal_difference", "points"],
            limit,
        ),
        scope=LEAGUE_SCOPE,
        followups=[
            f"Why did {leader['team_name']} perform well?",
            "Compare Arsenal and Bayern Munich.",
            "Who had the best away record?",
        ],
        chart={
            "type": "bar",
            "x": "points",
            "y": "team_name",
            "title": "League-phase points",
            "limit": min(limit, 10),
        },
    )


def stage_scoring(question: str, data: dict[str, pd.DataFrame]) -> EvidenceResult:
    stage = data["stage_summary"].sort_values(
        ["goals_per_match", "goals"], ascending=[False, False]
    ).copy()
    top = stage.iloc[0]
    return EvidenceResult(
        question=question,
        intent="stage_scoring",
        title="Scoring rate by stage",
        answer=(
            f"{top['stage']} had the highest recorded scoring rate at "
            f"{float(top['goals_per_match']):.2f} goals per match."
        ),
        facts=[
            {"label": "Highest-scoring stage", "value": str(top["stage"])},
            {"label": "Goals / match", "value": f"{float(top['goals_per_match']):.2f}"},
            {"label": "Matches", "value": str(int(top["matches"]))},
            {"label": "Goals", "value": str(int(top["goals"]))},
        ],
        table=_records(stage, ["stage", "matches", "goals", "goals_per_match"], 10),
        scope=FULL_SCOPE,
        caveats=[
            "Stage sample sizes differ substantially, so a high goals-per-match rate in a small knockout stage should not be treated as equally stable as the 144-match league phase."
        ],
        followups=[
            "Which team scored the most?",
            "Show the league-phase table.",
            "What happened in the final?",
        ],
        chart={"type": "bar", "x": "stage", "y": "goals_per_match", "title": "Goals per match by stage"},
    )


def top_scoring_teams(question: str, data: dict[str, pd.DataFrame], limit: int = 10) -> EvidenceResult:
    teams = data["team_summary"].sort_values(
        ["goals_for", "goal_difference"], ascending=[False, False]
    ).copy()
    top = teams.iloc[0]
    return EvidenceResult(
        question=question,
        intent="top_scoring_teams",
        title="Top-scoring teams",
        answer=(
            f"{top['team_name']} scored the most goals across the complete competition "
            f"with {int(top['goals_for'])}."
        ),
        facts=[
            {"label": "Top scorer", "value": str(top["team_name"])},
            {"label": "Goals", "value": str(int(top["goals_for"]))},
            {"label": "Matches", "value": str(int(top["matches_played"]))},
            {"label": "Goals / match", "value": f"{float(top['goals_per_match']):.2f}"},
        ],
        table=_records(
            teams,
            ["team_name", "matches_played", "goals_for", "goals_against", "goal_difference", "goals_per_match"],
            limit,
        ),
        scope=FULL_SCOPE,
        followups=[
            f"Show {top['team_name']}'s profile.",
            "Which teams had high possession but weak results?",
            "Compare Arsenal and PSG.",
        ],
        chart={"type": "bar", "x": "goals_for", "y": "team_name", "title": "Goals scored", "limit": limit},
    )


def team_profile(question: str, data: dict[str, pd.DataFrame], team: str) -> EvidenceResult:
    summary = data["team_summary"]
    league = data["league_table"]
    row = summary.loc[summary["team_name"] == team]
    if row.empty:
        raise ValueError(f"Unknown team: {team}")
    row = row.iloc[0]
    lrow = league.loc[league["team_name"] == team]
    l = lrow.iloc[0] if not lrow.empty else None

    facts = [
        {"label": "Matches", "value": str(int(row["matches_played"]))},
        {"label": "Goals for", "value": str(int(row["goals_for"]))},
        {"label": "Goals against", "value": str(int(row["goals_against"]))},
        {"label": "Goal difference", "value": f"{int(row['goal_difference']):+d}"},
    ]
    if l is not None:
        facts.extend([
            {"label": "League position", "value": str(int(l["position"]))},
            {"label": "League points", "value": str(int(l["points"]))},
        ])
    if pd.notna(row.get("avg_league_possession")):
        facts.extend([
            {"label": "League possession", "value": f"{float(row['avg_league_possession']):.1f}%"},
            {"label": "League shots / match", "value": f"{float(row['avg_league_shots']):.1f}"},
        ])

    if l is not None:
        answer = (
            f"{team} finished {int(l['position'])} in the league phase with "
            f"{int(l['points'])} points. Across the complete competition, the team scored "
            f"{int(row['goals_for'])} and conceded {int(row['goals_against'])}."
        )
    else:
        answer = (
            f"Across the complete competition, {team} played {int(row['matches_played'])} matches, "
            f"scored {int(row['goals_for'])} and conceded {int(row['goals_against'])}."
        )

    return EvidenceResult(
        question=question,
        intent="team_profile",
        title=f"{team} profile",
        answer=answer,
        facts=facts,
        scope=f"{FULL_SCOPE} {LEAGUE_SCOPE}",
        followups=[
            f"Show {team}'s form.",
            f"Show {team}'s matches.",
            f"Compare {team} and Arsenal." if team != "Arsenal" else "Compare Arsenal and Bayern Munich.",
        ],
    )


def compare_teams(
    question: str,
    data: dict[str, pd.DataFrame],
    team_a: str,
    team_b: str,
) -> EvidenceResult:
    summary = data["team_summary"].set_index("team_name")
    league = data["league_table"].set_index("team_name")

    if team_a not in summary.index or team_b not in summary.index:
        raise ValueError("One or both teams are unavailable.")

    a, b = summary.loc[team_a], summary.loc[team_b]
    la = league.loc[team_a] if team_a in league.index else None
    lb = league.loc[team_b] if team_b in league.index else None

    if la is not None and lb is not None:
        if int(la["points"]) > int(lb["points"]):
            league_edge = f"{team_a} had the stronger league phase by points"
        elif int(lb["points"]) > int(la["points"]):
            league_edge = f"{team_b} had the stronger league phase by points"
        else:
            league_edge = "The teams were level on league-phase points"
        answer = (
            f"{league_edge}: {team_a} {int(la['points'])} points versus "
            f"{team_b} {int(lb['points'])}. Across the full competition, "
            f"{team_a} scored {int(a['goals_for'])} goals and {team_b} scored {int(b['goals_for'])}."
        )
    else:
        answer = (
            f"Across the complete competition, {team_a} scored {int(a['goals_for'])} goals "
            f"and {team_b} scored {int(b['goals_for'])}."
        )

    rows = []
    for team, s, l in [(team_a, a, la), (team_b, b, lb)]:
        rows.append({
            "team": team,
            "league_position": int(l["position"]) if l is not None else None,
            "league_points": int(l["points"]) if l is not None else None,
            "matches": int(s["matches_played"]),
            "goals_for": int(s["goals_for"]),
            "goals_against": int(s["goals_against"]),
            "goal_difference": int(s["goal_difference"]),
            "avg_league_possession": round(float(s["avg_league_possession"]), 2)
            if pd.notna(s["avg_league_possession"]) else None,
            "avg_league_shots": round(float(s["avg_league_shots"]), 2)
            if pd.notna(s["avg_league_shots"]) else None,
        })

    return EvidenceResult(
        question=question,
        intent="compare_teams",
        title=f"{team_a} vs {team_b}",
        answer=answer,
        facts=[
            {"label": f"{team_a} league points", "value": str(int(la["points"])) if la is not None else "—"},
            {"label": f"{team_b} league points", "value": str(int(lb["points"])) if lb is not None else "—"},
            {"label": f"{team_a} goals", "value": str(int(a["goals_for"]))},
            {"label": f"{team_b} goals", "value": str(int(b["goals_for"]))},
        ],
        table=rows,
        scope=f"{FULL_SCOPE} League points/possession use the league-phase scope.",
        caveats=[
            "Full-competition goal totals and league-phase possession/points have different scopes and are kept labelled separately."
        ],
        followups=[
            f"Show {team_a}'s form.",
            f"Show {team_b}'s form.",
            f"Which of {team_a} and {team_b} had better away performance?",
        ],
        chart={"type": "grouped_bar", "x": "team", "ys": ["goals_for", "goals_against"], "title": "Full-competition goals"},
    )


def team_form(question: str, data: dict[str, pd.DataFrame], team: str) -> EvidenceResult:
    form = data["rolling_form"]
    subset = form.loc[form["team_name"] == team].sort_values(["date", "match_id"]).copy()
    if subset.empty:
        raise ValueError(f"No league-phase form found for {team}.")

    latest = subset.iloc[-1]
    last5 = subset.tail(5)
    return EvidenceResult(
        question=question,
        intent="team_form",
        title=f"{team} league-phase form",
        answer=(
            f"{team}'s final five league-phase matches produced "
            f"{int(last5['points'].sum())} points. The rolling-five value at the end "
            f"of the league phase was {int(latest['rolling_5_points'])}."
        ),
        facts=[
            {"label": "Last 5 points", "value": str(int(last5["points"].sum()))},
            {"label": "Last 5 goals for", "value": str(int(last5["goals_for"].sum()))},
            {"label": "Last 5 goals against", "value": str(int(last5["goals_against"].sum()))},
            {"label": "Final rolling-5", "value": str(int(latest["rolling_5_points"]))},
        ],
        table=_records(
            subset.tail(8),
            ["date", "match_number", "goals_for", "goals_against", "points", "rolling_5_points"],
            8,
        ),
        scope=LEAGUE_SCOPE,
        followups=[
            f"Show {team}'s profile.",
            f"Show {team}'s matches.",
            "Which teams finished the league phase strongest?",
        ],
        chart={"type": "line", "x": "match_number", "y": "rolling_5_points", "title": f"{team} rolling form"},
    )


def team_match_history(question: str, data: dict[str, pd.DataFrame], team: str, limit: int = 12) -> EvidenceResult:
    matches = data["matches"]
    subset = matches[
        (matches["home_team"] == team) | (matches["away_team"] == team)
    ].sort_values(["date", "match_id"], ascending=[False, False]).copy()

    rows = []
    for _, row in subset.head(limit).iterrows():
        rows.append({
            "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
            "stage": row["stage"],
            "home_team": row["home_team"],
            "score": display_score(row),
            "away_team": row["away_team"],
            "winner": row["winner"],
        })

    return EvidenceResult(
        question=question,
        intent="team_match_history",
        title=f"{team} match history",
        answer=f"{team} played {len(subset)} matches in the complete competition dataset.",
        facts=[
            {"label": "Matches", "value": str(len(subset))},
            {"label": "Latest match", "value": rows[0]["date"] if rows else "—"},
        ],
        table=rows,
        scope=FULL_SCOPE,
        followups=[
            f"Show {team}'s profile.",
            f"Show {team}'s form.",
            "What happened in the final?",
        ],
    )


def home_away_leaders(
    question: str,
    data: dict[str, pd.DataFrame],
    venue_role: str,
    limit: int = 10,
) -> EvidenceResult:
    venue = data["home_away"]
    subset = venue.loc[venue["venue_role"] == venue_role].sort_values(
        ["points_per_match", "points", "goals_for"],
        ascending=[False, False, False],
    ).copy()
    top = subset.iloc[0]
    adjective = venue_role.lower()
    return EvidenceResult(
        question=question,
        intent=f"best_{adjective}_teams",
        title=f"Best {adjective} league-phase records",
        answer=(
            f"{top['team_name']} had the strongest {adjective} points-per-match figure "
            f"at {float(top['points_per_match']):.2f}."
        ),
        facts=[
            {"label": "Leader", "value": str(top["team_name"])},
            {"label": "Points / match", "value": f"{float(top['points_per_match']):.2f}"},
            {"label": "Points", "value": str(int(top["points"]))},
            {"label": "Goals for", "value": str(int(top["goals_for"]))},
        ],
        table=_records(
            subset,
            ["team_name", "played", "points", "goals_for", "goals_against", "points_per_match"],
            limit,
        ),
        scope=LEAGUE_SCOPE,
        followups=[
            f"Show {top['team_name']}'s profile.",
            "Who finished first in the league phase?",
            "Which teams had high possession but weak results?",
        ],
        chart={"type": "bar", "x": "points_per_match", "y": "team_name", "title": f"{venue_role} points per match", "limit": limit},
    )


def high_possession_weak_results(question: str, data: dict[str, pd.DataFrame]) -> EvidenceResult:
    teams = data["team_summary"][
        ["team_name", "avg_league_possession", "avg_league_shots"]
    ].merge(
        data["league_table"][["team_name", "position", "points", "points_per_match"]],
        on="team_name",
        how="inner",
    )
    pos_median = teams["avg_league_possession"].median()
    points_median = teams["points"].median()
    candidates = teams[
        (teams["avg_league_possession"] >= pos_median)
        & (teams["points"] < points_median)
    ].sort_values(["avg_league_possession", "points"], ascending=[False, True])

    if candidates.empty:
        answer = "No teams meet the project's threshold for high possession with below-median league-phase points."
    else:
        top = candidates.iloc[0]
        answer = (
            f"Using a transparent median-based rule, {top['team_name']} is the clearest example: "
            f"{float(top['avg_league_possession']):.1f}% average possession with "
            f"{int(top['points'])} league-phase points."
        )

    return EvidenceResult(
        question=question,
        intent="high_possession_weak_results",
        title="High possession, weaker results",
        answer=answer,
        facts=[
            {"label": "Possession threshold", "value": f"≥ {pos_median:.1f}%"},
            {"label": "Points threshold", "value": f"< {points_median:.1f}"},
            {"label": "Teams identified", "value": str(len(candidates))},
        ],
        table=_records(
            candidates,
            ["team_name", "position", "points", "points_per_match", "avg_league_possession", "avg_league_shots"],
            12,
        ),
        scope=LEAGUE_SCOPE,
        caveats=[
            "This is an exploratory rule, not a causal model: 'high possession' means at or above the competition median and 'weaker results' means below-median league-phase points."
        ],
        followups=[
            "Which teams were efficient despite lower possession?",
            "Who had the best away record?",
            "Show the league-phase table.",
        ],
        chart={"type": "scatter", "x": "avg_league_possession", "y": "points", "text": "team_name", "title": "Possession vs points"},
    )


def efficient_low_possession(question: str, data: dict[str, pd.DataFrame]) -> EvidenceResult:
    teams = data["team_summary"][["team_name", "avg_league_possession"]].merge(
        data["league_table"][["team_name", "position", "points", "points_per_match", "goal_difference"]],
        on="team_name",
        how="inner",
    )
    pos_median = teams["avg_league_possession"].median()
    points_median = teams["points"].median()
    candidates = teams[
        (teams["avg_league_possession"] < pos_median)
        & (teams["points"] >= points_median)
    ].sort_values(["points", "goal_difference"], ascending=[False, False])

    if candidates.empty:
        answer = "No teams meet the project's lower-possession / above-median-points threshold."
    else:
        top = candidates.iloc[0]
        answer = (
            f"{top['team_name']} is the strongest example under the project's rule: "
            f"{float(top['avg_league_possession']):.1f}% possession and {int(top['points'])} points."
        )

    return EvidenceResult(
        question=question,
        intent="efficient_low_possession",
        title="Strong results with lower possession",
        answer=answer,
        facts=[
            {"label": "Possession threshold", "value": f"< {pos_median:.1f}%"},
            {"label": "Points threshold", "value": f"≥ {points_median:.1f}"},
            {"label": "Teams identified", "value": str(len(candidates))},
        ],
        table=_records(
            candidates,
            ["team_name", "position", "points", "goal_difference", "avg_league_possession"],
            12,
        ),
        scope=LEAGUE_SCOPE,
        caveats=[
            "This is a descriptive threshold-based comparison and does not establish that lower possession caused stronger results."
        ],
        followups=[
            "Which teams had high possession but weak results?",
            "Compare Arsenal and Bayern Munich.",
            "Who had the best away record?",
        ],
        chart={"type": "scatter", "x": "avg_league_possession", "y": "points", "text": "team_name", "title": "Possession vs points"},
    )


def top_players(
    question: str,
    data: dict[str, pd.DataFrame],
    position: str,
    limit: int = 5,
) -> EvidenceResult:
    players = data["player_rankings"]
    group = players.loc[players["position_group"] == position].sort_values("rank").copy()
    if group.empty:
        raise ValueError(f"No LPI candidates for position: {position}")
    top = group.iloc[0]
    return EvidenceResult(
        question=question,
        intent="top_players",
        title=f"Top {position.lower()} LPI rankings",
        answer=(
            f"{top['player']} ranks first among the captured {position.lower()} leaderboard "
            f"candidates with an LPI score of {float(top['performance_score']):.2f}."
        ),
        facts=[
            {"label": "Leader", "value": str(top["player"])},
            {"label": "Club", "value": str(top["squad"])},
            {"label": "LPI", "value": f"{float(top['performance_score']):.2f}"},
            {"label": "Candidate pool", "value": str(len(group))},
        ],
        table=_records(group, ["rank", "player", "squad", "performance_score"], limit),
        scope=PLAYER_SCOPE,
        caveats=[
            "The candidate pool is bounded by the preserved published leaderboards and is not a complete all-player event-data ranking."
        ],
        followups=[
            f"Why does {group.iloc[0]['player']} rank above {group.iloc[1]['player']}?" if len(group) > 1 else "",
            "Who is the highest-ranked goalkeeper?",
            "Who is the highest-ranked midfielder?",
        ],
        chart={"type": "bar", "x": "performance_score", "y": "player", "title": f"{position} LPI", "limit": limit},
    )


def player_profile(question: str, data: dict[str, pd.DataFrame], player: str) -> EvidenceResult:
    players = data["player_rankings"]
    row = players.loc[players["player"] == player]
    if row.empty:
        raise ValueError(f"Unknown player: {player}")
    row = row.iloc[0]
    signals = [
        c for c in player_signal_columns(players)
        if c in row.index and pd.notna(row[c])
    ]

    table = [
        {"signal": c.replace("points_", "").replace("_", " ").title(), "leaderboard_points": float(row[c])}
        for c in signals
    ]
    return EvidenceResult(
        question=question,
        intent="player_profile",
        title=f"{player} LPI profile",
        answer=(
            f"{player} ranks {int(row['rank'])} in the {row['position_group']} candidate pool "
            f"with an LPI score of {float(row['performance_score']):.2f}."
        ),
        facts=[
            {"label": "Position group", "value": str(row["position_group"])},
            {"label": "Club", "value": str(row["squad"])},
            {"label": "Rank", "value": str(int(row["rank"]))},
            {"label": "LPI", "value": f"{float(row['performance_score']):.2f}"},
        ],
        table=table,
        scope=PLAYER_SCOPE,
        followups=[
            f"Who are the top {str(row['position_group']).lower()}s?",
            "Compare Courtois and Raya." if row["position_group"] == "Goalkeeper" else "",
        ],
        chart={"type": "bar", "x": "signal", "y": "leaderboard_points", "title": f"{player} source signals"},
    )


def compare_players(
    question: str,
    data: dict[str, pd.DataFrame],
    player_a: str,
    player_b: str,
) -> EvidenceResult:
    players = data["player_rankings"]
    rows = players.loc[players["player"].isin([player_a, player_b])].copy()
    if len(rows) != 2:
        raise ValueError("One or both players are unavailable.")

    a = rows.loc[rows["player"] == player_a].iloc[0]
    b = rows.loc[rows["player"] == player_b].iloc[0]
    if a["position_group"] != b["position_group"]:
        return EvidenceResult(
            question=question,
            intent="compare_players",
            title=f"{player_a} vs {player_b}",
            answer=(
                "A direct LPI comparison is not appropriate because the two players are "
                "in different position groups with different source signals and weights."
            ),
            facts=[
                {"label": player_a, "value": str(a["position_group"])},
                {"label": player_b, "value": str(b["position_group"])},
            ],
            scope=PLAYER_SCOPE,
            caveats=["Cross-position LPI scores are intentionally not treated as directly comparable."],
            followups=[
                f"Show {player_a}'s LPI profile.",
                f"Show {player_b}'s LPI profile.",
            ],
        )

    signals = sorted(set(player_signal_columns(rows)))
    table = []
    for _, row in rows.iterrows():
        record: dict[str, Any] = {
            "player": row["player"],
            "club": row["squad"],
            "rank": int(row["rank"]),
            "performance_score": round(float(row["performance_score"]), 2),
        }
        for signal in signals:
            if signal in row.index and pd.notna(row[signal]):
                record[signal] = round(float(row[signal]), 2)
        table.append(record)

    winner = a if float(a["performance_score"]) >= float(b["performance_score"]) else b
    loser = b if winner["player"] == a["player"] else a
    return EvidenceResult(
        question=question,
        intent="compare_players",
        title=f"{player_a} vs {player_b}",
        answer=(
            f"{winner['player']} has the higher {winner['position_group']} LPI: "
            f"{float(winner['performance_score']):.2f} versus "
            f"{float(loser['performance_score']):.2f}. The difference comes from the "
            "position-specific preserved leaderboard signals shown below."
        ),
        facts=[
            {"label": player_a, "value": f"{float(a['performance_score']):.2f} LPI"},
            {"label": player_b, "value": f"{float(b['performance_score']):.2f} LPI"},
            {"label": "Position", "value": str(a["position_group"])},
        ],
        table=table,
        scope=PLAYER_SCOPE,
        caveats=[
            "A missing source-leaderboard signal means the player was outside that preserved top-six list, not that the real-world statistic was zero."
        ],
        followups=[
            f"Show {player_a}'s LPI profile.",
            f"Show {player_b}'s LPI profile.",
            f"Who are the top {str(a['position_group']).lower()}s?",
        ],
        chart={"type": "grouped_bar", "x": "player", "ys": signals, "title": "LPI source signals"},
    )


def final_match(question: str, data: dict[str, pd.DataFrame]) -> EvidenceResult:
    matches = data["matches"]
    final = matches.loc[matches["stage"] == "Final"].sort_values("date")
    if final.empty:
        raise ValueError("Final match not found.")
    row = final.iloc[-1]
    score = display_score(row)
    answer = f"The final finished {row['home_team']} {score} {row['away_team']}."
    if int(row.get("penalty_shootout", 0) or 0) == 1:
        answer += f" {row['winner']} advanced/won via the separate penalty shootout result."

    return EvidenceResult(
        question=question,
        intent="final_match",
        title="2025/26 final",
        answer=answer,
        facts=[
            {"label": "Home", "value": str(row["home_team"])},
            {"label": "Score", "value": score},
            {"label": "Away", "value": str(row["away_team"])},
            {"label": "Winner", "value": str(row["winner"])},
        ],
        table=[{
            "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
            "home_team": row["home_team"],
            "football_score": f"{int(row['home_goals'])}-{int(row['away_goals'])}",
            "away_team": row["away_team"],
            "extra_time": bool(row["extra_time"]),
            "penalty_shootout": bool(row["penalty_shootout"]),
            "penalty_score": (
                f"{int(row['penalty_home'])}-{int(row['penalty_away'])}"
                if pd.notna(row["penalty_home"]) and pd.notna(row["penalty_away"])
                else None
            ),
            "winner": row["winner"],
        }],
        scope=FULL_SCOPE,
        caveats=[
            "The football score and penalty-shootout score are stored separately; a shootout is not rewritten as a normal match score."
        ],
        followups=[
            f"Show {row['home_team']}'s profile.",
            f"Show {row['away_team']}'s profile.",
            "Which stage had the highest scoring rate?",
        ],
    )
