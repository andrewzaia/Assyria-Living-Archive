"""Deterministic tests for non-destructive source and accessibility audits."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_sources import audit, classify, load_records, probe
from audit_accessibility import audit as inspect_page


class ExternalSourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "sources.json"
        self.sample = [{"id":"sample","title":"Institutional source","publisher":"Institution",
                        "url":"https://example.org/article","type":"Primary source",
                        "access":"Read only at provider","checked":"2026-10-29"}]
        self.path.write_text(json.dumps(self.sample), encoding="utf-8")

    def test_offline_audit_is_explicitly_unprobed(self):
        records = load_records(self.path)
        report = audit(records)
        self.assertEqual(report["mode"], "offline-metadata-only")
        self.assertEqual(report["summary"], {"not-probed": 1})
        self.assertEqual(report["record_count"], 1)

    def test_no_local_private_or_duplicate_url_targets(self):
        for url in ("http://127.0.0.1/data", "https://localhost/admin",
                    "file:///etc/passwd", "http://192.168.0.2/private",
                    "https://internal.local/"):
            self.sample[0]["url"] = url
            self.path.write_text(json.dumps(self.sample), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe public source"):
                load_records(self.path)
        self.sample[0]["url"] = "https://example.org/"
        self.path.write_text(json.dumps(self.sample * 2), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_records(self.path)

    def test_403_429_and_transient_errors_are_not_broken_claims(self):
        for status in (401, 403, 429):
            self.assertEqual(classify(status, "https://a.org/", "https://a.org/"),
                             "restricted-or-rate-limited")
        self.assertEqual(classify(404, "https://a.org/", "https://a.org/"), "missing-review")
        self.assertEqual(classify(503, "https://a.org/", "https://a.org/"), "temporary-failure")
        self.assertEqual(classify(200, "https://a.org/", "https://a.org/"), "reachable")
        self.assertEqual(classify(200, "https://a.org/", "https://b.org/"), "redirect-review")

    def test_head_404_rechecked_with_get(self):
        def fake_request(url, method, timeout):
            return (404 if method == "HEAD" else 200, url)
        with patch("audit_sources._request", side_effect=fake_request) as mock:
            record = probe(self.sample[0])
        self.assertEqual(record["status"], "reachable")
        self.assertEqual(mock.call_count, 2)

    def test_remote_failure_never_claims_broken_source(self):
        with patch("audit_sources._request", side_effect=TimeoutError("Timed out")):
            item = probe(self.sample[0])
        self.assertEqual(item["status"], "network-unconfirmed")


class AccessibilityAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.site = Path(self.temporary.name)
        (self.site / "index.html").write_text('''<!doctype html><html lang="en-AU">
        <a class="skip" href="#main">Skip</a><button class="menu-toggle" aria-controls="mobile-site-nav" aria-expanded="false">Menu</button>
        <nav id="mobile-site-nav"></nav><dialog id="search-dialog" aria-labelledby="search-title"></dialog>
        <h2 id="search-title">Search</h2><main id="main"><h1>Welcome</h1><img src="x" alt="example"><label>Name <input id="person"></label></main></html>''', encoding="utf-8")

    def test_semantic_smoke_passes(self):
        self.assertEqual(inspect_page("/", self.site), [])

    def test_missing_alt_and_label_fail(self):
        html = (self.site / "index.html")
        html.write_text(html.read_text().replace('alt="example"', '').replace('<label>Name <input id="person"></label>', '<input id="person">'), encoding="utf-8")
        result = inspect_page("/", self.site)
        self.assertTrue(any("missing alt" in error for error in result))
        self.assertTrue(any("missing accessible label" in error for error in result))


if __name__ == "__main__":
    unittest.main()
