\
from __future__ import annotations

from html import escape
import streamlit as st


def hero(
    eyebrow: str,
    title: str,
    subtitle: str,
    meta: list[str] | None = None,
) -> None:
    pills = ""
    if meta:
        pills = "".join(
            f'<span class="ucl-pill">{escape(str(item))}</span>' for item in meta
        )
    st.markdown(
        f"""
        <section class="ucl-hero">
            <div class="ucl-eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
            <div class="ucl-pill-row">{pills}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str | None = None) -> None:
    extra = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="ucl-section-heading">
            <h2>{escape(title)}</h2>
            {extra}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str | int | float, detail: str = "") -> None:
    detail_html = f"<span>{escape(detail)}</span>" if detail else ""
    st.markdown(
        f"""
        <div class="ucl-metric-card">
            <div class="ucl-metric-label">{escape(str(label))}</div>
            <div class="ucl-metric-value">{escape(str(value))}</div>
            <div class="ucl-metric-detail">{detail_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, kicker: str = "Insight") -> None:
    st.markdown(
        f"""
        <div class="ucl-insight-card">
            <div class="ucl-insight-kicker">{escape(kicker)}</div>
            <div class="ucl-insight-title">{escape(title)}</div>
            <div class="ucl-insight-body">{escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def scope_note(text: str) -> None:
    st.markdown(
        f"""
        <div class="ucl-scope-note">
            <span class="ucl-scope-dot"></span>
            <span>{escape(text)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_card(title: str, description: str, page: str) -> None:
    st.markdown(
        f"""
        <div class="ucl-nav-copy">
            <div class="ucl-nav-title">{escape(title)}</div>
            <div class="ucl-nav-description">{escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(page, label=f"Open {title}")
