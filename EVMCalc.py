import streamlit as st

st.set_page_config(page_title="EVM Calculator", layout="centered")

st.markdown("""
<style>
    .block-container { max-width: 720px; padding-top: 2rem; }
    .metric-box {
        background: #1e2230;
        border: 1px solid #2d3347;
        border-radius: 8px;
        padding: 1.1rem 1.4rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #8b92a5;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #8b92a5;
        margin-top: 0.25rem;
    }
    .green  { color: #2ecc71; }
    .red    { color: #e74c3c; }
    .yellow { color: #f1c40f; }
    .white  { color: #f0f2f6; }
    .section-title {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8b92a5;
        margin: 1.8rem 0 0.6rem;
        border-bottom: 1px solid #2d3347;
        padding-bottom: 0.4rem;
    }
    .divider { border-top: 1px solid #2d3347; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("EVM Calculator")
st.caption("Earned Value Management — key performance indicators at a glance")

st.markdown('<div class="section-title">Project Inputs</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    BAC = st.number_input("BAC — Budget at Completion", min_value=0.0, value=500_000.0, step=1_000.0, format="%.2f")
with col2:
    PV  = st.number_input("PV — Planned Value",         min_value=0.0, value=300_000.0, step=1_000.0, format="%.2f")
with col3:
    EV  = st.number_input("EV — Earned Value",          min_value=0.0, value=270_000.0, step=1_000.0, format="%.2f")

AC = st.number_input("AC — Actual Cost", min_value=0.0, value=310_000.0, step=1_000.0, format="%.2f")

# ── Calculations ──────────────────────────────────────────────────────────────
def fmt_currency(v):
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:,.0f}"

def color_ratio(v, invert=False):
    good = v >= 1.0
    if invert:
        good = not good
    return "green" if good else "red"

CPI  = EV / AC         if AC  > 0 else None
SPI  = EV / PV         if PV  > 0 else None
EAC  = BAC / CPI       if CPI and CPI > 0 else None
ETC  = (EAC - AC)      if EAC is not None else None
VAC  = (BAC - EAC)     if EAC is not None else None
CV   = EV - AC
SV   = EV - PV

budget_exhausted = AC >= BAC
if budget_exhausted:
    TCPI = None
else:
    rem_work = BAC - EV
    rem_budget = BAC - AC
    TCPI = rem_work / rem_budget if rem_budget != 0 else None

# ── Efficiency Indices ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Efficiency Indices</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

def render_metric(col, label, value, sub, color_class):
    col.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

with c1:
    if CPI is not None:
        render_metric(c1, "CPI", f"{CPI:.3f}", "Cost efficiency", color_ratio(CPI))
    else:
        render_metric(c1, "CPI", "N/A", "AC is zero", "white")

with c2:
    if SPI is not None:
        render_metric(c2, "SPI", f"{SPI:.3f}", "Schedule efficiency", color_ratio(SPI))
    else:
        render_metric(c2, "SPI", "N/A", "PV is zero", "white")

with c3:
    if budget_exhausted:
        render_metric(c3, "TCPI", "—", "Budget exhausted", "red")
    elif TCPI is not None:
        render_metric(c3, "TCPI", f"{TCPI:.3f}", "Efficiency needed to finish", color_ratio(TCPI, invert=True))
    else:
        render_metric(c3, "TCPI", "N/A", "Cannot compute", "white")

# ── Forecast ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Forecast</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

with f1:
    val  = fmt_currency(EAC) if EAC is not None else "N/A"
    clr  = color_ratio(BAC / EAC, invert=False) if EAC and EAC > 0 else "white"
    render_metric(f1, "EAC", val, "Estimate at Completion", clr)

with f2:
    val = fmt_currency(ETC) if ETC is not None else "N/A"
    clr = "green" if ETC is not None and ETC >= 0 else "red"
    render_metric(f2, "ETC", val, "Estimate to Complete", clr)

with f3:
    val = fmt_currency(VAC) if VAC is not None else "N/A"
    clr = "green" if VAC is not None and VAC >= 0 else "red"
    render_metric(f3, "VAC", val, "Variance at Completion", clr)

# ── Variance ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Current Variance</div>', unsafe_allow_html=True)

v1, v2 = st.columns(2)
with v1:
    render_metric(v1, "CV — Cost Variance", fmt_currency(CV),
                  "EV − AC", "green" if CV >= 0 else "red")
with v2:
    render_metric(v2, "SV — Schedule Variance", fmt_currency(SV),
                  "EV − PV", "green" if SV >= 0 else "red")

# ── Status summary ────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if CPI is not None and SPI is not None:
    if CPI >= 1.0 and SPI >= 1.0:
        badge, badge_color = "ON TRACK", "#2ecc71"
    elif CPI < 0.85 or SPI < 0.85:
        badge, badge_color = "CRITICAL", "#e74c3c"
    else:
        badge, badge_color = "AT RISK", "#f1c40f"

    st.markdown(f"""
    <div style="text-align:center; padding: 0.6rem;">
        <span style="background:{badge_color}22; color:{badge_color};
                     border:1px solid {badge_color}55; border-radius:6px;
                     padding:0.4rem 1.2rem; font-size:0.85rem;
                     font-weight:700; letter-spacing:0.1em;">
            {badge}
        </span>
        <div style="color:#8b92a5; font-size:0.75rem; margin-top:0.5rem;">
            CPI {CPI:.2f} &nbsp;|&nbsp; SPI {SPI:.2f}
        </div>
    </div>""", unsafe_allow_html=True)
