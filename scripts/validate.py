"""Validate source references and generated local links without network access."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import ARTICLES as FOUNDATION_ARTICLES, TIMELINE
from biblical_content import ARTICLES as BIBLICAL_ARTICLES
from bible_support import validate_passages
EDITORIAL_ARTICLES = FOUNDATION_ARTICLES + BIBLICAL_ARTICLES
from archive_support import load_references, reference_sources
REFERENCES = load_references()
ARTICLES = EDITORIAL_ARTICLES + REFERENCES
from site_config import OUT, BASE_PATH, ALLOW_INDEXING, SITE_URL
from navigation import NAV_GROUPS, NAV_PATHS
from section_evidence import DATA as SECTION_DATA, validate as validate_section_evidence

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = []
        self.headings = 0
        self.canonical = []
        self.robots = None
        self.active_header_nav = None
        self.nav_links = {'Main navigation': [], 'Mobile navigation': []}
        self.nav_current = {'Main navigation': [], 'Mobile navigation': []}
        self.nav_details = {'Main navigation': 0, 'Mobile navigation': 0}

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.active_header_nav = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and attrs.get('aria-label') in self.nav_links:
            self.active_header_nav = attrs['aria-label']
        if tag == 'details' and self.active_header_nav:
            self.nav_details[self.active_header_nav] += 1
        if tag == 'a' and self.active_header_nav and 'href' in attrs:
            self.nav_links[self.active_header_nav].append(attrs['href'])
            if attrs.get('aria-current') == 'page':
                self.nav_current[self.active_header_nav].append(attrs['href'])
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href', ''))
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.robots = attrs.get('content')
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])

def main():
    errors = []
    from validate_atlas import validate as validate_atlas
    validate_atlas()
    validate_passages(EDITORIAL_ARTICLES)
    from validate_bible import validate as validate_bible
    validate_bible()
    sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    sources += reference_sources(REFERENCES)
    source_ids = [s['id'] for s in sources]
    validate_section_evidence(EDITORIAL_ARTICLES, sources)
    slugs = [a['slug'] for a in ARTICLES]
    if len(set(source_ids)) != len(source_ids):
        errors.append('Duplicate source IDs')
    if len(set(slugs)) != len(slugs):
        errors.append('Duplicate article slugs')
    for article in ARTICLES:
        if not article['sources'] or not article['sections']:
            errors.append(f"Article lacks sources or sections: {article['slug']}")
        for ref in article['sources']:
            if ref not in source_ids:
                errors.append(f"Unknown source {ref} in {article['slug']}")
        for slug in article['related']:
            if slug not in slugs:
                errors.append(f"Unknown related article {slug}")
    for event in TIMELINE:
        if event[4] not in slugs or event[5] not in source_ids:
            errors.append(f'Unknown timeline reference: {event[2]}')
    for article in EDITORIAL_ARTICLES:
        route = OUT / 'articles' / article['slug'] / 'index.html'
        if not route.exists():
            errors.append(f"Missing generated editorial guide: {article['slug']}")
            continue
        actual = route.read_text(encoding='utf-8').count('class="section-reading-trail"')
        expected = len(SECTION_DATA.get(article['slug'], {}))
        if actual != expected:
            errors.append(f"Incorrect section reading trail count in {article['slug']}: {actual} instead of {expected}")
    pages = {}
    for path in OUT.rglob('*.html'):
        parsed = Page()
        parsed.feed(path.read_text(encoding='utf-8'))
        pages[path] = parsed
    if not pages:
        errors.append('No generated HTML found; run python generate.py first')
    checked = 0
    required_navigation = {BASE_PATH + destination for destination in NAV_PATHS}
    for path, page in pages.items():
        page_route = '/' + path.relative_to(OUT).as_posix()
        if page_route.endswith('/index.html'):
            page_route = page_route[:-len('index.html')]
        for landmark in ('Main navigation', 'Mobile navigation'):
            missing = required_navigation - set(page.nav_links[landmark])
            if missing:
                errors.append(f'{path.relative_to(OUT)}: {landmark} missing {sorted(missing)}')
            if page.nav_details[landmark] != len(NAV_GROUPS):
                errors.append(f'{path.relative_to(OUT)}: expected {len(NAV_GROUPS)} menu groups in {landmark}')
            current = page.nav_current[landmark]
            expected_current = [BASE_PATH + page_route] if page_route in NAV_PATHS or (landmark == 'Mobile navigation' and page_route == '/reading-list/') else []
            if current != expected_current:
                errors.append(f'{path.relative_to(OUT)}: incorrect active destination in {landmark}: {current!r}')
        if BASE_PATH + '/reading-list/' not in page.refs:
            errors.append(f'{path.relative_to(OUT)}: reading list action missing')

        if page.headings != 1:
            errors.append(f'{path.relative_to(OUT)}: expected one h1')
        if len(set(page.ids)) != len(page.ids):
            errors.append(f'{path.relative_to(OUT)}: duplicate IDs')
        if page.robots != ('index,follow' if ALLOW_INDEXING else 'noindex,nofollow'):
            errors.append(f'{path.relative_to(OUT)}: unexpected indexing metadata')
        if len(page.canonical) != (1 if SITE_URL else 0):
            errors.append(f'{path.relative_to(OUT)}: unexpected canonical metadata')
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            local_path = unquote(url.path)
            if BASE_PATH and local_path.startswith('/'):
                if not local_path.startswith(BASE_PATH + '/'):
                    errors.append(f'{path.relative_to(OUT)}: link escapes base path: {ref}')
                    continue
                local_path = local_path[len(BASE_PATH):]
            target = (OUT / local_path.lstrip('/')) if local_path.startswith('/') else path.parent / local_path
            if not local_path:
                target = path
            if target.is_dir():
                target /= 'index.html'
            checked += 1
            if not target.exists():
                errors.append(f'{path.relative_to(OUT)}: missing {ref}')
            elif url.fragment and target in pages and url.fragment not in pages[target].ids:
                errors.append(f'{path.relative_to(OUT)}: missing fragment {ref}')
    for path in OUT.rglob('*.css'):
        for match in re.findall(r'url\(([^)]+)\)', path.read_text(encoding='utf-8')):
            url = match.strip('"\' ')
            if not urlsplit(url).scheme and not (path.parent / url).exists():
                errors.append(f'{path.relative_to(OUT)}: missing CSS asset {url}')
    catalogue = OUT / 'catalogue.json'
    if catalogue.exists():
        data = json.loads(catalogue.read_text(encoding='utf-8'))
        if len(data['articles']) != len(ARTICLES) or len(data['sources']) != len(sources):
            errors.append('Generated catalogue differs from source counts')
    else:
        errors.append('Missing article catalogue')
    from evidence_report import build as build_evidence
    evidence_file = OUT / 'evidence-index.json'
    if not evidence_file.exists():
        errors.append('Missing evidence relationship index')
    else:
        expected = build_evidence(EDITORIAL_ARTICLES, REFERENCES, sources)
        try:
            actual = json.loads(evidence_file.read_text(encoding='utf-8'))
            if actual != expected:
                errors.append('Evidence index differs from source and article metadata')
        except (OSError, ValueError) as exc:
            errors.append(f'Invalid evidence relationship index: {exc}')
    expected_sitemap = ALLOW_INDEXING and bool(SITE_URL)
    if (OUT / 'sitemap.xml').exists() != expected_sitemap:
        errors.append('Unexpected sitemap state')
    authored = [ROOT / 'content.py', ROOT / 'map_page.py', ROOT / 'bible_pages.py', ROOT / 'bible_support.py', ROOT / 'biblical_content.py', ROOT / 'generate.py', ROOT / 'site_config.py', ROOT / 'sources.json', ROOT / 'section_evidence.py', ROOT / 'data/section-evidence.json']
    authored += list(ROOT.glob('*.md')) + list((ROOT / 'static').glob('*.js'))
    authored += list((ROOT / 'static').glob('*.css')) + list(OUT.rglob('*.html'))
    for path in authored:
        text = path.read_text(encoding='utf-8')
        # Exact Scripture quotations preserve source punctuation; editorial prose uses ASCII hyphens.
        if path.suffix == '.html' and OUT / 'bible' in path.parents:
            text = re.sub(r'<blockquote\b[^>]*>.*?</blockquote>', '', text, flags=re.S)
        if re.search('[\u2010-\u2015\u2212]', text):
            errors.append(f'{path.relative_to(ROOT)}: prohibited dash character')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(pages)} pages, {checked} local references, {len(ARTICLES)} articles and {len(sources)} source records.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
