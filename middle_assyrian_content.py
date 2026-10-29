"""Middle Assyrian social history guides, independently attributed and period-sensitive.

The content is original editorial prose in data/middle-assyrian-articles.json.
Normative laws are distinct from actual legal practice; administrative tablets
are not representative surveys of all households. Later biblical Assyrian
passages are comparative readings, not dated Middle Assyrian archive evidence.
"""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data/middle-assyrian-articles.json"
ARTICLES = json.loads(DATA_PATH.read_text(encoding="utf-8"))

def validate():
    if len(ARTICLES) != 9:
        raise ValueError("Middle Assyrian collection must contain nine guides")
    slugs = set()
    for article in ARTICLES:
        if article["slug"] in slugs or not article["slug"].startswith("middle-assyrian-"):
            raise ValueError("Duplicate or invalid Middle Assyrian article slug")
        slugs.add(article["slug"])
        if article["category"] != "History & archaeology" or len(article["sections"]) != 5:
            raise ValueError("Middle Assyrian guide must include five original sections")
        if not article["sources"] or len(article["sources"]) != len(set(article["sources"])):
            raise ValueError("Middle Assyrian guide lacks distinct sources")
        if len({x["title"] for x in article["sections"]}) != 5:
            raise ValueError("Section titles must be unique")
        if any(len(x["text"].split()) < 75 for x in article["sections"]):
            raise ValueError("Original social history section requires substantive explanatory prose")
        if any(not isinstance(p, list) or len(p) != 4 for p in article["passages"]):
            raise ValueError("Invalid comparative Scripture route")
    return len(ARTICLES)
