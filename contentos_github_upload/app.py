import json
from io import BytesIO
import os
from pathlib import Path

import streamlit as st
from docx import Document

from contentos.core import Request, load_json
from contentos.brief_sources import BriefSourceError, extract_upload, extract_public_google_doc
from contentos.engine import DRAFT_MODEL, JUDGE_MODEL, run_demo, run_live
from contentos.guard import BudgetExceeded, DailyCap, Meter

st.set_page_config(page_title='Content Studio | Workflow Demo', page_icon='✦', layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
:root {--studio-paper:#f3f0e8;--studio-ink:#171717;--studio-blue:#2145ff;--studio-acid:#d9ff43;--studio-line:#d8d4c9;}
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background:var(--studio-paper) !important;color:var(--studio-ink);}
html, body, p, label, button, input, textarea, [data-testid="stMarkdownContainer"] {font-family:'Manrope',Arial,sans-serif;}
.block-container {max-width:1210px;padding-top:1rem;padding-bottom:3.5rem;}
[data-testid="stHeader"] {background:transparent !important;}
[data-testid="stSidebar"] {background:#eae7df !important;border-right:1px solid var(--studio-line);}
[data-testid="stSidebar"] .block-container {padding-top:1.4rem;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {font-size:.84rem;}
[data-testid="stVerticalBlock"] {gap:.7rem;}
h1,h2,h3 {color:var(--studio-ink);letter-spacing:-.045em !important;}
h1,h2 {font-family:'Newsreader',Georgia,serif !important;font-weight:500 !important;}
h3 {font-family:'Manrope',Arial,sans-serif;font-weight:750 !important;}
[data-testid="stHeadingWithActionElements"] h2 {font-size:clamp(1.65rem,2.5vw,2.2rem);margin-top:.6rem;}
[data-testid="stCaptionContainer"] {color:#68655e;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:var(--studio-line) !important;border-radius:14px !important;background:rgba(255,255,255,.52);}
[data-testid="stForm"] {border:1px solid var(--studio-line);border-radius:16px;background:rgba(255,255,255,.48);padding:1.1rem 1.35rem;}
[data-testid="stForm"] label {font-size:.83rem;font-weight:700;}
div[data-baseweb="input"] > div,div[data-baseweb="textarea"] > div,div[data-baseweb="select"] > div {background:#fffefa;border-color:var(--studio-line);border-radius:9px;}
div[data-testid="stMetric"] {border:1px solid var(--studio-line);background:#fffefa;border-radius:12px;padding:14px 17px;}
[data-testid="stMetricValue"] {font-family:'Newsreader',Georgia,serif;font-size:2.2rem;}
div.stButton > button[kind="primary"],div.stFormSubmitButton > button[kind="primary"] {background:var(--studio-blue);border:1px solid var(--studio-blue);color:white;border-radius:100px;font-weight:800;padding:.7rem 1.7rem;min-height:46px;box-shadow:none;}
div.stButton > button[kind="primary"]:hover,div.stFormSubmitButton > button[kind="primary"]:hover {background:#142fc4;border-color:#142fc4;color:white;}
[data-testid="stDownloadButton"] button {border-radius:100px;border-color:#bcb7aa;background:#fffefa;font-weight:700;}
[data-testid="stExpander"] {border:1px solid var(--studio-line);border-radius:12px;background:rgba(255,255,255,.4);}
[data-testid="stProgressBar"] > div > div {background:var(--studio-blue);}
[data-testid="stAlert"] {border-radius:11px;}
.studio-header{border-top:3px solid var(--studio-blue);border-bottom:1px solid var(--studio-line);padding:12px 0 14px;display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:13px;}
.studio-brand{font-weight:800;letter-spacing:-.055em;font-size:1.2rem;}
.studio-brand b{color:var(--studio-blue);}
.studio-header-meta{font-family:'DM Mono',monospace;font-size:.63rem;letter-spacing:.11em;color:#68655e;text-transform:uppercase;}
.studio-hero{background:#171c23;color:#f3f0e8;border-radius:15px;padding:clamp(23px,3.2vw,40px);margin-bottom:16px;position:relative;overflow:hidden;}
.studio-hero:after{content:'';position:absolute;width:190px;height:190px;right:-85px;top:-105px;border:30px solid rgba(217,255,67,.13);border-radius:50%;pointer-events:none;}
.studio-kicker{font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.12em;color:var(--studio-acid);margin-bottom:10px;}
.studio-hero h1{font-family:'Newsreader',Georgia,serif !important;color:#f3f0e8;font-weight:500;font-size:clamp(2.15rem,4vw,3.3rem);line-height:1.04;margin:0 0 12px;letter-spacing:-.05em;}
.studio-hero p{color:#d5d5d2;font-size:.9rem;line-height:1.65;max-width:730px;margin:0;}
.studio-hero strong{color:#fff;}
.studio-footnote{font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.035em;color:#79756d;margin:4px 0 14px;}
@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem;padding-top:.7rem}.studio-header-meta{display:none}.studio-hero{padding:24px 20px}.studio-hero h1{font-size:2.2rem}[data-testid="stForm"]{padding:.85rem}}

/* Contrast and accessibility: Streamlit's dark-theme tokens can leak into light surfaces. */
[data-testid="stSidebar"],[data-testid="stSidebar"] *:not(svg):not(path) {color:#24231f;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#373630 !important;opacity:1 !important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#5a574f !important;}
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label span,
[data-testid="stSidebar"] [role="radiogroup"] label p {color:#22211f !important;opacity:1 !important;}
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {background:#2145ff !important;border-color:#2145ff !important;}
[data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stTickBar"] {color:#49463f !important;}
[data-testid="stSidebar"] hr {border-color:#c8c3b8;}
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] p {color:#615d55 !important;opacity:1 !important;}
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] p {color:#625e55 !important;}
[data-testid="stAppViewContainer"] [data-testid="stForm"] label,
[data-testid="stAppViewContainer"] [data-testid="stForm"] label p,
[data-testid="stAppViewContainer"] [data-testid="stForm"] [data-testid="stWidgetLabel"] {color:#292722 !important;opacity:1 !important;}
[data-testid="stAppViewContainer"] [data-testid="stForm"] input,
[data-testid="stAppViewContainer"] [data-testid="stForm"] textarea {color:#24231f !important;-webkit-text-fill-color:#24231f;}
[data-testid="stAppViewContainer"] [data-testid="stForm"] input::placeholder,
[data-testid="stAppViewContainer"] [data-testid="stForm"] textarea::placeholder {color:#767168 !important;opacity:1;}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary,
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {color:#24231f !important;}
[data-testid="stAppViewContainer"] [data-testid="stMetricLabel"] p {color:#4f4b44 !important;}
[data-testid="stAppViewContainer"] [data-testid="stMetricValue"] {color:#171717 !important;}
.studio-hero p {color:#e5e5df !important;}
.studio-hero .studio-kicker {color:#d9ff43 !important;}

/* Welcome panel: lighter editorial card, stronger hierarchy and contrast. */
.studio-hero{background:#fffdf7 !important;color:#171717 !important;border:1px solid #d8d4c9;border-left:5px solid #2145ff;box-shadow:0 8px 28px rgba(23,28,35,.045);padding:clamp(22px,2.7vw,34px) !important;}
.studio-hero:after{width:140px;height:140px;right:-70px;top:-75px;border:24px solid rgba(33,69,255,.06);}
.studio-hero h1{color:#171717 !important;font-size:clamp(2rem,3.1vw,2.85rem) !important;line-height:1.1 !important;margin:0 0 12px !important;}
.studio-hero p{color:#48453e !important;font-size:.94rem;line-height:1.75;max-width:760px;}
.studio-hero strong{color:#171717 !important;}
.studio-hero .studio-kicker{color:#2145ff !important;font-weight:700;letter-spacing:.1em;}
.studio-hero .studio-steps{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:20px;}
.studio-hero .studio-steps span{font-family:'DM Mono',monospace;font-size:.67rem;color:#35332f;background:#f0eee6;border:1px solid #ddd9ce;padding:8px 11px;border-radius:100px;}
.studio-hero .studio-steps .studio-arrow{background:none;border:0;padding:0;color:#827d72;}
@media(max-width:760px){.studio-hero .studio-steps{gap:6px}.studio-hero .studio-steps span{font-size:.6rem;padding:7px 9px}}

/* Form widgets: explicitly reset Streamlit/BaseWeb dark-theme surfaces. */
:root {
  color-scheme:light;
  --primary-color:#2145ff;
  --background-color:#f3f0e8;
  --secondary-background-color:#fffdf7;
  --text-color:#171717;
}
[data-testid="stAppViewContainer"] [data-baseweb="input"],
[data-testid="stAppViewContainer"] [data-baseweb="base-input"],
[data-testid="stAppViewContainer"] [data-baseweb="textarea"],
[data-testid="stAppViewContainer"] [data-baseweb="select"],
[data-testid="stAppViewContainer"] [data-baseweb="input"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="base-input"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="textarea"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="select"] [role="combobox"],
[data-testid="stAppViewContainer"] [data-baseweb="input"] input,
[data-testid="stAppViewContainer"] [data-baseweb="textarea"] textarea {
  background-color:#fffdf7 !important;
  color:#171717 !important;
  -webkit-text-fill-color:#171717 !important;
  caret-color:#2145ff !important;
  color-scheme:light !important;
}
[data-testid="stAppViewContainer"] [data-baseweb="select"] *,
[data-testid="stAppViewContainer"] [data-baseweb="input"] *,
[data-testid="stAppViewContainer"] [data-baseweb="textarea"] * {
  color:#171717 !important;
}
[data-testid="stAppViewContainer"] [data-baseweb="select"] svg,
[data-testid="stAppViewContainer"] [data-baseweb="input"] svg {fill:#4b4943 !important;}
[data-testid="stAppViewContainer"] [data-baseweb="input"] input::placeholder,
[data-testid="stAppViewContainer"] [data-baseweb="textarea"] textarea::placeholder {
  color:#77736a !important;
  -webkit-text-fill-color:#77736a !important;
  opacity:1 !important;
}
[data-testid="stAppViewContainer"] [data-baseweb="select"] [aria-disabled="true"] {opacity:.6;}
[data-testid="stAppViewContainer"] [data-testid="stNumberInput"] button {
  background:#eeece5 !important;color:#25231f !important;border-color:#d8d4c9 !important;
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInput"] button svg {fill:#25231f !important;color:#25231f !important;}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] details,
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary,
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary * {
  background:#f1eee6 !important;color:#25231f !important;
}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] [data-testid="stVerticalBlock"] {
  background:#fffdf7;color:#171717;
}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary svg {fill:#25231f !important;color:#25231f !important;}
[data-testid="stAppViewContainer"] [data-testid="stForm"] [data-testid="stCheckbox"] label p {color:#25231f !important;}
[data-testid="stAppViewContainer"] [data-testid="stForm"] [data-testid="stCheckbox"] [aria-checked="true"] {background-color:#2145ff !important;border-color:#2145ff !important;}
/* Dropdown options render in a portal outside the form. */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"],[data-baseweb="menu"] li {
  background:#fffdf7 !important;color:#171717 !important;
}
[data-baseweb="popover"] [role="option"]:hover,[data-baseweb="menu"] li:hover {background:#ece9e0 !important;}
</style>""", unsafe_allow_html=True)
SAMPLE = Path(__file__).parent / 'data' / 'sample_run.json'
MODES = ['Recorded Claude sample (free)', 'Demo templates (free)', 'Live Claude (access code)']


def cfg(name: str, default: str = '') -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name, default)


@st.cache_resource
def daily_cap() -> DailyCap:
    return DailyCap(int(cfg('DAILY_RUN_CAP', '25')))


def workflow_overview(res: dict | None) -> None:
    """Compact, accessible workflow overview."""
    st.markdown('### The workflow')
    completed = res is not None
    passed = bool(res and res['passed'])
    attempts = len(res['attempts']) if res else 0
    steps = [
        ('01', 'Intake', 'Creative brief', completed),
        ('02', 'Strategy', 'GTM & audience', completed),
        ('03', 'Draft', 'Asset skill', completed),
        ('04', 'Review', 'Quality gates', completed),
        ('05', 'Derivatives', 'Channel assets', passed),
        ('06', 'Handoff', 'Editorial queue', passed),
    ]
    cols = st.columns(6, gap='small')
    for col, (number, title, detail, active) in zip(cols, steps):
        with col:
            with st.container(border=True):
                st.caption(number + ('  ✓' if active else ''))
                st.markdown('**' + title + '**')
                st.caption(detail)
    if completed:
        if passed:
            st.success(f'Quality gate passed · {attempts} evaluation attempt(s) · Simulated editorial handoff ready')
        else:
            st.warning(f'Quality gate not passed after {attempts} evaluation attempt(s) · Human review required')
    else:
        st.caption('Complete the creative brief and run the workflow to see each stage progress.')


def scorecard(att: dict) -> None:
    cols = st.columns(3)
    for i, (name, d) in enumerate(att['dimensions'].items()):
        with cols[i % 3], st.container(border=True):
            st.metric(name, f'{d["score"]}/100')
            st.progress(d['score'] / 100)
            if d.get('evidence'):
                st.caption(d['evidence'])
            if d.get('fix'):
                st.caption(f'Fix: {d["fix"]}')


def docx_bytes(markdown: str) -> bytes:
    doc = Document()
    for line in markdown.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith('### '):
            doc.add_heading(clean[4:], level=3)
        elif clean.startswith('## '):
            doc.add_heading(clean[3:], level=2)
        elif clean.startswith('# '):
            doc.add_heading(clean[2:], level=1)
        elif clean.startswith(('- ', '* ')):
            doc.add_paragraph(clean[2:], style='List Bullet')
        elif len(clean) > 3 and clean[0].isdigit() and '. ' in clean[:4]:
            doc.add_paragraph(clean.split('. ', 1)[1], style='List Number')
        else:
            doc.add_paragraph(clean)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def show(res: dict) -> None:
    with st.expander('01 / Strategy intelligence · fictional GTM context'):
        st.json(res['context'])
    best = next((a for a in res['attempts'] if a['attempt'] == res['best_attempt']), res['attempts'][-1])
    st.markdown('### 02 / Editorial quality review')
    c1, c2, c3 = st.columns(3)
    c1.metric('Overall score', f'{res["score"]}/100', 'Pass' if res['passed'] else 'Needs human revision', delta_color='off')
    c2.metric('Attempts', len(res['attempts']))
    c3.metric('Evaluator', best['evaluator'])
    st.caption('Pass = score above 80 with no claim-safety gate. Scores are illustrative AI/heuristic signals, not PMM or legal approval.')
    if best.get('gate'):
        st.warning(f'Gate triggered: {best["gate"]}')
    if res.get('truncated'):
        st.warning('Session budget reached before the loop finished; showing the best draft so far.')
    scorecard(best)
    if len(res['attempts']) > 1:
        st.line_chart({'score': [a['score'] for a in res['attempts']]})
    with st.expander('Attempt history'):
        st.json(res['attempts'])
    st.markdown('### 03 / Your draft')
    actual_words = len(res['draft'].split())
    target_words = res.get('request', {}).get('target_words', 0)
    st.caption(f'Draft length: {actual_words:,} words' + (f' · Requested: {target_words:,} words' if target_words else ''))
    st.markdown(res['draft'])
    st.download_button('Download draft (.md)', res['draft'], file_name='contentos-draft.md', mime='text/markdown')
    st.download_button('Download for Google Docs (.docx)', docx_bytes(res['draft']), file_name='contentos-draft.docx', mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    st.caption('To edit in Google Docs: download the .docx, upload it to your Google Drive, and open it with Google Docs. No account connection or billing required in this app.')
    st.markdown('### 04 / Channel derivatives')
    if res['derivatives']:
        for name, copy in res['derivatives'].items():
            with st.expander(name):
                st.write(copy)
    else:
        st.caption('Derivatives are generated only after a draft passes review.')
    st.markdown('### 05 / Editorial handoff (simulated)')
    if res['handoff']:
        a, b = st.columns(2)
        a.json(res['handoff']['ticket'])
        b.code(res['handoff']['slack'], language=None)
    else:
        st.warning('Below threshold: no handoff. Human revision required.')
    if res.get('models'):
        st.caption(f'Models: draft={res["models"]["draft"]}, judge={res["models"]["judge"]} · usage={res["usage"]}')


# ---------------- sidebar ----------------
if 'meter' not in st.session_state:
    st.session_state.meter = Meter(int(cfg('SESSION_TOKEN_LIMIT', '80000')))
if 'live_runs' not in st.session_state:
    st.session_state.live_runs = 0
require_code = cfg('REQUIRE_ACCESS_CODE', 'true').lower() != 'false'  # set false only if the app itself is private
live_ready = (cfg('ENABLE_LIVE_MODE').lower() == 'true' and bool(cfg('ANTHROPIC_API_KEY'))
              and (bool(cfg('ACCESS_CODE')) or not require_code))

st.markdown("""
<div class="studio-header"><div class="studio-brand">Content <b>Studio</b> <span aria-hidden="true">✦</span></div><div class="studio-header-meta">AN AGENTIC CONTENT OPERATIONS DEMO · 01 / 06</div></div>
<div class="studio-hero">
  <div class="studio-kicker">EDITORIAL SYSTEMS / INTERACTIVE WORKFLOW</div>
  <h1>Welcome to Content Studio.</h1>
  <p>Turn a creative brief into a structured content workflow. Set your audience and goals, generate a draft, review its quality, and prepare channel-specific assets for editorial handoff.</p>
  <div class="studio-steps" aria-label="Content workflow summary"><span>01 · Plan</span><span class="studio-arrow" aria-hidden="true">→</span><span>02 · Write</span><span class="studio-arrow" aria-hidden="true">→</span><span>03 · Review</span><span class="studio-arrow" aria-hidden="true">→</span><span>04 · Repurpose</span></div>
</div>
""", unsafe_allow_html=True)
st.caption('START HERE · Select Demo templates (free) in the sidebar, choose a content type, complete the brief, and run the workflow.')
with st.expander('About this demonstration · fictional data and review limitations'):
    st.write('All personas, messaging, reference examples, reviewers, assignments, and handoffs are fictional or synthetic. Scores are illustrative, not actual legal or editorial approvals. Slack and Wrike handoffs are simulated. Google Docs-compatible downloads are local exports; the app does not access visitors’ Google accounts. The free mode uses templates, not a live AI model.')


workflow_overview(st.session_state.get('res'))

with st.sidebar:
    st.markdown('**WORKSPACE SETTINGS**')
    mode = st.radio('Execution mode', MODES, index=1)
    code = ''
    if mode == MODES[2]:
        if not live_ready:
            st.warning('Live mode is not enabled on this deployment.')
        else:
            if require_code:
                code = st.text_input('Access code', type='password')
            st.caption(f'Session tokens used: {st.session_state.meter.used:,} / {st.session_state.meter.token_limit:,}')
    max_rev = st.slider('Max revision loops', 0, 3, 2, disabled=mode != MODES[2])
    st.divider()
    st.caption('Pipeline: Intake → GTM → Draft → Evaluate → Revise (bounded) → Derivatives → Handoff. Human review is always required before publishing.')

# ---------------- intake ----------------
st.markdown('### Build your creative brief')
st.caption('Set the audience, format and editorial direction. Optional controls let you tailor the output.')
motions = load_json('motions.json')
with st.form('request'):
    a, b = st.columns(2)
    with a:
        asset = st.selectbox('Primary content type', ['Blog post', 'Video script', 'eBook', 'Landing page', 'Ad copy', 'Social post'])
        title = st.text_input('Title', 'Building the business case for a unified data platform', max_chars=140)
        motion = st.selectbox('GTM motion', list(motions))
    with b:
        funnel = st.selectbox('Funnel stage', ['Awareness', 'Consideration', 'Decision'], index=1)
        st.markdown('**Derivative assets** · select any')
        d1, d2 = st.columns(2)
        with d1:
            linkedin = st.checkbox('LinkedIn posts', value=False)
            video = st.checkbox('Video script')
            email = st.checkbox('Email nurture')
        with d2:
            ads = st.checkbox('Ad copy', value=False)
            ebook = st.checkbox('eBook')
            onepager = st.checkbox('Sales one-pager')
        derivs = [name for name, selected in [('LinkedIn posts', linkedin), ('Ad copy', ads), ('Email nurture', email), ('Sales one-pager', onepager), ('Video script', video), ('eBook', ebook)] if selected]
        direction = st.text_area('Outline or creative direction', 'Focus on operational efficiency and measurable outcomes.', max_chars=1200)
        source_file = st.file_uploader('Attach a brief (PDF or Word .docx)', type=['pdf', 'docx'], help='Extracts selectable text; max 8 MB, 50 PDF pages.')
        source_url = st.text_input('Or link a Google Doc (link-accessible)', placeholder='https://docs.google.com/document/d/…/edit', help='Document must allow link-based text export. Private Docs require uploading a PDF or DOCX instead.')
    with st.expander('Creative brief · optional controls', expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            target_words = st.number_input('Target word count (0 = asset default)', min_value=0, max_value=10000, value=0, step=100)
            tone = st.selectbox('Tone of voice', ['Clear and professional', 'Executive and authoritative', 'Conversational', 'Bold and persuasive', 'Educational and approachable', 'Thought leadership'])
            audience = st.text_input('Audience details (optional)', placeholder='e.g. CFOs at mid-market SaaS companies')
        with c2:
            style = st.selectbox('Writing style', ['Practical and concise', 'Narrative and story-driven', 'Analytical and evidence-led', 'Step-by-step how-to', 'Editorial and opinionated'])
            outline = st.text_area('Outline (optional)', placeholder='Paste section headings or a detailed outline', height=120)
            additional_instructions = st.text_area('Additional instructions (optional)', placeholder='Must-cover points, things to avoid, preferred CTA', height=90)
    submitted = st.form_submit_button('Run content workflow  →', type='primary')

if submitted:
    if not title.strip():
        st.error('A title is required.')
        st.stop()
    source_text = ''
    if source_file is not None or source_url.strip():
        try:
            if source_file is not None:
                source_text += '\\n\\nUploaded brief (' + source_file.name + '):\\n' + extract_upload(source_file)
            if source_url.strip():
                source_text += '\\n\\nLinked Google Doc brief:\\n' + extract_public_google_doc(source_url)
        except BriefSourceError as exc:
            st.error(f'Could not use the attached brief: {exc}')
            st.stop()
    combined_direction = (direction.strip() + source_text).strip()
    if source_text:
        st.success(f'Brief extracted ({len(source_text):,} characters) and added to creative direction.')
    req = Request(title.strip(), asset, motion, funnel, combined_direction, derivs,
                  target_words=int(target_words), outline=outline.strip(), tone=tone,
                  style=style, audience=audience.strip(), additional_instructions=additional_instructions.strip())
    if mode == MODES[0]:
        if SAMPLE.exists():
            st.session_state.res = json.loads(SAMPLE.read_text(encoding='utf-8'))
            st.session_state.res['recorded'] = True
        else:
            st.info('No recorded sample is bundled yet; showing the deterministic demo instead.')
            st.session_state.res = run_demo(req)
    elif mode == MODES[1]:
        st.session_state.res = run_demo(req)
    else:
        if not live_ready:
            st.error('Live mode is not enabled on this deployment.')
            st.stop()
        if require_code and code != cfg('ACCESS_CODE'):
            st.error('Enter the access code to use live Claude.')
            st.stop()
        if st.session_state.live_runs >= int(cfg('SESSION_RUN_LIMIT', '3')):
            st.error('Session run limit reached. Use the recorded sample or demo mode.')
            st.stop()
        if not daily_cap().try_acquire():
            st.error('The daily live-run cap has been reached. Try the recorded sample.')
            st.stop()
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=cfg('ANTHROPIC_API_KEY'), timeout=60.0, max_retries=1)
            with st.status('Running agentic pipeline…', expanded=True) as status:
                st.session_state.res = run_live(req, client, st.session_state.meter, max_rev, on_event=st.write)
                status.update(label='Pipeline complete', state='complete')
            st.session_state.live_runs += 1
        except BudgetExceeded:
            st.error('Session token budget reached before a draft was produced.')
            st.stop()
        except Exception as exc:
            st.error(f'Live generation failed: {type(exc).__name__}. Check server configuration and provider limits.')
            st.stop()

if 'res' in st.session_state:
    if st.session_state.res.get('recorded'):
        st.info(f'Showing a recorded live Claude run ({st.session_state.res.get("recorded_at", "date unknown")}). '
                'Your form inputs apply only in Demo or Live mode.')
    show(st.session_state.res)
else:
    st.caption('Complete the brief above and select Run content workflow to preview the results.')

with st.expander('Reference library and implementation notes'):
    st.json(load_json('reference_library.json'))
    st.markdown('Reference library entries are fictional metadata, not retrieval-augmented generation. '
                'Published portfolio links are reference metadata only, not full-text retrieval or automated grading. '
                'Handoffs are simulated; no outbound Wrike or Slack actions occur.')
