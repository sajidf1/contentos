"""Optional live Claude drafting. Never expose keys in browser or repository."""
import os
from .core import Request, context_for


def generate_live(req: Request, model: str = 'claude-sonnet-4-5') -> str:
    from anthropic import Anthropic
    key = os.environ.get('ANTHROPIC_API_KEY')
    if not key:
        raise RuntimeError('ANTHROPIC_API_KEY is not configured on the server.')
    ctx = context_for(req)
    client = Anthropic(api_key=key, timeout=45.0, max_retries=1)
    msg = client.messages.create(
        model=model, max_tokens=1800,
        system=('You are an enterprise content drafting assistant for a FICTIONAL organization. '
                'Write clear, original, responsible marketing content. Never invent statistics, '
                'customer quotes, regulatory guarantees, or product claims. Mark facts requiring verification.'),
        messages=[{'role': 'user', 'content': f'Create a {req.asset_type} titled {req.title}. '
                   f'GTM: {req.gtm_motion}; persona: {ctx["persona"]}; funnel: {req.funnel}. '
                   f'Approved fictional messaging themes: {", ".join(ctx["keywords"])}. '
                   f'Direction: {req.direction}. Use Markdown headings and actionable takeaways.'}]
    )
    return '\n'.join(block.text for block in msg.content if getattr(block, 'type', None) == 'text')
