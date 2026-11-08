# ContentOS — Agentic Content Operations (Portfolio Edition)

An **independently built, fictional** portfolio project: structured intake → GTM/persona mapping → Claude-powered drafting skills → rubric evaluation → bounded revision loop → derivatives → simulated editorial handoff. **Not affiliated with or endorsed by any employer.** No proprietary prompts, assets, schemas, or data are included.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md).

## Modes

| Mode | Cost | What it does |
|---|---|---|
| Recorded Claude sample | Free | Shows a real Claude run **only after you record it** into `data/sample_run.json`; otherwise falls back to demo templates |
| Demo templates | Free | Deterministic offline templates and heuristic scoring |
| Live Claude | Your API credits | Draft → Claude evaluation → up to 3 revisions → derivatives. Requires an access code; capped per session and per day |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## Enable live Claude locally

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then edit it
streamlit run app.py
```

Verify the model IDs with your Anthropic account before enabling live mode. Live mode needs `ENABLE_LIVE_MODE=true`, `ANTHROPIC_API_KEY`, **and** `ACCESS_CODE` (it fails closed without one). If the Streamlit app itself is private (viewer allow-list), you can set `REQUIRE_ACCESS_CODE=false` so approved viewers skip the second password; session and daily caps still apply. Models default to `claude-sonnet-5-5` (draft/revise) and `claude-haiku-5-5` (evaluate/derive); confirm both are available on your account.

## Record the public sample

This requires valid Anthropic API credentials and incurs usage charges. Do not commit `.env`.

```bash
ANTHROPIC_API_KEY=sk-ant-... python record_sample.py
```

Commit the resulting `data/sample_run.json`. Visitors can then browse a real Claude run for free.

## Deploy to Streamlit Community Cloud

1. Check employer IP/confidentiality obligations, then push this directory to a **new personal GitHub repository**. Confirm `.env` and `secrets.toml` are not committed.
2. Create the app at share.streamlit.io pointing at `app.py`.
3. **Public showcase (recommended):** add no secrets. Visitors get the recorded sample and demo mode at zero cost.
4. **Private app (recommended for sharing live mode):** in the app's sharing settings, restrict viewing to specific email addresses, then set `REQUIRE_ACCESS_CODE=false`.
5. **Public app with live mode:** paste the secrets from `.streamlit/secrets.toml.example`, share the access code only with people you choose, and set a monthly spend limit in the Anthropic Console first.
6. Set `DAILY_RUN_CAP` conservatively. It resets when the app restarts, so the provider spend limit is your real backstop.

## What is real vs simulated?

| Component | Status |
|---|---|
| Intake and GTM mapping | Working, fictional data |
| Drafting | Real Claude (live) or deterministic templates (demo) |
| Evaluation | Claude rubric scoring + deterministic claim-safety gate (live); keyword heuristic (demo) |
| Revision loop | Real, capped at 3 loops, best attempt returned |
| Derivatives | Claude-generated after a pass (live); templates (demo) |
| PMM/legal approval | **Not performed**; scores are illustrative signals |
| Reference library | Fictional metadata, not retrieval |
| Wrike/Slack | Simulated payloads; no outbound actions |

## License

No license is granted by default. Add one only after reviewing ownership and disclosure obligations.
