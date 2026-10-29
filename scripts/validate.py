"""Validate source references and generated local links without network access."""
import json
import re
import sys
from html.parser import HTMLParser
from html import escape as html_escape
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
from claim_review import build as build_claim_reviews
from project_roadmap import DATA as ROADMAP_DATA, validate as validate_roadmap
from language_page import DATA as LANG_DATA, validate as validate_languages
from heritage_page import DATA as HERITAGE_DATA, validate as validate_heritage, TEMPLATES as HERITAGE_TEMPLATES
from governance_page import DATA as GOVERNANCE_DATA, validate as validate_governance, CHECKLISTS as GOVERNANCE_CHECKLISTS
from preservation import verify_manifest
from audit_page import AUDIT as SOURCE_AUDIT
from scripts.audit_accessibility import run as accessibility_smoke
from historical_evidence_content import ARTICLES as HISTORICAL_EVIDENCE_ARTICLES

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
    claim_report = build_claim_reviews(EDITORIAL_ARTICLES, sources)
    milestones = validate_roadmap()
    letter_count = validate_languages(EDITORIAL_ARTICLES, sources)
    heritage_count = validate_heritage(EDITORIAL_ARTICLES, sources)
    revision_count, correction_count = validate_governance()
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
    evidence_html = OUT / 'about/evidence/index.html'
    if not evidence_html.exists() or evidence_html.read_text(encoding='utf-8').count('id="claim-cl-') != claim_report['summary']['claim_records']:
        errors.append('Claim evidence queue is missing or incomplete in generated evidence register')
    about_html = OUT / 'about/index.html'
    if not about_html.exists():
        errors.append('Missing About roadmap page')
    else:
        html = about_html.read_text(encoding='utf-8')
        for milestone in milestones:
            if 'id="milestone-' + milestone['id'] + '"' not in html:
                errors.append('Roadmap milestone missing from Next Chapters: ' + milestone['id'])
        if 'id="next-chapters"' not in html:
            errors.append('Next Chapters anchor missing')
    roadmap_file = OUT / 'project-roadmap.json'
    if not roadmap_file.exists() or json.loads(roadmap_file.read_text(encoding='utf-8')) != ROADMAP_DATA:
        errors.append('Generated roadmap differs from maintained milestones')
    language_file = OUT / 'languages/index.html'
    if not language_file.exists():
        errors.append('Missing generated language reference hub')
    else:
        html = language_file.read_text(encoding='utf-8')
        if html.count('class="lang-letter"') != letter_count:
            errors.append('Incorrect Unicode letter count on generated language hub')
        if html.count('class="lang-glyph"') != letter_count:
            errors.append('Missing Syriac character display on language hub')
        for slug in LANG_DATA['reading_routes']:
            if '/articles/' + slug + '/' not in html:
                errors.append('Language hub reading route missing: ' + slug)
        for source_id in LANG_DATA['recording_sources']:
            if not any(source['id'] == source_id and source['url'] in html for source in sources):
                errors.append('Missing source-backed dialect recording route: ' + source_id)
    heritage_file = OUT / 'heritage/index.html'
    if not heritage_file.exists():
        errors.append('Missing generated community heritage hub')
    else:
        html = heritage_file.read_text(encoding='utf-8')
        if html.count('class="heritage-record"') != heritage_count:
            errors.append('Heritage hub record count differs from maintained public index')
        for record in HERITAGE_DATA['records']:
            if 'data-heritage-category="' + html_escape(record['category'], quote=True) + '"' not in html:
                errors.append('Missing public heritage theme: ' + record['id'])
            if '/articles/' + record['article_slug'] + '/' not in html:
                errors.append('Missing heritage article route: ' + record['id'])
            source = next((item for item in sources if item['id'] == record['source_id']), None)
            if not source or source['url'] not in html:
                errors.append('Missing original heritage source link: ' + record['id'])
        for _, path, _ in HERITAGE_TEMPLATES:
            if path not in html or not (OUT / path.lstrip('/')).exists():
                errors.append('Missing downloadable blank heritage worksheet: ' + path)
        if 'No original audio, transcripts, family photographs or private contact details' not in html:
            errors.append('Heritage privacy and custody statement missing')
    exported_heritage = OUT / 'heritage-records.json'
    if not exported_heritage.exists():
        errors.append('Missing open heritage reference index')
    elif json.loads(exported_heritage.read_text(encoding='utf-8')) != HERITAGE_DATA:
        errors.append('Heritage reference export differs from maintained source')
    governance_html = OUT / 'governance/index.html'
    if not governance_html.is_file():
        errors.append('Missing public editorial governance page')
    else:
        html = governance_html.read_text(encoding='utf-8')
        if html.count('class="governance-entry"') != revision_count:
            errors.append('Governance page must list all curated merged revisions')
        if ('id="governance-correction-count"' not in html or
            ('>' + str(correction_count) + ' public correction record') not in html):
            errors.append('Public correction record count missing or incorrect')
        for change in GOVERNANCE_DATA['changes']:
            if 'id="revision-' + change['id'].lower() + '"' not in html:
                errors.append('Public revision record not rendered: ' + change['id'])
            if 'https://github.com/' + GOVERNANCE_DATA['project'] + '/commit/' + change['commit'] not in html:
                errors.append('Public revision commit missing: ' + change['id'])
        for correction in GOVERNANCE_DATA['corrections']:
            if 'id="correction-' + correction['id'].lower() + '"' not in html:
                errors.append('Public correction notice missing: ' + correction['id'])
        for _, path, _ in GOVERNANCE_CHECKLISTS:
            if path not in html or not (OUT / path.lstrip('/')).is_file():
                errors.append('Missing public governance worksheet: ' + path)
        if 'Independent specialist review: not recorded.' not in html:
            errors.append('Governance page must distinguish build checks from specialist review')
    exported_editorial = OUT / 'editorial-revisions.json'
    if not exported_editorial.is_file():
        errors.append('Missing machine-readable editorial revision register')
    elif json.loads(exported_editorial.read_text(encoding='utf-8')) != GOVERNANCE_DATA:
        errors.append('Public editorial revision export differs from maintained source')
    stewardship_html = OUT / 'stewardship/index.html'
    if not stewardship_html.is_file():
        errors.append('Missing generated publication stewardship guide')
    else:
        html = stewardship_html.read_text(encoding='utf-8')
        for required in ('/preservation-manifest.json', 'id="integrity"', 'id="publication"',
                         'id="recovery"', 'id="human-review"', 'docs/PRESERVATION.md'):
            if required not in html:
                errors.append('Stewardship page missing disclosure or reference: ' + required)
        if ALLOW_INDEXING and 'Indexing enabled by release configuration' not in html:
            errors.append('Stewardship indexing state does not match this build')
        if not ALLOW_INDEXING and 'Search indexing deliberately disabled' not in html:
            errors.append('Stewardship page must show the active noindex state')
    try:
        manifest = verify_manifest(OUT)
        if manifest['base_path'] != BASE_PATH or manifest['indexing_enabled'] != ALLOW_INDEXING:
            errors.append('Preservation manifest does not match deployment configuration')
        if manifest['file_count'] < len(pages):
            errors.append('Preservation manifest appears to omit generated public assets')
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Preservation fixity verification failed: ' + str(exc))
    audit_page = OUT / 'audit/index.html'
    if not audit_page.is_file():
        errors.append('Missing generated source/accessibility audit room')
    else:
        html = audit_page.read_text(encoding='utf-8')
        for marker in ('id="sources"', 'id="accessibility"', 'id="method-and-limitations"',
                       '/source-integrity-index.json', 'not-probed'):
            if marker not in html:
                errors.append('Public audit page missing method or limitation: ' + marker)
    exported_sources = OUT / 'source-integrity-index.json'
    if not exported_sources.is_file():
        errors.append('Missing structurally checked source index')
    elif json.loads(exported_sources.read_text(encoding='utf-8')) != SOURCE_AUDIT:
        errors.append('Structural source index differs from maintained curated source records')
    if SOURCE_AUDIT['mode'] != 'offline-metadata-only' or SOURCE_AUDIT['record_count'] < 80:
        errors.append('Offline source audit must retain explicit unprobed source status')
    errors.extend(accessibility_smoke(OUT))
    dossier_index = OUT / 'dossiers/index.html'
    if not dossier_index.is_file():
        errors.append('Missing historical evidence dossier hub')
    else:
        hub_html = dossier_index.read_text(encoding='utf-8')
        if len(HISTORICAL_EVIDENCE_ARTICLES) != 8:
            errors.append('Historical evidence dossier count changed without editorial review')
        if hub_html.count('class="dossier-card"') != len(HISTORICAL_EVIDENCE_ARTICLES):
            errors.append('Historical evidence room does not expose all dossiers')
        for dossier in HISTORICAL_EVIDENCE_ARTICLES:
            if '/articles/' + dossier['slug'] + '/' not in hub_html:
                errors.append('Dossier not linked from hub: ' + dossier['slug'])
            if len(dossier['sections']) != 5 or len(SECTION_DATA.get(dossier['slug'], {})) != 5:
                errors.append('Dossier must retain five mapped source-specific sections: ' + dossier['slug'])
            if 'bible-webbe' not in dossier['sources'] or not dossier.get('passages'):
                errors.append('Biblical primary passages must be present on historical dossier: ' + dossier['slug'])
        dossier_ids = {item['slug'] for item in HISTORICAL_EVIDENCE_ARTICLES}
        queued = [item for item in claim_report['claims'] if item['article'] in dossier_ids]
        if len(queued) < 12 or any(item['review']['status'] != 'awaiting-independent-review' for item in queued):
            errors.append('New object-level claims must remain in a documented specialist review queue')
    expected_sitemap = ALLOW_INDEXING and bool(SITE_URL)
    if (OUT / 'sitemap.xml').exists() != expected_sitemap:
        errors.append('Unexpected sitemap state')
    authored = [ROOT / 'content.py', ROOT / 'map_page.py', ROOT / 'bible_pages.py', ROOT / 'bible_support.py', ROOT / 'biblical_content.py', ROOT / 'generate.py', ROOT / 'site_config.py', ROOT / 'sources.json', ROOT / 'section_evidence.py', ROOT / 'data/section-evidence.json', ROOT / 'claim_review.py', ROOT / 'data/claim-reviews.json', ROOT / 'project_roadmap.py', ROOT / 'data/project-roadmap.json', ROOT / 'language_page.py', ROOT / 'data/syriac-letters.json', ROOT / 'heritage_page.py', ROOT / 'data/heritage-records.json', ROOT / 'governance_page.py', ROOT / 'data/editorial-revisions.json', ROOT / 'stewardship_page.py', ROOT / 'preservation.py', ROOT / 'audit_page.py', ROOT / 'dossier_page.py', ROOT / 'historical_evidence_content.py', ROOT / 'scripts/audit_sources.py', ROOT / 'scripts/audit_accessibility.py']
    authored += list(ROOT.glob('*.md')) + list((ROOT / 'archive/heritage').glob('*.md')) + list((ROOT / 'archive/governance').glob('*.md')) + list((ROOT / 'docs').glob('*.md')) + list((ROOT / 'static').glob('*.js'))
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
