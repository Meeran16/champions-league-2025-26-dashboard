\
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import display_score, result_for_team, team_matches
from src.components import hero, metric_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout
from src.ui import configure_page, data_missing_message

configure_page("Team Analysis")

if not data_ready():
    data_missing_message(missing_files())

data = load_all()
matches = data["matches"]
team_summary = data["team_summary"]
league = data["league_table"]
home_away = data["home_away"]
rolling = data["rolling_form"]

teams = sorted(team_summary["team_name"].tolist())
team = st.selectbox("Team", teams, help="Select a club to update the full analytical profile.")

summary = team_summary.loc[team_summary["team_name"] == team].iloc[0]
league_row = league.loc[league["team_name"] == team]
team_games = team_matches(matches, team)

hero(
    "Club profile",
    team,
    "Complete-competition results combined with league-phase form and detailed match statistics.",
    [
        f"{int(summary['matches_played'])} matches",
        f"{int(summary['goals_for'])} goals",
        "League-phase detailed stats",
    ],
)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    metric_card("Matches", int(summary["matches_played"]), "All stages")
with c2:
    metric_card("Goals for", int(summary["goals_for"]), f"{summary['goals_per_match']:.2f} / match")
with c3:
    metric_card("Goals against", int(summary["goals_against"]), "All stages")
with c4:
    metric_card("Goal difference", f"{int(summary['goal_difference']):+d}", "Complete competition")
with c5:
    metric_card(
        "League points",
        int(league_row.iloc[0]["points"]) if not league_row.empty else "—",
        "League phase",
    )

section_header("League-phase performance", "Home/away efficiency and rolling points profile.")
left, right = st.columns(2)

with left:
    venue = home_away.loc[home_away["team_name"] == team].copy()
    fig = px.bar(
        venue,
        x="venue_role",
        y="points_per_match",
        text="points_per_match",
        hover_data=["played", "points", "goals_for", "goals_against"],
        labels={"venue_role": "Venue", "points_per_match": "Points / match"},
    )
    chart_layout(fig, x_title=None, y_title="Points / match", height=360)
    st.plotly_chart(fig, width="stretch")

with right:
    form = rolling.loc[rolling["team_name"] == team].copy()
    fig = px.line(
        form,
        x="match_number",
        y="rolling_5_points",
        markers=True,
        hover_data=["date", "goals_for", "goals_against", "points"],
        labels={
            "match_number": "League-phase match",
            "rolling_5_points": "Rolling points",
        },
    )
    chart_layout(fig, x_title="League-phase match", y_title="Rolling points", height=360)
    st.plotly_chart(fig, width="stretch")

section_header(
    "Detailed league-phase profile",
    "Averages are calculated only from the 8 league-phase matches with the richer statistics source.",
)
m1, m2, m3 = st.columns(3)
with m1:
    metric_card(
        "Possession",
        "—" if pd.isna(summary["avg_league_possession"]) else f"{summary['avg_league_possession']:.1f}%",
        "Average league phase",
    )
with m2:
    metric_card(
        "Shots / match",
        "—" if pd.isna(summary["avg_league_shots"]) else f"{summary['avg_league_shots']:.1f}",
        "Average league phase",
    )
with m3:
    metric_card(
        "Shots on target",
        "—" if pd.isna(summary["avg_league_shots_on_target"]) else f"{summary['avg_league_shots_on_target']:.1f}",
        "Per league-phase match",
    )

section_header("Match history", "Chronological results with score context preserved.")
display = team_games.copy()
display["Result"] = display.apply(lambda row: result_for_team(row, team), axis=1)
display["Score"] = display.apply(display_score, axis=1)
display["Opponent"] = display.apply(
    lambda row: row["away_team"] if row["home_team"] == team else row["home_team"],
    axis=1,
)
display["Venue"] = display.apply(
    lambda row: "Home" if row["home_team"] == team else "Away",
    axis=1,
)
st.dataframe(
    display[["date", "stage", "Venue", "Opponent", "Score", "Result"]]
    .sort_values("date", ascending=False)
    .rename(columns={"date": "Date", "stage": "Stage"}),
    hide_index=True,
    width="stretch",
    height=500,
)

scope_note(
    "Penalty shootouts are displayed separately from the football score. A drawn match "
    "is not rewritten as a normal-score win simply because one team advanced on penalties."
)
