"""Regression tests for format-specific free-demo writing skills."""
import unittest
from contentos.core import Request, demo_draft, demo_derivatives


def request(asset, derivatives=None, outline=""):
    return Request(
        title="A practical data strategy", asset_type=asset,
        gtm_motion="Data modernization", funnel="Consideration",
        direction="Help technology leaders prioritize investments",
        derivatives=derivatives or [], outline=outline,
        audience="CIOs",
    )


class WritingSkillsTests(unittest.TestCase):
    def test_each_primary_asset_has_a_distinct_shape(self):
        markers = {
            "Blog post": "## The takeaway",
            "eBook": "## Chapter plan",
            "Video script": "**VOICEOVER:**",
            "Landing page": "**CTA:",
            "Ad copy": "### 5.",
            "Social post": "### Post 3",
        }
        for asset, marker in markers.items():
            with self.subTest(asset=asset):
                draft = demo_draft(request(asset))
                self.assertIn(marker, draft)
                self.assertIn("A practical data strategy", draft)

    def test_supplied_blog_outline_shapes_sections(self):
        text = demo_draft(request("Blog post", outline="## Challenges\n## Solutions"))
        self.assertIn("## Challenges", text)
        self.assertIn("## Solutions", text)

    def test_derivatives_only_include_requested_types(self):
        req = request("Blog post", ["Video script", "eBook"])
        output = demo_derivatives(req)
        self.assertEqual(set(output), {"Video script", "eBook"})
        self.assertIn("**VISUAL:**", output["Video script"])
        self.assertIn("1. The decision", output["eBook"])

    def test_no_derivatives_means_no_derivatives(self):
        self.assertEqual(demo_derivatives(request("Blog post")), {})


if __name__ == "__main__":
    unittest.main()
