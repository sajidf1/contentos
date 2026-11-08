"""Narrative Architect — a deterministic editorial story-planning workbench."""
import re
import streamlit as st

st.set_page_config(page_title="Narrative Architect", page_icon="📰", layout="wide")
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
