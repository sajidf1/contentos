"""Synthetic demo workflow; no employer data or integrations."""
from dataclasses import dataclass, asdict
from typing import Any
import json
from pathlib import Path
from .demo_skills import draft as skill_draft, derivatives as skill_derivatives

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
    target_words: int = 0
    outline: str = ''
    tone: str = 'Clear and professional'
    style: str = 'Practical and concise'
    audience: str = ''
    additional_instructions: str = ''


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
    """Generate a format-specific illustrative draft (no live AI)."""
    return skill_draft(req, revision)


def demo_derivatives(req: Request) -> dict[str, str]:
    """Generate distinct format-specific derivative examples."""
    return skill_derivatives(req)


def handoff(req: Request, score: int) -> dict:
    owner = context_for(req)['owner']
    return {
        'ticket': {'id': 'DEMO-1042', 'title': req.title, 'assignee': owner,
                   'status': 'Editorial review', 'workback': ['Content lead review', 'PMM validation', 'Legal approval', 'Final edits', 'Publish']},
        'slack': f'[SIMULATED] New {req.asset_type} draft for {owner}. Quality score: {score}/100. Review requested.',
        'requester': 'Draft ready for review (simulated notification).'
    }
