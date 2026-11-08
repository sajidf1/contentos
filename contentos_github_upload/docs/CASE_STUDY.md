# Case Study: ContentOS — Governed, Agentic Content Operations

> Fill in the bracketed parts with accurate, approved information. Do not invent metrics.
> This project is independent and fictional; do not imply it reproduces any employer's system.

## The problem
Enterprise content teams juggle inconsistent intake, unclear audience alignment, slow review cycles, and unclear ownership at handoff. [One sentence from your own experience, if approved to share.]

## The approach
I modelled content creation as a governed pipeline: structured intake → GTM/persona mapping → skill-specific drafting → rubric-based evaluation → bounded revision → derivatives → editorial handoff, with a human owner at every escalation point.

## What I built
- **Intake and fictional GTM intelligence** that frames every draft for a persona, funnel stage, and approved themes.
- **Claude-powered skills** per asset type (blog, eBook, landing page, video script, ad copy, social).
- **Hybrid evaluation:** six-dimension rubric scored by Claude with cited evidence, plus a deterministic claim-safety gate.
- **Bounded revision loop** (max 3) that returns the best attempt and escalates failures to a human.
- **Cost-safe public deployment:** recorded sample, gated live mode, session and daily caps.

## Key decisions and trade-offs
1. Why the gate is deterministic (the judge model should not be able to approve risky claims).
2. Why evaluation uses a cheaper model than drafting.
3. Why failing drafts escalate instead of looping forever.
4. Why the public demo defaults to recorded output.

## Results
[Describe only what you can verify, e.g. the sample run's score trajectory from `data/sample_run.json`, test coverage, deploy status. Add real before/after observations from your own testing.]

## Limitations and next steps
[Copy from docs/ARCHITECTURE.md, in your own words.]

## My role
[Your accurate, approved contributions.]

**Links:** [GitHub repo] · [Live demo] · [Architecture doc]
