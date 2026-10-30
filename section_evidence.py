"""Curated section-level reading trails, distinct from specialist source verification.

The metadata explicitly links individual editorial sections to selected source records
or Bible passages. It does not imply each sentence has been checked, and unmapped
sections retain article-level bibliographies without inferred associations.
"""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent / 'data/section-evidence.json').read_text(encoding='utf-8'))


def trail(article, title):
    return DATA.get(article['slug'], {}).get(title, {})


def validate(articles, sources):
    by_slug = {article['slug']: article for article in articles}
    valid_source_ids = {source['id'] for source in sources}
    for slug, sections in DATA.items():
        if slug not in by_slug:
            raise ValueError('Section trail refers to unknown article: ' + slug)
        article = by_slug[slug]
        headings = [section['title'] for section in article['sections']]
        if len(set(headings)) != len(headings):
            raise ValueError('Ambiguous section titles in ' + slug)
        for title, evidence in sections.items():
            if title not in headings:
                raise ValueError('Section trail has unknown heading: ' + slug + ' / ' + title)
            if set(evidence) - {'sources', 'passages', 'locations'}:
                raise ValueError('Unknown section evidence fields: ' + slug + ' / ' + title)
            citations = evidence.get('sources', [])
            passages = evidence.get('passages', [])
            locations = evidence.get('locations', {})
            if (not isinstance(locations, dict) or any(
                    key not in citations or not isinstance(value, str) or not value.strip()
                    for key, value in locations.items())):
                raise ValueError('Invalid citation locator: ' + slug + ' / ' + title)
            if not citations and not passages:
                raise ValueError('Empty section trail: ' + slug + ' / ' + title)
            if len(citations) != len(set(citations)):
                raise ValueError('Duplicate source in section trail: ' + slug + ' / ' + title)
            if any(source_id not in valid_source_ids or source_id not in article['sources'] for source_id in citations):
                raise ValueError('Section source is not in its article bibliography: ' + slug + ' / ' + title)
            original = article.get('passages', [])
            found = set()
            for reference in passages:
                if not isinstance(reference, list) or len(reference) != 4:
                    raise ValueError('Invalid section Bible reference: ' + slug + ' / ' + title)
                book, chapter, first, last = reference
                if not isinstance(book, str) or not all(type(x) is int for x in (chapter, first, last)) or first < 1 or first > last:
                    raise ValueError('Invalid section Bible coordinates: ' + slug + ' / ' + title)
                if tuple(reference) in found:
                    raise ValueError('Duplicate Bible reference: ' + slug + ' / ' + title)
                found.add(tuple(reference))
                if not any(book == b and chapter == c and lo <= first <= last <= hi for b,c,lo,hi in original):
                    raise ValueError('Section Bible reference not covered by the guide: ' + slug + ' / ' + title)
    return {
        'mapped_articles': len(DATA),
        'mapped_sections': sum(len(sections) for sections in DATA.values()),
    }
