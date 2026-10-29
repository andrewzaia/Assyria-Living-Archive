"""Deterministic SHA-256 manifest for every generated public site file.

Integrity is a transfer/change check, not authenticity, backup retention or peer review.
The manifest excludes itself and is built only after all website files are written.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath

MANIFEST = "preservation-manifest.json"
REQUIRED = {"index.html", "robots.txt", "catalogue.json", "sources/index.html",
            "archive/references.json", "about/index.html", "bible/index.html",
            "archive/maps/assyria-atlas.json", "editorial-revisions.json"}


def _safe_files(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Generated site directory must exist and not be a symlink")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Preservation output contains a symlink: " + str(path))
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("Unexpected preservation file type: " + str(path))
        name = path.relative_to(root).as_posix()
        if name == MANIFEST:
            continue
        if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
            raise ValueError("Unsafe preservation path: " + name)
        result[name] = path
    if not REQUIRED.issubset(result):
        raise ValueError("Mandatory preservation files missing: " + ", ".join(sorted(REQUIRED - result.keys())))
    return result


def _digest(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def create_manifest(root, base_path, allow_indexing):
    if not isinstance(base_path, str) or not isinstance(allow_indexing, bool):
        raise ValueError("Manifest requires actual validated deployment settings")
    files = _safe_files(root)
    rows = []
    for name, path in files.items():
        sha, size = _digest(path)
        rows.append({"path": name, "bytes": size, "sha256": sha})
    manifest = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "purpose": "Built-site transfer fixity. Not a digital signature, independent archive backup, historical review, website accessibility certification or evidence that an external link is live.",
        "base_path": base_path,
        "indexing_enabled": allow_indexing,
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "files": rows,
    }
    Path(root, MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify_manifest(root):
    root = Path(root)
    manifest_path = root / MANIFEST
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("The generated site has no valid preservation manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("hash_algorithm") != "sha256":
        raise ValueError("Unsupported preservation manifest version or algorithm")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Preservation manifest contains no file records")
    files = _safe_files(root)
    paths = [row.get("path") for row in rows if isinstance(row, dict)]
    if len(paths) != len(rows) or len(set(paths)) != len(paths) or paths != sorted(paths):
        raise ValueError("Preservation manifest has duplicate, malformed or unordered paths")
    if set(paths) != set(files):
        missing = sorted(set(paths) - set(files))
        unexpected = sorted(set(files) - set(paths))
        raise ValueError("Preservation file list differs: missing=" + repr(missing[:5]) +
                         "; unexpected=" + repr(unexpected[:5]))
    total = 0
    for row in rows:
        name = row["path"]
        if not isinstance(name, str) or not name or name.startswith("/") or ".." in PurePosixPath(name).parts:
            raise ValueError("Unsafe recorded path")
        sha, size = _digest(files[name])
        if row.get("sha256") != sha or row.get("bytes") != size:
            raise ValueError("Preservation checksum or byte count differs: " + name)
        total += size
    if manifest.get("file_count") != len(rows) or manifest.get("total_bytes") != total:
        raise ValueError("Incorrect preservation manifest totals")
    if not isinstance(manifest.get("base_path"), str) or not isinstance(manifest.get("indexing_enabled"), bool):
        raise ValueError("Preservation manifest deployment metadata invalid")
    return manifest
