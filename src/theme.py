\
from __future__ import annotations

ACCENT = "#2457D6"
ACCENT_DARK = "#173B96"
NAVY = "#172033"
MUTED = "#64748B"
BORDER = "#E4E9F2"
SURFACE = "#FFFFFF"
BACKGROUND = "#F5F7FB"
SUCCESS = "#13795B"
WARNING = "#9A6700"

POSITION_ORDER = ["Forward", "Midfielder", "Defender", "Goalkeeper"]


def chart_layout(
    fig,
    *,
    title: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
    legend_title: str | None = None,
    height: int = 390,
):
    fig.update_layout(
        title=None,
        height=height,
        margin=dict(l=12, r=12, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Segoe UI, Arial, sans-serif",
            color=NAVY,
            size=13,
        ),
        hoverlabel=dict(
            bgcolor=SURFACE,
            font_color=NAVY,
            bordercolor=BORDER,
        ),
        legend=dict(
            title_text=legend_title,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )
    fig.update_xaxes(
        title=x_title,
        showgrid=False,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        title=y_title,
        gridcolor=BORDER,
        zeroline=False,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    return fig
