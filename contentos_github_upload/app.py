import json
import os
from pathlib import Path

import streamlit as st

from contentos.core import Request, load_json
from contentos.engine import DRAFT_MODEL, JUDGE_MODEL, run_demo, run_live
from contentos.guard import BudgetExceeded, DailyCap, Meter

st.set_page_config(page_title='ContentOS | Portfolio Edition', page_icon='🧠', layout='wide')
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


def workflow_dot(res: dict | None) -> str:
    done = res is not None
    passed = bool(res and res['passed'])
    n_rev = max(0, len(res['attempts']) - 1) if res else 0
    fill = lambda ok: '#d1fae5' if ok else '#f3f4f6'
    nodes = [('intake', 'Intake', done), ('gtm', 'GTM match', done), ('draft', 'Draft\\n(skill per asset)', done),
             ('judge', 'Evaluate\\n(rubric + gate)', done), ('revise', f'Revise\\n({n_rev} used)', n_rev > 0),
             ('derive', 'Derivatives', passed), ('handoff', 'Editorial handoff\\n(simulated)', passed),
             ('human', 'Human review', done and not passed)]
    lines = ['digraph G { rankdir=LR; bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#9ca3af"]; edge [color="#6b7280", fontsize=9, fontname="Helvetica"];']
    for key, label, ok in nodes:
        color = '#fde68a' if key == 'human' and ok else fill(ok)
        lines.append(f'{key} [label="{label}", fillcolor="{color}"];')
    lines += ['intake -> gtm -> draft -> judge;', 'judge -> revise [label="below threshold"];', 'revise -> judge;',
              'judge -> derive [label="pass"]; derive -> handoff;', 'judge -> human [label="still failing", style=dashed];', '}']
    return '\n'.join(lines)


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


def show(res: dict) -> None:
    st.subheader('Workflow')
    st.graphviz_chart(workflow_dot(res))
    st.subheader('Matched GTM intelligence (fictional)')
    st.json(res['context'])
    best = next((a for a in res['attempts'] if a['attempt'] == res['best_attempt']), res['attempts'][-1])
    st.subheader('Quality scorecard')
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
    st.subheader('Draft')
    st.markdown(res['draft'])
    st.download_button('Download draft (.md)', res['draft'], file_name='contentos-draft.md', mime='text/markdown')
    st.subheader('Derivative assets')
    if res['derivatives']:
        for name, copy in res['derivatives'].items():
            with st.expander(name):
                st.write(copy)
    else:
        st.caption('Derivatives are generated only after a draft passes review.')
    st.subheader('Editorial handoff (simulated)')
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

st.title('ContentOS · Agentic Content Operations')
st.caption('Independent fictional portfolio project · No employer data, prompts, or production integrations')

with st.sidebar:
    mode = st.radio('Execution mode', MODES)
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
motions = load_json('motions.json')
with st.form('request'):
    a, b = st.columns(2)
    with a:
        asset = st.selectbox('Primary asset', ['Blog post', 'eBook', 'Landing page', 'Video script', 'Ad copy', 'Social post'])
        title = st.text_input('Title', 'Building the business case for a unified data platform', max_chars=140)
        motion = st.selectbox('GTM motion', list(motions))
    with b:
        funnel = st.selectbox('Funnel stage', ['Awareness', 'Consideration', 'Decision'], index=1)
        derivs = st.multiselect('Derivative assets', ['LinkedIn posts', 'Ad copy', 'Email nurture', 'Sales one-pager'], default=['LinkedIn posts', 'Ad copy'])
        direction = st.text_area('Outline or creative direction', 'Focus on operational efficiency and measurable outcomes.', max_chars=1200)
    submitted = st.form_submit_button('Run content workflow', type='primary')

if submitted:
    if not title.strip():
        st.error('A title is required.')
        st.stop()
    req = Request(title.strip(), asset, motion, funnel, direction.strip(), derivs)
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
    st.graphviz_chart(workflow_dot(None))
    st.info('Choose a mode in the sidebar, then run the workflow.')

with st.expander('Reference library and implementation notes'):
    st.json(load_json('reference_library.json'))
    st.markdown('Reference library entries are fictional metadata, not retrieval-augmented generation. '
                'Handoffs are simulated; no outbound Wrike or Slack actions occur.')
