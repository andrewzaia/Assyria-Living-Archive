"""Reject invented identities, citations and unrecorded specialist approvals."""
import copy
import unittest
from identity_register import DATA, validate, build_view
from concordance import build_view as build_concordance_view
from content import ARTICLES as FOUNDATION
from biblical_content import ARTICLES as BIBLICAL
from case_files import DATA as OBJECTS
from text_comparisons import DATA as TEXTS


class IdentityTests(unittest.TestCase):
    def test_source_scoped_register(self):
        self.assertEqual(validate(), {"cases": 8, "evidence_links": 12})
        view = build_view(build_concordance_view(FOUNDATION + BIBLICAL, OBJECTS, TEXTS))
        self.assertEqual(len(view), 8)
        self.assertTrue(all(ref["url"].startswith("/") for c in view for ref in c["evidence"]))

    def _reject(self, fn, error):
        data = copy.deepcopy(DATA)
        fn(data["cases"])
        with self.assertRaisesRegex(ValueError, error):
            validate(data)

    def test_no_fabricated_object(self):
        self._reject(lambda c: c[0]["evidence"][0].update(slug="fabricated"), "Identity object")

    def test_no_fabricated_scripture(self):
        self._reject(lambda c: c[0]["evidence"][1].update(ref=["GEN", 10, 1, 2]), "Identity Scripture")

    def test_no_unverified_approval(self):
        self._reject(lambda c: c[0].update(review_status="reviewed"), "Unsubstantiated")

    def test_no_unknown_term(self):
        self._reject(lambda c: c[0]["terms"].append("invented"), "Unknown or duplicate")

    def test_no_duplicate_evidence(self):
        self._reject(lambda c: c[0]["evidence"].append(c[0]["evidence"][0].copy()), "Duplicate identity evidence")


if __name__ == "__main__":
    unittest.main()
