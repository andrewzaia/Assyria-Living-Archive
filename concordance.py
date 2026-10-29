"""Curated concordance: direct tablet lines are not historical harmonisations.

All associations are editorially selected, with explicit roles. It is not
a machine-generated full-text index, an Assyriological name resolver or a
certification that biblical and cuneiform reports describe identical events.
"""
import json
import re
from collections import defaultdict
from html import escape as H
from pathlib import Path

from bible_support import load_bible, reference_label, reference_url

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/concordance.json").read_text(encoding="utf-8"))
TERMS = DATA["terms"]
BY_ID = {term["id"]: term for term in TERMS}
TYPES = {"place", "person", "material", "institution", "practice", "textual-method"}
ROLES = {"edition-line", "object-context"}
PASSAGE_ROLES = {"biblical-text", "biblical-name-comparison"}


def validate(articles, cases, text_data):
    if DATA.get("schema_version") != 1 or "same historical event" not in DATA.get("method", ""):
        raise ValueError("Concordance must disclose non-equivalence of sources")
    if len(TERMS) < 25 or len(BY_ID) != len(TERMS):
        raise ValueError("Concordance has too few or duplicated identifiers")
    article_ids = {a["slug"] for a in articles}
    case_ids = {a["slug"]: a for a in cases}
    line_ids = {a["slug"]: {line["location"]: i + 1 for i, line in enumerate(a["lines"])}
                for a in text_data["items"]}
    verses = load_bible()["verses"]
    used_case_links = 0
    used_bible_links = 0
    for term in TERMS:
        ident = term["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
            raise ValueError("Concordance identifier must be URL-safe: " + ident)
        if term["type"] not in TYPES or not term["label"] or len(term["description"]) < 65:
            raise ValueError("Missing type, label or adequate editorial description: " + ident)
        if len(term["aliases"]) != len(set(a.lower() for a in term["aliases"])):
            raise ValueError("Duplicate alias in " + ident)
        if any(not a.strip() for a in term["aliases"]):
            raise ValueError("Empty concordance alias")
        if not term["objects"] and not term["articles"] and not term["passages"]:
            raise ValueError("Unreferenced concordance item: " + ident)
        if len(term["articles"]) != len(set(term["articles"])) or any(a not in article_ids for a in term["articles"]):
            raise ValueError("Unknown or repeated encyclopaedia link: " + ident)
        seen = set()
        for occurrence in term["objects"]:
            slug, line = occurrence["slug"], occurrence.get("line")
            key = (slug, line)
            if key in seen or slug not in case_ids:
                raise ValueError("Duplicate or missing object citation for " + ident)
            seen.add(key)
            if occurrence["role"] not in ROLES or not occurrence.get("note") or len(occurrence["note"]) < 42:
                raise ValueError("Object citation needs explicit evidence role and limitation: " + ident)
            if (line is None) != (occurrence["role"] == "object-context"):
                raise ValueError("Line evidence cannot be silently described as an object-level claim: " + ident)
            if line is not None and line not in line_ids[slug]:
                raise ValueError("Missing line in original scholarly edition: " + ident + " / " + slug)
            used_case_links += 1
        seen_passages = set()
        for mention in term["passages"]:
            reference = mention["ref"]
            if not isinstance(reference, list) or len(reference) != 4 or not mention.get("note"):
                raise ValueError("Incomplete biblical comparison in " + ident)
            book, chapter, first, last = reference
            if any(type(num) is not int for num in (chapter, first, last)) or min(chapter, first, last) < 1 or first > last:
                raise ValueError("Invalid biblical concordance coordinates: " + ident)
            if (book, chapter, first) not in verses or (book, chapter, last) not in verses:
                raise ValueError("Biblical comparison missing from local Scripture reader: " + ident)
            if tuple(reference) in seen_passages or mention["relation"] not in PASSAGE_ROLES or len(mention["note"]) < 42:
                raise ValueError("Duplicate or unqualified biblical comparison: " + ident)
            seen_passages.add(tuple(reference))
            used_bible_links += 1
    if not (used_case_links >= 30 and used_bible_links >= 10):
        raise ValueError("Concordance evidence is missing documented object or Scripture routes")
    return {"terms": len(TERMS), "object_links": used_case_links,
            "article_links": sum(len(t["articles"]) for t in TERMS),
            "passage_links": used_bible_links}


def _object_href(occurrence, line_locations):
    slug = occurrence["slug"]
    location = occurrence.get("line")
    if location:
        index = line_locations[slug][location]
        return "/articles/" + slug + "/#transliteration-" + slug + "-" + str(index)
    return "/articles/" + slug + "/"


def build_view(articles, cases, text_data):
    """Return pure UI data with grounded labels and object-deep-link anchors."""
    by_article = {a["slug"]: a for a in articles}
    by_case = {a["slug"]: a for a in cases}
    line_locations = {r["slug"]: {line["location"]: i + 1 for i, line in enumerate(r["lines"])}
                      for r in text_data["items"]}
    result = []
    for term in TERMS:
        original = dict(term)
        original["objects"] = [{
            **occ,
            "title": by_case[occ["slug"]]["title"],
            "edition": by_case[occ["slug"]]["edition"],
            "url": _object_href(occ, line_locations),
            "source_url": by_case[occ["slug"]]["source_url"],
        } for occ in term["objects"]]
        original["articles"] = [{"slug":slug,"title":by_article[slug]["title"],
                                 "url":"/articles/"+slug+"/"} for slug in term["articles"]]
        original["passages"] = [{**p,"label":reference_label(p["ref"]),
                                "url":reference_url(p["ref"])} for p in term["passages"]]
        result.append(original)
    return result


def article_links(slug):
    terms = [t for t in TERMS if slug in t["articles"] or any(o["slug"] == slug for o in t["objects"])]
    if not terms:
        return ""
    links = "".join('<li><a href="/concordance/#entry-' + H(t["id"]) + '">' + H(t["label"]) + '</a></li>'
                    for t in terms)
    return ('<section class="article-concordance" aria-labelledby="article-concordance-heading">'
            '<span class="eyebrow">CONNECTED RESEARCH</span>'
            '<h2 id="article-concordance-heading">Explore the concordance.</h2>'
            '<p>These are editorial reading links, not a claim that different documents describe the same event.</p>'
            '<ul>' + links + '</ul></section>')
