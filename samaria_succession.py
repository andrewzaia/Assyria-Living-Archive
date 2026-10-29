"""Source-bounded Samaria chronology and imperial succession cases.

The archive validates exact edited witness coordinates, biblical references and
review limitations. It does not perform epigraphic collation or determine the
historical victor of the Shalmaneser V / Sargon II attribution dispute.
"""
import json
import re
from pathlib import Path
from html import escape as H
from bible_support import load_bible, reference_label, reference_url

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/samaria-succession.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
STAGES = DATA["stages"]
EDITION_COORDINATES = {
    "rinap-tiglath-menahem32": ("Q003445", {"Obverse line 1"}),
    "rinap-tiglath-peqah42": ("Q003455", {"Obverse lines 15'-16' (broken text)", "Obverse lines 17'-18' (damaged verb)"}),
    "rinap-sargon-samaria7": ("Q006488", {"Lines 23-25, especially 23b-25a", "Line 24 and its exemplar commentary"}),
    "rinap-sargon-nimrud74": ("Q006555", {"Column iv, lines 25-38"}),
    "rinap-sargon-annals1": ("Q006482", {"Lines 12-17 (heavily restored)"}),
}
BIBLE_SCOPES = {
    "menahem-tribute": (("2KI", 15, 19, 20),),
    "north-israel-deportations": (("2KI", 15, 29, 29), ("1CH", 5, 26, 26)),
    "peqah-hoshea": (("2KI", 15, 30, 30),),
    "shalmaneser-siege": (("2KI", 17, 3, 6), ("2KI", 18, 9, 10)),
    "sargon-capture-claim": (("2KI", 17, 5, 6), ("2KI", 18, 9, 11)),
    "sargon-numbers": (("2KI", 17, 6, 6),),
    "sargon-prism-variation": (("2KI", 17, 6, 6),),
    "new-residents-samaria": (("2KI", 17, 24, 24), ("2KI", 17, 6, 6)),
}
SOURCE_SCOPES = {
    "menahem-tribute": "rinap-tiglath-menahem32",
    "north-israel-deportations": "rinap-tiglath-peqah42",
    "peqah-hoshea": "rinap-tiglath-peqah42",
    "shalmaneser-siege": "aebp-shalmaneser-v",
    "sargon-capture-claim": "rinap-sargon-samaria7",
    "sargon-numbers": "rinap-sargon-samaria7",
    "sargon-prism-variation": "rinap-sargon-nimrud74",
    "new-residents-samaria": "rinap-sargon-annals1",
}
CLASSES = {"bounded-agreement", "open-reading", "disputed-chronology",
           "competing-attribution", "text-variants", "restored-witness"}


def validate(sources, articles, data=None):
    data = DATA if data is None else data
    if data.get("schema_version") != 1 or "await qualified independent expert review" not in data.get("method", ""):
        raise ValueError("Samaria method must disclose independent-review gap")
    stages = data.get("stages", [])
    if [s["id"] for s in stages] != ["before-siege", "siege", "sargon", "aftermath"]:
        raise ValueError("Samaria teaching stages changed without review")
    cases = data.get("cases", [])
    if len(cases) != 8 or set(c["id"] for c in cases) != set(BIBLE_SCOPES):
        raise ValueError("Expected eight individually curated Samaria cases")
    sources_by_id = {s["id"]: s for s in sources}
    article_slugs = {a["slug"] for a in articles}
    verses = load_bible()["verses"]
    routes = 0
    for case in cases:
        ident = case["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
            raise ValueError("Unrecognised Samaria case slug: " + ident)
        if case["source_id"] != SOURCE_SCOPES[ident] or case["source_id"] not in sources_by_id:
            raise ValueError("Unreviewed source substitution: " + ident)
        source = sources_by_id[case["source_id"]]
        if not source["url"].startswith("https://"):
            raise ValueError("Non-HTTPS primary source: " + ident)
        if case["stage"] not in {s["id"] for s in stages} or case["class"] not in CLASSES:
            raise ValueError("Unreviewed chronological status: " + ident)
        if case["mode"] == "edition":
            marker, positions = EDITION_COORDINATES.get(case["source_id"], (None, set()))
            if not marker or marker not in source["url"] or marker not in case.get("edition", ""):
                raise ValueError("Royal inscription edition mismatch: " + ident)
            if case["location"] not in positions:
                raise ValueError("Unreviewed source lines or fake edition location: " + ident)
        elif case["mode"] == "specialist-synthesis":
            if ident != "shalmaneser-siege" or case["source_id"] != "aebp-shalmaneser-v" or case["edition"] is not None or case["location"] is not None:
                raise ValueError("A secondary Shalmaneser reign summary cannot impersonate a royal inscription")
            if "not a surviving siege inscription" not in case["object"].lower():
                raise ValueError("Shalmaneser context must not invent a siege inscription")
        else:
            raise ValueError("Unrecognised evidence witness mode: " + ident)
        if case["article"] not in article_slugs:
            raise ValueError("Missing original related historical study: " + ident)
        for key in ("year", "heading", "actors", "object", "royal", "scripture", "meeting", "limits", "uncertainty"):
            if not isinstance(case.get(key), str) or len(case[key].strip()) < 17:
                raise ValueError("Missing required comparison context: " + ident + "/" + key)
        passages = case["biblical"]
        if tuple(tuple(ref) for ref in passages) != BIBLE_SCOPES[ident]:
            raise ValueError("Bible passage coordinates changed without review: " + ident)
        for ref in passages:
            book, chapter, first, last = ref
            if any(type(x) is not int for x in (chapter, first, last)) or first < 1 or first > last or (
                book, chapter, first) not in verses or (book, chapter, last) not in verses:
                raise ValueError("Missing biblical passage: " + ident)
            routes += 1
        if ident == "peqah-hoshea" and not all(s in (case["royal"] + case["uncertainty"]).lower() for s in ("damaged", "killed")):
            raise ValueError("Pekah damaged verb must retain uncertainty")
        if ident == "sargon-numbers" and not all(s in case["royal"] for s in ("27,290", "27,280", "24,280")):
            raise ValueError("Sargon's divergent copy figures must remain visible")
        if ident == "sargon-prism-variation" and "47,280" not in case["royal"]:
            raise ValueError("Nimrud count alternative must be qualified")
    return {"cases": 8, "edition_cases": 7, "specialist_synthesis_cases": 1,
            "distinct_edition_ids": len({c["edition"] for c in cases if c["edition"]}),
            "bible_routes": routes, "stages": len(stages)}


def build_view(sources):
    by_id = {s["id"]: s for s in sources}
    return [{**c, "source_url": by_id[c["source_id"]]["url"], "source_title": by_id[c["source_id"]]["title"],
             "bible_links": [{"url": reference_url(ref), "label": reference_label(ref)} for ref in c["biblical"]]}
            for c in CASES]


def article_links(slug):
    cases = [c for c in CASES if c["article"] == slug]
    if not cases:
        return ""
    items = "".join('<li><a href="/samaria-succession/#case-' + H(c["id"]) + '">' +
                    H(c["heading"]) + '</a></li>' for c in cases)
    return ('<section class="samaria-article-links"><h2>Samaria and Assyrian succession - source comparisons</h2>'
            '<p>The biblical narrative and separately edited Assyrian records are not interchangeable. '
            'Compare exact inscription locations and unresolved chronology.</p><ul>' + items + '</ul></section>')
