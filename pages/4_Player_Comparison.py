\
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import clean_signal_name, player_signal_columns
from src.components import hero, metric_card, section_header, scope_note
from src.data_loader import data_ready, load_all, missing_files
from src.theme import chart_layout, POSITION_ORDER
from src.ui import configure_page, data_missing_message

configure_page("Player Comparison")

if not data_ready():
    data_missing_message(missing_files())

players = load_all()["player_rankings"]

position = st.selectbox("Position group", POSITION_ORDER)
group = players.loc[players["position_group"] == position].sort_values("rank").copy()
names = group["player"].tolist()

if len(names) < 2:
    st.warning("Not enough players are available in this position group.")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    player_a = st.selectbox("Player A", names, index=0)
with c2:
    player_b = st.selectbox("Player B", names, index=1)

if player_a == player_b:
    st.warning("Select two different players.")
    st.stop()

selected = group[group["player"].isin([player_a, player_b])].copy()
row_a = selected.loc[selected["player"] == player_a].iloc[0]
row_b = selected.loc[selected["player"] == player_b].iloc[0]

hero(
    "Head-to-head",
    f"{player_a} vs {player_b}",
    f"Same-position comparison within the {position} LPI model.",
    [position, "Explainable signals", "Same scoring model"],
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card(player_a, f"{row_a['performance_score']:.2f}", f"Rank {int(row_a['rank'])}")
with m2:
    metric_card("Club", row_a["squad"], "Player A")
with m3:
    metric_card(player_b, f"{row_b['performance_score']:.2f}", f"Rank {int(row_b['rank'])}")
with m4:
    metric_card("Club", row_b["squad"], "Player B")

signals = [c for c in player_signal_columns(selected) if selected[c].notna().any()]
records = []
for _, row in selected.iterrows():
    for signal in signals:
        value = row.get(signal)
        if pd.notna(value):
            records.append(
                {
                    "Player": row["player"],
                    "Signal": clean_signal_name(signal),
                    "Points": float(value),
                }
            )

if records:
    section_header(
        "Signal comparison",
        "Leaderboard-point contributions before the final position-specific weighting.",
    )
    fig = px.bar(
        pd.DataFrame(records),
        x="Signal",
        y="Points",
        color="Player",
        barmode="group",
    )
    chart_layout(fig, x_title=None, y_title="Leaderboard points", legend_title=None, height=390)
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig, width="stretch")

section_header("Comparison table")
st.dataframe(
    selected[["player", "squad", "rank", "performance_score"]].rename(
        columns={
            "player": "Player",
            "squad": "Club",
            "rank": "Rank",
            "performance_score": "LPI Score",
        }
    ),
    hide_index=True,
    width="stretch",
)

scope_note(
    "Cross-position comparisons are intentionally avoided because Forward, Midfielder, "
    "Defender and Goalkeeper use different signals and weights."
)
