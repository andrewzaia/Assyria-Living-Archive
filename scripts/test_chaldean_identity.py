"""Prevent sectarian source substitution and ancestry overclaims in archive identity essays."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import ARTICLES
from navigation import NAV_PATHS, NAV_COLUMNS
from section_evidence import DATA as TRAILS
from claim_review import DATA as CLAIMS

BY_SLUG = {a["slug"]: a for a in ARTICLES}
SOURCES = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
BY_SOURCE = {s["id"]: s for s in SOURCES}
RELATED = ("assyrian-identity", "faith-and-churches", "chaldean-church", "chaldean-name-and-heritage")
SCHOLARLY = {
    "gedsh-chaldeans", "parker-2018-chaldaean",
    "hanoosh-2019-chaldean-identity", "donabed-2012-appellative",
    "iranica-ancient-chaldeans", "hanoosh-2016-appellations",
    "gedsh-aramaic", "gedsh-syriac", "gedsh-assyrians",
    "wiley-payne-ancient-chaldaeans",
}

class HistoricalIdentityTests(unittest.TestCase):
    def test_guide_is_visible_sitewide(self):
        self.assertIn("/articles/chaldean-name-and-heritage/", NAV_PATHS)
        self.assertIn("/articles/chaldean-name-and-heritage/", NAV_COLUMNS["Explore"][1][1])
        self.assertEqual(len(BY_SLUG["chaldean-name-and-heritage"]["sections"]), 11)
        for slug in RELATED[:-1]:
            self.assertIn("chaldean-name-and-heritage", BY_SLUG[slug]["related"])

    def test_direct_ethnic_claim_not_inferred_from_church(self):
        church = BY_SLUG["chaldean-church"]
        prose = " ".join(s["text"] for s in church["sections"])
        self.assertIn("no directly verified source", prose.lower())
        self.assertIn("Assyrian heritage", prose)
        self.assertIn("modern ethnic self-identification", prose)
        guide = " ".join(s["text"] for s in BY_SLUG["chaldean-name-and-heritage"]["sections"])
        self.assertIn("Sharing an English name does not establish", guide)
        self.assertIn("Modern Chaldean Catholics", guide)
        self.assertIn("nineteenth-century", guide)
        self.assertIn("not", guide)

    def test_ancient_kaldu_remain_separate_historical_subject(self):
        essay = BY_SLUG["chaldean-name-and-heritage"]
        title = "Ancient Chaldeans in Babylonia are not the same historical category"
        text = next(s["text"] for s in essay["sections"] if s["title"] == title)
        self.assertIn("southern Babylonia", text)
        self.assertIn("distinct ethnic descent", text)
        self.assertIn("iranica-ancient-chaldeans", essay["sources"])

    def test_church_sites_marked_as_first_party_not_ethnicity_proof(self):
        for sid in ("modern-chaldean", "modern-chaldean-history"):
            src = BY_SOURCE[sid]
            self.assertIn("not independent", src["access"].lower())
            self.assertIn("ethnic", src["access"].lower())
        for slug in RELATED:
            article = BY_SLUG[slug]
            self.assertTrue(set(article["sources"]) & SCHOLARLY)
            self.assertIn("gedsh-chaldeans", article["sources"])

    def test_original_sources_and_abstract_scope_are_disclosed(self):
        expected = {
            "gedsh-chaldeans": "gedsh.bethmardutho.org/Chaldeans",
            "parker-2018-chaldaean": "doi.org/10.1093/ehr/cey334",
            "hanoosh-2019-chaldean-identity": "pdxscholar.library.pdx.edu/wll_fac/134/",
            "donabed-2012-appellative": "doi.org/10.1080/14608944.2012.733208",
            "iranica-ancient-chaldeans": "iranicaonline.org/articles/chaldeans-kaldu-west-semitic-tribes",
            "wiley-payne-ancient-chaldaeans": "doi.org/10.1002/9781444338386.wbeah30233",
        }
        for sid, url in expected.items():
            self.assertIn(url, BY_SOURCE[sid]["url"])
        self.assertIn("Full book unavailable", BY_SOURCE["hanoosh-2019-chaldean-identity"]["access"])
        self.assertIn("abstract", BY_SOURCE["parker-2018-chaldaean"]["access"].lower())

    def test_all_identity_essays_have_current_source_trails(self):
        for slug in RELATED:
            original = {s["title"] for s in BY_SLUG[slug]["sections"]}
            recorded = set(TRAILS[slug])
            self.assertEqual(recorded, original, slug)
            for section in TRAILS[slug].values():
                sources = section["sources"]
                self.assertTrue(set(sources) & SCHOLARLY, slug)
                self.assertTrue(set(sources) <= set(BY_SLUG[slug]["sources"]))
        self.assertEqual(sum(len(TRAILS[s]) for s in RELATED), 32)
        # The identity-specific coverage above is stable as other collections grow.
        self.assertTrue(set(RELATED).issubset(TRAILS))


    def test_no_ancient_kaldu_lineage_without_primary_evidence(self):
        guide = BY_SLUG["chaldean-name-and-heritage"]
        guide_text = " ".join(s["text"] for s in guide["sections"])
        church_text = " ".join(s["text"] for s in BY_SLUG["chaldean-church"]["sections"])
        identity_text = " ".join(s["text"] for s in BY_SLUG["assyrian-identity"]["sections"])
        self.assertIn("Evidence verdict: NOT DEMONSTRATED", guide_text)
        self.assertIn("Evidence status - NOT DEMONSTRATED", church_text)
        self.assertIn("Evidence finding: NOT DEMONSTRATED", identity_text)
        for prose in (guide_text,church_text,identity_text):
            self.assertIn("ancient Kaldu",prose)
            self.assertIn("Church of the East",prose)
        self.assertIn("modern self-description", guide_text.lower())
        self.assertIn("not independently consulted", BY_SOURCE["wiley-payne-ancient-chaldaeans"]["access"])

    def test_followup_claims_protect_lineage_proof_standard(self):
        claims = [c for c in CLAIMS["claims"] if 89 <= int(c["id"][3:]) <= 91]
        self.assertEqual([c["id"] for c in claims], ["CL-089","CL-090","CL-091"])
        for item in claims:
            self.assertEqual(item["review"]["status"],"awaiting-independent-review")
            self.assertIsNone(item["review"]["reviewer"])
            self.assertTrue("Kaldu" in item["claim"] or "Chaldean" in item["claim"])
            self.assertIn(item["section"], TRAILS[item["article"]])
        self.assertEqual(len(CLAIMS["claims"]),91)

    def test_disputed_naming_claims_remain_unreviewed(self):
        newer = [c for c in CLAIMS["claims"] if 81 <= int(c["id"][3:]) <= 88]
        self.assertEqual([c["id"] for c in newer], ["CL-%03d" % n for n in range(81,89)])
        for c in newer:
            self.assertIn(c["article"], RELATED)
            self.assertEqual(c["review"]["status"], "awaiting-independent-review")
            self.assertIsNone(c["review"]["reviewer"])
            self.assertTrue(c["evidence_sources"])
            self.assertTrue(set(c["evidence_sources"]) & SCHOLARLY)

if __name__ == "__main__":
    unittest.main()
