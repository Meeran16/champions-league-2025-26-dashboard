\
from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>
:root {
    --ucl-bg: #F5F7FB;
    --ucl-surface: #FFFFFF;
    --ucl-text: #172033;
    --ucl-muted: #64748B;
    --ucl-border: #E4E9F2;
    --ucl-accent: #2457D6;
    --ucl-accent-soft: #EEF3FF;
    --ucl-sidebar: #111827;
    --ucl-sidebar-soft: #1F2937;
}

html, body, [class*="css"] {
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: var(--ucl-bg);
}

[data-testid="stHeader"] {
    background: rgba(245, 247, 251, 0.84);
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] {
    background: var(--ucl-sidebar);
    border-right: 1px solid rgba(255,255,255,0.07);
}

[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

[data-testid="stSidebar"] a {
    border-radius: 10px;
}

[data-testid="stSidebar"] a:hover {
    background: var(--ucl-sidebar-soft);
}

.block-container {
    max-width: 1420px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

.ucl-hero {
    padding: 1.6rem 1.75rem 1.5rem;
    border: 1px solid var(--ucl-border);
    border-radius: 18px;
    background:
        radial-gradient(circle at top right, rgba(36,87,214,0.10), transparent 35%),
        var(--ucl-surface);
    box-shadow: 0 12px 34px rgba(23, 32, 51, 0.055);
    margin-bottom: 1.25rem;
}

.ucl-eyebrow {
    color: var(--ucl-accent);
    font-size: 0.77rem;
    font-weight: 750;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.ucl-hero h1 {
    margin: 0;
    color: var(--ucl-text);
    font-size: clamp(2rem, 3.4vw, 3.15rem);
    line-height: 1.03;
    letter-spacing: -0.035em;
}

.ucl-hero p {
    margin: 0.75rem 0 0;
    color: var(--ucl-muted);
    max-width: 860px;
    font-size: 1rem;
    line-height: 1.65;
}

.ucl-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

.ucl-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.34rem 0.65rem;
    border-radius: 999px;
    border: 1px solid #DCE5FB;
    background: var(--ucl-accent-soft);
    color: #24437D;
    font-size: 0.79rem;
    font-weight: 650;
}

.ucl-section-heading {
    margin: 1.25rem 0 0.75rem;
}

.ucl-section-heading h2 {
    margin: 0;
    color: var(--ucl-text);
    font-size: 1.25rem;
    letter-spacing: -0.015em;
}

.ucl-section-heading p {
    margin: 0.28rem 0 0;
    color: var(--ucl-muted);
    font-size: 0.91rem;
}

.ucl-metric-card {
    height: 100%;
    min-height: 126px;
    padding: 1rem 1.05rem;
    border-radius: 14px;
    border: 1px solid var(--ucl-border);
    background: var(--ucl-surface);
    box-shadow: 0 6px 18px rgba(23, 32, 51, 0.04);
}

.ucl-metric-label {
    color: var(--ucl-muted);
    font-size: 0.78rem;
    font-weight: 650;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.ucl-metric-value {
    color: var(--ucl-text);
    font-size: 1.85rem;
    font-weight: 760;
    letter-spacing: -0.035em;
    margin-top: 0.4rem;
}

.ucl-metric-detail {
    min-height: 1.25rem;
    margin-top: 0.35rem;
    color: var(--ucl-muted);
    font-size: 0.78rem;
}

.ucl-insight-card,
.ucl-nav-copy {
    padding: 1rem 1.05rem;
    border-radius: 14px;
    border: 1px solid var(--ucl-border);
    background: var(--ucl-surface);
}

.ucl-insight-kicker {
    color: var(--ucl-accent);
    font-size: 0.72rem;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.ucl-insight-title,
.ucl-nav-title {
    color: var(--ucl-text);
    font-size: 1rem;
    font-weight: 720;
    margin-top: 0.25rem;
}

.ucl-insight-body,
.ucl-nav-description {
    color: var(--ucl-muted);
    font-size: 0.86rem;
    line-height: 1.5;
    margin-top: 0.35rem;
}

.ucl-scope-note {
    display: flex;
    gap: 0.55rem;
    align-items: flex-start;
    padding: 0.75rem 0.9rem;
    border-radius: 10px;
    background: #F0F4FA;
    color: #536175;
    border: 1px solid #E1E7EF;
    font-size: 0.84rem;
    line-height: 1.45;
}

.ucl-scope-dot {
    width: 7px;
    height: 7px;
    flex: 0 0 auto;
    border-radius: 999px;
    background: var(--ucl-accent);
    margin-top: 0.39rem;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--ucl-border);
    border-radius: 12px;
    overflow: hidden;
    background: var(--ucl-surface);
}

[data-testid="stPlotlyChart"] {
    border: 1px solid var(--ucl-border);
    border-radius: 14px;
    padding: 0.3rem;
    background: var(--ucl-surface);
    box-shadow: 0 5px 16px rgba(23, 32, 51, 0.035);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 10px;
}

.stButton button,
[data-testid="stPageLink"] a {
    border-radius: 10px;
    border: 1px solid var(--ucl-border);
    background: var(--ucl-surface);
    color: var(--ucl-text);
    font-weight: 650;
}

.stButton button:hover,
[data-testid="stPageLink"] a:hover {
    border-color: #B7C8F7;
    color: var(--ucl-accent);
}

hr {
    border-color: var(--ucl-border);
}
</style>
"""


def configure_page(title: str, icon: str = "⚽") -> None:
    st.set_page_config(
        page_title=f"{title} | UCL 2025/26",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def data_missing_message(missing: list[str]) -> None:
    st.error(
        "Dashboard data has not been generated yet. "
        "Run `python scripts/export_dashboard_data.py` from the repository root."
    )
    if missing:
        st.code("\n".join(missing), language="text")
    st.stop()


def lpi_note() -> None:
    st.info(
        "Player scores use the project's Leaderboard Performance Index (LPI). "
        "This is a transparent analytical index for published leaderboard candidates, "
        "not an official UEFA player award."
    )
