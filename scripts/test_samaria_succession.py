"""Safeguard inscription identities, damaged readings and biblical coordinates."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from samaria_succession import DATA, validate, build_view, article_links
from content import ARTICLES as FOUNDATION
from biblical_content import ARTICLES as BIBLICAL


class SamariaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
        cls.articles = FOUNDATION + BIBLICAL

    def test_authorised_comparisons(self):
        self.assertEqual(validate(self.sources, self.articles), {
            "cases": 8, "edition_cases": 7, "specialist_synthesis_cases": 1,
            "distinct_edition_ids": 5, "bible_routes": 12, "stages": 4})
        self.assertEqual(len(build_view(self.sources)), 8)
        self.assertIn("samaria-succession/#case-menahem-tribute",
                      article_links("samaria-assyrian-chronology"))

    def rejects(self, change, pattern):
        data = copy.deepcopy(DATA)
        change(data)
        with self.assertRaisesRegex(ValueError, pattern):
            validate(self.sources, self.articles, data)

    def test_fabricated_cuneiform_line(self):
        self.rejects(lambda d: d["cases"][1].update(location="lines 500-999"), "Unreviewed source lines")

    def test_edition_substitution(self):
        self.rejects(lambda d: d["cases"][0].update(source_id="rinap-sargon-samaria7"), "Unreviewed source")

    def test_biblical_substitution(self):
        self.rejects(lambda d: d["cases"][3].update(biblical=[["2KI", 17, 3, 4]]), "Bible passage coordinates")

    def test_invented_shalmaneser_inscription(self):
        self.rejects(lambda d: d["cases"][3].update(mode="edition", edition="Fake tablet Q999999"), "Royal inscription edition")

    def test_sargon_numeric_variant_suppression(self):
        self.rejects(lambda d: d["cases"][5].update(royal="An exact royal census of 27,290 people."), "divergent copy figures")

    def test_royal_prism_variant_suppression(self):
        self.rejects(lambda d: d["cases"][6].update(royal="One unambiguous inscription."), "Nimrud count")

    def test_peqah_damaged_killing_verb(self):
        self.rejects(lambda d: d["cases"][2].update(uncertainty="Everyone agrees the action was clear.",
                                                    royal="Hoshea took over without any textual questions."), "damaged verb")

    def test_review_disclaimer_cannot_disappear(self):
        self.rejects(lambda d: d.update(method="All sources confirmed without limitation"), "review gap")


if __name__ == "__main__":
    unittest.main()
