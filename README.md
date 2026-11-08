# ContentOS — Editorial Intelligence in Practice

**A public portfolio of practical, independently built content strategy tools.**

[Try Content Studio](https://content-studio-demo.streamlit.app/) · [View the portfolio](https://www.sajidfarooq.com/#github-projects)

ContentOS explores a simple question: **What happens when editorial judgment, sales intelligence and content measurement become part of the same workflow?**

This repository contains three demonstrations built to make that thinking tangible. They are independent portfolio projects, not employer systems or production integrations.

## The projects

| Project | What it demonstrates | Where to look |
| --- | --- | --- |
| **Content Studio** | Creative intake, GTM mapping, template-based drafts, editorial preflight and simulated handoff; fictional Salesforce-style deal signals can be copied into the brief. | [Source and setup](contentos_github_upload/) · [Live demo](https://content-studio-demo.streamlit.app/) |
| **Narrative Architect** | Source-first story planning, hooks, nut grafs, narrative hierarchy and reporting gaps. | [Project](projects/narrative-architect/) |
| **Content Impact Lab** | Interactive content investment and pipeline-attribution scenarios using synthetic data. | [Project](projects/content-impact-lab/) |

## Try Content Studio

1. Open the [live demo](https://content-studio-demo.streamlit.app/).
2. Review the **fictional Salesforce-style opportunities** and select a deal.
3. Copy the synthetic sales brief, or check the box to attach it to the workflow.
4. Choose an asset, edit the creative direction and run the free demo.
5. Review the draft, editorial checks and simulated handoff.

**What this is — and isn't:** The publicly available demo runs on deterministic templates, **not live AI**. Attaching a sales brief carries context into the request but does not guarantee that every detail is reflected in generated copy. All CRM accounts, opportunity values, risk labels and call notes are invented. Content scores are illustrative heuristics, not legal, PMM or editorial approvals. No Salesforce, Slack or Wrike account is connected. Content Impact Lab's pipeline numbers are synthetic and not evidence of causal attribution or revenue impact.

The source includes an **optional** Anthropic-powered path for private experimentation, but it is **not enabled in the free public demo**. Enabling it requires your own credentials and may incur API charges.

## Run locally

```bash
git clone https://github.com/sajidf1/contentos.git
cd contentos/contentos_github_upload
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

The other two projects have their own READMEs and run instructions.

## How it is organized

```text
contentos_github_upload/
  app.py                  Streamlit interface
  contentos/              Workflow logic and demo modules
  data/                   Fictional GTM and editorial reference metadata
  docs/                   Architecture and implementation notes
  tests/                  Automated checks
projects/
  narrative-architect/
  content-impact-lab/
```

For technical details, see the [Content Studio README](contentos_github_upload/README.md), [architecture](contentos_github_upload/docs/ARCHITECTURE.md) and [synthetic CRM disclosure](contentos_github_upload/SALESFORCE_DEMO.md).

## Responsible demo design

- No employer CRM records, customer calls or proprietary internal content are used.
- Published editorial references are links and illustrative notes, **not verified full-text analysis or a training corpus**.
- Never commit `.env`, `.streamlit/secrets.toml`, API keys or real customer data.
- The public demo does not require visitors to supply an API key.
- There is no open-source license granted at present; contact the repository owner about reuse.

**Status:** Portfolio prototypes. They demonstrate workflow design and editorial reasoning rather than production readiness.
