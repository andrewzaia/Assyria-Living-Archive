"""Short, cited cuneiform excerpts with explicit uncertainty and non-translation status.

The line readings are attributed excerpts, not a locally mirrored text corpus.
Editorial glosses are descriptions, not an independent Akkadian translation.
"""
import json
import re
from html import escape as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/text-comparisons.json").read_text(encoding="utf-8"))
BY_SLUG = {record["slug"]: record for record in DATA["items"]}
STATES = {"excerpted", "edition-pending"}
UNCERTAINTY = {"attested", "damaged", "queried", "restored"}


def validate(cases, sources):
    if DATA.get("schema_version") != 1 or not DATA.get("method"):
        raise ValueError("Invalid cuneiform comparison schema or disclosure")
    original = {case["slug"]: case for case in cases}
    registry = {source["id"]: source for source in sources}
    entries = DATA["items"]
    if len(entries) != len(original) or set(BY_SLUG) != set(original) or len(entries) != len(BY_SLUG):
        raise ValueError("Comparison matrix must identify every object case exactly once")
    if sum(x["status"] == "excerpted" for x in entries) != 7:
        raise ValueError("Seven directly cited Middle Assyrian text editions are required")
    if sum(x["status"] == "edition-pending" for x in entries) != 2:
        raise ValueError("Unverified museum and chronicle readings must remain absent")
    seen = set()
    for entry in entries:
        slug = entry["slug"]
        if slug in seen:
            raise ValueError("Repeated cuneiform object")
        seen.add(slug)
        case = original[slug]
        if entry["status"] not in STATES:
            raise ValueError("Invalid comparison status")
        if not entry["edition_credit"] or len(entry["status_note"]) < 55 or not entry["editorial_scope"]:
            raise ValueError("Missing edition credit, scope or uncertainty")
        if case["source_id"] not in registry:
            raise ValueError("Comparison has no institutional source")
        if entry["status"] == "excerpted":
            if case["period"] != "middle" or len(entry["lines"]) < 2:
                raise ValueError("Only directly edited Middle Assyrian tablets may quote lines")
            if not ("ATMAP/TCMA" in entry["edition_credit"] and "CC BY-SA 3.0" in entry["edition_credit"]):
                raise ValueError("Cited original excerpts require publisher and edition licence")
        elif entry["lines"]:
            raise ValueError("Do not invent original-language text for unverified edition")
        for line in entry["lines"]:
            if set(line) != {"location", "transliteration", "gloss", "interpretation", "uncertainty", "note"}:
                raise ValueError("Line metadata must identify editorial gloss and provenance")
            if line["uncertainty"] not in UNCERTAINTY or not line["location"]:
                raise ValueError("Missing line coordinates or explicit uncertainty class")
            if not line["transliteration"] or len(line["transliteration"].split()) > 12:
                raise ValueError("Only very short source-attributed excerpts are allowed")
            if not line["gloss"] or not line["interpretation"] or len(line["note"]) < 20:
                raise ValueError("Unexplained original-language excerpt")
            if line["uncertainty"] == "restored" and "[" not in line["transliteration"]:
                raise ValueError("Restored line must preserve the source's missing-text notation")
            if line["uncertainty"] == "queried" and "?" not in (line["transliteration"] + " " + line["note"]):
                raise ValueError("Uncertain reading must retain the editor's query marker")
    return {
        "cases": len(entries),
        "excerpted": sum(x["status"] == "excerpted" for x in entries),
        "edition_pending": sum(x["status"] == "edition-pending" for x in entries),
        "line_excerpts": sum(len(x["lines"]) for x in entries),
    }


def _line_rows(entry):
    output = []
    for number, line in enumerate(entry["lines"], 1):
        tag = H(line["uncertainty"])
        anchor = 'transliteration-' + entry["slug"] + '-' + str(number)
        output.append(
            '<tr id="' + H(anchor) + '"><th scope="row">' + H(line["location"]) +
            '<span class="compare-state">' + tag + '</span></th>' +
            '<td><code lang="akk-Latn">' + H(line["transliteration"]) + '</code></td>' +
            '<td>' + H(line["gloss"]) + '</td>' +
            '<td>' + H(line["interpretation"]) +
            '<span class="compare-note">' + H(line["note"]) + '</span></td></tr>'
        )
    return "".join(output)


def render_lines(case, include_heading=True):
    entry = BY_SLUG[case["slug"]]
    heading_text = ("Read the edited lines side by side." if entry["status"] == "excerpted" else "A verified line edition is not yet available.")
    heading = '<h2 id="compare-lines-title">' + H(heading_text) + '</h2>' if include_heading else ""
    lead = (
        '<span class="eyebrow">ATTRIBUTED ANCIENT-TEXT EXCERPTS</span>' + heading +
        '<p class="compare-disclaimer">Transliteration represents cuneiform signs in modern notation; it is not the original cuneiform image. ' +
        'The two English columns are editorial cues and interpretation, <strong>not</strong> a new translation or verbatim reproduction ' +
        'of the scholarly edition. Check the linked publication for the full line sequence and the specialist English rendering.</p>'
    )
    if entry["status"] == "edition-pending":
        body = (
            '<p class="compare-unverified"><strong>No verified line-by-line text available.</strong> ' +
            H(entry["status_note"]) + '</p>' +
            '<p><a href="' + H(case["source_url"], quote=True) +
            '" rel="noopener noreferrer" target="_blank">Open the institutional object catalogue</a></p>'
        )
    else:
        body = (
            '<div class="compare-scroll" role="region" aria-label="Source transliteration and editorial reading comparisons" tabindex="0">' +
            '<table class="compare-table"><caption>Very short quoted excerpts by line, with original editorial glosses</caption>' +
            '<thead><tr><th scope="col">Edition line</th><th scope="col">Transliteration excerpt</th>' +
            '<th scope="col">English reading cue</th><th scope="col">Interpretation and uncertainty</th></tr></thead><tbody>' +
            _line_rows(entry) + '</tbody></table></div>' +
            '<p class="compare-attribution">Source: ' + H(entry["edition_credit"]) + '. <a href="https://creativecommons.org/licenses/by-sa/3.0/" rel="noopener noreferrer" target="_blank">Licence details</a>. ' +
            '<a href="' + H(case["source_url"], quote=True) +
            '" rel="noopener noreferrer" target="_blank">Read the complete original edition</a>. ' +
            'Only short attributed samples are included; no full scholarly translation is mirrored.</p>'
        )
    return (
        '<section class="text-comparison-panel" aria-label="Cuneiform text reading comparison">' +
        lead + '<p class="compare-scope">' + H(entry["editorial_scope"]) + '</p>' +
        body + '<p class="compare-caution">' + H(entry["status_note"]) + '</p>' +
        '<p class="compare-legend"><strong>Reading marks:</strong> [ ] = lost text supplied by editors; ' +
        'x = unidentified sign; # = damaged sign; ? = uncertain reading; raised corner marks = partly damaged signs. ' +
        '<a href="/articles/reading-cuneiform-transliteration/">Learn the notation</a> or ' +
        '<a href="/text-comparisons/">view all objects together</a>.</p></section>'
    )
