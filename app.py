import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# Page config  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EVM Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Session state – theme
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# ─────────────────────────────────────────────
# Theme palette  (single source of truth)
# ─────────────────────────────────────────────
def get_theme() -> dict:
    if st.session_state.dark_mode:
        return dict(
            dark=True,
            bg_app="#0d1117",
            bg_card="#161b27",
            bg_card2="#1a2035",
            bg_sidebar="#0f1420",
            border="#252d3d",
            border2="#2e3850",
            text_primary="#e6eaf2",
            text_secondary="#7a8499",
            text_sidebar="#b8c4d8",
            accent="#7aa2f7",
            accent2="#5b85e8",
            green="#4ade80",
            red="#f87171",
            yellow="#fbbf24",
            blue="#60a5fa",
            plot_template="plotly_dark",
            plot_bg="#161b27",
            plot_paper="#0d1117",
            grid="#1e2436",
            hover_bg="#1a2035",
            gauge_bg="#161b27",
        )
    else:
        return dict(
            dark=False,
            bg_app="#f1f5fb",
            bg_card="#ffffff",
            bg_card2="#f8faff",
            bg_sidebar="#e8eef8",
            border="#d4dced",
            border2="#c0cce0",
            text_primary="#1a2035",
            text_secondary="#5a6880",
            text_sidebar="#2a3550",
            accent="#3b68d6",
            accent2="#2952b8",
            green="#16a34a",
            red="#dc2626",
            yellow="#d97706",
            blue="#2563eb",
            plot_template="plotly_white",
            plot_bg="#ffffff",
            plot_paper="#f1f5fb",
            grid="#e2e8f4",
            hover_bg="#f1f5fb",
            gauge_bg="#ffffff",
        )


# ─────────────────────────────────────────────
# CSS injection  (re-runs on every theme toggle)
# ─────────────────────────────────────────────
def inject_css(T: dict) -> None:
    st.markdown(
        f"""
        <style>
        /* ── Reset & base ── */
        html, body, [class*="css"] {{
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        .stApp {{
            background-color: {T['bg_app']};
            color: {T['text_primary']};
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background-color: {T['bg_sidebar']} !important;
            border-right: 1px solid {T['border']} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {T['text_sidebar']} !important;
        }}
        [data-testid="stSidebar"] .stMarkdown h2 {{
            color: {T['accent']} !important;
            font-size: .9rem;
            letter-spacing: .08em;
            text-transform: uppercase;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: {T['border']} !important;
        }}

        /* ── Health badge ── */
        .health-badge {{
            background: {T['bg_card']};
            border: 1px solid {T['border']};
            border-radius: 16px;
            padding: 20px 28px;
            display: flex;
            align-items: center;
            gap: 22px;
            position: relative;
            overflow: hidden;
        }}
        .health-badge::before {{
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 5px;
            border-radius: 16px 0 0 16px;
        }}
        .health-badge.on-track::before {{ background: {T['green']}; }}
        .health-badge.at-risk::before  {{ background: {T['yellow']}; }}
        .health-badge.critical::before {{ background: {T['red']}; }}
        .health-icon {{
            font-size: 2.4rem;
            line-height: 1;
            min-width: 44px;
            text-align: center;
        }}
        .health-label {{
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: {T['text_secondary']};
            margin-bottom: 2px;
        }}
        .health-status {{
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: .04em;
            line-height: 1.1;
        }}
        .health-desc {{
            font-size: .78rem;
            color: {T['text_secondary']};
            margin-top: 3px;
        }}
        .health-indices {{
            margin-left: auto;
            display: flex;
            gap: 24px;
        }}
        .health-index {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }}
        .health-index .idx-label {{
            font-size: .65rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;
            color: {T['text_secondary']};
        }}
        .health-index .idx-value {{
            font-size: 1.35rem;
            font-weight: 800;
            font-variant-numeric: tabular-nums;
        }}

        /* Pulse animation for critical status */
        @keyframes pulse-red {{
            0%   {{ box-shadow: 0 0 0 0 rgba(248,113,113,.5); }}
            70%  {{ box-shadow: 0 0 0 12px rgba(248,113,113,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(248,113,113,0); }}
        }}
        .health-badge.critical {{
            animation: pulse-red 2s infinite;
        }}

        /* ── Metric cards ── */
        .metric-card {{
            background: {T['bg_card']};
            border-radius: 14px;
            padding: 18px 20px;
            border: 1px solid {T['border']};
            text-align: center;
            transition: transform .18s, box-shadow .18s;
            height: 100%;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 28px rgba(0,0,0,.15);
        }}
        .metric-label {{
            font-size: .67rem;
            font-weight: 700;
            letter-spacing: .11em;
            text-transform: uppercase;
            color: {T['text_secondary']};
            margin-bottom: 7px;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.05;
            font-variant-numeric: tabular-nums;
        }}
        .metric-sub {{
            font-size: .73rem;
            color: {T['text_secondary']};
            margin-top: 6px;
        }}
        .c-green  {{ color: {T['green']}; }}
        .c-red    {{ color: {T['red']}; }}
        .c-yellow {{ color: {T['yellow']}; }}
        .c-blue   {{ color: {T['blue']}; }}

        /* ── Gauge wrapper ── */
        .gauge-wrap {{
            background: {T['bg_card']};
            border: 1px solid {T['border']};
            border-radius: 14px;
            padding: 10px 6px 0;
        }}
        .gauge-title {{
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;
            color: {T['text_secondary']};
            text-align: center;
            padding-top: 6px;
        }}

        /* ── Section headers ── */
        .section-header {{
            font-size: .85rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;
            color: {T['accent']};
            padding-bottom: 8px;
            border-bottom: 1px solid {T['border']};
            margin-bottom: 16px;
        }}

        /* ── Insight cards ── */
        .insight-card {{
            background: {T['bg_card']};
            border-left: 4px solid {T['accent']};
            border-radius: 0 12px 12px 0;
            padding: 14px 18px;
            margin-bottom: 12px;
            border-top: 1px solid {T['border']};
            border-right: 1px solid {T['border']};
            border-bottom: 1px solid {T['border']};
        }}
        .insight-card.good {{ border-left-color: {T['green']}; }}
        .insight-card.bad  {{ border-left-color: {T['red']}; }}
        .insight-card.warn {{ border-left-color: {T['yellow']}; }}
        .insight-title {{
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .insight-card.good .insight-title {{ color: {T['green']}; }}
        .insight-card.bad  .insight-title {{ color: {T['red']}; }}
        .insight-card.warn .insight-title {{ color: {T['yellow']}; }}
        .insight-body {{
            font-size: .87rem;
            color: {T['text_secondary']};
            line-height: 1.6;
        }}

        /* ── Progress bar label ── */
        .prog-label {{
            font-size: .72rem;
            font-weight: 600;
            letter-spacing: .09em;
            text-transform: uppercase;
            color: {T['text_secondary']};
            margin-bottom: 5px;
        }}

        /* ── Dividers & misc ── */
        hr {{ border-color: {T['border']} !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        /* ── Streamlit element overrides for light mode ── */
        {'[data-testid="stDataFrame"], [data-testid="stTable"] { background: ' + T['bg_card'] + ' !important; }' if not T['dark'] else ''}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# EVM calculations
# ─────────────────────────────────────────────
def compute_evm(df: pd.DataFrame) -> dict:
    latest    = df.iloc[-1]
    pv        = latest["Planned Value"]
    ev        = latest["Earned Value"]
    ac        = latest["Actual Cost"]
    bac       = df["Planned Value"].max()

    cv   = ev - ac
    sv   = ev - pv
    cpi  = ev / ac  if ac  != 0 else float("nan")
    spi  = ev / pv  if pv  != 0 else float("nan")
    eac  = bac / cpi if not np.isnan(cpi) and cpi != 0 else float("nan")
    etc  = eac - ac
    vac  = bac - eac
    tcpi = (bac - ev) / (bac - ac) if (bac - ac) != 0 else float("nan")
    pct  = (ev / bac) * 100 if bac != 0 else 0

    return dict(
        cv=cv, sv=sv, cpi=cpi, spi=spi, tcpi=tcpi,
        eac=eac, etc=etc, vac=vac, bac=bac,
        pct_complete=pct,
        pv_latest=pv, ev_latest=ev, ac_latest=ac,
    )


def get_health(cpi: float, spi: float) -> tuple[str, str, str, str]:
    """Returns (status_key, label, icon, description)."""
    if cpi >= 1.0 and spi >= 1.0:
        return "on-track", "ON TRACK", "✦",  "All performance indices within acceptable thresholds."
    elif cpi < 0.85 or spi < 0.85:
        return "critical", "CRITICAL", "⚠",  f"Immediate corrective action required — CPI & SPI both below safe threshold."
    else:
        return "at-risk",  "AT RISK",  "◈",  "Performance trending negative. Escalate and monitor closely."


# ─────────────────────────────────────────────
# Helper formatters
# ─────────────────────────────────────────────
def fmt_currency(val: float) -> str:
    if np.isnan(val): return "N/A"
    sign = "-" if val < 0 else ""
    val  = abs(val)
    if val >= 1_000_000: return f"{sign}${val/1_000_000:.2f}M"
    if val >= 1_000:     return f"{sign}${val/1_000:.1f}K"
    return f"{sign}${val:.0f}"

def fmt_index(val: float) -> str:
    return "N/A" if (np.isnan(val) or np.isinf(val)) else f"{val:.3f}"

def c_class(val: float, invert: bool = False) -> str:
    ok = val >= 1.0
    if invert: ok = not ok
    return "c-green" if ok else "c-red"


# ─────────────────────────────────────────────
# HTML component builders
# ─────────────────────────────────────────────
def health_badge_html(cpi: float, spi: float, T: dict) -> str:
    key, label, icon, desc = get_health(cpi, spi)
    color_map = {"on-track": T["green"], "at-risk": T["yellow"], "critical": T["red"]}
    clr = color_map[key]
    return f"""
    <div class="health-badge {key}">
        <span class="health-icon" style="color:{clr};">{icon}</span>
        <div>
            <div class="health-label">Project Status</div>
            <div class="health-status" style="color:{clr};">{label}</div>
            <div class="health-desc">{desc}</div>
        </div>
        <div class="health-indices">
            <div class="health-index">
                <span class="idx-label">CPI</span>
                <span class="idx-value" style="color:{clr};">{cpi:.3f}</span>
            </div>
            <div class="health-index">
                <span class="idx-label">SPI</span>
                <span class="idx-value" style="color:{clr};">{spi:.3f}</span>
            </div>
        </div>
    </div>
    """

def metric_card_html(label: str, value: str, subtitle: str, css_class: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {css_class}">{value}</div>
        <div class="metric-sub">{subtitle}</div>
    </div>
    """

def insight_html(status: str, title: str, body: str) -> str:
    return f"""
    <div class="insight-card {status}">
        <div class="insight-title">{title}</div>
        <div class="insight-body">{body}</div>
    </div>
    """


# ─────────────────────────────────────────────
# Gauge chart  (CPI or SPI)
# ─────────────────────────────────────────────
def build_gauge(value: float, label: str, T: dict) -> go.Figure:
    safe_val = min(max(value if not np.isnan(value) else 0, 0), 1.75)

    if value >= 1.0:
        needle   = T["green"]
        delta_clr = T["green"]
    elif value >= 0.85:
        needle   = T["yellow"]
        delta_clr = T["yellow"]
    else:
        needle   = T["red"]
        delta_clr = T["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=safe_val,
        delta={
            "reference": 1.0,
            "valueformat": ".3f",
            "increasing": {"color": T["green"]},
            "decreasing": {"color": T["red"]},
        },
        number={
            "valueformat": ".3f",
            "font": {"size": 38, "color": needle, "family": "Segoe UI"},
        },
        title={
            "text": f"<b>{label}</b>",
            "font": {"size": 13, "color": T["text_secondary"], "family": "Segoe UI"},
        },
        gauge={
            "axis": {
                "range": [0, 1.75],
                "tickvals": [0, 0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75],
                "ticktext": ["0", "0.5", "0.75", "0.9", "1.0", "1.1", "1.25", "1.5", "1.75"],
                "tickfont": {"size": 9, "color": T["text_secondary"]},
                "linecolor": T["border"],
                "linewidth": 1,
                "gridcolor": T["border"],
            },
            "bar":      {"color": needle, "thickness": 0.18},
            "bgcolor":  T["gauge_bg"],
            "borderwidth": 0,
            "steps": [
                {"range": [0.00, 0.75], "color": "rgba(248,113,113,0.20)"},
                {"range": [0.75, 0.90], "color": "rgba(251,191, 36,0.18)"},
                {"range": [0.90, 1.00], "color": "rgba(251,191, 36,0.10)"},
                {"range": [1.00, 1.25], "color": "rgba( 74,222,128,0.16)"},
                {"range": [1.25, 1.75], "color": "rgba( 74,222,128,0.28)"},
            ],
            "threshold": {
                "line":      {"color": T["accent"], "width": 2.5},
                "thickness": 0.82,
                "value":     1.0,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=T["gauge_bg"],
        plot_bgcolor=T["gauge_bg"],
        font={"family": "Segoe UI", "color": T["text_primary"]},
        margin=dict(l=24, r=24, t=50, b=16),
        height=260,
    )
    return fig


# ─────────────────────────────────────────────
# S-Curve
# ─────────────────────────────────────────────
def build_scurve(df: pd.DataFrame, T: dict) -> go.Figure:
    months = df["Month"].astype(str)
    fig    = go.Figure()

    # Shaded overrun band
    fig.add_trace(go.Scatter(x=months, y=df["Planned Value"],
        fill=None, mode="lines", line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=months, y=df["Actual Cost"],
        fill="tonexty", fillcolor="rgba(248,113,113,.07)",
        mode="lines", line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"))

    fig.add_trace(go.Scatter(x=months, y=df["Planned Value"],
        mode="lines+markers", name="Planned Value (PV)",
        line=dict(color=T["accent"], width=2.5, dash="dot"),
        marker=dict(size=7, symbol="circle-open", line=dict(width=2, color=T["accent"])),
        hovertemplate="<b>%{x}</b><br>PV: $%{y:,.0f}<extra></extra>"))

    fig.add_trace(go.Scatter(x=months, y=df["Earned Value"],
        mode="lines+markers", name="Earned Value (EV)",
        line=dict(color=T["green"], width=2.5),
        marker=dict(size=7, symbol="diamond", color=T["green"]),
        hovertemplate="<b>%{x}</b><br>EV: $%{y:,.0f}<extra></extra>"))

    fig.add_trace(go.Scatter(x=months, y=df["Actual Cost"],
        mode="lines+markers", name="Actual Cost (AC)",
        line=dict(color=T["red"], width=2.5),
        marker=dict(size=7, symbol="square", color=T["red"]),
        hovertemplate="<b>%{x}</b><br>AC: $%{y:,.0f}<extra></extra>"))

    fig.update_layout(
        template=T["plot_template"],
        paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
        font=dict(family="Segoe UI", color=T["text_primary"], size=12),
        title=dict(text="S-Curve  ·  PV vs EV vs AC",
                   font=dict(size=14, color=T["text_primary"]), x=0, xanchor="left"),
        xaxis=dict(title="Period", gridcolor=T["grid"], linecolor=T["border"],
                   tickfont=dict(size=11)),
        yaxis=dict(title="Cumulative ($)", gridcolor=T["grid"], linecolor=T["border"],
                   tickformat="$,.0f", tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", bordercolor=T["border"],
                    font=dict(size=12)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                        font=dict(color=T["text_primary"], size=12)),
        margin=dict(l=60, r=30, t=60, b=50),
    )
    return fig


# ─────────────────────────────────────────────
# CPI / SPI trend bars
# ─────────────────────────────────────────────
def build_variance_chart(df: pd.DataFrame, T: dict) -> go.Figure:
    months   = df["Month"].astype(str)
    cpi_vals = (df["Earned Value"] / df["Actual Cost"]).replace([np.inf, -np.inf], np.nan)
    spi_vals = (df["Earned Value"] / df["Planned Value"]).replace([np.inf, -np.inf], np.nan)

    cpi_colors = [T["green"] if v >= 1 else T["red"]    for v in cpi_vals]
    spi_colors = [T["blue"]  if v >= 1 else T["yellow"] for v in spi_vals]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=cpi_vals, name="CPI",
        marker_color=cpi_colors, opacity=.88,
        hovertemplate="<b>%{x}</b><br>CPI: %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Bar(x=months, y=spi_vals, name="SPI",
        marker_color=spi_colors, opacity=.88,
        hovertemplate="<b>%{x}</b><br>SPI: %{y:.3f}<extra></extra>"))

    fig.add_hline(y=1, line_dash="dot", line_color=T["text_secondary"], line_width=1.5,
                  annotation_text="Target 1.0",
                  annotation_font=dict(color=T["text_secondary"], size=11))

    fig.update_layout(
        template=T["plot_template"],
        paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
        font=dict(family="Segoe UI", color=T["text_primary"], size=12),
        title=dict(text="CPI & SPI Trend",
                   font=dict(size=14, color=T["text_primary"]), x=0, xanchor="left"),
        xaxis=dict(title="Period", gridcolor=T["grid"], linecolor=T["border"]),
        yaxis=dict(title="Index Value", gridcolor=T["grid"], linecolor=T["border"],
                   tickformat=".2f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)"),
        barmode="group", bargap=.25, bargroupgap=.08,
        hovermode="x unified",
        hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                        font=dict(color=T["text_primary"], size=12)),
        margin=dict(l=60, r=30, t=60, b=50),
    )
    return fig


# ─────────────────────────────────────────────
# PM Insights
# ─────────────────────────────────────────────
def generate_insights(metrics: dict) -> list[dict]:
    cpi, spi, tcpi = metrics["cpi"], metrics["spi"], metrics["tcpi"]
    cv, sv = metrics["cv"], metrics["sv"]
    bac, eac, vac = metrics["bac"], metrics["eac"], metrics["vac"]
    pct = metrics["pct_complete"]
    insights = []

    # Overall health
    if cpi >= 1.0 and spi >= 1.0:
        insights.append({"status": "good", "title": "Overall Health: ON TRACK",
            "body": f"Performing well — under budget (CPI={cpi:.3f}) and ahead of schedule "
                    f"(SPI={spi:.3f}). Completion stands at <b>{pct:.1f}%</b> of total scope."})
    elif cpi < 1.0 and spi < 1.0:
        insights.append({"status": "bad", "title": "Overall Health: CRITICAL — Double Threat",
            "body": f"Project is <b>over budget AND behind schedule</b>. CPI={cpi:.3f}, "
                    f"SPI={spi:.3f}. Escalate immediately and convene a recovery plan."})
    elif cpi < 1.0:
        insights.append({"status": "bad", "title": "Overall Health: OVER BUDGET",
            "body": f"Schedule holding (SPI={spi:.3f}), but spending ${1/cpi:.2f} for every "
                    f"$1.00 of value earned (CPI={cpi:.3f}). Review cost drivers urgently."})
    else:
        insights.append({"status": "warn", "title": "Overall Health: BEHIND SCHEDULE",
            "body": f"Cost under control (CPI={cpi:.3f}), but lagging baseline schedule "
                    f"(SPI={spi:.3f}). Consider fast-tracking critical path activities."})

    # Cost Variance
    cv_s = fmt_currency(abs(cv))
    if cv >= 0:
        insights.append({"status": "good", "title": "Cost Variance (CV): Favourable",
            "body": f"Earned <b>{cv_s} more</b> value than spent. Positive variance signals efficient cost management."})
    else:
        insights.append({"status": "bad", "title": "Cost Variance (CV): Unfavourable",
            "body": f"Spent <b>{cv_s} more</b> than earned value. Review labour, procurement, and scope creep."})

    # Schedule Variance
    sv_s = fmt_currency(abs(sv))
    if sv >= 0:
        insights.append({"status": "good", "title": "Schedule Variance (SV): Ahead of Plan",
            "body": f"Delivered <b>{sv_s} more</b> planned work than expected at this point. Buffer available to absorb future risk."})
    else:
        insights.append({"status": "warn", "title": "Schedule Variance (SV): Behind Plan",
            "body": f"<b>{sv_s} behind</b> planned schedule. Identify critical-path delays and escalate to sponsor."})

    # TCPI
    bac_breached = metrics["ac_latest"] >= bac
    if bac_breached:
        insights.append({"status": "bad", "title": "TCPI: Original Budget Already Exceeded",
            "body": f"AC ({fmt_currency(metrics['ac_latest'])}) > BAC ({fmt_currency(bac)}). "
                    f"TCPI is no longer valid. Forecasted EAC: <b>{fmt_currency(eac)}</b>. "
                    f"Discuss re-baseline or Management Reserve drawdown with sponsor."})
    elif not np.isnan(tcpi) and tcpi <= 1.1:
        insights.append({"status": "good" if tcpi <= 1.0 else "warn",
            "title": f"TCPI = {tcpi:.3f}: Target {'Achievable' if tcpi <= 1.0 else 'Challenging'}",
            "body": f"Remaining work must be done at efficiency <b>{tcpi:.3f}</b> to stay within "
                    f"BAC of {fmt_currency(bac)}. "
                    + ("Current pace is sufficient." if tcpi <= 1.0
                       else "Slightly above 1.0 — tight but manageable.")})
    else:
        insights.append({"status": "bad", "title": f"TCPI = {fmt_index(tcpi)}: BAC Unrealistic",
            "body": f"Required future efficiency {fmt_index(tcpi)} far exceeds current CPI {cpi:.3f}. "
                    f"Forecasted EAC <b>{fmt_currency(eac)}</b> — overrun of "
                    f"<b>{fmt_currency(abs(vac))}</b>. Re-baseline recommended."})

    return insights


# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────
REQUIRED_COLS = {"Month", "Planned Value", "Earned Value", "Actual Cost"}

def load_data(source) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(source)
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
            return None
        df = df[list(REQUIRED_COLS)].dropna()
        for c in ["Planned Value", "Earned Value", "Actual Cost"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna().reset_index(drop=True)
        if df.empty:
            st.error("No valid rows found after parsing.")
            return None
        return df
    except Exception as e:
        st.error(f"Failed to parse CSV: {e}")
        return None


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## EVM Command Center")
    st.markdown("---")

    # Theme toggle
    dark = st.toggle("Dark mode", value=st.session_state.dark_mode, key="theme_toggle")
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")
    st.markdown("**Upload Project Data**")
    uploaded = st.file_uploader(
        "CSV (Month · Planned Value · Earned Value · Actual Cost)",
        type=["csv"],
        help="Upload cumulative monthly EVM data.",
    )

    st.markdown("---")
    st.markdown("**Required Columns**")
    st.code("Month\nPlanned Value\nEarned Value\nActual Cost", language="text")

    st.markdown("---")
    st.markdown("**Key Formulas**")
    st.markdown(
        "| Metric | Formula |\n|---|---|\n"
        "| CV | EV − AC |\n| SV | EV − PV |\n"
        "| CPI | EV / AC |\n| SPI | EV / PV |\n"
        "| TCPI | (BAC−EV)/(BAC−AC) |\n| EAC | BAC / CPI |"
    )

    st.markdown("---")
    st.caption("Streamlit + Plotly · PMBOK 7th Ed.")


# ─────────────────────────────────────────────
# Resolve theme & inject CSS (after sidebar so
# session_state is final for this run)
# ─────────────────────────────────────────────
T = get_theme()
inject_css(T)


# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
if uploaded:
    df = load_data(uploaded)
else:
    df = load_data("sample_data.csv")
    st.info("Showing sample data. Upload your CSV in the sidebar.", icon="ℹ️")

if df is None:
    st.warning("Please upload a valid CSV file to begin.")
    st.stop()

metrics = compute_evm(df)


# ─────────────────────────────────────────────
# ── HEADER: Title + Health Badge ──
# ─────────────────────────────────────────────
col_title, col_badge = st.columns([1, 1.6])

with col_title:
    st.markdown(
        f"<h1 style='color:{T['text_primary']};font-size:1.65rem;font-weight:900;"
        f"margin-bottom:2px;letter-spacing:-.01em;'>EVM Command Center</h1>"
        f"<p style='color:{T['text_secondary']};font-size:.82rem;margin-top:0;'>"
        f"Earned Value Management · PMBOK 7th Ed. · Real-time Analytics</p>",
        unsafe_allow_html=True,
    )

with col_badge:
    st.markdown(
        health_badge_html(metrics["cpi"], metrics["spi"], T),
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Progress + BAC
# ─────────────────────────────────────────────
col_prog, col_bac = st.columns([3, 1])
with col_prog:
    st.markdown(
        f"<div class='prog-label'>Project Completion — "
        f"{metrics['pct_complete']:.1f}% of scope earned (EV / BAC)</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(metrics["pct_complete"] / 100, 1.0))
with col_bac:
    st.markdown(
        f"<div style='text-align:right;font-size:.82rem;color:{T['text_secondary']};"
        f"padding-top:8px;'>BAC: "
        f"<span style='color:{T['blue']};font-weight:800;'>{fmt_currency(metrics['bac'])}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 1: Performance Gauges ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Performance Gauges</div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)
with g1:
    st.markdown('<div class="gauge-wrap">', unsafe_allow_html=True)
    st.plotly_chart(
        build_gauge(metrics["cpi"], "Cost Performance Index (CPI)", T),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.markdown(
        f"<p style='text-align:center;font-size:.75rem;color:{T['text_secondary']};"
        f"padding-bottom:10px;margin:0;'>"
        f"Green ≥ 1.0 · Amber 0.85–1.0 · Red &lt; 0.85 · Target line at 1.0</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

with g2:
    st.markdown('<div class="gauge-wrap">', unsafe_allow_html=True)
    st.plotly_chart(
        build_gauge(metrics["spi"], "Schedule Performance Index (SPI)", T),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.markdown(
        f"<p style='text-align:center;font-size:.75rem;color:{T['text_secondary']};"
        f"padding-bottom:10px;margin:0;'>"
        f"Green ≥ 1.0 · Amber 0.85–1.0 · Red &lt; 0.85 · Target line at 1.0</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 2: Core Metric Cards ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Performance Indices</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
for col, label, val, css, sub in [
    (c1, "Cost Perf. Index",      fmt_index(metrics["cpi"]),    c_class(metrics["cpi"]),         "EV / AC"),
    (c2, "Schedule Perf. Index",  fmt_index(metrics["spi"]),    c_class(metrics["spi"]),         "EV / PV"),
    (c3, "To-Complete Perf.",     fmt_index(metrics["tcpi"]),   c_class(metrics["tcpi"], True),  "(BAC−EV)/(BAC−AC)"),
    (c4, "Cost Variance",         fmt_currency(metrics["cv"]),  "c-green" if metrics["cv"] >= 0 else "c-red",  "EV − AC"),
    (c5, "Schedule Variance",     fmt_currency(metrics["sv"]),  "c-green" if metrics["sv"] >= 0 else "c-red",  "EV − PV"),
]:
    with col:
        st.markdown(metric_card_html(label, val, sub, css), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 3: Forecast Cards ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Forecast &amp; Completion</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
for col, label, val, css, sub in [
    (f1, "Estimate at Completion", fmt_currency(metrics["eac"]), "c-blue",  "BAC / CPI"),
    (f2, "Estimate to Complete",   fmt_currency(metrics["etc"]), "c-blue",  "EAC − AC"),
    (f3, "Variance at Completion", fmt_currency(metrics["vac"]),
         "c-green" if metrics["vac"] >= 0 else "c-red", "BAC − EAC"),
    (f4, "Percent Complete",       f"{metrics['pct_complete']:.1f}%", "c-blue", "EV / BAC"),
]:
    with col:
        st.markdown(metric_card_html(label, val, sub, css), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 4: S-Curve ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">S-Curve Analysis</div>', unsafe_allow_html=True)
st.plotly_chart(build_scurve(df, T), use_container_width=True,
                config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 5: Index Trend ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Index Trend Analysis</div>', unsafe_allow_html=True)
st.plotly_chart(build_variance_chart(df, T), use_container_width=True,
                config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 6: PM Insights ──
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">PM Insights &amp; Recommendations</div>',
            unsafe_allow_html=True)

insights  = generate_insights(metrics)
ins_left, ins_right = st.columns(2)
for i, ins in enumerate(insights):
    with (ins_left if i % 2 == 0 else ins_right):
        st.markdown(insight_html(ins["status"], ins["title"], ins["body"]),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 7: Raw data table ──
# ─────────────────────────────────────────────
with st.expander("Raw Data & Computed Metrics", expanded=False):
    disp = df.copy()
    disp["CPI"] = (disp["Earned Value"] / disp["Actual Cost"]).round(3)
    disp["SPI"] = (disp["Earned Value"] / disp["Planned Value"]).round(3)
    disp["CV"]  = (disp["Earned Value"] - disp["Actual Cost"]).apply(fmt_currency)
    disp["SV"]  = (disp["Earned Value"] - disp["Planned Value"]).apply(fmt_currency)
    for c in ["Planned Value", "Earned Value", "Actual Cost"]:
        disp[c] = disp[c].apply(fmt_currency)
    st.dataframe(disp, use_container_width=True, hide_index=True)
