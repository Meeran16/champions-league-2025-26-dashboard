\
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.express as px
import streamlit as st

from src.analytics import clean_signal_name, player_signal_columns
from src.components import hero, metric_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout, POSITION_ORDER
from src.ui import configure_page, data_missing_message

configure_page("Player Rankings")

if not data_ready():
    data_missing_message(missing_files())

players = load_all()["player_rankings"]

position = st.selectbox(
    "Position group",
    POSITION_ORDER,
    help="Different positions use different LPI signals and weights.",
)

group = players.loc[players["position_group"] == position].sort_values("rank").copy()
top = group.head(5).copy()

hero(
    "Player analytics",
    f"{position} Rankings",
    "A transparent Leaderboard Performance Index built from preserved published leaderboard signals.",
    ["Top-5 view", "Explainable scoring", "Offline reproducible"],
)

leader = top.iloc[0]
c1, c2, c3 = st.columns(3)
with c1:
    metric_card("Leader", leader["player"], leader["squad"])
with c2:
    metric_card("LPI score", f"{leader['performance_score']:.2f}", "0–100 analytical index")
with c3:
    metric_card("Candidate pool", len(group), f"{position} candidates")

section_header("Top five", "Position-specific LPI results.")
fig = px.bar(
    top.sort_values("performance_score"),
    x="performance_score",
    y="player",
    orientation="h",
    text="performance_score",
    hover_data=["squad", "rank"],
    labels={"performance_score": "LPI score", "player": "Player"},
)
chart_layout(fig, x_title="LPI score", y_title=None, height=390)
fig.update_xaxes(range=[0, 100])
st.plotly_chart(fig, width="stretch")

st.dataframe(
    top[["rank", "player", "squad", "performance_score"]].rename(
        columns={
            "rank": "Rank",
            "player": "Player",
            "squad": "Club",
            "performance_score": "LPI Score",
        }
    ),
    hide_index=True,
    width="stretch",
)

signals = [c for c in player_signal_columns(group) if group[c].notna().any()]
if signals:
    section_header(
        "Why the score looks this way",
        "Inspect the source-leaderboard point signals behind an individual player's LPI.",
    )
    selected = st.selectbox("Player", top["player"].tolist())
    row = group.loc[group["player"] == selected].iloc[0]
    signal_data = [
        {"Signal": clean_signal_name(column), "Points": float(row[column])}
        for column in signals
        if row[column] == row[column]
    ]
    if signal_data:
        fig = px.bar(signal_data, x="Signal", y="Points", text="Points")
        chart_layout(fig, x_title=None, y_title="Leaderboard points", height=340)
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, width="stretch")

with st.expander("LPI methodology"):
    st.markdown(
        """
        Published leaderboard rank is converted to points:
        **1st = 100, 2nd = 80, 3rd = 65, 4th = 50, 5th = 35, 6th = 20**.

        - **Forward:** Goals 45%, attempts on target 35%, assists 20%
        - **Midfielder:** Tackles 35%, recoveries 30%, assists 25%, attempts on target 10%
        - **Defender:** Recoveries 50%, tackles 25%, assists 25%
        - **Goalkeeper:** Saves leaderboard 60%, clean-sheet signal 40%
        """
    )

scope_note(
    "The LPI is a project-defined analytical index, not an official UEFA award. "
    "Absence from a published top-six list means zero leaderboard points for that signal, "
    "not zero real-world performance."
)
