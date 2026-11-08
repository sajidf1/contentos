"""Synthetic demo workflow; no employer data or integrations."""
from dataclasses import dataclass, asdict
from typing import Any
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def load_json(name: str) -> Any:
    return json.loads((DATA / name).read_text(encoding='utf-8'))


@dataclass
class Request:
    title: str
    asset_type: str
    gtm_motion: str
    funnel: str
    direction: str
    derivatives: list[str]


def context_for(req: Request) -> dict:
    motions = load_json('motions.json')
    return motions[req.gtm_motion]


def score_text(text: str, req: Request) -> dict:
    """Transparent illustrative rubric, NOT legal/PMM certification."""
    lower = text.lower()
    persona = context_for(req)
    checks = {
        'Brand & voice': min(100, 60 + (20 if 'you' in lower else 0) + (20 if len(text.split()) >= 80 else 0)),
        'GTM alignment': min(100, 55 + 15 * sum(phrase.lower() in lower for phrase in persona['keywords'][:3])),
        'SEO readiness': min(100, 60 + (20 if req.title.lower() in lower else 0) + (20 if '##' in text else 0)),
        'PMM review (preliminary)': 85 if any(k.lower() in lower for k in persona['keywords']) else 55,
        'Legal review (preliminary)': 90 if not any(w in lower for w in ['guaranteed', '100% compliant', 'risk-free']) else 35,
        'Reference alignment': 85 if len(text.split()) >= 60 else 65,
    }
    score = round(sum(checks.values()) / len(checks))
    return {'score': score, 'checks': checks, 'passed': score > 80 and checks['Legal review (preliminary)'] >= 60,
            'disclaimer': 'Heuristic demo scores are illustrative and do not replace human editorial, legal, or PMM approval.'}


def demo_draft(req: Request, revision: int = 0) -> str:
    ctx = context_for(req)
    keywords = ', '.join(ctx['keywords'])
    base = f'''# {req.title}

## Why this matters

For {ctx['persona'].lower()}, a thoughtful approach to {req.gtm_motion.lower()} helps teams make better decisions. You can connect the work to {keywords} while keeping the message practical and grounded.

## The opportunity

You need a repeatable framework for evaluating tradeoffs, building internal alignment, and defining measurable outcomes. The strongest approach starts with a clear objective and the right stakeholders.

## A practical approach

1. Define the audience and the business decision.
2. Align stakeholders on expected outcomes and useful evidence.
3. Pilot a focused initiative and document what changes.
4. Review results with the team and refine the next iteration.

## What to do next

You can use this framework to create a clear plan, identify ownership, and communicate progress. This example is fictional and makes no product performance claims.

## Editorial notes

Requested direction: {req.direction or 'Use a clear, practical executive tone.'}
Funnel stage: {req.funnel}. Target persona: {ctx['persona']}.
'''
    if revision:
        base += '\n## Measurement and iteration\n\nYou can track stakeholder adoption, cycle time, and the quality of resulting decisions. Document assumptions and ask reviewers to validate all claims before publication.\n'
    return base


def demo_derivatives(req: Request) -> dict[str, str]:
    return {name: f'{name}: {req.title}. Explore a practical approach for {context_for(req)["persona"].lower()}. Learn more in the full {req.asset_type.lower()}.' for name in req.derivatives}


def handoff(req: Request, score: int) -> dict:
    owner = context_for(req)['owner']
    return {
        'ticket': {'id': 'DEMO-1042', 'title': req.title, 'assignee': owner,
                   'status': 'Editorial review', 'workback': ['Content lead review', 'PMM validation', 'Legal approval', 'Final edits', 'Publish']},
        'slack': f'[SIMULATED] New {req.asset_type} draft for {owner}. Quality score: {score}/100. Review requested.',
        'requester': 'Draft ready for review (simulated notification).'
    }
