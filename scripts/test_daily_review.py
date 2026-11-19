"""Unit tests for daily read-only maintenance reporting."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from daily_review import markdown, rotate, snapshot


class DailyReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        (self.root / "static").mkdir()
        self.when = dt.date(2026, 11, 21)
        self.records = [
            {"id": "AP-0001", "country": "Turkey", "title": "1843 villages",
             "summary": "Recorded violence", "sources": [{"url": "https://example.org/a"}]},
            {"id": "AP-0002", "country": "Turkey", "title": "1846 villages",
             "summary": "Recorded violence", "sources": [{"url": "https://example.org/b"}]},
        ]
        self.audit = {"sources": [{"url": "https://example.org/a",
                                    "captured_record_ids": ["AP-0001"]}]}
        self.roadmap = {"milestones": [{"id": "assyrian-persecution",
                                         "status": "in-progress",
                                         "title": "Persecution map",
                                         "delivered": "2 attributed records"}]}
        self.curated = [
            {"id": "a", "title": "A", "publisher": "P", "url": "https://example.org/a",
             "type": "Primary source", "access": "Online", "checked": "2026-10-29"},
            {"id": "b", "title": "B", "publisher": "P", "url": "https://example.org/b",
             "type": "Primary source", "access": "Online", "checked": "2026-10-29"},
        ]
        self.write()

    def write(self):
        for name, data in (
            ("static/persecution-records.json", {"records": self.records}),
            ("data/persecution-source-audit.json", self.audit),
            ("data/project-roadmap.json", self.roadmap),
            ("sources.json", self.curated)
        ):
            (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def test_rotating_sources_is_deterministic_and_bounded(self):
        items = list(range(7))
        self.assertEqual(rotate(items, self.when, 3), rotate(items, self.when, 3))
        self.assertEqual(len(rotate(items, self.when, 3)), 3)
        self.assertEqual(len(set(rotate(items, self.when, 3))), 3)
        self.assertEqual(len(rotate(items, self.when, 100)), len(items))
        with self.assertRaises(ValueError):
            rotate(items, self.when, 0)

    def test_read_only_snapshot_finds_untriaged_cases(self):
        result = snapshot(self.root, self.when, sample=1, network=False)
        self.assertEqual(result["catalogue_records"], 2)
        self.assertEqual(result["catalogue_countries"], 1)
        self.assertEqual(result["outstanding_source_triage"], 1)
        self.assertEqual(result["priority_cases"][0]["id"], "AP-0002")
        self.assertEqual(result["source_health"]["summary"], {"not-probed": 1})
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual(self.root.joinpath("sources.json").read_text(encoding="utf-8"),
                         json.dumps(self.curated))

    def test_source_mismatch_detected_without_rewriting(self):
        self.audit["sources"][0]["url"] = "https://example.org/mismatched"
        self.write()
        result = snapshot(self.root, self.when)
        self.assertTrue(any("mismatch" in issue.lower()
                            for issue in result["diagnostics"]))

    def test_stale_roadmap_and_unknown_source_record_flagged(self):
        self.roadmap["milestones"][0]["delivered"] = "1 attributed record"
        self.audit["sources"][0]["captured_record_ids"].append("AP-9999")
        self.write()
        result = snapshot(self.root, self.when)
        self.assertTrue(any("Roadmap" in issue for issue in result["diagnostics"]))
        self.assertTrue(any("AP-9999" in issue for issue in result["diagnostics"]))

    def test_daily_summary_is_explicit_about_evidence_limits(self):
        result = snapshot(self.root, self.when)
        text = markdown(result, validation="success",
                        run_url="https://github.com/andrewzaia/Assyria-Living-Archive/actions/runs/1")
        self.assertIn("AP-0002", text)
        self.assertIn("not marked reviewed", text)
        self.assertIn("does not change the website", text)
        self.assertIn("Repository validation:** success", text)
        self.assertNotIn("\u2014", text)

    def test_network_scan_is_explicit_and_bounded(self):
        fake = {"record_count": 1, "summary": {"restricted-or-rate-limited": 1},
                "results": [{"id": "a", "status": "restricted-or-rate-limited",
                             "http_status": 403}]}
        with patch("daily_review.audit", return_value=fake) as scan:
            result = snapshot(self.root, self.when, sample=1, network=True)
        scan.assert_called_once()
        self.assertTrue(scan.call_args.kwargs["network"])
        self.assertEqual(len(scan.call_args.args[0]), 1)
        self.assertIn("HTTP 403", markdown(result))


if __name__ == "__main__":
    unittest.main()
