"""Negative and positive checks for source-edition and Scripture alignment."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from royal_witnesses import DATA, validate, build_view, article_links
from content import ARTICLES as FOUNDATION
from biblical_content import ARTICLES as BIBLICAL


class RoyalWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
        cls.articles = FOUNDATION + BIBLICAL

    def test_curated_edition_and_bible_scopes(self):
        self.assertEqual(validate(self.sources, self.articles), {
            "comparisons": 6, "inscription_comparisons": 5,
            "museum_comparisons": 1, "bible_routes": 10, "edition_identifiers": 3})
        view = build_view(self.sources)
        self.assertTrue(all(c["source_url"].startswith("https://") for c in view))
        self.assertEqual(len(view[4]["bible_links"]), 1)
        self.assertIn("royal-witnesses/#witness-hezekiah-tribute-quantities",
                      article_links("sennacherib-prism-hezekiah"))

    def reject(self, mutation, pattern):
        data = copy.deepcopy(DATA)
        mutation(data["cases"])
        with self.assertRaisesRegex(ValueError, pattern):
            validate(self.sources, self.articles, data)

    def test_nonexistent_inscription_line_is_rejected(self):
        self.reject(lambda rows: rows[1].update(lines="Edited lines 900-1000"), "Invented")

    def test_wrong_original_edition_identifier_is_rejected(self):
        self.reject(lambda rows: rows[2].update(edition_id="RINAP 3 / Q999999"), "identifier")

    def test_unreviewed_new_bible_pairing_is_rejected(self):
        self.reject(lambda rows: rows[1]["biblical"].__setitem__(0, ["ISA", 20, 2, 6]), "Unreviewed")

    def test_museum_relief_must_not_gain_text_lines(self):
        self.reject(lambda rows: rows[5].update(lines="Column iii 200"), "relief")

    def test_tribute_difference_must_remain_visible(self):
        self.reject(lambda rows: rows[4].update(difference="The reports are completely equal and identical."),
                    "conflicting tribute")

    def test_unknown_article_rejected(self):
        self.reject(lambda rows: rows[0].update(article="unknown-article"), "Unknown")

    def test_unrecognized_citation_rejected(self):
        self.reject(lambda rows: rows[0].update(source_id="unverified-source"), "source")


if __name__ == "__main__":
    unittest.main()
