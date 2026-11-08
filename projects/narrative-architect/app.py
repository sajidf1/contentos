"""Narrative Architect — a deterministic editorial story-planning workbench."""
import re
import streamlit as st

st.set_page_config(page_title="Narrative Architect", page_icon="📰", layout="wide")
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
 <div class="studio-brand">Narrative <b>Architect</b> <span class="brand-symbol" aria-hidden="true">✦</span></div>
 <div class="studio-header-meta">EDITORIAL INTELLIGENCE · 02 / 03</div>
</div>
<div class="studio-hero">
 <div class="studio-kicker">SOURCE-FIRST STORY PLANNING</div>
 <h1>From notes to a stronger story.</h1>
 <p>Turn interview notes, research, or a rough editorial idea into a source-first story architecture. The planner identifies a starting hook, structures the narrative, surfaces evidence and reporting gaps, and creates a downloadable editorial brief. It uses your supplied material—not invented quotes or AI-generated reporting.</p>
 <div class="studio-steps"><span>01 · Source</span><span class="studio-arrow">→</span><span>02 · Structure</span><span class="studio-arrow">→</span><span>03 · Verify</span></div>
</div>
<div class="studio-topnav">
 <a href="https://content-studio-demo.streamlit.app/" target="_blank" rel="noopener noreferrer">Content Studio ↗</a>
 <a href="https://content-impact-lab.streamlit.app/" target="_blank" rel="noopener noreferrer">Content Impact Lab ↗</a>
 <a href="https://github.com/sajidf1/contentos" target="_blank" rel="noopener noreferrer">GitHub source ↗</a>
</div>
""", unsafe_allow_html=True)

st.caption("Turn supplied research or interview notes into a source-first story plan. No paid AI API required.")
st.info("PUBLIC DEMO · Preloaded notes are fictional. This planner neither verifies facts nor calls an AI service.")
DEMO_NOTES = "SYNTHETIC EXAMPLE — NOT A REAL INTERVIEW OR CUSTOMER RECORD\nA fictional enterprise technology buyer says its AI pilots stall when teams cannot agree on data ownership and governance.\nIn this invented scenario, the finance leader requests a clear success metric before approving a production rollout.\nThe fictional data leader says teams need a named owner for model quality, security review and operational handoff.\nThe hypothetical pilot team proposes a 60-day evaluation of reliability, user adoption and business impact.\nA potential counterargument is that smaller pilots may succeed without a formal governance program."
if "source_notes" not in st.session_state:
    st.session_state.source_notes = DEMO_NOTES
st.markdown("### Editorial assignment")
with st.container(border=True):
    field1, field2, field3 = st.columns(3)
    with field1:
        audience = st.text_input("Reader", "Enterprise technology decision-makers")
    with field2:
        angle = st.selectbox("Story lens", ["News and change", "Customer problem", "Contrarian argument", "Executive perspective"])
    with field3:
        asset = st.selectbox("Output", ["Reported article", "Executive byline", "Research-led feature"])
st.caption("This is a structured editorial planning tool, not generative AI. Verify every claim before publication.")
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
