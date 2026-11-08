"""Deterministic, format-specific demo writing skills.

These are transparent illustrative templates, not model-generated prose.
No portfolio work is copied or ingested.
"""
import re


def _clean(value: str, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def _brief(req):
    audience = _clean(req.audience) or "technology and business leaders"
    focus = _clean(req.direction, 320) or "a measurable, practical business outcome"
    return audience, focus


def _headings(req):
    outline = req.outline.strip()
    if not outline:
        return []
    result = []
    for line in outline.splitlines():
        line = re.sub(r"^\s*(?:#{1,6}\s*|[-*]\s*|\d+[.)]\s*)", "", line).strip()
        if line and len(line) < 130:
            result.append(line)
    return result[:7]


def _section(title, audience, focus):
    return (f"## {title}\n\nFor {audience}, the useful question is not whether to pursue an initiative, "
            f"but what decision it improves. Start by defining the current friction, the people affected, "
            f"and the evidence needed to evaluate {focus.lower()}.\n\n"
            "A practical next step is to identify one decision owner, one measurable baseline, "
            "and a review point before expanding the work. Any external proof points require [VERIFY].")


def draft(req, revision=0):
    audience, focus = _brief(req)
    heads = _headings(req)
    kind = req.asset_type
    if kind == "Blog post":
        sections = heads or ["The decision behind the opportunity", "Where teams get stuck", "A practical framework", "What to measure next"]
        body = (f"# {req.title}\n\nThe hardest part of a business initiative is often not the technology. "
                f"It's deciding what needs to change, who owns the decision, and what evidence would make the investment worthwhile. "
                f"For {audience}, this piece explores {focus.lower()}.\n\n")
        body += "\n\n".join(_section(h, audience, focus) for h in sections)
        body += "\n\n## The takeaway\n\nChoose one measurable outcome, establish a baseline, and make the next decision explicit. **Next step:** convene the stakeholders who will own the result."
    elif kind == "eBook":
        chapters = heads or ["The business problem", "A framework for prioritization", "Building alignment", "From pilot to practice", "Measurement and next steps"]
        body = f"# {req.title}\n\n*Illustrative eBook excerpt and chapter plan — not a full-length eBook.*\n\n## Executive summary\n\nFor {audience}, the opportunity is to turn {focus.lower()} into an actionable decision framework. This guide separates questions to answer, evidence to collect, and decisions to make.\n\n## Chapter plan\n\n"
        body += "\n".join(f"{i}. **{h}** — What to decide, what to verify, and how to move forward." for i,h in enumerate(chapters,1))
        body += "\n\n## Introduction\n\nA compelling strategy begins with a tension: ambitious goals compete with limited time, evidence, and organizational attention. This guide offers a practical way to move from broad aspiration to a testable plan.\n\n"
        body += _section(chapters[0], audience, focus)
        body += "\n\n## Reader checklist\n\n- [ ] Define the decision and accountable owner\n- [ ] Document baseline and assumptions\n- [ ] Identify claims that need verification\n- [ ] Agree on a measurable next milestone"
    elif kind == "Video script":
        beats = [("0:00–0:05 · Hook","A single question appears on screen",f"What would change if your team could make one critical decision with more confidence?"),
                 ("0:05–0:20 · Stakes","Quick cuts: team discussion, dashboard, decision meeting",f"For {audience}, {focus.lower()} starts with knowing what problem matters most."),
                 ("0:20–0:40 · Insight","Three on-screen cards: outcome, owner, evidence","A useful plan needs three things: a clear outcome, an accountable owner, and evidence you can trust."),
                 ("0:40–1:00 · Action","Simple workflow animation","Choose one use case. Establish a baseline. Test your assumptions before you scale."),
                 ("1:00–1:10 · Close","Title card and CTA","Start with the decision. Then build the process around it.")]
        body = f"# {req.title}\n\n**Format:** Explainer video · **Estimated runtime:** ~70 seconds · **Audience:** {audience}\n\n"
        body += "\n\n".join(f"### {t}\n\n**VISUAL:** {v}\n\n**VOICEOVER:** {vo}" for t,v,vo in beats)
        body += "\n\n**Production note:** Replace illustrative visuals with approved footage and verify all factual claims."
    elif kind == "Landing page":
        body = f"# {req.title}\n\n## Make the next decision clearer\n\nA practical approach to {focus.lower()} for {audience}.\n\n### Focus on outcomes\n\nDefine the business problem before selecting the solution.\n\n### Build alignment\n\nGive stakeholders a shared view of tradeoffs, ownership, and evidence.\n\n### Measure progress\n\nStart with a baseline and an achievable first milestone.\n\n**Proof point:** [VERIFY: insert approved customer evidence]\n\n**CTA: Explore the framework**"
    elif kind == "Ad copy":
        angles = [("The decision","Better decisions begin with clearer priorities."),("The friction","Too many competing initiatives? Start with one measurable outcome."),("The team","Align the people who own the outcome before you scale."),("The proof","Trade assumptions for a testable plan."),("The next step","Turn a big goal into a practical first move.")]
        body = f"# {req.title} — Ad variants\n\n" + "\n\n".join(f"### {i}. {a}\n\n{line} **CTA:** Explore the approach." for i,(a,line) in enumerate(angles,1))
    elif kind == "Social post":
        body = f"# {req.title} — Social variants\n\n### Post 1 · The tension\n\nA big initiative can fail before it begins: when no one agrees on the decision it should improve.\n\nFor {audience}, start with the outcome, owner, and baseline. What's the first decision you'd clarify?\n\n### Post 2 · The framework\n\nThree questions before you scale:\n\n1. What changes?\n2. Who owns it?\n3. What evidence would convince us?\n\nA useful strategy makes those answers visible.\n\n### Post 3 · The next step\n\nThe best first move isn't always a bigger plan. Sometimes it's a smaller, measurable test.\n\nChoose one assumption and learn from it."
    else:
        raise ValueError(f"Unsupported asset type: {kind}")
    if revision:
        body += "\n\n## Editorial revision note\n\nValidate claims, tighten the opening, and confirm the requested format with a human editor."
    if req.direction.strip() or req.additional_instructions.strip():
        body += "\n\n---\n\n*Editorial brief received; this deterministic free demo does not fully interpret uploaded instructions. For a tailored draft, use a model-backed workflow.*"
    return body


def derivatives(req):
    audience, focus = _brief(req)
    results = {}
    for name in req.derivatives:
        if name == "Video script":
            results[name] = (f"**VISUAL:** A decision-maker reviews competing priorities.\n\n**VOICEOVER:** "
                             f"What if {focus.lower()} started with one clearer decision? "
                             "Define the outcome, align the owner, and test the evidence.\n\n**CTA:** Explore the framework.")
        elif name == "eBook":
            results[name] = (f"# {req.title}: An executive field guide\n\n"
                             "1. The decision to make\n2. The evidence to gather\n3. The team to align\n"
                             "4. A practical pilot\n5. What to measure\n\n"
                             f"**Opening:** For {audience}, progress starts by translating ambition into a decision.")
        elif name == "LinkedIn posts":
            results[name] = (f"Big strategies often stall on small decisions.\n\n"
                             f"For {audience}, start with a clear outcome, an owner, and a baseline. "
                             "What would you measure first?")
        elif name == "Ad copy":
            results[name] = f"**Headline:** Turn strategy into action\n\n**Body:** Clarify priorities and build a measurable plan.\n\n**CTA:** Learn more"
        elif name == "Email nurture":
            results[name] = (f"**Subject:** A practical way to move forward\n\n"
                             f"Hi there,\n\nIf {focus.lower()} is on your agenda, "
                             "start by defining the decision, the owner, and the evidence. "
                             "Explore the framework to plan your next step.\n\n**CTA:** Read the guide")
        elif name == "Sales one-pager":
            results[name] = (f"## The challenge\n{focus}\n\n## The approach\n"
                             "Define the decision, align stakeholders, and measure a pilot.\n\n"
                             "## Proof needed\n[VERIFY: approved customer outcomes]\n\n## Next step\nAgree on a discovery session.")
    return results
