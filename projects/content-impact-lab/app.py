"""Content Impact Lab — synthetic attribution and prioritization sandbox."""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Content Impact Lab", page_icon="📈", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#f3f0e8!important;color:#171717}
html,body,p,label,button,input,textarea,[data-testid="stMarkdownContainer"]{font-family:Manrope,Arial,sans-serif}
.block-container{max-width:1210px;padding-top:.7rem;padding-bottom:3.5rem}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important}
h2{font-family:Newsreader,Georgia,serif!important;letter-spacing:-.04em!important}
div[data-testid="stMetric"]{background:#fffdf8;border:1px solid #d8d4c9;border-radius:12px;padding:15px}
div[data-testid="stAlert"]{border-radius:11px}
div[data-testid="stButton"] button[kind="primary"]{background:#2145ff;color:#fff;border-radius:100px;border:1px solid #2145ff;font-weight:800}
div[data-testid="stButton"] button{border-radius:100px;font-weight:700}
div[data-testid="stDownloadButton"] button{border-radius:100px}
div[data-baseweb="input"]>div,div[data-baseweb="textarea"]>div,div[data-baseweb="select"]>div{background:#fffefa!important;border-color:#d8d4c9!important;border-radius:9px}

/* Shared Content Studio visual language — blue, ink and warm paper; no lime. */
:root{--studio-acid:#2145ff!important}
.studio-header{border-top:3px solid #2145ff;border-bottom:1px solid #d8d4c9;padding:9px 0 12px;display:flex;align-items:center;justify-content:space-between;gap:14px;margin:0 0 12px}
.studio-brand{font:800 1.2rem/1.3 Manrope,Arial,sans-serif;letter-spacing:-.055em;color:#171717}
.studio-brand b,.studio-brand .brand-symbol{color:#2145ff}
.studio-header-meta{font:500 .63rem/1.5 'DM Mono',monospace;letter-spacing:.09em;color:#68655e;text-transform:uppercase}
.studio-hero{background:#fffdf7!important;color:#171717!important;border:1px solid #d8d4c9;border-left:5px solid #2145ff;border-radius:15px;padding:20px 25px!important;margin:0 0 14px!important;box-shadow:0 8px 28px rgba(23,28,35,.045);position:relative;overflow:hidden}
.studio-hero:after{content:"";position:absolute;width:140px;height:140px;right:-70px;top:-75px;border:24px solid rgba(33,69,255,.06);border-radius:50%;pointer-events:none}
.studio-hero h1{font:500 clamp(1.8rem,3vw,2.65rem)/1.12 Newsreader,Georgia,serif!important;letter-spacing:-.045em!important;color:#171717!important;margin:0 0 8px!important}
.studio-hero p{font:400 .9rem/1.65 Manrope,Arial,sans-serif;color:#48453e!important;max-width:780px;margin:0}
.studio-hero .studio-kicker{font:700 .65rem/1.5 'DM Mono',monospace;letter-spacing:.1em;color:#2145ff!important;background:none!important;padding:0!important;margin:0 0 8px!important}
.studio-steps{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:14px}
.studio-steps span{font:600 .65rem/1.4 'DM Mono',monospace;color:#35332f;background:#f0eee6;border:1px solid #ddd9ce;border-radius:100px;padding:7px 10px}
.studio-steps .studio-arrow{background:none;border:0;padding:0;color:#827d72}
.studio-topnav{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.studio-topnav a{font:700 .78rem/1.4 Manrope,Arial,sans-serif;color:#2145ff;text-decoration:none;border:1px solid #aab6ff;background:#fffefa;border-radius:100px;padding:9px 14px}
.studio-topnav a:hover{background:#e9edff}
@media(max-width:760px){.studio-header-meta{display:none}.studio-hero{padding:20px!important}.studio-topnav a{font-size:.7rem}}

</style>""", unsafe_allow_html=True)
st.markdown("""
<div class="studio-header">
 <div class="studio-brand">Content Impact <b>Lab</b> <span class="brand-symbol" aria-hidden="true">✦</span></div>
 <div class="studio-header-meta">EDITORIAL INTELLIGENCE · 03 / 03</div>
</div>
<div class="studio-hero">
 <div class="studio-kicker">CONTENT MEASUREMENT WORKFLOW</div>
 <h1>From content to clearer impact.</h1>
 <p>Compare fictional B2B content programs, test how sourced versus influenced pipeline credit changes their apparent value, and model where an incremental budget might go. Interactive attribution controls, portfolio comparisons, and a downloadable scenario make the trade-offs visible. All numbers are synthetic; this is a decision sandbox, not an ROI forecast.</p>
 <div class="studio-steps"><span>01 · Compare</span><span class="studio-arrow">→</span><span>02 · Model</span><span class="studio-arrow">→</span><span>03 · Prioritize</span></div>
</div>
<div class="studio-topnav">
 <a href="https://content-studio-demo.streamlit.app/" target="_blank" rel="noopener noreferrer">Content Studio ↗</a>
 <a href="https://narrative-architect-app.streamlit.app/" target="_blank" rel="noopener noreferrer">Narrative Architect ↗</a>
 <a href="https://github.com/sajidf1/contentos" target="_blank" rel="noopener noreferrer">GitHub source ↗</a>
</div>
""", unsafe_allow_html=True)

st.caption("Explore how editorial investment and attribution assumptions change a B2B content portfolio's apparent impact.")
st.warning("All figures are synthetic and illustrative, not actual employer, campaign or Salesforce data.", icon="ℹ️")
data = pd.DataFrame([
    {"Program":"Executive thought leadership","Spend":24000,"Views":62000,"Engaged":7100,"Influenced pipeline":540000,"Sourced pipeline":85000,"Tier":1},
    {"Program":"Flagship original research","Spend":36000,"Views":88000,"Engaged":12400,"Influenced pipeline":880000,"Sourced pipeline":185000,"Tier":1},
    {"Program":"Product launch narrative","Spend":21000,"Views":51000,"Engaged":5800,"Influenced pipeline":690000,"Sourced pipeline":125000,"Tier":2},
    {"Program":"SEO educational articles","Spend":11000,"Views":112000,"Engaged":9600,"Influenced pipeline":260000,"Sourced pipeline":42000,"Tier":3},
    {"Program":"Automated social derivatives","Spend":4000,"Views":74000,"Engaged":3400,"Influenced pipeline":110000,"Sourced pipeline":12000,"Tier":4},
])
st.markdown("### Attribution assumptions")
with st.container(border=True):
    field1, field2, field3 = st.columns(3)
    with field1:
        credit = st.slider("Credit applied to influenced pipeline", 0, 100, 20, 5, format="%d%%") / 100
    with field2:
        sourced_credit = st.slider("Credit applied to sourced pipeline", 0, 100, 100, 5, format="%d%%") / 100
    with field3:
        budget = st.number_input("Incremental investment to allocate ($)", min_value=0, value=20000, step=5000)
st.caption("Influenced and sourced pipeline can overlap. The model is a scenario index, not audited ROI.")
data["Weighted pipeline index"] = data["Influenced pipeline"] * credit + data["Sourced pipeline"] * sourced_credit
data["Index / spend"] = (data["Weighted pipeline index"] / data["Spend"]).round(2)
a,b,c=st.columns(3)
a.metric("Synthetic spend", f"${data['Spend'].sum():,.0f}")
b.metric("Synthetic influenced pipeline", f"${data['Influenced pipeline'].sum():,.0f}")
c.metric("Weighted pipeline index", f"${data['Weighted pipeline index'].sum():,.0f}")
st.subheader("Portfolio comparison")
st.bar_chart(data.set_index("Program")[["Spend","Weighted pipeline index"]])
st.dataframe(data, use_container_width=True, hide_index=True)
st.subheader("Scenario: allocate incremental budget")
top = data.sort_values("Index / spend", ascending=False).iloc[0]
st.write(f"Under these assumptions, **{top['Program']}** has the highest weighted pipeline index per dollar of synthetic spend ({top['Index / spend']:.2f}).")
st.write(f"Allocating ${budget:,.0f} at the same modeled efficiency would imply a **${budget * top['Index / spend']:,.0f} weighted pipeline index**. This is a linear what-if calculation, not a forecast or causal estimate.")
st.download_button("Download synthetic scenario CSV", data.to_csv(index=False), "content-impact-synthetic.csv", "text/csv")
