# Narrative Architect

A small public Streamlit demo of **source-first editorial planning**: turn notes into a story scaffold without making up reporting.

**Try it:** The app opens with a clearly labeled **fictional interview scenario**. Click **Build story architecture** to see the proposed hook, nut-graf scaffold, reporting sequence and evidence gaps. Use **Clear notes** to provide your own non-confidential material. The export is an editorial assignment brief, not a published article.

## Deploy independently on Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and choose **Create app → Yup, I have an app**.
2. Repository: `sajidf1/contentos`
3. Branch: `main`
4. Main file path: `projects/narrative-architect/app.py`
5. Choose a unique URL, optionally `narrative-architect-demo`, and deploy **Public**.

This directory has its own `requirements.txt` and `.streamlit/config.toml`, so it does not require Content Studio's packages or credentials. **The URL does not exist until you create the app in your Streamlit account.**

## Run locally

```bash
git clone https://github.com/sajidf1/contentos.git
cd contentos
pip install -r projects/narrative-architect/requirements.txt
streamlit run projects/narrative-architect/app.py
```

## What this demo does not do

The story plan is deterministic, not generative AI or automated fact-checking. The starter notes are invented, not sourced from real customers, employers, journalists or interviews. Any user-supplied claims must be independently verified before publication. No API keys, database or external services are needed.
