"""Checks for editorial preflight signals."""
import unittest
from contentos.core import Request
from contentos.editorial_audit import audit


def brief():
    return Request("Better decisions", "Blog post", "Data modernization",
                   "Consideration", "", [])


class EditorialAuditTests(unittest.TestCase):
    def test_claims_and_style_flags(self):
        result = audit("# Better decisions\n\nWe utilize a guaranteed approach.", brief())
        self.assertTrue(result["legal"])
        self.assertTrue(result["ap"])
        self.assertTrue(result["seo"]["topic_in_copy"])

    def test_portfolio_metadata_is_not_full_text(self):
        result = audit("# Better decisions\n\nUseful explanation.", brief())
        self.assertGreater(result["portfolio"]["references"], 0)
        self.assertIn("not been ingested", result["portfolio"]["note"])

    def test_social_copy_gets_channel_specific_guidance(self):
        req = brief()
        req.asset_type = "Social post"
        result = audit("# Better decisions\n\nOne useful idea.", req)
        self.assertTrue(any("destination page" in x for x in result["seo"]["recommendations"]))


if __name__ == "__main__":
    unittest.main()
