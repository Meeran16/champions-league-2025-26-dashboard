\
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.express as px
import streamlit as st

from src.components import hero, metric_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout
from src.ui import configure_page, data_missing_message

configure_page("Tournament Overview")

if not data_ready():
    data_missing_message(missing_files())

data = load_all()
summary = data["summary"].iloc[0]
matches = data["matches"]
stage = data["stage_summary"]
league = data["league_table"]
teams = data["team_summary"]

hero(
    "Competition view",
    "Tournament Overview",
    "Stage structure, match outcomes, league-phase standings and complete-competition scoring.",
    ["189 matches", "36 teams", "League + knockout"],
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Teams", int(summary["teams"]), "Tournament field")
with c2:
    metric_card("Matches", int(summary["matches"]), "Complete schedule")
with c3:
    metric_card("Goals", int(summary["goals"]), "All stages")
with c4:
    metric_card("Avg. goals", f"{summary['goals_per_match']:.2f}", "Per match")

section_header("Competition structure", "How the tournament volume and match outcomes are distributed.")
left, right = st.columns(2)

with left:
    fig = px.bar(
        stage,
        x="stage",
        y="matches",
        text="matches",
        hover_data=["goals", "goals_per_match"],
        labels={"stage": "Stage", "matches": "Matches"},
    )
    chart_layout(fig, x_title=None, y_title="Matches", height=370)
    st.plotly_chart(fig, width="stretch")

with right:
    outcome_map = {"H": "Home win", "D": "Draw", "A": "Away win"}
    outcome = (
        matches["match_outcome"]
        .map(outcome_map)
        .fillna(matches["match_outcome"])
        .value_counts()
        .rename_axis("outcome")
        .reset_index(name="matches")
    )
    fig = px.pie(outcome, names="outcome", values="matches", hole=0.54)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    chart_layout(fig, height=370)
    st.plotly_chart(fig, width="stretch")

section_header(
    "League-phase table",
    "Reconstructed from the 144 league-phase matches using standard three-point scoring.",
)
table = league[
    [
        "position", "team_name", "played", "wins", "draws", "losses",
        "goals_for", "goals_against", "goal_difference", "points",
    ]
].rename(
    columns={
        "position": "Pos",
        "team_name": "Team",
        "played": "P",
        "wins": "W",
        "draws": "D",
        "losses": "L",
        "goals_for": "GF",
        "goals_against": "GA",
        "goal_difference": "GD",
        "points": "Pts",
    }
)
st.dataframe(table, hide_index=True, width="stretch", height=560)

section_header("Scoring leaders", "Highest-scoring teams across the complete competition.")
plot_df = teams.nlargest(15, "goals_for").sort_values("goals_for")
fig = px.bar(
    plot_df,
    x="goals_for",
    y="team_name",
    orientation="h",
    hover_data=["matches_played", "goals_against", "goal_difference"],
    labels={"goals_for": "Goals", "team_name": "Team"},
)
chart_layout(fig, x_title="Goals", y_title=None, height=510)
st.plotly_chart(fig, width="stretch")

scope_note(
    "Tournament-level scoring uses all 189 matches. Detailed possession and shooting "
    "analysis remains restricted to the league phase because that is the scope of the richer source."
)
