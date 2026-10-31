"""Offline, provenance-aware media for Assyria Living Archive articles.

Image rights must be verified at acquisition time. Runtime page generation
only reads assets already committed to the repository.
"""
from html import escape as H
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from archive_support import normalise
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
LIBRARY_FILE = ROOT / 'data' / 'media-library.json'
IMAGE_DIR = ROOT / 'static' / 'assets' / 'archive-media'
EXCLUSIONS_FILE = ROOT / 'data' / 'media-exclusions.json'


def load_exclusions():
    """Documented image-to-article rejections; no automatic global bans."""
    data = json.loads(EXCLUSIONS_FILE.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or not isinstance(data.get('exclusions'), list):
        raise ValueError('Invalid media exclusion register')
    denied = set()
    for item in data['exclusions']:
        slug, title = item.get('article_slug', ''), item.get('original_title', '')
        if (not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug) or
                not title.startswith('File:') or
                not str(item.get('reason', '')).strip() or
                urlsplit(item.get('evidence_url', '')).scheme != 'https'):
            raise ValueError('Incomplete or unsafe media editorial exclusion')
        key = (slug, title.replace('_', ' ').casefold())
        if key in denied:
            raise ValueError('Duplicate media exclusion')
        denied.add(key)
    return denied


# These titles represent specific article subjects, not general topical guesses.
# Lead images remain contextual unless an editor independently authenticates
# the depicted object or person.
DIRECT_ARTICLE_TOPICS = {
    'assyrian-identity': 'Assyrian people',
    'aramaic': 'Aramaic',
    'sureth': 'Suret language',
    'syriac-scripts': 'Syriac alphabet',
    'chaldean-church': 'Chaldean Catholic Church',
    'music': 'Assyrian music',
    'tur-abdin': 'Tur Abdin',
    'edessa': 'Edessa',
    'sennacherib-prism-hezekiah': "Sennacherib's Prism",
    'middle-assyrian-overview': 'Middle Assyrian Empire',
    'bible-esarhaddon': 'Esarhaddon',
    'bible-samaria': 'Fall of Samaria',
}

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
    if article.get('kind') == 'preserved_reference':
        path = urlsplit(article['record']['source_url']).path
        if path.startswith('/wiki/'):
            return unquote(path[6:]).replace('_', ' '), 'subject'
    if article['slug'] in DIRECT_ARTICLE_TOPICS:
        return DIRECT_ARTICLE_TOPICS[article['slug']], 'context'
    for source_id in article.get('sources', []):
        source = source_map.get(source_id, {})
        if source.get('type') == 'Preserved encyclopaedia reference' and source.get('title'):
            return source['title'], 'context'
        parsed = urlsplit(source.get('url', ''))
        if parsed.netloc == 'en.wikipedia.org' and parsed.path.startswith('/wiki/'):
            return unquote(parsed.path[6:]).replace('_', ' '), 'context'
    if article['slug'] in CONTEXT_TOPICS:
        return CONTEXT_TOPICS[article['slug']], 'context'
    return article['title'], 'candidate'


def media_candidates(article, reference_media=None):
    if article.get('kind') == 'preserved_reference':
        return article.get('media_candidates', [])[:16]
    for source_id in article.get('sources', []):
        media = (reference_media or {}).get(source_id, [])
        if media:
            return media[:16]
    return []


def load_library():
    if not LIBRARY_FILE.exists():
        return {'schema_version': 1, 'assets': {}, 'articles': {}}
    data = json.loads(LIBRARY_FILE.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported media library schema version')
    return data


def validate_library(library=None, check_files=True):
    lib = library if library is not None else load_library()
    if lib.get('schema_version') != 1 or not isinstance(lib.get('assets'), dict) or not isinstance(lib.get('articles'), dict):
        raise ValueError('Invalid media library format')
    for media_id, asset in lib['assets'].items():
        if not re.fullmatch('[0-9a-f]{24}', media_id):
            raise ValueError('Invalid asset identifier')
        filename = asset.get('file', '')
        if not re.fullmatch(r'/assets/archive-media/[0-9a-f]{24}\.webp', filename):
            raise ValueError('Media must be a locally stored WebP image: ' + filename)
        for field in ('source_url', 'creator', 'licence', 'licence_url', 'sha256', 'original_title'):
            if not asset.get(field):
                raise ValueError('Missing image provenance: ' + media_id + '/' + field)
        if not asset['source_url'].startswith('https://commons.wikimedia.org/wiki/File:'):
            raise ValueError('Image source must be a Commons file page')
        try:
            rights_url = urlsplit(asset['licence_url'])
        except ValueError as exc:
            raise ValueError('Invalid image licence URL') from exc
        if (rights_url.scheme != 'https' or
                rights_url.hostname not in ('creativecommons.org', 'commons.wikimedia.org') or
                rights_url.username or rights_url.password):
            raise ValueError('Unverified image licence URL')
        if not re.fullmatch('[0-9a-f]{64}', asset['sha256']):
            raise ValueError('Invalid image checksum')
        if check_files:
            path = ROOT / 'static' / filename.lstrip('/')
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
                raise ValueError('Missing or changed local image: ' + filename)
    exclusions = load_exclusions()
    for slug, selections in lib['articles'].items():
        if not re.fullmatch('[a-z0-9][a-z0-9-]*', slug) or not isinstance(selections, list):
            raise ValueError('Invalid article media selection')
        for entry in selections:
            if entry.get('asset_id') in lib['assets']:
                title = lib['assets'][entry['asset_id']]['original_title']
                if (slug, title.replace('_', ' ').casefold()) in exclusions:
                    raise ValueError('Image rejected for this article on documented grounds: ' + slug)
            if entry.get('asset_id') not in lib['assets']:
                raise ValueError('Article references unknown image: ' + slug)
            if not isinstance(entry.get('alt'), str) or not entry['alt'].strip():
                raise ValueError('Image has no alternative text: ' + slug)
            if entry.get('relation') not in ('subject', 'context'):
                raise ValueError('Image context not identified: ' + slug)
    return True


def render(article, library):
    choices = library['articles'].get(article['slug'], [])
    if not choices:
        return ''
    # Preserve source metadata in JSON, but normalise editorial display punctuation.
    safe_text = lambda value: H(normalise(str(value)), quote=True)
    safe_url = lambda value: H(quote(str(value), safe=":/?&=%#,+_-'()"), quote=True)
    blocks = []
    for entry in choices:
        asset = library['assets'][entry['asset_id']]
        contextual = entry['relation'] == 'context'
        subject_label = 'Related contextual image. ' if contextual else ''
        caption = (entry.get('caption') or entry['alt']).strip()
        rights_heading = 'Rights status' if asset['licence'].casefold() in ('public domain', 'pd') else 'Licence'
        blocks.append(
            '<figure class="archive-media-item">'
            '<a href="' + safe_url(asset['source_url']) + '" target="_blank" rel="noopener noreferrer">'
            '<img src="' + safe_url(asset['file']) + '" alt="' + safe_text(entry['alt']) +
            '" loading="lazy" decoding="async"></a>'
            '<figcaption>' + safe_text(subject_label) + safe_text(caption) +
            '. <span class="media-credit">Image by ' + safe_text(asset['creator']) +
            '. <a href="' + safe_url(asset['source_url']) + '" target="_blank" rel="noopener noreferrer">Original file and attribution</a>' +
            '. ' + rights_heading + ': <a href="' + safe_url(asset['licence_url']) +
            '" target="_blank" rel="noopener noreferrer">' + safe_text(asset['licence']) +
            '</a>. Resized and converted to WebP for this archive.</span></figcaption></figure>'
        )
    return ('<section class="archive-media" aria-label="Illustrations with source credits">'
            '<span class="eyebrow">Illustrated sources</span><div class="archive-media-gallery">' +
            ''.join(blocks) + '</div></section>')


def report(articles, library):
    rows = []
    for a in articles:
        count = len(library['articles'].get(a['slug'], []))
        rows.append({'slug': a['slug'], 'category': a['category'],
                     'local_media_count': count, 'has_local_legacy_image': bool(a.get('image')),
                     'has_image': bool(count or a.get('image'))})
    return {'schema_version': 1, 'total_articles': len(rows),
            'articles_with_any_local_image': sum(r['has_image'] for r in rows),
            'articles_without_local_image': sum(not r['has_image'] for r in rows),
            'locally_archived_licensed_files': len(library['assets']),
            'articles_with_new_local_media': sum(r['local_media_count'] > 0 for r in rows),
            'category_coverage': {cat: {
                'total': sum(r['category'] == cat for r in rows),
                'with_image': sum(r['category'] == cat and r['has_image'] for r in rows)}
                for cat in sorted(set(r['category'] for r in rows))},
            'unillustrated_articles': [r['slug'] for r in rows if not r['has_image']],
            'coverage': rows,
            'method': 'Only checked-in, checksum-verified media files count; external candidate links do not count as image coverage.'}


def triage(articles, library, reference_media=None, source_map=None):
    """Build an evidence-driven review queue, never asserting that media does not exist.

    Candidates from preserved source pages are discovery leads, not independent
    evidence of relevance or reuse permission. Recorded licence metadata is not
    a sign-off on whether an image actually depicts the article's subject.
    """
    from collections import Counter
    reference_media = reference_media or {}
    source_map = source_map or {}
    reuse = Counter(
        item['asset_id'] for entries in library['articles'].values() for item in entries
    )
    pending = []
    review = []
    by_category = {}
    for article in articles:
        slug = article['slug']
        category = article['category']
        cat = by_category.setdefault(category, {
            'total': 0, 'illustrated': 0, 'requires_discovery': 0,
            'placement_reviews': 0, 'generic_caption_reviews': 0
        })
        cat['total'] += 1
        images = library['articles'].get(slug, [])
        illustrated = bool(images or article.get('image'))
        cat['illustrated' if illustrated else 'requires_discovery'] += 1
        candidates = media_candidates(article, reference_media)
        if not illustrated:
            title, relation = wikipedia_title(article, source_map)
            pending.append({
                'slug': slug, 'title': article['title'], 'category': category,
                'kind': article.get('kind', 'editorial'),
                'retained_source_image_candidates': len(candidates),
                'lead_source_topic': title if relation != 'candidate' else None,
                'status': 'further_research_needed',
                'note': ('Unillustrated is not evidence that no suitable media exists. '
                         'Review source figures, subject-specific collections and file rights.')
            })
        for entry in images:
            asset = library['assets'][entry['asset_id']]
            generic = bool(re.search(
                r'^(?:Source-associated illustration for|Lead image linked from)',
                entry.get('alt', '') + ' ' + entry.get('caption', ''), re.I
            ))
            flags = []
            if generic:
                flags.append('generic_description')
                cat['generic_caption_reviews'] += 1
            if entry['relation'] == 'context':
                flags.append('contextual_association_not_subject_authentication')
            if reuse[entry['asset_id']] >= 4:
                flags.append('heavily_reused_illustration')
            review.append({
                'slug': slug, 'article_title': article['title'], 'category': category,
                'asset_id': entry['asset_id'], 'original_title': asset['original_title'],
                'original_source_url': asset['source_url'],
                'relation': entry['relation'], 'review_status': 'not_editorially_verified',
                'review_flags': flags,
                'note': 'Verify historical identity, date, depiction, caption, and article relevance.'
            })
            cat['placement_reviews'] += 1
    return {
        'schema_version': 1,
        'total_articles': len(articles),
        'articles_with_image': len(articles) - len(pending),
        'articles_needing_further_media_research': len(pending),
        'placements_needing_editorial_relevance_review': len(review),
        'placements_with_generic_source_descriptions': sum(
            'generic_description' in r['review_flags'] for r in review
        ),
        'placements_with_contextual_association': sum(
            'contextual_association_not_subject_authentication' in r['review_flags']
            for r in review
        ),
        'placements_with_heavy_reuse': sum(
            'heavily_reused_illustration' in r['review_flags'] for r in review
        ),
        'category_progress': by_category,
        'research_queue': pending,
        'placement_review_queue': review,
        'method': (
            'All statuses are open research or editorial checks. Rights metadata '
            'and checked-in images confirm technical provenance, but never prove '
            'depiction accuracy. A media-free article is acceptable only after '
            'a recorded, source-supported determination.'
        )
    }
