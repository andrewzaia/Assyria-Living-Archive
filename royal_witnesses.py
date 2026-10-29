"""Verified reference coordinates for royal edition and biblical witness comparisons.

Source URLs and edited line ranges are manually curated against ORACC and museum
catalogues. This module validates known references and does not authenticate
the underlying historical assertions, translate ancient text, or merge narratives.
"""
import json
import re
from pathlib import Path
from bible_support import load_bible, reference_label, reference_url

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/royal-witnesses.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
EDITIONS = {
    "oracc-riao-jehu-caption": ("Q004693", "Caption, obverse line 1"),
    "oracc-rinap2-ashdod": ("Q006488", "Edited lines 90-109"),
    "oracc-rinap3-sennacherib22": ("Q003496", None),
}
VALID_RANGES = {
    "oracc-riao-jehu-caption": {"Caption, obverse line 1"},
    "oracc-rinap2-ashdod": {"Edited lines 90-109"},
    "oracc-rinap3-sennacherib22": {
        "Column iii, lines 18-27", "Column iii, lines 27-37",
        "Column iii, lines 37-49 (quantities at lines 41-42)"
    },
}
STATUSES = {"qualified-parallel", "distinct-claims", "unresolved-discrepancy", "different-medium"}


def validate(sources, articles, data=None):
    data = DATA if data is None else data
    cases = data.get("cases", [])
    if data.get("schema_version") != 1 or "pending independent specialist review" not in data.get("method", ""):
        raise ValueError("Royal comparison methodology or review limitation missing")
    if len(cases) != 6 or len({x["id"] for x in cases}) != len(cases):
        raise ValueError("Expected six unique curated witness comparisons")
    source_by_id = {s["id"]: s for s in sources}
    article_slugs = {a["slug"] for a in articles}
    bible_verses = load_bible()["verses"]
    routes = 0
    for case in cases:
        ident = case["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
            raise ValueError("Invalid royal comparison identifier: " + ident)
        if case["ruler"] not in {"Shalmaneser III", "Sargon II", "Sennacherib"}:
            raise ValueError("Unsubstantiated royal identity: " + ident)
        if case["status"] not in STATUSES or case["article"] not in article_slugs:
            raise ValueError("Unknown royal witness status or article: " + ident)
        if case["source_id"] not in source_by_id:
            raise ValueError("Missing cited royal witness source: " + ident)
        source = source_by_id[case["source_id"]]
        if not source["url"].startswith("https://"):
            raise ValueError("Invalid original edition URL: " + ident)
        if case["kind"] == "royal-inscription":
            marker = EDITIONS.get(case["source_id"], (None,))[0]
            if not marker or marker not in source["url"] or marker not in case["edition_id"]:
                raise ValueError("Royal edition identifier missing or mismatched: " + ident)
            if case["lines"] not in VALID_RANGES[case["source_id"]]:
                raise ValueError("Invented or unverified inscription line coordinates: " + ident)
        elif case["kind"] == "museum-object":
            if case["source_id"] != "bm-lachish-panel" or case["lines"] is not None or case["edition_id"] is not None or "124904" not in case["object_id"]:
                raise ValueError("Museum relief cannot be represented as an edited inscription: " + ident)
        else:
            raise ValueError("Unknown royal evidence medium: " + ident)
        for name in ("title", "event_date", "royal", "scripture", "shared", "difference", "uncertainty", "object_id"):
            if not isinstance(case.get(name), str) or len(case[name].strip()) < 20:
                raise ValueError("Missing essential evidence description: " + ident + " / " + name)
        passages = case["biblical"]
        if not passages or len({tuple(p) for p in passages}) != len(passages):
            raise ValueError("Missing or duplicated biblical passage: " + ident)
        for ref in passages:
            if len(ref) != 4 or not isinstance(ref[0], str):
                raise ValueError("Malformed biblical passage: " + ident)
            book, chapter, first, last = ref
            if any(type(x) is not int for x in (chapter, first, last)) or first < 1 or first > last:
                raise ValueError("Invalid biblical passage coordinates: " + ident)
            if (book, chapter, first) not in bible_verses or (book, chapter, last) not in bible_verses:
                raise ValueError("Unattested biblical verse coordinate: " + ident)
            routes += 1
    return {"comparisons": len(cases), "inscription_comparisons": sum(c["kind"] == "royal-inscription" for c in cases),
            "museum_comparisons": sum(c["kind"] == "museum-object" for c in cases),
            "bible_routes": routes, "edition_identifiers": len({c["edition_id"] for c in cases if c["edition_id"]})}


def build_view(sources):
    by_id = {s["id"]: s for s in sources}
    return [{**case,
             "source_url": by_id[case["source_id"]]["url"],
             "source_title": by_id[case["source_id"]]["title"],
             "bible_links": [{"label": reference_label(ref), "url": reference_url(ref)}
                             for ref in case["biblical"]]}
            for case in CASES]
