"""Negative and positive checks for manually curated source-to-text relationships."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import concordance
from content import ARTICLES as FOUNDATION
from biblical_content import ARTICLES as BIBLICAL


class ConcordanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.articles = FOUNDATION + BIBLICAL
        cls.cases = json.loads((ROOT / "data/object-case-files.json").read_text(encoding="utf-8"))
        cls.texts = json.loads((ROOT / "data/text-comparisons.json").read_text(encoding="utf-8"))

    def test_counts_and_distinct_source_relationships(self):
        report = concordance.validate(self.articles, self.cases, self.texts)
        self.assertEqual(report, {"terms": 25, "object_links": 32,
                                  "article_links": 43, "passage_links": 11})
        view = concordance.build_view(self.articles, self.cases, self.texts)
        self.assertEqual(len(view), 25)
        barley = next(t for t in view if t["id"] == "barley")
        self.assertEqual(len(barley["objects"]), 3)
        self.assertTrue(any("#transliteration-tablet-kaj-233-horse-barley-1" in o["url"]
                            for o in barley["objects"]))

    def _reject(self, update, pattern):
        terms = copy.deepcopy(concordance.TERMS)
        update(terms)
        with patch.object(concordance, "TERMS", terms), self.assertRaisesRegex(ValueError, pattern):
            concordance.validate(self.articles, self.cases, self.texts)

    def test_unknown_object_ref_is_rejected(self):
        self._reject(lambda x: x[0]["objects"].append({
            "slug": "invented-tablet", "role": "object-context",
            "note": "This record has no historical source and must be rejected."
        }), "missing object")

    def test_nonexistent_edition_line_is_rejected(self):
        self._reject(lambda x: x[5]["objects"][0].update({"line": "Obverse 999"}),
                     "Missing line")

    def test_cannot_fabricate_a_line_for_unedited_museum_tablet(self):
        self._reject(lambda x: x[12]["objects"][0].update({
            "line": "Obverse 2", "role": "edition-line"
        }), "Missing line")

    def test_wrong_biblical_coordinates_are_rejected(self):
        self._reject(lambda x: x[2]["passages"][0].update({"ref": ["NAH", 1, 1, 1000]}),
                     "missing from local Scripture")

    def test_unapproved_association_to_article_is_rejected(self):
        self._reject(lambda x: x[2]["articles"].append("fictional-article"),
                     "encyclopaedia")

    def test_disallow_disguised_line_as_object_context(self):
        self._reject(lambda x: x[5]["objects"][0].update({"role": "object-context"}),
                     "Line evidence")

    def test_bible_links_are_explicit_and_not_claimed_as_shared_events(self):
        ass=next(x for x in concordance.TERMS if x["id"]=="biblical-asshur")
        self.assertEqual(ass["objects"], [])
        self.assertEqual(len(ass["passages"]), 2)
        self.assertIn("same historical event", concordance.DATA["method"])

    def test_bidirectional_article_links(self):
        text = concordance.article_links("tablet-kaj-233-horse-barley")
        self.assertIn('/concordance/#entry-barley', text)
        self.assertIn('/concordance/#entry-service-horse', text)


if __name__ == "__main__":
    unittest.main()
