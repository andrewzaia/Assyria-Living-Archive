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
from middle_assyrian_content import ARTICLES as MIDDLE_ASSYRIAN_ARTICLES, validate as validate_middle_assyrian
from case_files import DATA as CASE_FILES, validate as validate_case_files
from text_comparisons import DATA as TEXT_COMPARISONS, BY_SLUG as TEXT_COMPARISON_BY_SLUG, validate as validate_text_comparisons
from concordance import DATA as CONCORDANCE, TERMS as CONCORDANCE_TERMS, validate as validate_concordance, build_view as build_concordance_view
from identity_register import DATA as IDENTITY_DATA, CASES as IDENTITY_CASES, validate as validate_identity
from royal_witnesses import DATA as ROYAL_DATA, CASES as ROYAL_CASES, validate as validate_royal

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
    middle_count = validate_middle_assyrian()
    middle_hub = OUT / 'middle-assyrian/index.html'
    if not middle_hub.is_file():
        errors.append('Missing Middle Assyrian social history hub')
    else:
        middle_html = middle_hub.read_text(encoding='utf-8')
        if middle_html.count('class="middle-card"') != middle_count:
            errors.append('Middle Assyrian hub must list every original research guide')
        if 'law is a prescription' not in middle_html or 'Bible remains primary' not in middle_html:
            errors.append('Middle Assyrian hub missing genre and biblical source limitations')
        for item in MIDDLE_ASSYRIAN_ARTICLES:
            slug = item['slug']
            if '/articles/' + slug + '/' not in middle_html:
                errors.append('Missing social history reading route in hub: ' + slug)
            if len(SECTION_DATA.get(slug, {})) != len(item['sections']):
                errors.append('Missing Middle Assyrian section evidence trails: ' + slug)
    middle_slugs = {article['slug'] for article in MIDDLE_ASSYRIAN_ARTICLES}
    middle_claims = [item for item in claim_report['claims'] if item['article'] in middle_slugs]
    if len(middle_claims) < 14 or any(item['review']['status'] != 'awaiting-independent-review' for item in middle_claims):
        errors.append('Middle Assyrian anchored claims require documented specialist review queue')
    # Accession-level object studies require independently identifiable edition metadata.
    validate_case_files(sources)
    case_hub = OUT / 'case-files/index.html'
    if not case_hub.is_file():
        errors.append('Missing individual archaeological case file hub')
    else:
        case_html = case_hub.read_text(encoding='utf-8')
        if case_html.count('class="case-file-card"') != len(CASE_FILES):
            errors.append('Object case file hub has missing or duplicated entries')
        if 'The Babylonian Chronicle is a' not in case_html or 'independent philological' not in case_html:
            errors.append('Case file hub must disclose source period and review limits')
        for case in CASE_FILES:
            slug = case['slug']
            if '/articles/' + slug + '/' not in case_html:
                errors.append('Case file not linked in hub: ' + slug)
            html_file = OUT / 'articles' / slug / 'index.html'
            if not html_file.is_file():
                errors.append('Missing generated object file: ' + slug)
                continue
            body = html_file.read_text(encoding='utf-8')
            if 'id="object-panel-heading"' not in body:
                errors.append('Missing object identification panel in ' + slug)
            for marker in (case['catalogue'], case['edition'], case['findspot'], case['line_focus']):
                if html_escape(marker, quote=True) not in body and html_escape(marker) not in body:
                    errors.append('Object provenance metadata absent from article ' + slug)
            if len(SECTION_DATA.get(slug, {})) != len(case['sections']):
                errors.append('Missing mapped object evidence sections: ' + slug)
    exported_cases = OUT / 'object-case-files.json'
    if not exported_cases.is_file() or json.loads(exported_cases.read_text(encoding='utf-8')) != CASE_FILES:
        errors.append('Generated object case file catalogue does not match curated data')
    case_slugs = {item['slug'] for item in CASE_FILES}
    case_claims = [item for item in claim_report['claims'] if item['article'] in case_slugs]
    if len(case_claims) < 12 or any(item['review']['status'] != 'awaiting-independent-review' for item in case_claims):
        errors.append('Object-level statements need an explicitly pending independent-review queue')
    # Short original-language excerpts must remain attributed and must never be
    # invented when an individual tablet edition has not been verified.
    compare_report = validate_text_comparisons(CASE_FILES, sources)
    if compare_report != {'cases': 9, 'excerpted': 7, 'edition_pending': 2, 'line_excerpts': 16}:
        errors.append('Unexpected cuneiform comparison counts or edition coverage')
    compare_hub = OUT / 'text-comparisons/index.html'
    if not compare_hub.is_file():
        errors.append('Missing ancient text comparison research hub')
    else:
        hub = compare_hub.read_text(encoding='utf-8')
        if hub.count('class="text-room-item"') != len(CASE_FILES):
            errors.append('Comparison room must list all the object case files')
        if 'not replacement scholarly translations' not in hub and 'not a new translation' not in hub:
            errors.append('Research room must clearly distinguish editorial gloss and authentic scholarly translation')
        for case in CASE_FILES:
            slug = case['slug']
            record = TEXT_COMPARISON_BY_SLUG[slug]
            if 'id="comparison-' + slug + '"' not in hub:
                errors.append('Missing line comparison in research room: ' + slug)
            article_page = OUT / 'articles' / slug / 'index.html'
            if not article_page.is_file():
                errors.append('Missing archaeological object article for transliteration: ' + slug)
                continue
            html_data = article_page.read_text(encoding='utf-8')
            if 'id="compare-lines-title"' not in html_data or 'text-comparisons.css' not in html_data:
                errors.append('Missing line comparison panel on object article: ' + slug)
            if record['status'] == 'edition-pending':
                if 'No verified line-by-line text available.' not in html_data or 'class="compare-table"' in html_data:
                    errors.append('No ancient-language text may be invented for uncollated object: ' + slug)
            else:
                if 'class="compare-table"' not in html_data:
                    errors.append('Missing readable source-comparison table on edited tablet: ' + slug)
                for line in record['lines']:
                    if html_escape(line['transliteration']) not in html_data:
                        errors.append('A source line excerpt is missing from ' + slug)
    comparison_json = OUT / 'text-comparisons.json'
    if not comparison_json.is_file() or json.loads(comparison_json.read_text(encoding='utf-8')) != TEXT_COMPARISONS:
        errors.append('Published text comparison JSON does not match curated excerpts')
    method_article = 'reading-cuneiform-transliteration'
    if len(SECTION_DATA.get(method_article, {})) != 5:
        errors.append('Transliteration methods guide must retain five mapped sections')
    comparison_slugs = {case['slug'] for case in CASE_FILES} | {method_article}
    comparison_claims = [item for item in claim_report['claims'] if item['article'] in comparison_slugs]
    if len(comparison_claims) < 21 or any(item['review']['status'] != 'awaiting-independent-review' for item in comparison_claims):
        errors.append('Text and translation comparison claims must remain pending independent review')
    # Concordance links are scoped citations: exact edited line, catalogue context,
    # original editorial chapter, or a separately identified biblical passage.
    concordance_report = validate_concordance(EDITORIAL_ARTICLES, CASE_FILES, TEXT_COMPARISONS)
    if concordance_report != {'terms': 25, 'object_links': 32, 'article_links': 43, 'passage_links': 11}:
        errors.append('Curated concordance coverage changed without editorial review')
    concordance_html_path = OUT / 'concordance/index.html'
    if not concordance_html_path.is_file():
        errors.append('Concordance research index was not generated')
    else:
        concordance_html = concordance_html_path.read_text(encoding='utf-8')
        if concordance_html.count('class="concordance-term"') != len(CONCORDANCE_TERMS):
            errors.append('Concordance index is missing curated term cards')
        if 'id="concordance-query"' not in concordance_html or 'id="concordance-type"' not in concordance_html:
            errors.append('Concordance searchable and category-filter controls missing')
        if 'concordance.js' not in concordance_html or 'concordance.css' not in concordance_html:
            errors.append('Concordance assets not linked')
        for term in CONCORDANCE_TERMS:
            if 'id="entry-' + term['id'] + '"' not in concordance_html:
                errors.append('Concordance term not directly addressable: ' + term['id'])
    exported = OUT / 'concordance.json'
    if not exported.is_file() or json.loads(exported.read_text(encoding='utf-8')) != CONCORDANCE:
        errors.append('Public concordance JSON differs from curated source')
    for record in build_concordance_view(EDITORIAL_ARTICLES, CASE_FILES, TEXT_COMPARISONS):
        for obj in record['objects']:
            if obj.get('line'):
                location = obj['url'].split('#', 1)[-1]
                html_file = OUT / 'articles' / obj['slug'] / 'index.html'
                if not html_file.is_file() or 'id="' + location + '"' not in html_file.read_text(encoding='utf-8'):
                    errors.append('Concordance citation not anchored to actual edited line: ' + obj['url'])
    # Every name dossier must resolve only already credited concordance references.
    identity_counts = validate_identity()
    if identity_counts != {"cases": 8, "evidence_links": 12}:
        errors.append('Identity register changed without source-level review')
    identity_page = OUT / 'identity-register/index.html'
    if not identity_page.is_file():
        errors.append('Name and identity research page was not generated')
    else:
        identity_html = identity_page.read_text(encoding='utf-8')
        if identity_html.count('class="identity-case"') != len(IDENTITY_CASES):
            errors.append('Name and identity dossier cards are incomplete')
        for case in IDENTITY_CASES:
            if 'id="identity-' + case['id'] + '"' not in identity_html:
                errors.append('Missing identity dossier deep link: ' + case['id'])
        if 'Independent specialist review pending' not in identity_html or 'identity-register.css' not in identity_html:
            errors.append('Identity register missing review disclosure or styles')
    identity_export = OUT / 'identity-cases.json'
    if not identity_export.is_file() or json.loads(identity_export.read_text(encoding='utf-8')) != IDENTITY_DATA:
        errors.append('Identity JSON export differs from authored reference data')
    concordance_page_path = OUT / 'concordance/index.html'
    if not concordance_page_path.is_file() or '/identity-register/' not in concordance_page_path.read_text(encoding='utf-8'):
        errors.append('Ancient text concordance missing identity-review route')
    # Directly identified inscription lines, physical panels and biblical passages
    # must stay mutually distinguishable. This checks references, not ancient truth.
    royal_report = validate_royal(sources, EDITORIAL_ARTICLES)
    if royal_report != {"comparisons": 6, "inscription_comparisons": 5,
                        "museum_comparisons": 1, "bible_routes": 10, "edition_identifiers": 3}:
        errors.append('Royal source and biblical comparison coverage changed unexpectedly')
    royal_html = OUT / 'royal-witnesses/index.html'
    if not royal_html.is_file():
        errors.append('Missing royal inscription and Bible research room')
    else:
        royal_page = royal_html.read_text(encoding='utf-8')
        if royal_page.count('class="royal-case"') != len(ROYAL_CASES):
            errors.append('Missing royal source comparison cards')
        for item in ROYAL_CASES:
            if 'id="witness-' + item['id'] + '"' not in royal_page:
                errors.append('Missing royal source deep link ' + item['id'])
        if 'specialist review pending' not in royal_page or 'royal-witnesses.css' not in royal_page:
            errors.append('Royal comparison disclaimer or style missing')
    royal_export = OUT / 'royal-witnesses.json'
    if not royal_export.is_file() or json.loads(royal_export.read_text(encoding='utf-8')) != ROYAL_DATA:
        errors.append('Generated royal witness dataset mismatches curated source')
    dossier_html = OUT / 'dossiers/index.html'
    if not dossier_html.is_file() or '/royal-witnesses/' not in dossier_html.read_text(encoding='utf-8'):
        errors.append('Historic dossiers missing royal witness backlink')
    for item in ROYAL_CASES:
        article_html = OUT / 'articles' / item['article'] / 'index.html'
        if not article_html.is_file() or '/royal-witnesses/#witness-' + item['id'] not in article_html.read_text(encoding='utf-8'):
            errors.append('Missing reciprocal original royal reading route ' + item['id'])
    expected_sitemap = ALLOW_INDEXING and bool(SITE_URL)
    if (OUT / 'sitemap.xml').exists() != expected_sitemap:
        errors.append('Unexpected sitemap state')
    authored = [ROOT / 'content.py', ROOT / 'map_page.py', ROOT / 'bible_pages.py', ROOT / 'bible_support.py', ROOT / 'biblical_content.py', ROOT / 'generate.py', ROOT / 'site_config.py', ROOT / 'sources.json', ROOT / 'section_evidence.py', ROOT / 'data/section-evidence.json', ROOT / 'claim_review.py', ROOT / 'data/claim-reviews.json', ROOT / 'project_roadmap.py', ROOT / 'data/project-roadmap.json', ROOT / 'language_page.py', ROOT / 'data/syriac-letters.json', ROOT / 'heritage_page.py', ROOT / 'data/heritage-records.json', ROOT / 'governance_page.py', ROOT / 'data/editorial-revisions.json', ROOT / 'stewardship_page.py', ROOT / 'preservation.py', ROOT / 'audit_page.py', ROOT / 'dossier_page.py', ROOT / 'historical_evidence_content.py', ROOT / 'middle_assyrian_page.py', ROOT / 'middle_assyrian_content.py', ROOT / 'case_files.py', ROOT / 'case_files_page.py', ROOT / 'data/object-case-files.json', ROOT / 'text_comparisons.py', ROOT / 'text_comparisons_page.py', ROOT / 'text_comparison_content.py', ROOT / 'data/text-comparisons.json', ROOT / 'concordance.py', ROOT / 'concordance_page.py', ROOT / 'data/concordance.json', ROOT / 'identity_register.py', ROOT / 'identity_page.py', ROOT / 'data/identity-cases.json', ROOT / 'royal_witnesses.py', ROOT / 'royal_witnesses_page.py', ROOT / 'data/royal-witnesses.json', ROOT / 'scripts/audit_sources.py', ROOT / 'scripts/audit_accessibility.py']
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
