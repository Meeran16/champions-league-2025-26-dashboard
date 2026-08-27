from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ai.models import EvidenceResult
from src.components import metric_card, scope_note, section_header
from src.theme import chart_layout


def _table_frame(result: EvidenceResult) -> pd.DataFrame:
    return pd.DataFrame(result.table)


def render_chart(result: EvidenceResult) -> None:
    if not result.chart or not result.table:
        return

    df = _table_frame(result)
    spec = result.chart
    chart_type = spec.get("type")
    title = spec.get("title", "")

    try:
        if chart_type == "bar":
            limit = int(spec.get("limit", len(df)))
            plot_df = df.head(limit).copy()
            x, y = spec["x"], spec["y"]
            if x in plot_df.columns and y in plot_df.columns:
                # Horizontal bars when category is on y.
                fig = px.bar(
                    plot_df.sort_values(x),
                    x=x,
                    y=y,
                    orientation="h",
                    text=x,
                )
                chart_layout(fig, x_title=x.replace("_", " ").title(), y_title=None, height=380)
                st.plotly_chart(fig, width="stretch")
                return

        if chart_type == "line":
            x, y = spec["x"], spec["y"]
            if x in df.columns and y in df.columns:
                fig = px.line(df, x=x, y=y, markers=True)
                chart_layout(
                    fig,
                    x_title=x.replace("_", " ").title(),
                    y_title=y.replace("_", " ").title(),
                    height=360,
                )
                st.plotly_chart(fig, width="stretch")
                return

        if chart_type == "scatter":
            x, y = spec["x"], spec["y"]
            text = spec.get("text")
            if x in df.columns and y in df.columns:
                fig = px.scatter(df, x=x, y=y, text=text if text in df.columns else None)
                if text in df.columns:
                    fig.update_traces(textposition="top center")
                chart_layout(
                    fig,
                    x_title=x.replace("_", " ").title(),
                    y_title=y.replace("_", " ").title(),
                    height=390,
                )
                st.plotly_chart(fig, width="stretch")
                return

        if chart_type == "grouped_bar":
            x = spec["x"]
            ys = [y for y in spec.get("ys", []) if y in df.columns]
            if x in df.columns and ys:
                long = df[[x] + ys].melt(id_vars=x, var_name="Metric", value_name="Value")
                fig = px.bar(long, x=x, y="Value", color="Metric", barmode="group")
                chart_layout(fig, x_title=None, y_title="Value", legend_title=None, height=380)
                st.plotly_chart(fig, width="stretch")
                return
    except Exception:
        # Evidence table remains the source of truth if a visualization cannot render.
        return


def render_evidence(result: EvidenceResult) -> None:
    st.markdown(f"### {result.title}")
    st.write(result.answer)

    if result.facts:
        columns = st.columns(min(len(result.facts), 4))
        for index, fact in enumerate(result.facts):
            with columns[index % len(columns)]:
                metric_card(fact["label"], fact["value"], "Grounded evidence")

    if result.table:
        section_header("Evidence", "Structured values returned by the approved analytics function.")
        render_chart(result)
        st.dataframe(_table_frame(result), hide_index=True, width="stretch")

    if result.scope:
        section_header("Data scope")
        scope_note(result.scope)

    if result.caveats:
        with st.expander("Methodology / caveats"):
            for caveat in result.caveats:
                st.markdown(f"- {caveat}")

    followups = [f for f in result.followups if f]
    if followups:
        section_header("Suggested follow-ups")
        for followup in followups[:5]:
            st.caption(f"• {followup}")
