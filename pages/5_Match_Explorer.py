\
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import display_score
from src.components import hero, metric_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout
from src.ui import configure_page, data_missing_message

configure_page("Match Explorer")

if not data_ready():
    data_missing_message(missing_files())

matches = load_all()["matches"].copy()
matches["Score"] = matches.apply(display_score, axis=1)

hero(
    "Match intelligence",
    "Match Explorer",
    "Filter the complete competition and inspect detailed league-phase match statistics when available.",
    ["189 matches", "Stage filters", "Match-level detail"],
)

all_teams = sorted(set(matches["home_team"]).union(matches["away_team"]))
all_stages = matches["stage"].dropna().drop_duplicates().tolist()

f1, f2 = st.columns(2)
with f1:
    teams = st.multiselect("Team", all_teams, placeholder="All teams")
with f2:
    stages = st.multiselect("Stage", all_stages, placeholder="All stages")

filtered = matches.copy()
if teams:
    filtered = filtered[
        filtered["home_team"].isin(teams) | filtered["away_team"].isin(teams)
    ]
if stages:
    filtered = filtered[filtered["stage"].isin(stages)]

if filtered.empty:
    st.warning("No matches match the selected filters.")
    st.stop()

date_min = filtered["date"].min()
date_max = filtered["date"].max()
selected_dates = st.date_input(
    "Date range",
    value=(date_min.date(), date_max.date()),
    min_value=matches["date"].min().date(),
    max_value=matches["date"].max().date(),
)
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start, end = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

c1, c2, c3 = st.columns(3)
with c1:
    metric_card("Matches shown", len(filtered), "Current filter")
with c2:
    metric_card("Teams represented", len(set(filtered["home_team"]).union(filtered["away_team"])), "Current filter")
with c3:
    metric_card("Stages", filtered["stage"].nunique(), "Current filter")

section_header("Results", "Filtered competition matches.")
table = filtered[
    ["date", "stage", "home_team", "Score", "away_team", "winner"]
].sort_values("date", ascending=False)
st.dataframe(
    table.rename(
        columns={
            "date": "Date",
            "stage": "Stage",
            "home_team": "Home",
            "away_team": "Away",
            "winner": "Winner",
        }
    ),
    hide_index=True,
    width="stretch",
    height=440,
)

section_header("Match detail", "Inspect one result and its available match-stat profile.")
ordered = filtered.sort_values(["date", "match_id"], ascending=[False, False])
labels = ordered.apply(
    lambda r: f"{r['date'].date()} · {r['home_team']} {r['Score']} {r['away_team']}",
    axis=1,
)
selected_label = st.selectbox("Match", labels.tolist())
selected_index = labels[labels == selected_label].index[0]
row = filtered.loc[selected_index]

d1, d2, d3, d4 = st.columns(4)
with d1:
    metric_card("Home", row["home_team"], "Home team")
with d2:
    metric_card("Score", row["Score"], "Football score")
with d3:
    metric_card("Away", row["away_team"], "Away team")
with d4:
    metric_card("Stage", row["stage"], str(row["date"].date()))

if pd.notna(row.get("home_possession")):
    stat_rows = pd.DataFrame(
        {
            "Metric": ["Possession (%)", "Shots", "Shots on target", "Saves"],
            row["home_team"]: [
                row["home_possession"],
                row["home_shots_total"],
                row["home_shots_on_target_count"],
                row["home_saves_count"],
            ],
            row["away_team"]: [
                row["away_possession"],
                row["away_shots_total"],
                row["away_shots_on_target_count"],
                row["away_saves_count"],
            ],
        }
    )
    section_header("League-phase match statistics")
    st.dataframe(stat_rows, hide_index=True, width="stretch")

    long = stat_rows.melt(id_vars="Metric", var_name="Team", value_name="Value")
    fig = px.bar(long, x="Metric", y="Value", color="Team", barmode="group")
    chart_layout(fig, x_title=None, y_title="Value", height=370)
    st.plotly_chart(fig, width="stretch")
else:
    scope_note(
        "Detailed possession, shooting and save fields are unavailable for this match "
        "because the richer statistics source covers the league phase only."
    )

if pd.notna(row.get("venue")) or pd.notna(row.get("referee")):
    with st.expander("Match metadata"):
        st.write(f"**Venue:** {row.get('venue') if pd.notna(row.get('venue')) else '—'}")
        st.write(f"**Referee:** {row.get('referee') if pd.notna(row.get('referee')) else '—'}")
