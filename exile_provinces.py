"""Evidence-role-aware archive of exile, resettlement and provincial experience."""
from html import escape as H
from pathlib import Path
import json
import re
from bible_support import load_bible, reference_label, reference_url

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/exile-provinces.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
CATEGORIES = DATA["categories"]
# Stable, source-checked reference identities. Do not accept arbitrary replacements.
SCOPE = {
    "northern-captivity": ("rinap-tiglath-peqah42", (("2KI",15,29,29),("1CH",5,26,26))),
    "halah-identification": ("aebp-israel", (("2KI",17,6,6),("2KI",18,11,11))),
    "guzana-habor": ("aebp-israel", (("2KI",17,6,6),("1CH",5,26,26))),
    "median-cities": ("aebp-israel", (("2KI",17,6,6),("2KI",18,11,11))),
    "sargonic-resettlement": ("rinap-sargon-samaria7", (("2KI",17,6,6),("2KI",17,24,24))),
    "new-residents": ("aebp-deportation", (("2KI",17,24,24),)),
    "samaria-tax-letter": ("saa-samaria-corn-tax", (("2KI",17,24,24),)),
    "travel-supplies": ("aebp-deportation", (("2KI",17,6,6),)),
    "marriage-and-bride-price": ("aebp-deportation", (("2KI",17,24,24),)),
    "tiglath-scribes-relief": ("bm-tiglath-census-relief", (("2KI",15,29,29),)),
    "lachish-distinct": ("bm-lachish-deportees", (("2KI",18,13,17),)),
    "limits-of-archaeology": ("oxford-faust-provinces", (("2KI",17,24,24),)),
}
# Exact manuscript, text identifiers and accession scopes keep unrelated sources apart.
DIRECT = {
    "northern-captivity": ("edited-text", "Q003455", "Obverse lines 15'-17'"),
    "sargonic-resettlement": ("edited-text", "Q006488", "lines 23-25"),
    "samaria-tax-letter": ("edited-text", "P334789", "obverse 4-6 and reverse 1-9"),
    "tiglath-scribes-relief": ("museum-object", "1848,1104.5", "BM 118882"),
    "lachish-distinct": ("museum-object", "124908", "Room XXXVI panel 9"),
}
SECONDARY = {
    "halah-identification": "scholarly-context",
    "guzana-habor": "scholarly-context",
    "median-cities": "scholarly-context",
    "new-residents": "scholarly-context",
    "travel-supplies": "specialist-identified-text",
    "marriage-and-bride-price": "specialist-identified-text",
    "limits-of-archaeology": "academic-synthesis",
}


def validate(sources, articles, data=None):
    d = DATA if data is None else data
    if d.get("schema_version") != 1 or "has not independently collated" not in d.get("method",""):
        raise ValueError("Exile research must disclose original-language review limits")
    if len(d.get("cases",[])) != 12 or set(x["id"] for x in d["cases"]) != set(SCOPE):
        raise ValueError("Expected twelve distinct pre-reviewed research cases")
    category_ids = [x["id"] for x in d.get("categories",[])]
    if category_ids != ["origins","destinations","administration","daily-life","limits"]:
        raise ValueError("Exile reading categories changed without review")
    found_sources = {x["id"]:x for x in sources}
    slugs = {a["slug"] for a in articles}
    verses = load_bible()["verses"]
    n = 0
    for c in d["cases"]:
        ident=c["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",ident):
            raise ValueError("Invalid research case identifier: "+ident)
        source,scope=SCOPE[ident]
        if c["source_id"] != source or source not in found_sources:
            raise ValueError("Unverified or swapped exile source: "+ident)
        if c["category"] not in category_ids or c["article"] not in slugs:
            raise ValueError("Missing category or original article: "+ident)
        if tuple(tuple(p) for p in c["biblical"]) != scope:
            raise ValueError("Bible scope changed without source review: "+ident)
        for book,chapter,first,last in scope:
            if (book,chapter,first) not in verses or (book,chapter,last) not in verses:
                raise ValueError("Bible reading route absent from local text: "+ident)
            n+=1
        if len(c.get("secondary",[]))!=len(set(c.get("secondary",[]))):
            raise ValueError("Duplicate supplementary source: "+ident)
        if source in c["secondary"] or any(s not in found_sources for s in c["secondary"]):
            raise ValueError("Unsupported secondary source or self-citation: "+ident)
        primary=found_sources[source]
        if not primary["url"].startswith("https://"):
            raise ValueError("Source link must be HTTPS: "+ident)
        if ident in DIRECT:
            medium,marker,location=DIRECT[ident]
            if c["kind"] != medium or marker not in primary["url"]+c["source_location"] or location.lower() not in c["source_location"].lower():
                raise ValueError("False original edition, location or museum accession: "+ident)
            if medium=="edited-text" and not any(s in primary["type"].lower() for s in ("primary","direct")):
                raise ValueError("Inscription or administrative letter not primary: "+ident)
        elif c["kind"] != SECONDARY[ident]:
            raise ValueError("Secondary synthesis cannot impersonate original tablet: "+ident)
        for field in ("title","date","scope","source_location","witness","scripture","comparison","limits"):
            if not isinstance(c.get(field),str) or len(c[field].strip()) < (4 if field=="date" else 17):
                raise ValueError("Missing interpretation field: "+ident+"/"+field)
        if ident in ("travel-supplies","marriage-and-bride-price"):
            required="SAA 19 17" if ident=="travel-supplies" else "SAA 19 18"
            if required not in c["source_location"] or "Aramaean" not in c["scope"]:
                raise ValueError("Distinct Aramaean correspondence must not be relabelled Israelite: "+ident)
        if ident=="guzana-habor" and "SAA 16 63" not in c["source_location"]:
            raise ValueError("Guzana research lead must remain explicitly secondary and identified")
        if ident=="lachish-distinct" and "not Samaria" not in c["limits"]:
            raise ValueError("Later Lachish prisoners must not be presented as Samaria deportees")
        if ident=="limits-of-archaeology" and "abstract" not in c["limits"]:
            raise ValueError("Paywalled article scope limitation must remain visible")
    return {"cases":len(d["cases"]),"bible_routes":n,"original_text_cases":3,
            "museum_object_cases":2,"context_cases":7,"categories":5,
            "distinct_supporting_sources":len({s for c in d["cases"] for s in [c["source_id"]]+c["secondary"]})}


def build_view(sources):
    byid={x["id"]:x for x in sources}
    return [{**c,"source_title":byid[c["source_id"]]["title"],
             "source_url":byid[c["source_id"]]["url"],
             "source_kind":byid[c["source_id"]]["type"],
             "secondary_links":[{"id":sid,"title":byid[sid]["title"],"url":byid[sid]["url"]}
                                for sid in c["secondary"]],
             "bible_links":[{"label":reference_label(p),"url":reference_url(p)} for p in c["biblical"]]}
            for c in CASES]


def article_links(slug):
    related=[c for c in CASES if c["article"]==slug]
    if not related:
        return ""
    links="".join('<li><a href="/exile-provinces/#exile-'+H(c["id"])+'">'+
                  H(c["title"])+'</a></li>' for c in related)
    return ('<section class="exile-article-links"><h2>Exile and provincial life - source studies</h2>'
            '<p>See the original evidence medium, biblical passages and outstanding uncertainty for each case. '
            'Other peoples and later campaigns are kept distinct.</p><ul>'+links+'</ul></section>')
