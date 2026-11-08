from contentos.salesforce_demo import OPPORTUNITIES, recommended_opportunities, brief_for


def test_synthetic_opportunities_have_clear_labels():
    assert len(OPPORTUNITIES) >= 3
    for opp in OPPORTUNITIES:
        assert "fictional" in opp["account"].lower()
        assert opp["id"].startswith("DEMO-OPP-")
        assert opp["call_note"].startswith("Synthetic call summary:")


def test_prioritizes_high_risk():
    ranked = recommended_opportunities()
    assert ranked[0]["risk"] == "High"
    assert ranked[-1]["risk"] == "Low"


def test_brief_is_copy_ready_and_disclaimed():
    brief = brief_for(OPPORTUNITIES[0])
    assert "FICTIONAL DATA ONLY" in brief
    assert OPPORTUNITIES[0]["signal"] in brief
    assert "do not invent customer quotes" in brief
