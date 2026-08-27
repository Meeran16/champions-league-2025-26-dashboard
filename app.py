\
from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.components import hero, insight_card, metric_card, nav_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout
from src.ui import configure_page, data_missing_message

configure_page("Home")

if not data_ready():
    data_missing_message(missing_files())

data = load_all()
summary = data["summary"].iloc[0]
league = data["league_table"]
stage = data["stage_summary"]
teams = data["team_summary"]

hero(
    "UEFA Champions League 2025/26",
    "Competition Analytics Command Center",
    "A validated SQL + Python analytics product for tournament, team, match and player exploration.",
    [
        f"{int(summary['teams'])} teams",
        f"{int(summary['matches'])} matches",
        f"{int(summary['league_phase_matches'])} detailed league-phase matches",
        "SQLite → Streamlit",
    ],
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Teams", int(summary["teams"]), "Complete competition")
with c2:
    metric_card("Matches", int(summary["matches"]), "League + knockout")
with c3:
    metric_card("Goals", int(summary["goals"]), "Complete competition")
with c4:
    metric_card("Goals / match", f"{summary['goals_per_match']:.2f}", "Tournament average")

section_header(
    "Tournament pulse",
    "A compact view of stage volume and the strongest league-phase teams.",
)

left, right = st.columns([1.05, 0.95])

with left:
    fig = px.bar(
        stage,
        x="stage",
        y="matches",
        text="matches",
        hover_data=["goals", "goals_per_match"],
        labels={"stage": "Stage", "matches": "Matches"},
    )
    chart_layout(fig, x_title=None, y_title="Matches", height=360)
    st.plotly_chart(fig, width="stretch")

with right:
    top5 = league.head(5)[
        ["position", "team_name", "played", "wins", "goal_difference", "points"]
    ].rename(
        columns={
            "position": "Pos",
            "team_name": "Team",
            "played": "P",
            "wins": "W",
            "goal_difference": "GD",
            "points": "Pts",
        }
    )
    st.dataframe(top5, hide_index=True, width="stretch", height=360)

section_header(
    "What the data says",
    "Generated directly from the validated analytical outputs.",
)
i1, i2, i3 = st.columns(3)

leader = league.iloc[0]
top_scorer_team = teams.sort_values(
    ["goals_for", "goal_difference"], ascending=[False, False]
).iloc[0]
highest_stage = stage.sort_values(["goals_per_match", "goals"], ascending=False).iloc[0]

with i1:
    insight_card(
        f"{leader['team_name']} led the league phase",
        f"{int(leader['points'])} points with a goal difference of {int(leader['goal_difference']):+d}.",
        "League phase",
    )
with i2:
    insight_card(
        f"{top_scorer_team['team_name']} led total scoring",
        f"{int(top_scorer_team['goals_for'])} goals across {int(top_scorer_team['matches_played'])} matches.",
        "Attack",
    )
with i3:
    insight_card(
        f"{highest_stage['stage']} had the highest scoring rate",
        f"{highest_stage['goals_per_match']:.2f} goals per match.",
        "Stage profile",
    )

section_header(
    "Explore",
    "Each page answers a different analytical question while preserving the same source boundaries.",
)

n1, n2, n3 = st.columns(3)
with n1:
    nav_card(
        "Tournament Overview",
        "Standings, stage structure, outcomes and scoring.",
        "pages/1_Tournament_Overview.py",
    )
with n2:
    nav_card(
        "Team Analysis",
        "Club profile, rolling form and league-phase detail.",
        "pages/2_Team_Analysis.py",
    )
with n3:
    nav_card(
        "Player Rankings",
        "Position-specific LPI rankings and source signals.",
        "pages/3_Player_Rankings.py",
    )

n4, n5 = st.columns(2)
with n4:
    nav_card(
        "Player Comparison",
        "Compare two players within the same LPI position group.",
        "pages/4_Player_Comparison.py",
    )
with n5:
    nav_card(
        "Match Explorer",
        "Filter the full tournament and inspect match-level detail.",
        "pages/5_Match_Explorer.py",
    )

section_header("Data trust")
scope_note(
    "Complete results cover 189 matches. Possession and shooting detail covers the "
    "144-match league phase only. Player LPI results use preserved leaderboard snapshots. "
    "The dashboard does not infer missing knockout statistics."
)
