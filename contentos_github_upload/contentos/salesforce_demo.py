"""Synthetic CRM opportunity signals for the public portfolio demonstration.

No Salesforce connection, real accounts, personal data, or real call transcripts.
"""
from __future__ import annotations

OPPORTUNITIES = [
    {
        "id": "DEMO-OPP-101", "account": "Northstar Analytics (fictional)",
        "industry": "Financial services", "stage": "Proposal", "amount_usd": 420000,
        "days_in_stage": 39, "risk": "High", "priority": "Tier 1",
        "product": "Unified data platform",
        "signal": "Security review and procurement objections have stalled a strategic expansion.",
        "call_note": "Synthetic call summary: Buyer asked for a quantified migration case and a security-focused executive explainer.",
        "content": "Executive-ready business case and security FAQ",
        "audience": "CIO, CISO and finance stakeholders",
    },
    {
        "id": "DEMO-OPP-102", "account": "Meridian Retail Group (fictional)",
        "industry": "Retail", "stage": "Evaluation", "amount_usd": 185000,
        "days_in_stage": 24, "risk": "Medium", "priority": "Tier 2",
        "product": "Real-time analytics",
        "signal": "The buying committee needs proof of time to value before a pilot decision.",
        "call_note": "Synthetic call summary: Operations leader asked for a practical deployment example and success measures.",
        "content": "Industry-specific pilot playbook",
        "audience": "VP of operations and data leaders",
    },
    {
        "id": "DEMO-OPP-103", "account": "Harborline Software (fictional)",
        "industry": "B2B SaaS", "stage": "Negotiation", "amount_usd": 310000,
        "days_in_stage": 47, "risk": "High", "priority": "Tier 1",
        "product": "AI-powered customer insights",
        "signal": "A competing vendor has raised doubts about governance and measurable ROI.",
        "call_note": "Synthetic call summary: CFO requested an ROI framework and legal team asked for governance documentation.",
        "content": "CFO-oriented ROI narrative and governance one-pager",
        "audience": "CFO, legal and product leadership",
    },
    {
        "id": "DEMO-OPP-104", "account": "Cedar Peak Manufacturing (fictional)",
        "industry": "Manufacturing", "stage": "Discovery", "amount_usd": 95000,
        "days_in_stage": 12, "risk": "Low", "priority": "Tier 3",
        "product": "Workflow automation",
        "signal": "Early interest; buyer wants a clear explanation of common use cases.",
        "call_note": "Synthetic call summary: Team requested an introductory overview and practical examples.",
        "content": "Educational blog and short social derivatives",
        "audience": "IT and operations managers",
    },
]


def recommended_opportunities():
    """High-risk opportunities first, then by illustrative deal size."""
    rank = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(OPPORTUNITIES, key=lambda row: (rank[row["risk"]], -row["amount_usd"]))


def brief_for(opp: dict) -> str:
    """Portable, copyable editorial brief grounded in the synthetic row."""
    return (
        "SYNTHETIC SALESFORCE-STYLE OPPORTUNITY — FICTIONAL DATA ONLY\n"
        f"Opportunity: {opp['id']} | Account: {opp['account']}\n"
        f"Industry: {opp['industry']} | Stage: {opp['stage']} | Deal value: ${opp['amount_usd']:,}\n"
        f"Days in stage: {opp['days_in_stage']} | Risk: {opp['risk']} | Editorial priority: {opp['priority']}\n"
        f"Product theme: {opp['product']}\n"
        f"Sales signal: {opp['signal']}\n"
        f"Illustrative call note: {opp['call_note']}\n"
        f"Suggested content: {opp['content']}\n"
        f"Audience: {opp['audience']}\n"
        "Writing guidance: Use a journalistic hook and early nut graf where relevant. "
        "Treat this as a hypothetical scenario; do not invent customer quotes, "
        "performance claims or actual case-study results. Require human editorial approval."
    )
