"""Narrative Architect — a deterministic editorial story-planning workbench."""
import re
import streamlit as st

st.set_page_config(page_title="Narrative Architect", page_icon="📰", layout="wide")
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
st.markdown('<div class="studio-banner"><strong>Stories start with evidence.</strong><span>A source-first editorial planning workbench with fictional interview notes.</span></div>', unsafe_allow_html=True)
st.markdown("**Explore the other tools**")
nav_left, nav_right = st.columns(2)
with nav_left:
    st.link_button("Content Studio — live demo ↗", "https://content-studio-demo.streamlit.app/", use_container_width=True)
with nav_right:
    st.link_button("Content Impact Lab — live demo ↗", "https://content-impact-lab.streamlit.app/", use_container_width=True)
st.caption("The other project's GitHub page includes its deployment details. Direct live-demo links will be added once the public URLs are confirmed.")

st.title("Narrative Architect")
st.caption("Turn supplied research or interview notes into a source-first story plan. No paid AI API required.")
st.info("PUBLIC DEMO · Preloaded notes are fictional. This planner neither verifies facts nor calls an AI service.")
DEMO_NOTES = "SYNTHETIC EXAMPLE — NOT A REAL INTERVIEW OR CUSTOMER RECORD\nA fictional enterprise technology buyer says its AI pilots stall when teams cannot agree on data ownership and governance.\nIn this invented scenario, the finance leader requests a clear success metric before approving a production rollout.\nThe fictional data leader says teams need a named owner for model quality, security review and operational handoff.\nThe hypothetical pilot team proposes a 60-day evaluation of reliability, user adoption and business impact.\nA potential counterargument is that smaller pilots may succeed without a formal governance program."
if "source_notes" not in st.session_state:
    st.session_state.source_notes = DEMO_NOTES
with st.sidebar:
    st.header("Editorial assignment")
    audience = st.text_input("Reader", "Enterprise technology decision-makers")
    angle = st.selectbox("Story lens", ["News and change", "Customer problem", "Contrarian argument", "Executive perspective"])
    asset = st.selectbox("Output", ["Reported article", "Executive byline", "Research-led feature"])
    st.info("This is a structured editorial planning tool, not generative AI. Review and verify every claim before publication.")
headline = st.text_input("Working story topic", "Why enterprise AI pilots struggle to reach production")
demo_col, clear_col = st.columns(2)
with demo_col:
    if st.button("Load fictional example", use_container_width=True):
        st.session_state.source_notes = DEMO_NOTES
with clear_col:
    if st.button("Clear notes", use_container_width=True):
        st.session_state.source_notes = ""
source = st.text_area("Source notes / fictional sample", key="source_notes", height=220, placeholder="Paste non-confidential notes here. Put each observation on a new line.")
def sentences(text):
    return [s.strip(" •-\t") for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 12]
if st.button("Build story architecture", type="primary"):
    facts = sentences(source)
    if not facts:
        st.warning("Add interview notes or research material first. The planner will not invent evidence.")
    else:
        hook = facts[0]
        supporting = facts[1:4]
        st.subheader("Story architecture")
        st.markdown("**Proposed headline**")
        st.write(headline.strip() or "Working headline needed")
        st.markdown("**Opening hook — sourced starting point**")
        st.write(hook)
        st.markdown("**Nut graf — editorial scaffold (rewrite with verified reporting)**")
        st.write(f"This story examines {headline.lower().rstrip('.')} for {audience.lower()}. The central question is what has changed, why it matters now, and what evidence supports the conclusion.")
        st.markdown("**Inverted-pyramid sequence**")
        st.write("1. Most consequential verified finding and its immediate implications")
        st.write("2. Context, scale, stakes and why the reader should care")
        st.write("3. Supporting evidence, counterarguments and expert perspectives")
        st.write("4. Background, caveats and practical implications")
        st.markdown("**Available supporting material**")
        for item in supporting:
            st.write("•", item)
        st.markdown("**Reporting gaps to close**")
        st.write("• Independent corroboration and a primary-source citation")
        st.write("• A concrete example or data point to quantify the stakes")
        st.write("• An informed counterargument or limitation")
        st.write("• Attribution and permission for any direct quotation")
        st.markdown("**Editorial brief**")
        brief = (f"Asset: {asset}\\nAngle: {angle}\\nAudience: {audience}\\nTopic: {headline}\\n"
                 f"Evidence statements supplied: {len(facts)}\\nSource status: supplied or fictional, unverified")
        st.code(brief, language="text")
        st.download_button("Download editorial brief", brief, file_name="narrative-architect-brief.txt", mime="text/plain")
