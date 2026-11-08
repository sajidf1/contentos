# Content Impact Lab

An interactive Streamlit sandbox for examining how content investment, attribution assumptions and editorial tiering influence a B2B content portfolio's apparent business value.

## Features
- Synthetic portfolio across five editorial programs and four tiers
- Adjustable influenced/sourced pipeline credit
- Scenario-based budget allocation
- Transparent formulas and CSV export

## Important limitations
All figures are **synthetic**. Weighted pipeline is an **index**, not revenue, ROI, causal attribution or a validated forecast. Sourced and influenced pipeline may overlap. The project does not connect to Salesforce.

## Run
```bash
pip install streamlit pandas
streamlit run projects/content-impact-lab/app.py
```
