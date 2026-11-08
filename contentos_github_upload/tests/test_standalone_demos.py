"""Smoke tests for independently deployed public demos.

These run without API keys, real customer data, or outside services.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


def test_narrative_architect_public_demo():
    app = ROOT / "projects" / "narrative-architect" / "app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    assert not at.exception
    assert "SYNTHETIC EXAMPLE" in at.text_area[0].value
    assert at.button[2].label == "Build story architecture"
    at.button[2].click().run()
    assert not at.exception
    assert any("Story architecture" in heading.value for heading in at.subheader)


def test_content_impact_lab_public_demo():
    app = ROOT / "projects" / "content-impact-lab" / "app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    assert not at.exception
    assert len(at.metric) == 3
    assert len(at.slider) == 2
    assert at.number_input[0].value >= 0
