"""Source-linked illustration discovery with explicit image licensing.

A historical article source is not automatically a licence for its photographs.
This module renders a cautious discovery slot for a Commons-licensed image,
which the client only displays after it retrieves per-file rights metadata.
"""
from html import escape
import json
from urllib.parse import quote, unquote, urlsplit

WIKIPEDIA = "https://en.wikipedia.org/wiki/"
COMMONS_SEARCH = "https://commons.wikimedia.org/w/index.php?search="

# A handful of non-obvious editorial subjects have identifiable Wikipedia
# visual contexts. These are contextual topics, NEVER purported portraits.
CONTEXT_TOPICS = {
    "bible-origins": "Assyria",
    "bible-pul-menahem": "Tiglath-Pileser III",
    "bible-tiglath-pileser": "Tiglath-Pileser III",
    "bible-samaria": "Fall of Samaria",
    "bible-deportation": "Neo-Assyrian Empire",
    "bible-sargon": "Sargon II",
    "bible-sennacherib-invasion": "Sennacherib",
    "bible-hezekiah-deliverance": "Sennacherib",
    "bible-nahum": "Nineveh",
    "bible-zephaniah": "Nineveh",
}


def wikipedia_title(article, source_map):
    """Prefer the article's preserved source, else an actual cited Wikipedia topic."""
    if article.get("kind") == "preserved_reference":
        url = article["record"]["source_url"]
        path = urlsplit(url).path
        if path.startswith("/wiki/"):
            return unquote(path[6:]).replace("_", " "), "subject"

    for source_id in article.get("sources", []):
        source = source_map.get(source_id, {})
        url = source.get("url", "")
        parsed = urlsplit(url)
        if parsed.netloc == "en.wikipedia.org" and parsed.path.startswith("/wiki/"):
            return unquote(parsed.path[6:]).replace("_", " "), "context"

    if article["slug"] in CONTEXT_TOPICS:
        return CONTEXT_TOPICS[article["slug"]], "context"

    # An exact article title is a search candidate, not proof an image exists.
    # It is kept as a subject lookup so Wikimedia's missing-page response is
    # reported honestly, rather than decorating a biography with unrelated art.
    return article["title"], "candidate"


def media_candidates(article, reference_media=None):
    if article.get("kind") == "preserved_reference":
        return article.get("media_candidates", [])[:8]
    if reference_media:
        for source_id in article.get("sources", []):
            if reference_media.get(source_id):
                return reference_media[source_id][:8]
    return []


def render(article, source_map, reference_media=None):
    title, relation = wikipedia_title(article, source_map)
    candidates = media_candidates(article, reference_media)
    payload = escape(json.dumps(candidates, ensure_ascii=False), quote=True)
    source_url = WIKIPEDIA + quote(title.replace(" ", "_"), safe="()'_,")
    commons_url = COMMONS_SEARCH + quote(title) + "&title=Special:MediaSearch&type=image"
    label = "Source subject" if relation == "subject" else "Related source topic" if relation == "context" else "Image search candidate"
    return (
        '<section class="media-research" aria-label="Illustrations and media"'
        ' data-article-media data-media-page="' + escape(title, quote=True) + '"'
        ' data-media-relation="' + relation + '" data-media-candidates="' + payload + '">'
        '<div class="media-research-heading"><span class="eyebrow">Visual evidence</span>'
        '<h2>Images and objects</h2></div>'
        '<p class="media-research-intro">Photographs, artefacts and historic illustrations must be '
        'linked to their actual subjects, creators and image licences. A linked text source alone '
        'does not confer permission to reproduce its images.</p>'
        '<div class="media-research-gallery" aria-label="Images and source credits"></div>'
        '<figure class="media-research-figure" hidden>'
        '<a class="media-research-original" href="' + escape(source_url, quote=True) + '" target="_blank" rel="noopener noreferrer">'
        '<img alt="" loading="lazy" decoding="async"></a>'
        '<figcaption class="media-research-credit"></figcaption>'
        '</figure>'
        '<p class="media-research-status" role="status">Checking image-specific reuse rights and source captions.</p>'
        '<p class="media-research-links"><span>' + label + ': ' + escape(title) + '.</span> '
        '<a href="' + escape(source_url, quote=True) + '" target="_blank" rel="noopener noreferrer">Article used for image lookup</a>'
        ' / <a href="' + escape(commons_url, quote=True) + '" target="_blank" rel="noopener noreferrer">Browse Commons media</a></p>'
        '</section>'
    )


def report(articles, source_map, reference_media=None):
    static = sum(bool(a.get("image")) for a in articles)
    return {
        "total_articles": len(articles),
        "original_editorial_images": static,
        "articles_with_discovery_slots": len(articles),
        "articles_with_retained_media_candidates": sum(bool(media_candidates(a, reference_media)) for a in articles),
        "licensed_dynamic_images_verified_at_build": 0,
        "status": "Discovery slots are not evidence that an image was successfully retrieved.",
        "method": "The browser checks Wikimedia Commons image-specific metadata before an illustration is displayed. Missing, incompatible or unavailable media remain explicitly unconfirmed.",
        "coverage": [
            {"slug": article["slug"], "category": article["category"],
             "has_local_image": bool(article.get("image")),
             "image_subject": wikipedia_title(article, source_map)[0],
             "image_relation": wikipedia_title(article, source_map)[1],
             "retained_media_candidates": len(media_candidates(article, reference_media)),
             "image_licence_confirmed_at_build": False}
            for article in articles
        ],
    }
