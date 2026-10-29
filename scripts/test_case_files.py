"""Regression tests for accessioned archaeological and tablet study metadata."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import case_files


class ObjectCaseFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))

    def test_all_nine_cases_have_valid_objects_and_periods(self):
        self.assertEqual(case_files.validate(self.sources), 9)
        self.assertEqual(sum(x["period"] == "middle" for x in case_files.DATA), 8)
        self.assertEqual(sum(x["period"] == "later" for x in case_files.DATA), 1)
        self.assertEqual({x["source_id"] for x in case_files.DATA}.__len__(), 9)
        self.assertEqual(sum(len(x["sections"]) for x in case_files.DATA), 36)
        self.assertTrue(all(x["line_focus"] and x["catalogue"] for x in case_files.DATA))

    def test_source_url_must_agree_with_curated_record(self):
        cases = copy.deepcopy(case_files.DATA)
        cases[0]["source_url"] = "https://example.org/pretend-tablet"
        with patch.object(case_files, "DATA", cases), self.assertRaisesRegex(ValueError, "source URL"):
            case_files.validate(self.sources)

    def test_late_chronicle_cannot_be_labelled_middle_assyrian(self):
        cases = copy.deepcopy(case_files.DATA)
        cases[-1]["period"] = "middle"
        with patch.object(case_files, "DATA", cases), self.assertRaisesRegex(ValueError, "Chronicle"):
            case_files.validate(self.sources)

    def test_missing_edition_scope_fails(self):
        cases = copy.deepcopy(case_files.DATA)
        cases[0]["line_focus"] = ""
        with patch.object(case_files, "DATA", cases), self.assertRaisesRegex(ValueError, "metadata"):
            case_files.validate(self.sources)

    def test_object_panels_keep_citation_and_missing_review_disclaimer(self):
        for item in case_files.DATA:
            panel = case_files.object_panel(item)
            self.assertIn(item["catalogue"], panel)
            self.assertIn(item["edition"], panel)
            self.assertIn(item["source_url"], panel)
            self.assertIn("not independently collated", panel)


if __name__ == "__main__":
    unittest.main()
