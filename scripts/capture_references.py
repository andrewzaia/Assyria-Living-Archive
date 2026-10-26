"""Explicitly refresh selected, openly licensed references. Never runs during a build."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.parse import urlencode, quote
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'archive'
UA = 'AssyriaLivingArchive/1.0 (educational preservation; https://github.com/andrewzaia/Assyria-Living-Archive)'
TERMS = 'https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content'
LICENCE = 'https://creativecommons.org/licenses/by-sa/4.0/'

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def request(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = response.read()
        return data, dict(response.headers)

def capture(title, category):
    query = dict(action='parse', page=title, prop='text|revid|displaytitle|sections',
                 format='json', formatversion=2, redirects=1, maxlag=5)
    endpoint = 'https://en.wikipedia.org/w/api.php?' + urlencode(query)
    payload, headers = request(endpoint)
    result = json.loads(payload)
    if 'error' in result:
        raise ValueError(result['error'].get('info', str(result['error'])))
    parsed = result['parse']
    revision = int(parsed['revid'])
    page_id = int(parsed['pageid'])
    canonical = parsed['title']
    slug = slugify(canonical)
    folder = ARCHIVE / 'wikipedia' / 'raw'
    folder.mkdir(parents=True, exist_ok=True)
    filename = f'{page_id}-{revision}-{hashlib.sha256(payload).hexdigest()[:12]}.json'
    path = folder / filename
    path.write_bytes(payload)
    return dict(
        id='wikipedia-' + slug, slug='reference-' + slug, title=canonical, requested_title=title,
        category=category, kind='encyclopaedia', publisher='Wikipedia', authors=['Wikipedia contributors'],
        source_url='https://en.wikipedia.org/wiki/' + quote(canonical.replace(' ', '_'), safe="_()-'"),
        revision_url=f'https://en.wikipedia.org/w/index.php?oldid={revision}',
        history_url='https://en.wikipedia.org/w/index.php?' + urlencode(dict(title=canonical, action='history')),
        revision_id=revision, page_id=page_id,
        retrieved_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        licence='CC BY-SA 4.0', licence_url=LICENCE, rights_basis_url=TERMS,
        raw_path='wikipedia/raw/' + filename, sha256=hashlib.sha256(payload).hexdigest(), size_bytes=len(payload),
        content_type=headers.get('Content-Type', 'application/json'),
        changes='Reader formatting is adapted; embedded media and navigation are omitted, links are resolved locally where available, and dash punctuation is normalised. The original API response is preserved unchanged.',
        review_status='Preserved external reference; not independently fact-checked by this project.'
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Capture a new revision even when a source is already retained')
    parser.add_argument('--limit', type=int, help='Limit the selected set during an explicit acquisition run')
    parser.add_argument('--max-new',type=int,help='Bound the number of new acquisition attempts without dropping retained records')
    args = parser.parse_args()
    selection = json.loads((ROOT / 'data/reference-selection.json').read_text())
    selected = [(title, category) for category, titles in selection.items() for title in titles]
    if args.limit:
        selected = selected[:args.limit]
    manifest_path = ARCHIVE / 'encyclopaedia-references.json'
    if not manifest_path.exists():
        manifest_path = ARCHIVE / 'references.json'
    existing = json.loads(manifest_path.read_text()).get('records', []) if manifest_path.exists() else []
    saved = {record['requested_title']: record for record in existing}
    pending = [(title, category) for title, category in selected if args.refresh or title not in saved]
    pending.sort(key=lambda pair: {'People & diaspora':0,'Places & heritage':1}.get(pair[1],2))
    if args.max_new:
        pending = pending[:args.max_new]
    failures = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(capture, title, category): title for title, category in pending}
        for count, job in enumerate(as_completed(jobs), 1):
            title = jobs[job]
            try:
                record = job.result()
                saved[title] = record
                print(f'Captured {count}/{len(pending)}: {record["title"]}', flush=True)
            except Exception as error:
                failures.append(dict(title=title, error=str(error)))
                print(f'Unavailable: {title}: {error}', flush=True)
            # Keep every successful checkpoint reproducible if interrupted.
            ordered = [saved[title] for title, _ in selected if title in saved]
            unique = {record['page_id']: record for record in ordered}
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(dict(
                schema_version=1, records=list(unique.values()), unresolved=failures,
                rights_note='Selected Wikipedia text is retained under CC BY-SA 4.0 with source/revision/history attribution. Media is not automatically covered by the text licence.'
            ), ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Retained {len(saved)} requested records; {len(failures)} unresolved selections.', flush=True)

if __name__ == '__main__':
    main()
