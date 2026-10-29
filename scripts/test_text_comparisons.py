"""Regression checks for source-attributed transliteration and translation limits."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import text_comparisons


class TextComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "data/object-case-files.json").read_text(encoding="utf-8"))
        cls.sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))

    def test_expected_edited_and_uncollated_readings(self):
        report = text_comparisons.validate(self.cases, self.sources)
        self.assertEqual(report, {"cases": 9, "excerpted": 7, "edition_pending": 2, "line_excerpts": 16})

    def test_missing_cuneiform_transliteration_is_rejected(self):
        data = copy.deepcopy(text_comparisons.DATA)
        data["items"][0]["lines"][0]["transliteration"] = ""
        with patch.object(text_comparisons, "DATA", data), self.assertRaisesRegex(ValueError, "short"):
            text_comparisons.validate(self.cases, self.sources)

    def test_cannot_invent_lines_for_museum_object(self):
        data = copy.deepcopy(text_comparisons.DATA)
        data["items"][-2]["lines"] = copy.deepcopy(data["items"][0]["lines"])
        with patch.object(text_comparisons, "DATA", data), self.assertRaisesRegex(ValueError, "Do not invent"):
            text_comparisons.validate(self.cases, self.sources)

    def test_cannot_silently_delete_restoration_brackets(self):
        data = copy.deepcopy(text_comparisons.DATA)
        line = next(l for item in data["items"] for l in item["lines"] if l["uncertainty"] == "restored")
        line["transliteration"] = "li-mu"
        with patch.object(text_comparisons, "DATA", data), self.assertRaisesRegex(ValueError, "Restored"):
            text_comparisons.validate(self.cases, self.sources)

    def test_copy_requires_edition_attribution_and_license(self):
        data = copy.deepcopy(text_comparisons.DATA)
        data["items"][0]["edition_credit"] = "Generic source"
        with patch.object(text_comparisons, "DATA", data), self.assertRaisesRegex(ValueError, "licence"):
            text_comparisons.validate(self.cases, self.sources)

    def test_missing_edition_panel_never_fabricates_text(self):
        cases = {case["slug"]: case for case in self.cases}
        panel = text_comparisons.render_lines(cases["met-62-85-3-sealed-tablet"])
        self.assertIn("No verified line-by-line text available.", panel)
        self.assertNotIn("class=\"compare-table\"", panel)
        self.assertIn(cases["met-62-85-3-sealed-tablet"]["source_url"], panel)

    def test_edited_case_keeps_very_short_original_excerpt_and_attribution(self):
        case = self.cases[2]
        panel = text_comparisons.render_lines(case)
        self.assertIn("16 ANŠE 5 BAN₂ ŠE", panel)
        self.assertIn("CC BY-SA 3.0", panel)
        self.assertIn("not</strong> a new translation", panel)
        self.assertIn("class=\"compare-table\"", panel)


if __name__ == "__main__":
    unittest.main()
