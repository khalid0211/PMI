import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# Page config  (MUST be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EVM Calculator · PMI Lahore 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Light-theme palette  (single source of truth)
# ─────────────────────────────────────────────
T = dict(
    bg_app      = "#f1f5fb",
    bg_card     = "#ffffff",
    bg_card2    = "#f8faff",
    bg_sidebar  = "#e8eef8",
    border      = "#d4dced",
    text_primary  = "#1a2035",
    text_secondary= "#5a6880",
    text_sidebar  = "#2a3550",
    accent      = "#3b68d6",
    green       = "#16a34a",
    red         = "#dc2626",
    yellow      = "#d97706",
    blue        = "#2563eb",
    purple      = "#7c3aed",
    plot_bg     = "#ffffff",
    plot_paper  = "#f1f5fb",
    grid        = "#e2e8f4",
    hover_bg    = "#f1f5fb",
)

# ─────────────────────────────────────────────
# CSS injection
# ─────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(f"""
    <style>
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
    [data-testid="stSidebar"] hr {{
        border-color: {T['border']} !important;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}

    /* ── Metric cards ── */
    .metric-card {{
        background: {T['bg_card']};
        border-radius: 14px;
        padding: 20px 22px;
        border: 1px solid {T['border']};
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,.06);
        height: 100%;
        transition: transform .18s, box-shadow .18s;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(0,0,0,.10);
    }}
    .metric-label {{
        font-size: .63rem;
        font-weight: 700;
        letter-spacing: .13em;
        text-transform: uppercase;
        color: {T['text_secondary']};
        margin-bottom: 9px;
    }}
    .metric-value {{
        font-size: 2.05rem;
        font-weight: 800;
        line-height: 1.05;
        font-variant-numeric: tabular-nums;
    }}
    .metric-sub {{
        font-size: .71rem;
        color: {T['text_secondary']};
        margin-top: 7px;
        font-family: 'Consolas', monospace;
    }}
    .metric-badge {{
        display: inline-block;
        font-size: .58rem;
        font-weight: 700;
        letter-spacing: .11em;
        text-transform: uppercase;
        padding: 3px 11px;
        border-radius: 20px;
        margin-top: 9px;
    }}

    /* ── Color helpers ── */
    .c-green  {{ color: {T['green']}; }}
    .c-red    {{ color: {T['red']}; }}
    .c-yellow {{ color: {T['yellow']}; }}
    .c-blue   {{ color: {T['blue']}; }}
    .c-purple {{ color: {T['purple']}; }}

    .badge-green  {{ background:#dcfce7; color:{T['green']}; }}
    .badge-red    {{ background:#fee2e2; color:{T['red']}; }}
    .badge-yellow {{ background:#fef3c7; color:{T['yellow']}; }}

    /* ── Section headers ── */
    .section-header {{
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .11em;
        text-transform: uppercase;
        color: {T['accent']};
        padding-bottom: 9px;
        border-bottom: 2px solid {T['border']};
        margin-bottom: 18px;
        margin-top: 4px;
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
        box-shadow: 0 2px 8px rgba(0,0,0,.04);
    }}
    .insight-card.good {{ border-left-color: {T['green']}; }}
    .insight-card.bad  {{ border-left-color: {T['red']}; }}
    .insight-card.warn {{ border-left-color: {T['yellow']}; }}
    .insight-card.info {{ border-left-color: {T['blue']}; }}
    .insight-title {{
        font-size: .69rem;
        font-weight: 700;
        letter-spacing: .09em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }}
    .insight-card.good .insight-title {{ color: {T['green']}; }}
    .insight-card.bad  .insight-title {{ color: {T['red']}; }}
    .insight-card.warn .insight-title {{ color: {T['yellow']}; }}
    .insight-card.info .insight-title {{ color: {T['blue']}; }}
    .insight-body {{
        font-size: .86rem;
        color: {T['text_secondary']};
        line-height: 1.65;
    }}

    /* ── Health banner ── */
    .health-banner {{
        border-radius: 16px;
        padding: 20px 26px;
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid {T['border']};
        box-shadow: 0 4px 20px rgba(0,0,0,.07);
    }}
    .health-label {{
        font-size: .62rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        color: {T['text_secondary']};
        margin-bottom: 4px;
    }}
    .health-status {{
        font-size: 1.55rem;
        font-weight: 900;
        letter-spacing: .03em;
        line-height: 1.1;
    }}
    .health-desc {{
        font-size: .77rem;
        color: {T['text_secondary']};
        margin-top: 4px;
    }}

    /* ── Progress label ── */
    .prog-label {{
        font-size: .7rem;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
        color: {T['text_secondary']};
        margin-bottom: 5px;
    }}
    hr {{ border-color: {T['border']} !important; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────
def fmt_pkr(val: float) -> str:
    if val != val: return "N/A"          # NaN check
    sign = "-" if val < 0 else ""
    v    = abs(val)
    if v >= 1_000_000: return f"{sign}PKR {v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{sign}PKR {v/1_000:.1f}K"
    return f"{sign}PKR {v:.0f}"

def fmt_idx(val: float) -> str:
    return "N/A" if (val != val or val == float("inf")) else f"{val:.3f}"


# ─────────────────────────────────────────────
# EVM calculations
# ─────────────────────────────────────────────
def compute_evm(bac: float, pv: float, ev: float, ac: float) -> dict:
    cpi  = ev / ac         if ac  != 0 else float("nan")
    spi  = ev / pv         if pv  != 0 else float("nan")
    tcpi = (bac - ev) / (bac - ac) if (bac - ac) != 0 else float("nan")
    eac  = bac / cpi       if (cpi == cpi and cpi != 0) else float("nan")
    etc  = eac - ac        if eac == eac else float("nan")
    vac  = bac - eac       if eac == eac else float("nan")
    pct  = (ev / bac) * 100 if bac != 0 else 0.0
    return dict(
        cv=ev - ac, sv=ev - pv,
        cpi=cpi, spi=spi, tcpi=tcpi,
        eac=eac, etc=etc, vac=vac, pct=pct,
    )


# ─────────────────────────────────────────────
# S-Curve builder
# ─────────────────────────────────────────────
def _sigmoid_curve(n: int, total: float) -> np.ndarray:
    """Cumulative S-curve via logistic function, scaled to [0, total]."""
    x   = np.linspace(-6, 6, n)
    sig = 1 / (1 + np.exp(-x))
    sig = (sig - sig[0]) / (sig[-1] - sig[0])
    return sig * total


def build_scurve(bac, pv, ev, ac, orig_dur, cur_period) -> go.Figure:
    n   = int(orig_dur)
    cur = int(cur_period)
    cpi = ev / ac if ac != 0 else 1.0
    eac = bac / cpi if cpi != 0 else bac

    periods      = list(range(1, n + 1))
    pv_curve     = _sigmoid_curve(n, bac)
    actual_x     = list(range(1, cur + 1))
    ev_actual    = np.linspace(0, ev, cur)
    ac_actual    = np.linspace(0, ac, cur)
    forecast_x   = list(range(cur, n + 1))
    ev_forecast  = np.linspace(ev, bac, max(len(forecast_x), 2))
    ac_forecast  = np.linspace(ac, eac, max(len(forecast_x), 2))

    fig = go.Figure()

    # ── BAC reference line ──────────────────────
    fig.add_hline(
        y=bac, line_dash="dot", line_color=T["text_secondary"], line_width=1.2,
        annotation_text=f" BAC = {fmt_pkr(bac)}",
        annotation_position="right",
        annotation_font=dict(color=T["text_secondary"], size=10),
    )

    # ── PV baseline S-curve ─────────────────────
    fig.add_trace(go.Scatter(
        x=periods, y=pv_curve,
        mode="lines+markers", name="Planned Value (PV)",
        line=dict(color=T["accent"], width=2.5, dash="dot"),
        marker=dict(size=5, symbol="circle-open",
                    line=dict(width=2, color=T["accent"])),
        hovertemplate="Period %{x}<br>PV: PKR %{y:,.0f}<extra></extra>",
    ))

    # ── EV actual ──────────────────────────────
    fig.add_trace(go.Scatter(
        x=actual_x, y=ev_actual,
        mode="lines+markers", name="Earned Value (EV)",
        line=dict(color=T["green"], width=2.5),
        marker=dict(size=7, symbol="diamond", color=T["green"]),
        hovertemplate="Period %{x}<br>EV: PKR %{y:,.0f}<extra></extra>",
    ))

    # ── EV forecast (dashed) ────────────────────
    if len(forecast_x) > 1:
        fig.add_trace(go.Scatter(
            x=forecast_x, y=ev_forecast[:len(forecast_x)],
            mode="lines", name="EV Forecast",
            line=dict(color=T["green"], width=1.8, dash="dash"),
            hovertemplate="Period %{x}<br>EV Forecast: PKR %{y:,.0f}<extra></extra>",
        ))

    # ── AC actual ──────────────────────────────
    fig.add_trace(go.Scatter(
        x=actual_x, y=ac_actual,
        mode="lines+markers", name="Actual Cost (AC)",
        line=dict(color=T["red"], width=2.5),
        marker=dict(size=7, symbol="square", color=T["red"]),
        hovertemplate="Period %{x}<br>AC: PKR %{y:,.0f}<extra></extra>",
    ))

    # ── AC forecast to EAC (dashed) ─────────────
    if len(forecast_x) > 1:
        fig.add_trace(go.Scatter(
            x=forecast_x, y=ac_forecast[:len(forecast_x)],
            mode="lines", name=f"AC → EAC ({fmt_pkr(eac)})",
            line=dict(color=T["red"], width=1.8, dash="dash"),
            hovertemplate="Period %{x}<br>AC Forecast: PKR %{y:,.0f}<extra></extra>",
        ))

    # ── Current period marker ───────────────────
    fig.add_vline(
        x=cur, line_dash="dot", line_color="#94a3b8", line_width=1.5,
        annotation_text=f" Period {cur}  ▲ Now",
        annotation_position="top right",
        annotation_font=dict(color=T["text_secondary"], size=10),
    )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=T["plot_paper"], plot_bgcolor=T["plot_bg"],
        font=dict(family="Segoe UI", color=T["text_primary"], size=12),
        title=dict(
            text="S-Curve  ·  PV vs EV vs AC  (Solid = Actuals  ·  Dashed = Forecast)",
            font=dict(size=14, color=T["text_primary"]), x=0, xanchor="left",
        ),
        xaxis=dict(
            title="Period",
            gridcolor=T["grid"], linecolor=T["border"],
            tickmode="linear", dtick=1 if n <= 18 else (2 if n <= 36 else 3),
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Cumulative Value (PKR)",
            gridcolor=T["grid"], linecolor=T["border"],
            tickprefix="PKR ", tickformat=",.0f", tickfont=dict(size=11),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(255,255,255,.85)", bordercolor=T["border"],
            font=dict(size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                        font=dict(color=T["text_primary"], size=12)),
        margin=dict(l=70, r=40, t=75, b=55),
        height=430,
    )
    return fig


# ─────────────────────────────────────────────
# HTML helpers
# ─────────────────────────────────────────────
def metric_card_html(label, value, formula, css_class,
                     badge_text=None, badge_class=None) -> str:
    badge = (f'<div class="metric-badge {badge_class}">{badge_text}</div>'
             if badge_text else "")
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {css_class}">{value}</div>
        <div class="metric-sub">{formula}</div>
        {badge}
    </div>"""


def insight_html(status, title, body) -> str:
    return f"""
    <div class="insight-card {status}">
        <div class="insight-title">{title}</div>
        <div class="insight-body">{body}</div>
    </div>"""


def health_banner_html(cpi, spi) -> str:
    if cpi >= 1.0 and spi >= 1.0:
        icon, label, desc = "✅", "ON TRACK", \
            "Both cost and schedule indices are within acceptable thresholds."
        bg, clr = "#f0fdf4", T["green"]
    elif cpi < 0.85 or spi < 0.85:
        icon, label, desc = "🚨", "CRITICAL", \
            "Immediate corrective action required — indices critically below threshold."
        bg, clr = "#fff1f2", T["red"]
    else:
        icon, label, desc = "⚠️", "AT RISK", \
            "Performance trending negative. Escalate and monitor closely."
        bg, clr = "#fffbeb", T["yellow"]

    # Pre-compute blocks to avoid f-string quote conflicts (Python < 3.12)
    def _idx_block(key, val):
        return (
            f'<div style="text-align:center;">'
            f'<div style="font-size:.6rem;font-weight:700;letter-spacing:.14em;'
            f'text-transform:uppercase;color:{T["text_secondary"]};">{key}</div>'
            f'<div style="font-size:1.5rem;font-weight:900;color:{clr};">{val:.3f}</div>'
            f'</div>'
        )

    cpi_block = _idx_block("CPI", cpi)
    spi_block = _idx_block("SPI", spi)

    return (
        f'<div class="health-banner" style="background:{bg};border-color:{clr}44;">'
        f'<div style="font-size:2.5rem;line-height:1;">{icon}</div>'
        f'<div>'
        f'<div class="health-label">Overall Project Status</div>'
        f'<div class="health-status" style="color:{clr};">{label}</div>'
        f'<div class="health-desc">{desc}</div>'
        f'</div>'
        f'<div style="margin-left:auto;display:flex;gap:28px;align-items:center;">'
        f'{cpi_block}{spi_block}'
        f'</div>'
        f'</div>'
    )


# ─────────────────────────────────────────────
# PMI Lahore banner
# ─────────────────────────────────────────────
def pmi_banner_html() -> str:
    return """
    <div style="
        background: linear-gradient(135deg,#0d2247 0%,#1a3a6b 50%,#0d2247 100%);
        border:1px solid #2e5fa3; border-radius:14px;
        padding:14px 28px; display:flex; align-items:center;
        justify-content:space-between; margin-bottom:20px;
        position:relative; overflow:hidden;">
        <div style="position:absolute;inset:0;
            background:linear-gradient(90deg,rgba(240,165,0,.12),rgba(240,165,0,0) 55%);
            pointer-events:none;"></div>
        <div style="position:absolute;top:0;right:0;bottom:0;width:4px;
            background:linear-gradient(180deg,#f0a500,#e07b00);
            border-radius:0 14px 14px 0;"></div>
        <div style="display:flex;align-items:center;gap:18px;position:relative;">
            <div style="font-size:2.2rem;">🏆</div>
            <div>
                <div style="font-size:.6rem;font-weight:700;letter-spacing:.18em;
                    text-transform:uppercase;color:#f0a500;margin-bottom:3px;">
                    PMI Lahore Chapter · Official Symposium</div>
                <div style="font-size:1.25rem;font-weight:900;color:#fff;
                    letter-spacing:.03em;">PMI Lahore Symposium 2026</div>
                <div style="font-size:.75rem;color:rgba(255,255,255,.55);margin-top:3px;">
                    Project Management Institute · Advancing the Practice of Project Management</div>
            </div>
        </div>
        <div style="position:relative;">
            <div style="background:rgba(240,165,0,.15);border:1px solid rgba(240,165,0,.35);
                border-radius:20px;padding:5px 16px;font-size:.72rem;font-weight:700;
                letter-spacing:.1em;text-transform:uppercase;color:#f0a500;">
                EVM Calculator</div>
        </div>
    </div>"""


# ─────────────────────────────────────────────
# PM Insights
# ─────────────────────────────────────────────
def generate_insights(m: dict, bac: float, orig_dur: int, cur_period: int) -> list:
    cpi, spi, tcpi = m["cpi"], m["spi"], m["tcpi"]
    cv, sv         = m["cv"],  m["sv"]
    eac, vac, pct  = m["eac"], m["vac"], m["pct"]
    insights       = []

    # ── 1. Overall health ───────────────────
    if cpi >= 1.0 and spi >= 1.0:
        insights.append(("good", "✅ Overall Health — ON TRACK",
            f"Project is performing well: under budget (CPI = {cpi:.3f}) and "
            f"ahead of schedule (SPI = {spi:.3f}). Scope earned stands at "
            f"<b>{pct:.1f}%</b> of the total BAC. Maintain discipline and "
            f"document lessons learned for future projects."))
    elif cpi < 1.0 and spi < 1.0:
        insights.append(("bad", "🚨 Overall Health — CRITICAL: Double Threat",
            f"Project is <b>over budget AND behind schedule</b> simultaneously. "
            f"CPI = {cpi:.3f} (spending PKR {1/cpi:.2f} per PKR 1.00 earned), "
            f"SPI = {spi:.3f}. Convene an emergency recovery board and consider "
            f"re-baselining or invoking Management Reserve."))
    elif cpi < 1.0:
        insights.append(("bad", "💸 Overall Health — OVER BUDGET",
            f"Schedule is holding (SPI = {spi:.3f}), but cost is bleeding — "
            f"spending <b>PKR {1/cpi:.2f} per PKR 1.00</b> of value earned "
            f"(CPI = {cpi:.3f}). Conduct a root-cause analysis on labour, "
            f"procurement, and scope creep immediately."))
    else:
        insights.append(("warn", "⏰ Overall Health — BEHIND SCHEDULE",
            f"Cost is under control (CPI = {cpi:.3f}), but the project is "
            f"lagging the baseline (SPI = {spi:.3f}). Consider fast-tracking "
            f"or crashing critical-path activities. Communicate schedule risk "
            f"to the sponsor without delay."))

    # ── 2. Cost Variance ────────────────────
    cv_s = fmt_pkr(abs(cv))
    if cv >= 0:
        insights.append(("good", "Cost Variance (CV) — Favourable",
            f"You have earned <b>{cv_s} more</b> value than the cost incurred. "
            f"Positive variance signals efficient cost management. Continue "
            f"monitoring for scope creep that could erode this buffer."))
    else:
        insights.append(("bad", "Cost Variance (CV) — Unfavourable",
            f"You have spent <b>{cv_s} more</b> than earned value to date. "
            f"Review labour utilisation, contractor billing, and approved change "
            f"orders. Implement earned-value recovery actions immediately."))

    # ── 3. Schedule Variance ────────────────
    sv_s = fmt_pkr(abs(sv))
    if sv >= 0:
        insights.append(("good", "Schedule Variance (SV) — Ahead of Plan",
            f"Delivered <b>{sv_s} more</b> planned work than expected at this "
            f"point. Buffer is available to absorb future schedule risks or "
            f"resource constraints."))
    else:
        insights.append(("warn", "Schedule Variance (SV) — Behind Plan",
            f"<b>{sv_s} behind</b> the planned schedule. Identify critical-path "
            f"delays and escalate to the project sponsor. Re-sequence activities "
            f"where possible and assign additional resources if the budget permits."))

    # ── 4. TCPI ─────────────────────────────
    if tcpi != tcpi or m.get("ac_breached"):          # NaN or breached
        insights.append(("bad", "TCPI — Original Budget Already Exceeded",
            f"Actual Cost exceeds BAC — TCPI is undefined. Forecasted EAC: "
            f"<b>{fmt_pkr(eac)}</b>. Discuss Management Reserve drawdown or "
            f"formal re-baseline with the project sponsor immediately."))
    elif tcpi <= 1.0:
        insights.append(("good", f"TCPI = {tcpi:.3f} — Target Achievable",
            f"Remaining work must be executed at an efficiency of <b>{tcpi:.3f}</b> "
            f"— at or below current CPI. The original BAC of {fmt_pkr(bac)} "
            f"is within reach if current discipline is maintained."))
    elif tcpi <= 1.1:
        insights.append(("warn", f"TCPI = {tcpi:.3f} — Challenging but Possible",
            f"Remaining work requires <b>{tcpi:.3f}</b> efficiency — higher than "
            f"the current CPI of {cpi:.3f}. Tight but manageable with targeted "
            f"cost-reduction actions and tighter change control."))
    else:
        insights.append(("bad", f"TCPI = {fmt_idx(tcpi)} — BAC is Unrealistic",
            f"Required future efficiency ({fmt_idx(tcpi)}) far exceeds current "
            f"CPI ({cpi:.3f}). Forecasted EAC: <b>{fmt_pkr(eac)}</b> — overrun "
            f"of <b>{fmt_pkr(abs(vac))}</b>. Formal re-baseline is strongly "
            f"recommended."))

    # ── 5. Time forecast ────────────────────
    if spi == spi and spi > 0:
        est_dur = orig_dur / spi
        delay   = est_dur - orig_dur
        if delay > 0:
            insights.append(("warn", f"Time Forecast — ~{delay:.1f} Period(s) Behind",
                f"At current SPI ({spi:.3f}), the project is estimated to complete "
                f"in <b>{est_dur:.1f} periods</b> vs. the planned {orig_dur}. "
                f"Approximate delay: <b>{delay:.1f} period(s)</b>. Explore "
                f"schedule compression options on the critical path."))
        else:
            insights.append(("good", f"Time Forecast — On Track or Early",
                f"At current SPI ({spi:.3f}), estimated completion in "
                f"<b>{est_dur:.1f} periods</b> — at or before the baseline of "
                f"{orig_dur} periods. A schedule buffer of ~{abs(delay):.1f} "
                f"period(s) is available."))

    return insights


# ─────────────────────────────────────────────
# Helper: color class for an index value
# ─────────────────────────────────────────────
def _idx_css(val: float, invert: bool = False) -> str:
    ok = (val >= 1.0) if not invert else (val <= 1.0)
    at_risk = (val >= 0.85) if not invert else (val <= 1.15)
    return "c-green" if ok else ("c-yellow" if at_risk else "c-red")

def _idx_badge(val: float, invert: bool = False):
    ok = (val >= 1.0) if not invert else (val <= 1.0)
    at_risk = (val >= 0.85) if not invert else (val <= 1.15)
    if ok:       return "GOOD",      "badge-green"
    if at_risk:  return "AT RISK",   "badge-yellow"
    return "CRITICAL", "badge-red"


# ═════════════════════════════════════════════
#  MAIN  ──  Layout starts here
# ═════════════════════════════════════════════
inject_css()

# ─────────────────────────────────────────────
# Sidebar  ── Inputs
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:12px 0 18px;">
        <div style="font-size:1.9rem;">📊</div>
        <div style="font-weight:900;font-size:1.05rem;color:{T['text_primary']};
            letter-spacing:.02em;">EVM Calculator</div>
        <div style="font-size:.7rem;color:{T['text_secondary']};margin-top:3px;">
            PMI Lahore Symposium 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📋 Project Parameters**")

    bac = st.number_input(
        "Budget at Completion (BAC)",
        min_value=0.0, value=10_000_000.0, step=100_000.0, format="%.0f",
        help="Total authorised budget for the entire project scope.",
    )
    orig_dur = st.number_input(
        "Original Duration (Periods)",
        min_value=1, max_value=120, value=12, step=1,
        help="Total planned project duration in periods (months / weeks / sprints).",
    )
    cur_period = st.number_input(
        "Current Period",
        min_value=1, max_value=int(orig_dur), value=min(6, int(orig_dur)), step=1,
        help="The reporting period being analysed.",
    )

    st.markdown("---")
    st.markdown("**📈 Current Performance Data**")

    pv = st.number_input(
        "Planned Value (PV)", min_value=0.0,
        value=round(bac * (cur_period / orig_dur) * 0.95, -3),
        step=100_000.0, format="%.0f",
        help="Cumulative budgeted cost of scheduled work (BCWS).",
    )
    ev = st.number_input(
        "Earned Value (EV)", min_value=0.0,
        value=round(bac * (cur_period / orig_dur) * 0.80, -3),
        step=100_000.0, format="%.0f",
        help="Cumulative budgeted value of work actually performed (BCWP).",
    )
    ac = st.number_input(
        "Actual Cost (AC)", min_value=0.0,
        value=round(bac * (cur_period / orig_dur) * 0.90, -3),
        step=100_000.0, format="%.0f",
        help="Cumulative actual cost incurred for work performed (ACWP).",
    )

    st.markdown("---")
    st.markdown("**📐 EVM Formula Reference**")
    st.markdown(
        "| Metric | Formula |\n|---|---|\n"
        "| CV | EV − AC |\n| SV | EV − PV |\n"
        "| CPI | EV / AC |\n| SPI | EV / PV |\n"
        "| TCPI | (BAC−EV)/(BAC−AC) |\n"
        "| EAC | BAC / CPI |\n| ETC | EAC − AC |\n| VAC | BAC − EAC |"
    )
    st.markdown("---")
    st.caption("PMBOK® 7th Ed. · Streamlit + Plotly")


# ─────────────────────────────────────────────
# Compute EVM
# ─────────────────────────────────────────────
m = compute_evm(bac, pv, ev, ac)
m["ac_breached"] = (ac >= bac)


# ─────────────────────────────────────────────
# PMI Lahore Banner
# ─────────────────────────────────────────────
st.markdown(pmi_banner_html(), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Page header  +  Health badge
# ─────────────────────────────────────────────
col_title, col_health = st.columns([1, 1.8])

with col_title:
    st.markdown(
        f"<h1 style='color:{T['text_primary']};font-size:1.7rem;font-weight:900;"
        f"margin-bottom:2px;letter-spacing:-.01em;'>EVM Command Center</h1>"
        f"<p style='color:{T['text_secondary']};font-size:.82rem;margin-top:0;'>"
        f"Earned Value Management · PMBOK 7th Ed. · "
        f"Period <b>{int(cur_period)}</b> of <b>{int(orig_dur)}</b></p>",
        unsafe_allow_html=True,
    )

with col_health:
    st.markdown(health_banner_html(m["cpi"], m["spi"]), unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Progress bar
# ─────────────────────────────────────────────
col_prog, col_bac_label = st.columns([3, 1])
with col_prog:
    st.markdown(
        f"<div class='prog-label'>Project Completion — "
        f"{m['pct']:.1f}% of Scope Earned (EV / BAC)</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(m["pct"] / 100, 1.0))
with col_bac_label:
    st.markdown(
        f"<div style='text-align:right;font-size:.82rem;"
        f"color:{T['text_secondary']};padding-top:8px;'>"
        f"BAC: <span style='color:{T['blue']};font-weight:800;'>"
        f"{fmt_pkr(bac)}</span></div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 1 — Performance Indices
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Performance Indices</div>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, label, val, formula, inv in [
    (c1, "Cost Performance Index",     m["cpi"],  "CPI = EV / AC",            False),
    (c2, "Schedule Performance Index", m["spi"],  "SPI = EV / PV",            False),
    (c3, "To-Complete Perf. Index",    m["tcpi"], "TCPI = (BAC−EV) / (BAC−AC)", True),
]:
    bt, bc = _idx_badge(val, inv)
    with col:
        st.markdown(
            metric_card_html(label, fmt_idx(val), formula,
                             _idx_css(val, inv), bt, bc),
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 2 — Variance Analysis
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📉 Variance Analysis</div>',
            unsafe_allow_html=True)

c4, c5 = st.columns(2)
for col, label, val, formula in [
    (c4, "Cost Variance (CV)",     m["cv"], "CV = EV − AC"),
    (c5, "Schedule Variance (SV)", m["sv"], "SV = EV − PV"),
]:
    css = "c-green" if val >= 0 else "c-red"
    bt  = "FAVOURABLE" if val >= 0 else "UNFAVOURABLE"
    bc  = "badge-green" if val >= 0 else "badge-red"
    with col:
        st.markdown(metric_card_html(label, fmt_pkr(val), formula, css, bt, bc),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 3 — Forecast & Completion
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🔭 Forecast &amp; Completion</div>',
            unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
for col, label, display_val, formula, css in [
    (f1, "Estimate at Completion", fmt_pkr(m["eac"]),      "EAC = BAC / CPI", "c-blue"),
    (f2, "Estimate to Complete",   fmt_pkr(m["etc"]),      "ETC = EAC − AC",  "c-blue"),
    (f3, "Variance at Completion", fmt_pkr(m["vac"]),      "VAC = BAC − EAC",
         "c-green" if m["vac"] >= 0 else "c-red"),
    (f4, "Percent Complete",       f"{m['pct']:.1f}%",     "EV / BAC × 100",  "c-blue"),
]:
    with col:
        st.markdown(metric_card_html(label, display_val, formula, css),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 4 — S-Curve
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📈 S-Curve Analysis</div>',
            unsafe_allow_html=True)

st.plotly_chart(
    build_scurve(bac, pv, ev, ac, int(orig_dur), int(cur_period)),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 5 — PM Insights
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">💡 PM Insights &amp; Recommendations</div>',
            unsafe_allow_html=True)

insights = generate_insights(m, bac, int(orig_dur), int(cur_period))
col_l, col_r = st.columns(2)
for i, (status, title, body) in enumerate(insights):
    with (col_l if i % 2 == 0 else col_r):
        st.markdown(insight_html(status, title, body), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 6 — Input summary & computed values
# ─────────────────────────────────────────────
with st.expander("📋 Input Summary & Computed EVM Values", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Project Inputs**")
        for k, v in [
            ("Budget at Completion (BAC)", fmt_pkr(bac)),
            ("Planned Value (PV)",         fmt_pkr(pv)),
            ("Earned Value (EV)",          fmt_pkr(ev)),
            ("Actual Cost (AC)",           fmt_pkr(ac)),
            ("Original Duration",          f"{int(orig_dur)} periods"),
            ("Current Period",             str(int(cur_period))),
        ]:
            st.markdown(f"**{k}:** {v}")
    with col_b:
        st.markdown("**Computed EVM Metrics**")
        for k, v in [
            ("CPI",          fmt_idx(m["cpi"])),
            ("SPI",          fmt_idx(m["spi"])),
            ("TCPI",         fmt_idx(m["tcpi"])),
            ("CV",           fmt_pkr(m["cv"])),
            ("SV",           fmt_pkr(m["sv"])),
            ("EAC",          fmt_pkr(m["eac"])),
            ("ETC",          fmt_pkr(m["etc"])),
            ("VAC",          fmt_pkr(m["vac"])),
            ("% Complete",   f"{m['pct']:.1f}%"),
        ]:
            st.markdown(f"**{k}:** {v}")
