# Salesforce-style intelligence (synthetic demo)

Content Studio includes a **fictional, locally bundled** opportunity table. It is **not connected to Salesforce** and contains no customer records, real call transcripts, CRM authentication or live performance data.

Visitors can:
1. Review synthetic opportunities, stages, risk labels, deal values and invented call summaries.
2. Select an opportunity to see a deterministic suggested content assignment.
3. Copy or download the resulting text brief.
4. Optionally attach the selected brief to the Content Studio request.

**Important limitation:** The free Streamlit mode uses deterministic templates rather than a live LLM. Attaching the brief preserves the CRM context in the request, but it does not guarantee that every deal-specific fact appears in the resulting draft. No real customer claims, quotes or ROI figures should be inferred from this demo.

The opportunity risk and priority are curated demonstration labels; they are not predictive scores. No Salesforce API, OAuth or paid AI service is used.
