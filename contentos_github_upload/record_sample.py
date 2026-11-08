"""Record one real Claude run to data/sample_run.json so public visitors can browse it for free.

Usage:  ANTHROPIC_API_KEY=... python record_sample.py
"""
import datetime
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
from anthropic import Anthropic  # noqa: E402
from contentos.core import Request  # noqa: E402
from contentos.engine import run_live  # noqa: E402
from contentos.guard import Meter  # noqa: E402

req = Request('Building the business case for a unified data platform', 'Blog post',
              'Enterprise expansion', 'Consideration',
              'Focus on operational efficiency and measurable outcomes.', ['LinkedIn posts', 'Ad copy'])
client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'], timeout=60.0, max_retries=1)
res = run_live(req, client, Meter(150_000), max_revisions=2, on_event=print)
res['recorded_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
out = Path(__file__).parent / 'data' / 'sample_run.json'
out.write_text(json.dumps(res, indent=2), encoding='utf-8')
print(f'Saved {out} — score {res["score"]}/100, passed={res["passed"]}, usage={res["usage"]}')
