import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import numpy as np

# ─────────────────────────────────────────────
# Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EVM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Global CSS – dark theme + card styling
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ── Base ── */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp {
            background-color: #0f1117;
            color: #e0e0e0;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #161b27;
            border-right: 1px solid #2a2f3e;
        }
        [data-testid="stSidebar"] * { color: #c9d1e0 !important; }
        [data-testid="stSidebar"] .stMarkdown h2 {
            color: #7aa2f7 !important;
            font-size: 1rem;
            letter-spacing: .06em;
            text-transform: uppercase;
        }

        /* ── Metric cards ── */
        .metric-card {
            background: #1a1f2e;
            border-radius: 12px;
            padding: 20px 24px;
            border: 1px solid #2a2f3e;
            text-align: center;
            transition: transform .2s, box-shadow .2s;
            height: 100%;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,.4);
        }
        .metric-label {
            font-size: .72rem;
            font-weight: 600;
            letter-spacing: .1em;
            text-transform: uppercase;
            color: #8892a4;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1.1;
        }
        .metric-sub {
            font-size: .78rem;
            color: #8892a4;
            margin-top: 6px;
        }
        .green  { color: #4ade80; }
        .red    { color: #f87171; }
        .yellow { color: #fbbf24; }
        .blue   { color: #60a5fa; }

        /* ── Section headers ── */
        .section-header {
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: #7aa2f7;
            padding-bottom: 6px;
            border-bottom: 1px solid #2a2f3e;
            margin-bottom: 18px;
        }

        /* ── Insight cards ── */
        .insight-card {
            background: #1a1f2e;
            border-left: 4px solid #7aa2f7;
            border-radius: 0 10px 10px 0;
            padding: 14px 18px;
            margin-bottom: 12px;
        }
        .insight-card.good   { border-color: #4ade80; }
        .insight-card.bad    { border-color: #f87171; }
        .insight-card.warn   { border-color: #fbbf24; }
        .insight-card .insight-title {
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .07em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .insight-card.good  .insight-title { color: #4ade80; }
        .insight-card.bad   .insight-title { color: #f87171; }
        .insight-card.warn  .insight-title { color: #fbbf24; }
        .insight-card .insight-body { font-size: .9rem; color: #c9d1e0; line-height: 1.55; }

        /* ── Table ── */
        .data-table th {
            background: #1e2436 !important;
            color: #7aa2f7 !important;
        }
        .data-table td { color: #c9d1e0 !important; }

        /* ── Dividers ── */
        hr { border-color: #2a2f3e; }

        /* ── Hide Streamlit branding ── */
        #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────

def fmt_currency(val: float) -> str:
    """Format a number as compact currency string."""
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:.0f}"


def fmt_index(val: float) -> str:
    if np.isnan(val) or np.isinf(val):
        return "N/A"
    return f"{val:.3f}"


def color_class(val: float, neutral_threshold: float = 1.0, invert: bool = False) -> str:
    """Return CSS class based on performance threshold."""
    if invert:
        return "green" if val <= neutral_threshold else "red"
    return "green" if val >= neutral_threshold else "red"


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
# EVM calculations
# ─────────────────────────────────────────────

def compute_evm(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    pv_latest  = latest["Planned Value"]
    ev_latest  = latest["Earned Value"]
    ac_latest  = latest["Actual Cost"]
    bac        = df["Planned Value"].max()   # Budget at Completion

    cv   = ev_latest - ac_latest
    sv   = ev_latest - pv_latest
    cpi  = ev_latest / ac_latest  if ac_latest  != 0 else float("nan")
    spi  = ev_latest / pv_latest  if pv_latest  != 0 else float("nan")
    eac  = bac / cpi              if cpi         != 0 else float("nan")
    etc  = eac - ac_latest
    vac  = bac - eac
    tcpi = (bac - ev_latest) / (bac - ac_latest) if (bac - ac_latest) != 0 else float("nan")
    pct_complete = (ev_latest / bac) * 100 if bac != 0 else 0

    return {
        "cv": cv,   "sv": sv,
        "cpi": cpi, "spi": spi, "tcpi": tcpi,
        "eac": eac, "etc": etc, "vac": vac,
        "bac": bac, "pct_complete": pct_complete,
        "pv_latest": pv_latest,
        "ev_latest": ev_latest,
        "ac_latest": ac_latest,
    }


# ─────────────────────────────────────────────
# Plotly S-Curve
# ─────────────────────────────────────────────

def build_scurve(df: pd.DataFrame) -> go.Figure:
    months = df["Month"].astype(str)

    fig = go.Figure()

    # Shaded area between PV and AC for cost overrun intuition
    fig.add_trace(go.Scatter(
        x=months, y=df["Planned Value"],
        fill=None, mode="lines",
        line=dict(color="rgba(122,162,247,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=df["Actual Cost"],
        fill="tonexty",
        fillcolor="rgba(248,113,113,.08)",
        mode="lines",
        line=dict(color="rgba(248,113,113,0)"),
        showlegend=False, hoverinfo="skip",
    ))

    # PV line
    fig.add_trace(go.Scatter(
        x=months, y=df["Planned Value"],
        mode="lines+markers",
        name="Planned Value (PV)",
        line=dict(color="#7aa2f7", width=2.5, dash="dot"),
        marker=dict(size=7, symbol="circle-open", line=dict(width=2, color="#7aa2f7")),
        hovertemplate="<b>%{x}</b><br>PV: $%{y:,.0f}<extra></extra>",
    ))

    # EV line
    fig.add_trace(go.Scatter(
        x=months, y=df["Earned Value"],
        mode="lines+markers",
        name="Earned Value (EV)",
        line=dict(color="#4ade80", width=2.5),
        marker=dict(size=7, symbol="diamond", color="#4ade80"),
        hovertemplate="<b>%{x}</b><br>EV: $%{y:,.0f}<extra></extra>",
    ))

    # AC line
    fig.add_trace(go.Scatter(
        x=months, y=df["Actual Cost"],
        mode="lines+markers",
        name="Actual Cost (AC)",
        line=dict(color="#f87171", width=2.5),
        marker=dict(size=7, symbol="square", color="#f87171"),
        hovertemplate="<b>%{x}</b><br>AC: $%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(family="Segoe UI", color="#c9d1e0", size=12),
        title=dict(
            text="S-Curve: Planned Value vs Earned Value vs Actual Cost",
            font=dict(size=15, color="#e0e0e0"),
            x=0.0, xanchor="left",
        ),
        xaxis=dict(
            title="Time Period",
            gridcolor="#2a2f3e",
            linecolor="#2a2f3e",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Cumulative Cost ($)",
            gridcolor="#2a2f3e",
            linecolor="#2a2f3e",
            tickformat="$,.0f",
            tickfont=dict(size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#2a2f3e",
            font=dict(size=12),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1a1f2e",
            bordercolor="#2a2f3e",
            font=dict(color="#e0e0e0", size=12),
        ),
        margin=dict(l=60, r=30, t=60, b=50),
    )
    return fig


# ─────────────────────────────────────────────
# CPI / SPI variance bar chart
# ─────────────────────────────────────────────

def build_variance_chart(df: pd.DataFrame) -> go.Figure:
    months = df["Month"].astype(str)
    cpi_vals = (df["Earned Value"] / df["Actual Cost"]).replace([np.inf, -np.inf], np.nan)
    spi_vals = (df["Earned Value"] / df["Planned Value"]).replace([np.inf, -np.inf], np.nan)

    cpi_colors = ["#4ade80" if v >= 1 else "#f87171" for v in cpi_vals]
    spi_colors = ["#60a5fa" if v >= 1 else "#fbbf24" for v in spi_vals]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=cpi_vals,
        name="CPI", marker_color=cpi_colors, opacity=.85,
        hovertemplate="<b>%{x}</b><br>CPI: %{y:.3f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=months, y=spi_vals,
        name="SPI", marker_color=spi_colors, opacity=.85,
        hovertemplate="<b>%{x}</b><br>SPI: %{y:.3f}<extra></extra>",
    ))
    fig.add_hline(y=1, line_dash="dot", line_color="#8892a4", line_width=1.5,
                  annotation_text="Target = 1.0",
                  annotation_font=dict(color="#8892a4", size=11))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(family="Segoe UI", color="#c9d1e0", size=12),
        title=dict(
            text="CPI & SPI Trend Over Time",
            font=dict(size=15, color="#e0e0e0"),
            x=0.0, xanchor="left",
        ),
        xaxis=dict(title="Time Period", gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        yaxis=dict(title="Index Value", gridcolor="#2a2f3e", linecolor="#2a2f3e",
                   tickformat=".2f"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        barmode="group",
        bargap=.25, bargroupgap=.08,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1f2e", bordercolor="#2a2f3e",
                        font=dict(color="#e0e0e0", size=12)),
        margin=dict(l=60, r=30, t=60, b=50),
    )
    return fig


# ─────────────────────────────────────────────
# PM Insights generator
# ─────────────────────────────────────────────

def generate_insights(metrics: dict) -> list[dict]:
    insights = []
    cpi, spi, tcpi = metrics["cpi"], metrics["spi"], metrics["tcpi"]
    cv, sv  = metrics["cv"], metrics["sv"]
    vac     = metrics["vac"]
    pct     = metrics["pct_complete"]
    bac     = metrics["bac"]
    eac     = metrics["eac"]

    # ── Overall health ──
    if cpi >= 1 and spi >= 1:
        insights.append({
            "status": "good", "title": "Overall Project Health: ON TRACK",
            "body": (
                f"The project is performing well. Work is being completed ahead of schedule "
                f"(SPI = {spi:.3f}) and under budget (CPI = {cpi:.3f}). "
                f"Current completion stands at <b>{pct:.1f}%</b> of total scope."
            ),
        })
    elif cpi < 1 and spi < 1:
        insights.append({
            "status": "bad", "title": "Overall Project Health: CRITICAL",
            "body": (
                f"The project is <b>over budget</b> and <b>behind schedule</b> simultaneously — "
                f"a double threat. CPI = {cpi:.3f} and SPI = {spi:.3f}. "
                f"Immediate corrective action is required."
            ),
        })
    elif cpi < 1:
        insights.append({
            "status": "bad", "title": "Overall Project Health: OVER BUDGET",
            "body": (
                f"Schedule is holding (SPI = {spi:.3f}), but costs are running over plan. "
                f"CPI = {cpi:.3f} — for every $1 budgeted, the team is spending "
                f"<b>${1/cpi:.2f}</b>. Review resource utilisation and cost drivers."
            ),
        })
    else:
        insights.append({
            "status": "warn", "title": "Overall Project Health: BEHIND SCHEDULE",
            "body": (
                f"Cost is under control (CPI = {cpi:.3f}), but the project is lagging behind "
                f"the baseline schedule. SPI = {spi:.3f}. Consider re-sequencing tasks or "
                f"adding resource capacity to recover the schedule."
            ),
        })

    # ── Cost Variance ──
    cv_str = fmt_currency(abs(cv))
    if cv >= 0:
        insights.append({
            "status": "good", "title": "Cost Variance (CV): Favourable",
            "body": f"The project has earned <b>{cv_str} more</b> value than it has spent. "
                    f"This positive variance signals efficient cost management.",
        })
    else:
        insights.append({
            "status": "bad", "title": "Cost Variance (CV): Unfavourable",
            "body": f"The project has spent <b>{cv_str} more</b> than the value earned. "
                    f"Review labour rates, procurement costs, and scope creep drivers.",
        })

    # ── Schedule Variance ──
    sv_str = fmt_currency(abs(sv))
    if sv >= 0:
        insights.append({
            "status": "good", "title": "Schedule Variance (SV): Ahead of Plan",
            "body": f"The team has delivered <b>{sv_str} more</b> planned work than scheduled "
                    f"for this point in time. The buffer can be used to absorb future risks.",
        })
    else:
        insights.append({
            "status": "warn", "title": "Schedule Variance (SV): Behind Plan",
            "body": f"The project is <b>{sv_str} behind</b> the planned schedule. "
                    f"Identify the critical path activities causing delay and escalate to sponsors.",
        })

    # ── TCPI ──
    bac_breached = metrics["ac_latest"] >= bac
    if bac_breached:
        insights.append({
            "status": "bad", "title": "TCPI: Budget Already Exceeded",
            "body": (
                f"Actual costs ({fmt_currency(metrics['ac_latest'])}) have surpassed the original BAC "
                f"({fmt_currency(bac)}). The TCPI formula is no longer meaningful. "
                f"The forecasted EAC is <b>{fmt_currency(eac)}</b>. A formal re-baseline or "
                f"Management Reserve drawdown should be discussed with the project sponsor."
            ),
        })
    elif not np.isnan(tcpi) and tcpi <= 1.1:
        insights.append({
            "status": "good" if tcpi <= 1.0 else "warn",
            "title": f"TCPI = {tcpi:.3f}: Completion Target {'Achievable' if tcpi <= 1.0 else 'Challenging'}",
            "body": (
                f"To finish within the original BAC of {fmt_currency(bac)}, the remaining work "
                f"must be performed at a TCPI efficiency of <b>{tcpi:.3f}</b>. "
                + ("This is better than 1.0 — performance can ease up slightly." if tcpi <= 1.0
                   else "This is slightly above 1.0 — tight but manageable with discipline.")
            ),
        })
    else:
        insights.append({
            "status": "bad",
            "title": f"TCPI = {fmt_index(tcpi)}: BAC Target Unrealistic",
            "body": (
                f"Completing within the original budget requires future efficiency of "
                f"{fmt_index(tcpi)}, far above the current CPI of {cpi:.3f}. "
                f"The forecasted cost at completion (EAC) is <b>{fmt_currency(eac)}</b> — "
                f"a <b>{fmt_currency(abs(vac))}</b> overrun vs the original BAC. "
                f"A budget re-baseline conversation with the sponsor is strongly recommended."
            ),
        })

    return insights


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## EVM Dashboard")
    st.markdown("---")
    st.markdown("**Upload Project Data**")
    uploaded = st.file_uploader(
        "CSV file (Month, Planned Value,\nEarned Value, Actual Cost)",
        type=["csv"],
        help="Upload a CSV with cumulative monthly EVM data.",
    )
    st.markdown("---")
    st.markdown("**Required CSV Columns**")
    st.code("Month\nPlanned Value\nEarned Value\nActual Cost", language="text")

    st.markdown("---")
    st.markdown("**Key Formulas**")
    st.markdown(
        """
        | Metric | Formula |
        |--------|---------|
        | CV     | EV − AC  |
        | SV     | EV − PV  |
        | CPI    | EV / AC  |
        | SPI    | EV / PV  |
        | TCPI   | (BAC−EV)/(BAC−AC) |
        | EAC    | BAC / CPI |
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Built with Streamlit + Plotly · EVM per PMBOK 7th Ed.")


# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────

REQUIRED_COLS = {"Month", "Planned Value", "Earned Value", "Actual Cost"}

def load_data(source) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(source)
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            st.error(f"CSV is missing required columns: {', '.join(missing)}")
            return None
        df = df[list(REQUIRED_COLS)].dropna()
        for col in ["Planned Value", "Earned Value", "Actual Cost"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna()
        if df.empty:
            st.error("No valid rows found after parsing. Check your data.")
            return None
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Failed to parse CSV: {e}")
        return None


if uploaded:
    df = load_data(uploaded)
else:
    df = load_data("sample_data.csv")
    st.info("Using built-in sample data. Upload your own CSV in the sidebar to analyse a real project.", icon="ℹ️")


# ─────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#e0e0e0;font-size:1.8rem;font-weight:800;margin-bottom:2px;'>"
    "Earned Value Management Dashboard"
    "</h1>"
    "<p style='color:#8892a4;font-size:.9rem;margin-top:0;'>Real-time project performance analytics · PMBOK aligned</p>",
    unsafe_allow_html=True,
)
st.markdown("<hr>", unsafe_allow_html=True)

if df is None:
    st.warning("Please upload a valid CSV file to begin.")
    st.stop()

metrics = compute_evm(df)

# ── Progress banner ───────────────────────────
progress_pct = metrics["pct_complete"] / 100
col_prog, col_bac = st.columns([3, 1])
with col_prog:
    st.markdown(
        f"<div style='font-size:.8rem;color:#8892a4;margin-bottom:4px;'>"
        f"PROJECT COMPLETION  —  {metrics['pct_complete']:.1f}% of scope earned"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(progress_pct, 1.0))
with col_bac:
    st.markdown(
        f"<div style='text-align:right;font-size:.85rem;color:#8892a4;padding-top:8px;'>"
        f"BAC: <span style='color:#60a5fa;font-weight:700;'>{fmt_currency(metrics['bac'])}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 1 – Core EVM Indices
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Performance Indices</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

cards = [
    (c1, "CPI", fmt_index(metrics["cpi"]),
     "Cost Perf. Index", color_class(metrics["cpi"]),
     "Efficiency of budget use"),
    (c2, "SPI", fmt_index(metrics["spi"]),
     "Schedule Perf. Index", color_class(metrics["spi"]),
     "Efficiency of time use"),
    (c3, "TCPI", fmt_index(metrics["tcpi"]),
     "To-Complete Perf. Index", color_class(metrics["tcpi"], invert=True),
     "Required future efficiency"),
    (c4, "CV", fmt_currency(metrics["cv"]),
     "Cost Variance", "green" if metrics["cv"] >= 0 else "red",
     "EV − AC (positive = under budget)"),
    (c5, "SV", fmt_currency(metrics["sv"]),
     "Schedule Variance", "green" if metrics["sv"] >= 0 else "red",
     "EV − PV (positive = ahead)"),
]

for col, label, val, full_name, css, sub in cards:
    with col:
        st.markdown(
            metric_card_html(full_name, val, sub, css),
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 2 – Forecast Metrics
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Forecast & Completion</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
forecast_cards = [
    (f1, "EAC", fmt_currency(metrics["eac"]),
     "Estimate at Completion", "blue", "Projected total cost"),
    (f2, "ETC", fmt_currency(metrics["etc"]),
     "Estimate to Complete", "blue", "Remaining cost to finish"),
    (f3, "VAC", fmt_currency(metrics["vac"]),
     "Variance at Completion", "green" if metrics["vac"] >= 0 else "red",
     "BAC − EAC  (budget surplus/deficit)"),
    (f4, "% Complete", f"{metrics['pct_complete']:.1f}%",
     "Percent Complete", "blue", "EV / BAC"),
]
for col, label, val, full_name, css, sub in forecast_cards:
    with col:
        st.markdown(
            metric_card_html(full_name, val, sub, css),
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 3 – S-Curve chart
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">S-Curve Analysis</div>', unsafe_allow_html=True)
st.plotly_chart(build_scurve(df), use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 4 – CPI / SPI trend bars
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Index Trend Analysis</div>', unsafe_allow_html=True)
st.plotly_chart(build_variance_chart(df), use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 5 – PM Insights
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">PM Insights &amp; Recommendations</div>', unsafe_allow_html=True)

insights = generate_insights(metrics)
ins_cols = st.columns(2)
for i, ins in enumerate(insights):
    with ins_cols[i % 2]:
        st.markdown(
            insight_html(ins["status"], ins["title"], ins["body"]),
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section 6 – Raw data table
# ─────────────────────────────────────────────
with st.expander("Raw Data & Computed Metrics Table", expanded=False):
    display_df = df.copy()
    display_df["CPI"] = (display_df["Earned Value"] / display_df["Actual Cost"]).round(3)
    display_df["SPI"] = (display_df["Earned Value"] / display_df["Planned Value"]).round(3)
    display_df["CV"]  = (display_df["Earned Value"] - display_df["Actual Cost"]).apply(fmt_currency)
    display_df["SV"]  = (display_df["Earned Value"] - display_df["Planned Value"]).apply(fmt_currency)

    for col in ["Planned Value", "Earned Value", "Actual Cost"]:
        display_df[col] = display_df[col].apply(fmt_currency)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )
