"""Accession Wikimedia Commons images into the repository, never into page hotlinks.

Run manually or through the trusted main-branch archive-media workflow.
Network access is only used by this editorial ingestion utility. Site builds
remain offline and do not attempt to download or substitute assets.
"""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import article_media as media
from generate import ARTICLES, SM, REFERENCE_MEDIA

USER_AGENT = 'AssyriaLivingArchiveMediaArchiver/1.0 (https://www.assyrialivingarchive.org/; academic preservation) Python-urllib'
COMMONS_API = 'https://commons.wikimedia.org/w/api.php'
WIKIPEDIA_API = 'https://en.wikipedia.org/w/api.php'
MAX_DOWNLOAD_BYTES = 9_000_000
MAX_WEBP_BYTES = 1_800_000


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)


def plain(value):
    p = PlainText()
    p.feed(str(value or ''))
    return ' '.join(html.unescape(''.join(p.text)).split())[:450]


def is_host(url, host):
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and p.hostname == host and not p.username and not p.password
    except (ValueError, TypeError):
        return False


def read_url(url, *, delay, max_bytes=MAX_DOWNLOAD_BYTES):
    if not (is_host(url, 'upload.wikimedia.org') or
            is_host(url, 'commons.wikimedia.org') or
            is_host(url, 'en.wikipedia.org')):
        raise ValueError('Non-Wikimedia acquisition URL rejected')
    last_error = None
    for retry in range(4):
        time.sleep(delay)
        try:
            req = Request(url, headers={
                'User-Agent': USER_AGENT, 'Accept': 'application/json,image/webp,image/jpeg,image/png,*/*',
            })
            with urlopen(req, timeout=30) as response:
                if not is_host(response.geturl(), 'upload.wikimedia.org') and not is_host(response.geturl(), 'commons.wikimedia.org') and not is_host(response.geturl(), 'en.wikipedia.org'):
                    raise ValueError('Unsafe image redirect')
                size = int(response.headers.get('Content-Length') or '0')
                if size > max_bytes:
                    raise ValueError('Source image exceeds download limit')
                value = response.read(max_bytes + 1)
                if len(value) > max_bytes:
                    raise ValueError('Source response exceeds download limit')
                return value
        except HTTPError as exc:
            last_error = exc
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            try:
                wait = min(max(int(exc.headers.get('Retry-After', '0')), 2 ** (retry + 1)), 90)
            except (TypeError, ValueError):
                wait = 2 ** (retry + 1)
            time.sleep(wait)
        except (TimeoutError, URLError) as exc:
            last_error = exc
            time.sleep(2 ** (retry + 1))
    raise RuntimeError('Media request failed after retries') from last_error


def api(url, params, delay):
    query = urlencode({'action': 'query', 'format': 'json', 'formatversion': '2', **params})
    return json.loads(read_url(url + '?' + query, delay=delay, max_bytes=3_000_000))


def normalise_licence_url(raw):
    """Accept only trusted rights links and upgrade Wikimedia's older HTTP forms."""
    value = html.unescape(str(raw or '')).strip()
    if value.startswith('//'):
        value = 'https:' + value
    elif value.startswith('http://'):
        value = 'https://' + value[len('http://'):]
    try:
        parsed = urlsplit(value)
    except ValueError:
        return ''
    if (parsed.scheme != 'https' or
            parsed.hostname not in ('creativecommons.org', 'commons.wikimedia.org') or
            parsed.username or parsed.password):
        return ''
    return value


def save_progress(registry):
    """Atomically checkpoint verified files, retaining work if a later query fails."""
    media.validate_library(registry)
    target = media.LIBRARY_FILE
    staging = target.with_name(target.name + '.tmp')
    staging.write_text(json.dumps(registry, ensure_ascii=True, indent=2,
                                  sort_keys=True) + '\n', encoding='utf-8')
    staging.replace(target)


def eligible(info):
    if not info or info.get('mime') not in ('image/jpeg', 'image/png', 'image/webp'):
        return None
    meta = info.get('extmetadata') or {}
    label = plain((meta.get('LicenseShortName') or {}).get('value'))
    licence_url = normalise_licence_url((meta.get('LicenseUrl') or {}).get('value', ''))
    creator = plain((meta.get('Artist') or {}).get('value') or (meta.get('Credit') or {}).get('value'))
    source = info.get('descriptionurl', '')
    thumb = info.get('thumburl', '')
    accepted = re.fullmatch(r'(?:CC0(?: 1\.0)?|CC BY(?:-SA)?(?: [1-4]\.0)?|Public domain|PD)', label, re.I)
    if not accepted or not creator or not licence_url:
        return None
    if not is_host(source, 'commons.wikimedia.org') or not source.startswith('https://commons.wikimedia.org/wiki/File:'):
        return None
    if not is_host(thumb, 'upload.wikimedia.org'):
        return None
    return {'creator': creator, 'licence': label, 'licence_url': licence_url,
            'source_url': source, 'download_url': thumb}


def optimise(source_bytes):
    from PIL import Image, ImageOps, UnidentifiedImageError
    Image.MAX_IMAGE_PIXELS = 25_000_000
    with Image.open(io.BytesIO(source_bytes)) as img:
        if img.format not in ('JPEG', 'PNG', 'WEBP'):
            return None
        img = ImageOps.exif_transpose(img)
        img.thumbnail((1100, 1100), Image.Resampling.LANCZOS)
        img = img.convert('RGBA' if img.mode in ('RGBA', 'LA') or 'transparency' in img.info else 'RGB')
        out = io.BytesIO()
        img.save(out, format='WEBP', quality=79, method=5)
        data = out.getvalue()
        return data if len(data) <= MAX_WEBP_BYTES else None


def candidate_info(title, delay):
    if not title:
        return {}
    titles = ['File:' + name.removeprefix('File:') for name in title[:8]]
    response = api(COMMONS_API, {
        'prop': 'imageinfo', 'iiprop': 'url|mime|extmetadata',
        'iiurlwidth': '1000',
        'iiextmetadatafilter': 'LicenseShortName|LicenseUrl|Artist|Credit',
        'titles': '|'.join(titles),
    }, delay)
    return {p.get('title', '').replace('_', ' ').casefold(): p.get('imageinfo', [None])[0]
            for p in response.get('query', {}).get('pages', []) if p.get('imageinfo')}


def fallback(article, delay):
    title, relation = media.wikipedia_title(article, SM)
    if relation == 'candidate':
        return []
    response = api(WIKIPEDIA_API, {
        'prop': 'pageimages', 'piprop': 'name', 'redirects': '1', 'titles': title,
    }, delay)
    pages = response.get('query', {}).get('pages', [])
    for page in pages:
        filename = page.get('pageimage', '')
        if filename:
            return [{'file': filename.removeprefix('File:'),
                     'alt': 'Source-associated illustration for ' + title,
                     'caption': 'Lead image linked from ' + title}]
    return []


def add_source_illustrations(article, registry, selections, candidates,
                             relation, delay, max_per_article, counters):
    """Accession only image-specific licensed media or reuse previously verified files."""
    if not candidates or len(selections) >= max_per_article:
        return
    existing_titles = {
        registry['assets'][item['asset_id']]['original_title'].replace('_', ' ').casefold()
        for item in selections
    }
    queued = []
    for candidate in candidates:
        if not candidate.get('file'):
            continue
        title = 'File:' + candidate['file'].removeprefix('File:')
        if title.replace('_', ' ').casefold() not in existing_titles:
            queued.append((title, candidate))
    if not queued:
        return

    # Reuse already licensed local binaries without further network requests.
    known = {
        asset['original_title'].replace('_', ' ').casefold(): asset_id
        for asset_id, asset in registry['assets'].items()
    }
    need_lookup = [candidate['file'] for title, candidate in queued
                   if title.replace('_', ' ').casefold() not in known]
    infos = {}
    if need_lookup:
        try:
            infos = candidate_info(need_lookup, delay)
        except (HTTPError, URLError, RuntimeError, ValueError, TimeoutError) as exc:
            counters['lookup_failures'] += 1
            print(article['slug'], 'licence metadata unavailable:', type(exc).__name__, flush=True)

    for title, candidate in queued:
        if len(selections) >= max_per_article:
            break
        key = title.replace('_', ' ').casefold()
        media_id = known.get(key)
        if not media_id:
            rights = eligible(infos.get(key))
            if not rights:
                continue
            try:
                raw = read_url(rights['download_url'], delay=delay)
                data = optimise(raw)
            except (HTTPError, URLError, RuntimeError, ValueError, TimeoutError, OSError) as exc:
                print(article['slug'], 'image skipped:', type(exc).__name__, flush=True)
                continue
            if not data:
                continue
            checksum = hashlib.sha256(data).hexdigest()
            media_id = hashlib.sha256((title + ':' + checksum).encode('utf-8')).hexdigest()[:24]
            local_file = '/assets/archive-media/' + media_id + '.webp'
            target = ROOT / 'static' / local_file.lstrip('/')
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
            registry['assets'][media_id] = {
                'file': local_file,
                'sha256': checksum,
                'creator': rights['creator'],
                'licence': rights['licence'],
                'licence_url': rights['licence_url'],
                'source_url': rights['source_url'],
                'original_title': title,
            }
            known[key] = media_id
        if not any(item['asset_id'] == media_id for item in selections):
            selections.append({
                'asset_id': media_id,
                'alt': plain(candidate.get('alt') or title),
                'caption': plain(candidate.get('caption') or candidate.get('alt') or title),
                'relation': relation,
            })
            existing_titles.add(key)
            counters['new_article_images'] += 1


def ingest_article(article, registry, delay, max_per_article, counters):
    slug = article['slug']
    selections = list(registry['articles'].get(slug, []))
    if len(selections) >= max_per_article:
        counters['previously_archived'] += 1
        return

    relation = 'subject' if article.get('kind') == 'preserved_reference' else 'context'
    candidates = media.media_candidates(article, REFERENCE_MEDIA)
    add_source_illustrations(article, registry, selections, candidates,
                             relation, delay, max_per_article, counters)

    # Retained figure links often contain only icons, missing file records or
    # files with unsuitable licences. An exact Wikipedia lead illustration is a
    # second source candidate, not proof that the artwork depicts the subject.
    # Avoid needless duplicate requests and never replace a licensed source
    # figure with a less precise contextual illustration.
    if not selections and not article.get('image'):
        try:
            fallback_items = fallback(article, delay)
        except (HTTPError, URLError, RuntimeError, ValueError, TimeoutError) as exc:
            counters['lookup_failures'] += 1
            print(slug, 'lead image metadata unavailable:', type(exc).__name__, flush=True)
            fallback_items = []
        first_titles = {
            item['file'].replace('_', ' ').casefold()
            for item in candidates if item.get('file')
        }
        fresh = [item for item in fallback_items
                 if item.get('file', '').replace('_', ' ').casefold() not in first_titles]
        add_source_illustrations(article, registry, selections, fresh,
                                 relation, delay, max_per_article, counters)
        if not candidates and not fallback_items:
            counters['no_source_images'] += 1

    if selections:
        registry['articles'][slug] = selections
    elif candidates:
        counters['without_eligible_licence'] += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-per-article', type=int, default=2)
    parser.add_argument('--max-assets', type=int, default=1000)
    parser.add_argument('--max-articles', type=int, default=0, help='0 scans all articles')
    parser.add_argument('--delay', type=float, default=0.5)
    args = parser.parse_args()
    if not 1 <= args.max_per_article <= 3 or not 1 <= args.max_assets <= 1500 or args.delay < 0.3:
        parser.error('Unreasonable acquisition volume or request rate')
    registry = media.load_library()
    media.validate_library(registry)
    counters = dict(previously_archived=0, new_article_images=0, lookup_failures=0,
                    no_source_images=0, without_eligible_licence=0)
    articles = ARTICLES[:args.max_articles] if args.max_articles else ARTICLES
    for number, article in enumerate(articles, 1):
        if len(registry['assets']) >= args.max_assets:
            break
        ingest_article(article, registry, args.delay, args.max_per_article, counters)
        if number % 25 == 0:
            save_progress(registry)
            print('Checkpoint saved. Scanned:', number, 'of', len(articles),
                  'assets:', len(registry['assets']), flush=True)
    save_progress(registry)
    print('Archived, local-only:', json.dumps(counters, sort_keys=True), 'assets:', len(registry['assets']))
    if not registry['assets']:
        raise SystemExit('No licensed Wikimedia files were downloaded. Not recording false success.')


if __name__ == '__main__':
    main()
