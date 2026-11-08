import json
from types import SimpleNamespace as NS

import pytest

from contentos.core import Request
from contentos.engine import evaluate, heuristic_eval, run_demo, run_live
from contentos.guard import BudgetExceeded, DailyCap, Meter
from contentos.skills import DIMENSIONS


def req(**kw):
    base = dict(title='A sample title', asset_type='Blog post', gtm_motion='Enterprise expansion',
                funnel='Consideration', direction='Keep it practical', derivatives=['Ad copy'])
    base.update(kw)
    return Request(**base)


def judge_json(score, claim=None):
    dims = {k: {'score': score, 'evidence': 'ok', 'fix': 'tighten intro' if score < 85 else ''} for k in DIMENSIONS}
    if claim is not None:
        dims['Claim safety (preliminary legal)']['score'] = claim
    return json.dumps({'dimensions': dims})


class FakeClient:
    """Scripted responses: judge calls (haiku) pop from `scores`; draft calls return text."""
    def __init__(self, scores, draft='# T\n\nYou can plan this.', judge_claim=None, tokens=(100, 200)):
        self.scores, self.draft, self.claim, self.tokens, self.calls = list(scores), draft, judge_claim, tokens, []
        self.messages = self

    def create(self, model, max_tokens, system, messages):
        self.calls.append(model)
        user = messages[0]['content']
        if 'Score the draft' in user:
            text = judge_json(self.scores.pop(0), self.claim)
        elif 'one derivative per name' in user:
            text = json.dumps({'Ad copy': 'Short ad.'})
        else:
            text = self.draft
        return NS(content=[NS(type='text', text=text)], usage=NS(input_tokens=self.tokens[0], output_tokens=self.tokens[1]))


def test_loop_revises_then_passes():
    c = FakeClient([60, 90])
    res = run_live(req(), c, Meter(), max_revisions=2)
    assert res['passed'] and len(res['attempts']) == 2 and res['handoff'] and res['derivatives'] == {'Ad copy': 'Short ad.'}
    assert res['usage']['calls'] == 5  # draft, judge, revise, judge, derive


def test_loop_is_bounded_and_escalates():
    c = FakeClient([50, 55, 58, 59])
    res = run_live(req(), c, Meter(), max_revisions=2)
    assert len(res['attempts']) == 3 and not res['passed'] and res['handoff'] is None and res['derivatives'] == {}
    assert res['best_attempt'] == 3


def test_claim_gate_overrides_high_average():
    c = FakeClient([95], draft='This is guaranteed and risk-free.')
    ev = evaluate(c, Meter(), req(), 'This is guaranteed and risk-free.')
    assert not ev['passed'] and ev['gate']


def test_low_claim_safety_fails_even_with_high_average():
    ev = evaluate(FakeClient([99], judge_claim=40), Meter(), req(), 'clean text')
    assert ev['score'] > 80 and not ev['passed']


def test_bad_judge_json_falls_back_to_heuristic():
    c = FakeClient([])
    c.scores = None
    orig = c.create
    c.create = lambda **k: NS(content=[NS(type='text', text='not json')], usage=NS(input_tokens=1, output_tokens=1)) \
        if 'Score the draft' in k['messages'][0]['content'] else orig(**k)
    res = run_live(req(), c, Meter(), max_revisions=0)
    assert res['attempts'][0]['evaluator'] == 'heuristic-fallback'


def test_budget_truncates_with_partial_result():
    c = FakeClient([60, 60, 60], tokens=(5000, 5000))
    res = run_live(req(), c, Meter(25_000), max_revisions=3)
    assert res['truncated'] and res['draft']


def test_budget_before_any_draft_raises():
    with pytest.raises(BudgetExceeded):
        run_live(req(), FakeClient([90]), Meter(0))


def test_daily_cap():
    cap = DailyCap(2)
    assert cap.try_acquire() and cap.try_acquire() and not cap.try_acquire()


def test_demo_schema_matches_live():
    d = run_demo(req())
    assert {'draft', 'attempts', 'passed', 'score', 'derivatives', 'handoff', 'usage'} <= d.keys()
    assert heuristic_eval(d['draft'], req())['dimensions']


def _app_live(env, code=None):
    import os
    from streamlit.testing.v1 import AppTest
    for k in ('ENABLE_LIVE_MODE', 'ANTHROPIC_API_KEY', 'ACCESS_CODE', 'REQUIRE_ACCESS_CODE'):
        os.environ.pop(k, None)
    os.environ.update(env)
    at = AppTest.from_file(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
    at.radio[0].set_value(at.radio[0].options[2]).run()
    return at


def test_live_fails_closed_without_code_by_default():
    at = _app_live({'ENABLE_LIVE_MODE': 'true', 'ANTHROPIC_API_KEY': 'x'})
    assert any('not enabled' in w.value for w in at.warning)


def test_private_app_mode_skips_code_prompt():
    at = _app_live({'ENABLE_LIVE_MODE': 'true', 'ANTHROPIC_API_KEY': 'x', 'REQUIRE_ACCESS_CODE': 'false'})
    assert not any(t.label == 'Access code' for t in at.text_input)
    assert not any('not enabled' in w.value for w in at.warning)


def test_code_prompt_shown_when_required():
    at = _app_live({'ENABLE_LIVE_MODE': 'true', 'ANTHROPIC_API_KEY': 'x', 'ACCESS_CODE': 's'})
    assert any(t.label == 'Access code' for t in at.text_input)
