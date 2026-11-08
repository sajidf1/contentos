# Content Impact Lab

An interactive sandbox for exploring how attribution assumptions can change the apparent business contribution of a B2B content portfolio.

**Try it:** Five editorial programs and their spend, engagement and pipeline signals are already filled in with **fictional numbers**. Adjust influenced and sourced pipeline weights, compare the ranking and change a hypothetical incremental budget. Download the scenario as a CSV.

## Deploy independently on Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and choose **Create app → Yup, I have an app**.
2. Repository: `sajidf1/contentos`
3. Branch: `main`
4. Main file path: `projects/content-impact-lab/app.py`
5. Choose a unique URL, optionally `content-impact-lab-demo`, and deploy **Public**.

This directory contains its own `requirements.txt` and `.streamlit/config.toml`. No Salesforce, credentials or paid APIs are used. **The URL does not exist until you create the app in your Streamlit account.**

## Run locally

```bash
git clone https://github.com/sajidf1/contentos.git
cd contentos
pip install -r projects/content-impact-lab/requirements.txt
streamlit run projects/content-impact-lab/app.py
```

## Interpret the output correctly

Every program, spend figure, view count and pipeline value is synthetic. The weighted pipeline value is a **what-if index**, not revenue, ROI, causal attribution or an audited forecast. Sourced and influenced pipeline can overlap, so combining them can double-count opportunities. The linear incremental-budget calculation is illustrative, not a prediction. No real employer or customer records are present.
