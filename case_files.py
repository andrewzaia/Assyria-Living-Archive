"""Accessioned archaeological case files and explicit source limitations.

The curated case files use institutional object IDs and edition routes. A
source link is not a claimed independent collation of Akkadian tablet signs.
"""
import json
import re
from html import escape as H
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/object-case-files.json").read_text(encoding="utf-8"))
BY_SLUG = {item["slug"]: item for item in DATA}

REQUIRED = ("slug", "title", "summary", "catalogue", "edition", "findspot",
            "dating", "genre", "line_focus", "period", "kind", "source_id",
            "source_url", "sections", "sources", "related", "note", "passages")


def validate(sources):
    if len(DATA) != 9 or len(BY_SLUG) != len(DATA):
        raise ValueError("Expected nine unique archaeological case files")
    known = {source["id"]: source for source in sources}
    for item in DATA:
        if any(key not in item or not item[key] and key != "passages" for key in REQUIRED):
            raise ValueError("Case file lacks identifying metadata: " + str(item.get("slug")))
        if not re.fullmatch(r"(tablet|met|bm)-[a-z0-9-]+", item["slug"]):
            raise ValueError("Invalid case file slug")
        if item["period"] not in {"middle", "later"}:
            raise ValueError("Case file must state its period")
        if item["slug"].startswith("bm-") != (item["period"] == "later"):
            raise ValueError("Chronicle must not be presented as a Middle Assyrian text")
        if len(item["sections"]) != 4 or len({part["title"] for part in item["sections"]}) != 4:
            raise ValueError("Each case file needs four distinct original sections")
        if any(len(part["text"].split()) < 48 for part in item["sections"]):
            raise ValueError("Case file sections need substantive explanatory prose")
        if len(item["sources"]) != len(set(item["sources"])):
            raise ValueError("Repeated source ID in case file")
        if item["source_id"] not in known or item["source_id"] not in item["sources"]:
            raise ValueError("Object source ID must be in curated bibliography")
        if item["source_url"] != known[item["source_id"]]["url"]:
            raise ValueError("Object source URL must match curated source record")
        parsed = urlsplit(item["source_url"])
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("An object record must link to an institutional HTTPS source")
        if any(source not in known for source in item["sources"]):
            raise ValueError("Case file bibliography contains unknown source")
        if len(item["related"]) < 2:
            raise ValueError("Case file must have connected historical reading routes")
        if item["period"] == "later" and (not item["passages"] or "bible-webbe" not in item["sources"]):
            raise ValueError("The Babylonian chronicle case needs explicit biblical-primary comparison")
        if item["period"] == "middle" and item["passages"]:
            raise ValueError("Do not silently infer a contemporaneous biblical passage for a Middle Assyrian tablet")
        if not any(word in item["note"].lower() for word in ("philological", "review")):
            raise ValueError("Each file must disclose outstanding independent review")
    return len(DATA)


def object_panel(item):
    """Show period, accession, provenance, edition and checked line scope."""
    def pair(label, value):
        return '<div><dt>' + H(label) + '</dt><dd>' + H(value) + '</dd></div>'
    details = (
        pair("Object / collection no.", item["catalogue"]) +
        pair("Edition and text ID", item["edition"]) +
        pair("Findspot / archive", item["findspot"]) +
        pair("Dating", item["dating"]) +
        pair("Document type", item["genre"]) +
        pair("Read these lines", item["line_focus"])
    )
    return (
        '<section class="object-panel" aria-labelledby="object-panel-heading">' +
        '<span class="eyebrow">OBJECT LEVEL EVIDENCE / ' + H(item["period"].upper()) + '</span>' +
        '<h2 id="object-panel-heading">Identify the object first.</h2><dl>' + details + '</dl>' +
        '<p><a href="' + H(item["source_url"], quote=True) + '" rel="noopener noreferrer" target="_blank">' +
        'Open the original institutional object or text edition</a>. This catalogue link provides an identified record; ' +
        'the archive has not independently collated ancient signs or verified every translation choice.</p></section>'
    )
