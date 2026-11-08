"""Content Impact Lab — synthetic attribution and prioritization sandbox."""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Content Impact Lab", page_icon="📈", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
:root {--studio-paper:#f3f0e8;--studio-ink:#171717;--studio-blue:#2145ff;--studio-acid:#d9ff43;--studio-line:#d8d4c9}
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:var(--studio-paper)!important;color:var(--studio-ink)}
html,body,p,label,button,input,textarea,[data-testid="stMarkdownContainer"]{font-family:Manrope,Arial,sans-serif}
.block-container{max-width:1210px;padding-top:1.4rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#eae7df!important;border-right:1px solid var(--studio-line)}
h1,h2{font-family:Newsreader,Georgia,serif!important;letter-spacing:-.045em!important;color:var(--studio-ink)}
h1{font-size:clamp(2.7rem,5vw,4.6rem)!important;font-weight:500!important}
h3{font-family:Manrope,Arial,sans-serif!important;letter-spacing:-.025em}
div[data-testid="stMetric"]{background:#fffdf8;border:1px solid var(--studio-line);border-radius:14px;padding:18px}
div[data-testid="stAlert"]{border-radius:12px}
div[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
div[data-testid="stButton"] button[kind="primary"]{background:var(--studio-blue);color:white;border-radius:9px;border:0;font-weight:800}
div[data-testid="stButton"] button{border-radius:9px;font-weight:700}
div[data-testid="stLinkButton"] a{border-radius:9px!important;border:1px solid #2145ff!important;color:#2145ff!important;font-weight:800!important}
.studio-kicker{display:inline-block;font:700 11px/1.5 'DM Mono',monospace;letter-spacing:.1em;color:#171717;background:#d9ff43;padding:8px 12px;border-radius:5px;margin:5px 0 14px}
.studio-banner{background:#171c23;border:1px solid #333c47;border-top:5px solid #d9ff43;border-radius:15px;padding:25px 28px;margin:14px 0 28px}
.studio-banner strong{display:block;font:500 clamp(26px,3.5vw,43px)/1.1 Newsreader,Georgia,serif;color:#fff}
.studio-banner span{display:block;color:#e0e4e7;font:500 14px/1.7 Manrope,Arial,sans-serif;margin-top:9px}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="studio-kicker">EDITORIAL INTELLIGENCE / PUBLIC DEMO</div>', unsafe_allow_html=True)
st.markdown('<div class="studio-banner"><strong>Measure the work. Question the assumptions.</strong><span>An interactive, synthetic content investment and attribution sandbox.</span></div>', unsafe_allow_html=True)
st.markdown("**Explore the other tools**")
nav_left, nav_right = st.columns(2)
with nav_left:
    st.link_button("Content Studio — live demo ↗", "https://content-studio-demo.streamlit.app/", use_container_width=True)
with nav_right:
    st.link_button("Narrative Architect — live demo ↗", "https://narrative-architect-app.streamlit.app/", use_container_width=True)
st.caption("The other project's GitHub page includes its deployment details. Direct live-demo links will be added once the public URLs are confirmed.")

st.title("Content Impact Lab")
st.caption("Explore how editorial investment and attribution assumptions change a B2B content portfolio's apparent impact.")
st.warning("All figures are synthetic and illustrative, not actual employer, campaign or Salesforce data.", icon="ℹ️")
data = pd.DataFrame([
    {"Program":"Executive thought leadership","Spend":24000,"Views":62000,"Engaged":7100,"Influenced pipeline":540000,"Sourced pipeline":85000,"Tier":1},
    {"Program":"Flagship original research","Spend":36000,"Views":88000,"Engaged":12400,"Influenced pipeline":880000,"Sourced pipeline":185000,"Tier":1},
    {"Program":"Product launch narrative","Spend":21000,"Views":51000,"Engaged":5800,"Influenced pipeline":690000,"Sourced pipeline":125000,"Tier":2},
    {"Program":"SEO educational articles","Spend":11000,"Views":112000,"Engaged":9600,"Influenced pipeline":260000,"Sourced pipeline":42000,"Tier":3},
    {"Program":"Automated social derivatives","Spend":4000,"Views":74000,"Engaged":3400,"Influenced pipeline":110000,"Sourced pipeline":12000,"Tier":4},
])
with st.sidebar:
    st.header("Attribution assumptions")
    credit = st.slider("Credit applied to influenced pipeline", 0, 100, 20, 5, format="%d%%") / 100
    sourced_credit = st.slider("Credit applied to sourced pipeline", 0, 100, 100, 5, format="%d%%") / 100
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
