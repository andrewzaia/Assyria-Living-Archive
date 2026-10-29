"""Export a deterministic ZIP of a previously built site and verify restore integrity.

The ZIP is a transfer copy. Keep independent offline/offsite copies; CI artifacts
and GitHub repositories alone are not an independent preservation repository.
"""
import argparse
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from preservation import MANIFEST, verify_manifest


def export(root, output, restore_check=True):
    root = Path(root).resolve()
    output = Path(output).resolve()
    if output == root / MANIFEST or output.is_relative_to(root):
        raise ValueError("Export ZIP must be written outside the generated site")
    manifest = verify_manifest(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    names = [entry["path"] for entry in manifest["files"]] + [MANIFEST]
    try:
        with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for name in names:
                info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                with archive.open(info, "w", force_zip64=True) as destination:
                    with (root / name).open("rb") as source:
                        for chunk in iter(lambda: source.read(1024 * 1024), b""):
                            destination.write(chunk)
        if restore_check:
            with tempfile.TemporaryDirectory(prefix="assyria-restore-") as staging:
                restored = Path(staging)
                with ZipFile(output) as archive:
                    members = archive.namelist()
                    if len(members) != len(names) or set(members) != set(names):
                        raise ValueError("Export member list differs from preservation manifest")
                    for name in members:
                        path = restored / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with archive.open(name) as source, path.open("wb") as dest:
                            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                                dest.write(chunk)
                recovered = verify_manifest(restored)
                if recovered != manifest:
                    raise ValueError("Restored archive manifest metadata differs")
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return len(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "dist")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-restore-check", action="store_true",
                        help="Not recommended; skips independent extraction and hashing")
    args = parser.parse_args()
    count = export(args.site, args.output, restore_check=not args.skip_restore_check)
    print(f"Preserved and packed {count} files into {args.output}; " +
          ("verification skipped" if args.skip_restore_check else "restore checks passed"))


if __name__ == "__main__":
    main()
