"""Regression checks for Scripture, provincial evidence and source roles."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from exile_provinces import DATA,validate,build_view,article_links
from content import ARTICLES as FOUNDATION
from biblical_content import ARTICLES as BIBLICAL

class ExileEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
        cls.articles=FOUNDATION+BIBLICAL

    def test_authored_studies_and_reading_routes(self):
        self.assertEqual(validate(self.sources,self.articles),{
            "cases":12,"bible_routes":17,"original_text_cases":3,
            "museum_object_cases":2,"context_cases":7,"categories":5,
            "distinct_supporting_sources":13})
        self.assertEqual(len(build_view(self.sources)),12)
        self.assertIn("/exile-provinces/#exile-halah-identification",article_links("assyrian-deportations-texts"))

    def rejects(self,change,reason):
        d=copy.deepcopy(DATA)
        change(d)
        with self.assertRaisesRegex(ValueError,reason):
            validate(self.sources,self.articles,d)

    def test_fake_original_inscription_coordinates(self):
        self.rejects(lambda d:d["cases"][0].update(source_location="Q003455 column 999"),"False original edition")

    def test_fake_tax_letter_identity(self):
        self.rejects(lambda d:d["cases"][6].update(source_location="P999999 reverse 400"),"False original edition")

    def test_swapped_evidence_source(self):
        self.rejects(lambda d:d["cases"][6].update(source_id="aebp-deportation"),"Unverified or swapped")

    def test_swapped_scripture_reference(self):
        self.rejects(lambda d:d["cases"][1].update(biblical=[["2KI",17,7,7]]),"Bible scope")

    def test_saa_aramaean_provenance_cannot_be_relabelled(self):
        self.rejects(lambda d:d["cases"][7].update(scope="Israelites of the deportation convoy"),"Distinct Aramaean")

    def test_lachish_cannot_be_mislabelled_samaria(self):
        self.rejects(lambda d:d["cases"][10].update(limits="Pictured northern Israelite households"),"Later Lachish")

    def test_scholarship_cannot_masquerade_as_primary_inscription(self):
        self.rejects(lambda d:d["cases"][11].update(kind="edited-text"),"Secondary synthesis")

    def test_oxford_full_text_not_claimed(self):
        self.rejects(lambda d:d["cases"][11].update(limits="I have fully checked the original argument in every paragraph."),"abstract")

    def test_review_caveat_cannot_disappear(self):
        self.rejects(lambda d:d.update(method="Everything certified"),"review limits")

    def test_claims_keep_reading_roles(self):
        x=next(c for c in DATA["cases"] if c["id"]=="samaria-tax-letter")
        self.assertEqual(x["kind"],"edited-text")
        self.assertIn("SAA 01 220",x["source_location"])
        self.assertIn("P334789",x["source_location"])
        self.assertEqual(DATA["cases"][7]["kind"],"specialist-identified-text")
        self.assertEqual(DATA["cases"][9]["kind"],"museum-object")

if __name__=="__main__":
    unittest.main()
