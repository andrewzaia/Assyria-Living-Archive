"""Negative tests for site preservation, manifest changes, and ZIP recovery."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from preservation import REQUIRED, MANIFEST, create_manifest, verify_manifest
from export_archive import export


class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name, "site")
        self.root.mkdir()
        for name in sorted(REQUIRED):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture:" + name, encoding="utf-8")

    def test_manifest_deterministic_and_strict(self):
        first = create_manifest(self.root, "/Assyria-Living-Archive", False)
        second = create_manifest(self.root, "/Assyria-Living-Archive", False)
        self.assertEqual(first, second)
        self.assertEqual(verify_manifest(self.root), first)
        self.assertEqual(first["file_count"], len(REQUIRED))
        self.assertFalse(first["indexing_enabled"])

    def test_tampered_content_fails_integrity(self):
        create_manifest(self.root, "", False)
        (self.root / "index.html").write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify_manifest(self.root)

    def test_added_or_deleted_file_fails_integrity(self):
        create_manifest(self.root, "", False)
        (self.root / "another-file.txt").write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "file list differs"):
            verify_manifest(self.root)
        (self.root / "another-file.txt").unlink()
        (self.root / "catalogue.json").unlink()
        with self.assertRaises(ValueError):
            verify_manifest(self.root)

    def test_repeated_manifest_record_fails_integrity(self):
        create_manifest(self.root, "", False)
        manifest = json.loads((self.root / MANIFEST).read_text(encoding="utf-8"))
        manifest["files"].append(manifest["files"][0])
        (self.root / MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify_manifest(self.root)

    def test_zip_restore_and_safe_output(self):
        create_manifest(self.root, "", False)
        output = Path(self.temporary.name, "backup.zip")
        self.assertEqual(export(self.root, output), len(REQUIRED) + 1)
        self.assertTrue(output.exists())
        with self.assertRaisesRegex(ValueError, "outside"):
            export(self.root, self.root / "backup.zip")


if __name__ == "__main__":
    unittest.main()
