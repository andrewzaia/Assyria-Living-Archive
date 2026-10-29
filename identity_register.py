"""Evidence-scoped identity distinctions, without automatic ancient name merging."""
import json
import re
from pathlib import Path
from concordance import BY_ID

DATA = json.loads((Path(__file__).resolve().parent / "data/identity-cases.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
DECISIONS = {"different-witnesses", "catalogue-alias", "single-edition", "scripture-only-index"}


def validate(data=None):
    data = DATA if data is None else data
    if data.get("schema_version") != 1 or "pending independent specialist review" not in data.get("method", ""):
        raise ValueError("Missing explicit identity review limitation")
    records = data.get("cases", [])
    if len(records) < 8 or len({r["id"] for r in records}) != len(records):
        raise ValueError("Missing or duplicated identity case")
    links = 0
    for case in records:
        ident = case["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
            raise ValueError("Invalid identity case ID: " + ident)
        if case["type"] not in {"person", "place"} or case["decision"] not in DECISIONS:
            raise ValueError("Invalid identity type or decision: " + ident)
        if case["review_status"] != "pending-independent-review":
            raise ValueError("Unsubstantiated completed identity review: " + ident)
        for key in ("title", "question", "finding", "limit", "next"):
            if not isinstance(case.get(key), str) or len(case[key].strip()) < 28:
                raise ValueError("Incomplete identity case " + ident + " / " + key)
        if not case.get("forms") or not all(isinstance(v, str) and v.strip() for v in case["forms"]):
            raise ValueError("Missing name forms in " + ident)
        ids = case["terms"]
        if not ids or len(set(ids)) != len(ids) or any(t not in BY_ID for t in ids):
            raise ValueError("Unknown or duplicate identity concordance term: " + ident)
        if not case["evidence"]:
            raise ValueError("Missing identity evidence for " + ident)
        seen = set()
        for ref in case["evidence"]:
            term = ref["term"]
            kind = ref["kind"]
            if term not in ids or kind not in {"object", "scripture"} or len(ref.get("note", "")) < 35:
                raise ValueError("Invalid identity evidence role or limitation: " + ident)
            original = BY_ID[term]
            if kind == "object":
                if "ref" in ref or not any(obj["slug"] == ref.get("slug") for obj in original["objects"]):
                    raise ValueError("Identity object not in cited concordance term: " + ident)
                key = (term, kind, ref["slug"])
            else:
                if "slug" in ref or not isinstance(ref.get("ref"), list) or not any(
                    mention["ref"] == ref["ref"] for mention in original["passages"]
                ):
                    raise ValueError("Identity Scripture not in cited concordance term: " + ident)
                key = (term, kind, tuple(ref["ref"]))
            if key in seen:
                raise ValueError("Duplicate identity evidence: " + ident)
            seen.add(key)
            links += 1
    return {"cases": len(records), "evidence_links": links}


def build_view(concordance_view):
    terms = {term["id"]: term for term in concordance_view}
    result = []
    for case in CASES:
        references = []
        for ref in case["evidence"]:
            term = terms[ref["term"]]
            if ref["kind"] == "object":
                linked = next(obj for obj in term["objects"] if obj["slug"] == ref["slug"])
                label, url = linked["title"], linked["url"]
            else:
                linked = next(p for p in term["passages"] if p["ref"] == ref["ref"])
                label, url = linked["label"], linked["url"]
            references.append({**ref, "label": label, "url": url,
                               "term_url": "/concordance/#entry-" + ref["term"],
                               "term_label": term["label"]})
        result.append({**case, "evidence": references})
    return result
