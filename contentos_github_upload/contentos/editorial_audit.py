"""Transparent editorial, US claims-risk and on-page SEO preflight checks.

Heuristics, not AP Stylebook licensing, legal advice or search ranking predictions.
Portfolio benchmarks are metadata-based craft criteria, not text similarity.
"""
import re
from .core import load_json

CLAIMS = [
    (r"\b(?:guaranteed|risk[- ]free|100% compliant|no risk)\b", "Avoid absolute performance or compliance promises without substantiation."),
    (r"\b(?:best|number one|#1|leading|proven)\b", "Review comparative or superiority claims; document support and context."),
    (r"\b(?:customers? (?:say|love)|testimonials?)\b", "Verify testimonial permissions, accuracy and material connections."),
    (r"\b(?:free|save \d+%|\$\d+)\b", "Confirm pricing, conditions, savings and disclosures."),
]
AP_CHECKS = [
    (r"\b(?:utilize|utilization)\b", "Prefer 'use' where it preserves meaning."),
    (r"\b(?:leverage|synergy|paradigm shift)\b", "Replace jargon with specific plain-language meaning."),
    (r"\b(?:alot|irregardless)\b", "Correct spelling and usage."),
    (r"\b(?:e-mail|web site)\b", "Use 'email' and 'website' in general references."),
    (r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)\b", "Review date format and remove ordinal suffixes."),
]


def _findings(text, checks):
    findings = []
    for pattern, guidance in checks:
        matches = list(re.finditer(pattern, text, flags=re.I))
        if matches:
            findings.append({"example": matches[0].group(0), "guidance": guidance, "count": len(matches)})
    return findings


def audit(text, req):
    title = req.title.strip()
    words = re.findall(r"\b[\w'-]+\b", text)
    headings = re.findall(r"^#{1,3}\s+(.+)$", text, re.M)
    topic = re.sub(r"[^a-z0-9 ]", " ", title.lower()).strip()
    plain = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    topic_present = bool(topic and topic in plain)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip() and not p.startswith("#")]
    long_paragraphs = sum(len(p.split()) > 110 for p in paragraphs)
    seo = []
    if not topic_present:
        seo.append("Work the primary topic naturally into the opening copy; avoid keyword stuffing.")
    if not headings:
        seo.append("Add a descriptive title or section labels appropriate to the format.")
    if long_paragraphs:
        seo.append(f"Break up {long_paragraphs} long paragraph(s) for readability.")
    if req.asset_type in ("Blog post", "eBook", "Landing page"):
        if len(headings) < 3:
            seo.append("Use descriptive, reader-focused subheadings to improve scanability.")
        seo.append("Before publishing, write a unique search title and meta description; check intent, internal links, canonical URL and image alt text in the CMS.")
    else:
        seo.append("For distribution, optimize the destination page and channel metadata; traditional page SEO does not directly apply to every script, ad or social post.")
    seo.append("Search intent, rankings, backlinks, indexability and SERP competition require external data and cannot be verified here.")
    narrative = []
    if req.asset_type in ("Blog post", "eBook"):
        body_paragraphs = [p.strip() for p in paragraphs if not p.lstrip().startswith(("*", "-"))]
        if len(body_paragraphs) < 3:
            narrative.append("Develop a clear journalistic lead, supporting context and an early nut graf.")
        else:
            early = " ".join(body_paragraphs[2:5]).lower()
            signals = ("this article", "this guide", "why it matters", "the stakes", "for ", "this report", "the question")
            if not any(signal in early for signal in signals):
                narrative.append("Review paragraphs 3-5 for a nut graf explaining why this matters and who is affected.")
        narrative.append("Check inverted-pyramid ordering: lead with the most important substantiated point, then supporting evidence, context and implications.")
    else:
        narrative.append("Apply a strong journalistic hook where natural; do not force a long-form nut graf into short conversion copy.")
    references = load_json("editorial_benchmarks.json")["references"]
    criteria = []
    for ref in references:
        for feature in ref.get("study", []):
            if feature not in criteria:
                criteria.append(feature)
    return {
        "ap": _findings(text, AP_CHECKS),
        "journalistic_structure": narrative,
        "legal": _findings(text, CLAIMS),
        "seo": {"topic": title, "topic_in_copy": topic_present, "headings": len(headings),
                "word_count": len(words), "recommendations": seo},
        "portfolio": {"references": len(references), "craft_criteria": criteria,
                      "note": "Portfolio-derived editorial craft prompts only. Source documents and transcripts have not been ingested; no similarity or quality comparison to full works is claimed."},
        "disclaimer": "AP-informed editorial checks are selective, not a complete or licensed AP Stylebook. US legal flags are general issue spotting, not legal advice or approval. SEO suggestions are on-page heuristics, not ranking forecasts.",
    }
