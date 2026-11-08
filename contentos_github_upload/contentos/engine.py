"""Agentic engine: skill-based drafting -> LLM rubric evaluation -> bounded revision loop -> derivatives.

Every function takes the Anthropic client as an argument so tests can pass a fake.
Evaluation is hybrid: Claude scores each rubric dimension with evidence, and deterministic
code computes the final score and applies a hard claim-safety gate the model cannot override.
"""
import json
import os
import re
from dataclasses import asdict

from .core import Request, context_for, demo_draft, demo_derivatives, handoff, score_text
from .guard import BudgetExceeded, Meter
from .skills import DIMENSIONS, RISKY_PHRASES, SKILLS, SYSTEM, EDITORIAL_PRINCIPLES, ASSET_PLAYBOOKS, REVIEW_GUIDANCE

DRAFT_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-5-5')
JUDGE_MODEL = os.environ.get('CLAUDE_JUDGE_MODEL', 'claude-haiku-5-5')
PASS_ABOVE = 80          # final score must be strictly greater than this
SAFETY_FLOOR = 60        # claim-safety below this fails regardless of the average
CLAIM_KEY = 'Claim safety (preliminary legal)'


class EvalError(ValueError):
    pass


def _call(client, meter: Meter, model: str, user: str, max_tokens: int, system: str = SYSTEM) -> str:
    meter.check()
    msg = client.messages.create(model=model, max_tokens=max_tokens, system=system,
                                 messages=[{'role': 'user', 'content': user}])
    meter.add(msg.usage.input_tokens, msg.usage.output_tokens)
    return '\n'.join(b.text for b in msg.content if getattr(b, 'type', None) == 'text').strip()


def _json_from(text: str) -> dict:
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        raise EvalError('no JSON object in model output')
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as exc:
        raise EvalError(str(exc)) from exc


def _brief(req: Request) -> str:
    ctx = context_for(req)
    return (f'Asset: {req.asset_type}. Title: {req.title}. GTM motion: {req.gtm_motion}. '
            f'Persona: {ctx["persona"]}. Funnel stage: {req.funnel}. '
            f'Approved fictional themes: {", ".join(ctx["keywords"])}. '
            f'Target word count: {req.target_words or "asset default"}. '
            f'Additional audience detail: {req.audience or "use mapped persona"}. '
            f'Tone: {req.tone}. Style: {req.style}. '
            f'Optional outline: {req.outline or "none supplied"}. '
            f'Additional instructions: {req.additional_instructions or "none"}.')


def generate(client, meter, req: Request, model: str = DRAFT_MODEL) -> str:
    skill = SKILLS[req.asset_type]
    user = (f'{_brief(req)}\nLength: {skill["length"]}. Structure: {skill["shape"]}.\n'
            f'Editorial principles: {EDITORIAL_PRINCIPLES}\n'\n            f'Asset-specific playbook: {ASSET_PLAYBOOKS[req.asset_type]}\n'\n            f'<direction>{req.direction}</direction>\nReturn only the Markdown asset.')
    return _call(client, meter, model, user, max_tokens=1800)


def evaluate(client, meter, req: Request, draft: str, model: str = JUDGE_MODEL) -> dict:
    rubric = '\n'.join(f'- {k}: {v}' for k, v in DIMENSIONS.items())
    user = (f'Score the draft 0-100 on each dimension. Be strict and evidence-based.\n{rubric}\n\n'
            f'Additional craft review criteria: {json.dumps(REVIEW_GUIDANCE)}\n'\n            f'Asset playbook: {ASSET_PLAYBOOKS[req.asset_type]}\n'\n            f'Brief: {_brief(req)}\n'
            'Return ONLY JSON: {"dimensions": {"<exact dimension name>": {"score": int, '
            '"evidence": "<=25 words pointing at the draft", "fix": "<=25 words, empty if score>=85"}}}\n'
            f'<draft>\n{draft}\n</draft>')
    raw = _json_from(_call(client, meter, model, user, max_tokens=900))
    dims = {}
    for name in DIMENSIONS:
        d = raw.get('dimensions', {}).get(name)
        if not isinstance(d, dict) or not isinstance(d.get('score'), (int, float)):
            raise EvalError(f'missing dimension: {name}')
        dims[name] = {'score': max(0, min(100, int(d['score']))),
                      'evidence': str(d.get('evidence', ''))[:240], 'fix': str(d.get('fix', ''))[:240]}
    return _finalize(dims, draft, evaluator='llm')


def _finalize(dims: dict, draft: str, evaluator: str) -> dict:
    gate = None
    hits = [p for p in RISKY_PHRASES if p in draft.lower()]
    if hits:  # deterministic floor the model cannot override
        dims[CLAIM_KEY]['score'] = min(dims[CLAIM_KEY]['score'], 35)
        dims[CLAIM_KEY]['fix'] = f'Remove risky claim language: {", ".join(hits)}.'
        gate = f'Risky phrases detected: {", ".join(hits)}'
    score = round(sum(d['score'] for d in dims.values()) / len(dims))
    if dims[CLAIM_KEY]['score'] < SAFETY_FLOOR:
        gate = gate or 'Claim safety below floor'
    return {'score': score, 'passed': score > PASS_ABOVE and gate is None,
            'dimensions': dims, 'gate': gate, 'evaluator': evaluator}


def heuristic_eval(draft: str, req: Request) -> dict:
    """Fallback if the LLM judge output cannot be parsed."""
    checks = score_text(draft, req)['checks']
    dims = {k: {'score': v, 'evidence': 'Keyword/structure heuristic.', 'fix': ''} for k, v in checks.items()}
    dims.setdefault(CLAIM_KEY, dims.get('Legal review (preliminary)', {'score': 70, 'evidence': '', 'fix': ''}))
    return _finalize(dims, draft, evaluator='heuristic-fallback')


def revise(client, meter, req: Request, draft: str, ev: dict, model: str = DRAFT_MODEL) -> str:
    fixes = '\n'.join(f'- {k} ({d["score"]}): {d["fix"] or d["evidence"]}'
                      for k, d in ev['dimensions'].items() if d['score'] < 85)
    user = (f'{_brief(req)}\nRevise the draft to fix these reviewer findings without changing the asset '
            f'type or title:\n{fixes}\nEditorial principles: {EDITORIAL_PRINCIPLES}\n'\n            f'Asset playbook: {ASSET_PLAYBOOKS[req.asset_type]}\nReturn only the revised Markdown.\n<draft>\n{draft}\n</draft>')
    return _call(client, meter, model, user, max_tokens=1800)


def derive(client, meter, req: Request, draft: str, model: str = JUDGE_MODEL) -> dict:
    if not req.derivatives:
        return {}
    user = (f'{_brief(req)}\nFrom the approved draft, write one derivative per name (max 80 words each, '
            f'no invented stats): {json.dumps(req.derivatives)}.\n'
            'Return ONLY a JSON object mapping each name to its copy.\n'
            f'<draft>\n{draft}\n</draft>')
    try:
        out = _json_from(_call(client, meter, model, user, max_tokens=900))
        return {n: str(out[n]) for n in req.derivatives if n in out} or demo_derivatives(req)
    except EvalError:
        return demo_derivatives(req)


def run_live(req: Request, client, meter: Meter, max_revisions: int = 2, on_event=lambda m: None,
             draft_model: str = DRAFT_MODEL, judge_model: str = JUDGE_MODEL) -> dict:
    max_revisions = max(0, min(max_revisions, 3))
    on_event(f'Drafting with the "{req.asset_type}" skill ({draft_model})…')
    draft = generate(client, meter, req, draft_model)
    attempts, best, truncated = [], None, False
    try:
        for i in range(max_revisions + 1):
            on_event(f'Evaluating attempt {i + 1} against the rubric ({judge_model})…')
            try:
                ev = evaluate(client, meter, req, draft, judge_model)
            except EvalError:
                on_event('Judge output unparseable; using heuristic fallback.')
                ev = heuristic_eval(draft, req)
            attempts.append({'attempt': i + 1, 'words': len(draft.split()), **ev})
            if best is None or ev['score'] > best[0]['score']:
                best = (ev, draft, i + 1)
            on_event(f'Attempt {i + 1}: {ev["score"]}/100 — {"pass" if ev["passed"] else "needs revision"}')
            if ev['passed'] or i == max_revisions:
                break
            on_event('Revising from reviewer findings…')
            draft = revise(client, meter, req, draft, ev, draft_model)
    except BudgetExceeded:
        truncated = True
        on_event('Session budget reached; returning best draft so far.')
    ev, final_draft, best_n = best or (heuristic_eval(draft, req), draft, 1)
    if not attempts:
        attempts.append({'attempt': 1, 'words': len(draft.split()), **ev})
    result = {'mode': 'live', 'request': asdict(req), 'context': context_for(req), 'draft': final_draft,
              'attempts': attempts, 'best_attempt': best_n, 'passed': ev['passed'], 'score': ev['score'],
              'truncated': truncated, 'derivatives': {}, 'handoff': None,
              'models': {'draft': draft_model, 'judge': judge_model}}
    if ev['passed']:
        try:
            on_event('Generating derivative assets…')
            result['derivatives'] = derive(client, meter, req, final_draft, judge_model)
        except BudgetExceeded:
            result['derivatives'] = demo_derivatives(req)
        result['handoff'] = handoff(req, ev['score'])
    result['usage'] = meter.snapshot()
    return result


def run_demo(req: Request) -> dict:
    """Deterministic, offline run that returns the same result schema."""
    attempts, draft = [], demo_draft(req)
    for i in range(3):
        rep = score_text(draft, req)
        dims = {k: {'score': v, 'evidence': '', 'fix': ''} for k, v in rep['checks'].items()}
        attempts.append({'attempt': i + 1, 'words': len(draft.split()), 'score': rep['score'],
                         'passed': rep['passed'], 'dimensions': dims, 'gate': None, 'evaluator': 'heuristic'})
        if rep['passed']:
            break
        draft = demo_draft(req, revision=i + 1)
    last = attempts[-1]
    return {'mode': 'demo', 'request': asdict(req), 'context': context_for(req), 'draft': draft,
            'attempts': attempts, 'best_attempt': last['attempt'], 'passed': last['passed'],
            'score': last['score'], 'truncated': False, 'derivatives': demo_derivatives(req) if last['passed'] else {},
            'handoff': handoff(req, last['score']) if last['passed'] else None,
            'models': {}, 'usage': {'calls': 0, 'input_tokens': 0, 'output_tokens': 0}}
