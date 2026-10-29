"""Public catalogue of externally published heritage references, with local planning downloads."""
import json
import re
from collections import Counter
from html import escape as h
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data/heritage-records.json').read_text(encoding='utf-8'))
TEMPLATES = (
    ('Story planning worksheet', '/archive/heritage/story-planning-template.md',
     'Organise place names, dates, source references and outstanding rights without sending data.'),
    ('Interview question prompts', '/archive/heritage/interview-prompts.md',
     'Open-ended questions that respect a participant\'s choices and privacy.'),
    ('Permissions review checklist', '/archive/heritage/permissions-review-checklist.md',
     'Separate recording, preservation, research access, publication and later reuse.'),
)


def validate(articles, sources):
    article_index = {a['slug']: a for a in articles}
    source_index = {s['id']: s for s in sources}
    if DATA.get('schema_version') != 1 or DATA.get('publication_status') != 'external-links-only':
        raise ValueError('Heritage records must be a public external-reference-only index')
    if not DATA.get('policy') or not re.fullmatch(r'20[0-9]{2}-[01][0-9]-[0-3][0-9]', DATA.get('updated_on', '')):
        raise ValueError('Invalid heritage policy or last update date')
    cats = DATA.get('categories', [])
    if len(cats) < 3 or len(set(cats)) != len(cats):
        raise ValueError('Heritage themes must be unique and documented')
    records = DATA.get('records', [])
    if len(records) < 6:
        raise ValueError('Heritage examples must offer a genuine selection of published sources')
    ids = []
    forbidden = {'name', 'email', 'phone', 'address', 'transcript', 'recording', 'upload', 'consent_signature', 'contact'}
    for record in records:
        key = record.get('id', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key):
            raise ValueError('Invalid heritage record identifier')
        ids.append(key)
        if forbidden & set(record):
            raise ValueError('Public heritage records must not contain private intake fields')
        if record.get('category') not in cats:
            raise ValueError('Unknown heritage theme: ' + key)
        if record.get('source_id') not in source_index:
            raise ValueError('Unrecognised source ID for heritage record: ' + key)
        if record.get('article_slug') not in article_index:
            raise ValueError('Missing related article for heritage record: ' + key)
        if record.get('locally_copied') is not False or record.get('record_status') != 'externally-published-reference':
            raise ValueError('Heritage references must not claim archived private media or approval')
        if record.get('rights') != 'Provider-held or item-specific; check the external custodian\'s permissions':
            raise ValueError('Heritage material must retain the explicit item-level rights disclaimer')
        for field in ('title', 'era', 'place', 'description', 'source_role', 'access'):
            if not isinstance(record.get(field), str) or len(record[field].strip()) < 5:
                raise ValueError('Heritage reference missing description: ' + key + '/' + field)
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate heritage reference IDs')
    if set(Counter(r['category'] for r in records)) != set(cats):
        raise ValueError('Every heritage category must have at least one reference')
    if not all((ROOT / path.lstrip('/')).is_file() for _, path, _ in TEMPLATES):
        raise ValueError('Missing local heritage planning template')
    return len(records)


def render(heading, articles, sources):
    validate(articles, sources)
    articles_by_slug = {a['slug']: a for a in articles}
    sources_by_id = {s['id']: s for s in sources}
    categories = DATA['categories']
    options = '<option value="all">All heritage themes</option>' + ''.join(
        '<option value="' + h(label, quote=True) + '">' + h(label) + '</option>' for label in categories
    )
    records = []
    for record in DATA['records']:
        src = sources_by_id[record['source_id']]
        slug = record['article_slug']
        records.append(
            '<li class="heritage-record" data-heritage-category="' + h(record['category'], quote=True) + '">' +
            '<div class="heritage-record-meta"><span>' + h(record['category']) + '</span><small>' +
            h(record['era']) + '</small></div><h3>' + h(record['title']) + '</h3>' +
            '<p class="heritage-place">' + h(record['place']) + '</p>' +
            '<p>' + h(record['description']) + '</p>' +
            '<div class="heritage-source-role"><strong>Evidence type:</strong> ' + h(record['source_role']) + '</div>' +
            '<p class="heritage-rights">Externally hosted reference only. Reuse requires checking the custodian\'s terms.</p>' +
            '<div class="heritage-record-links"><a href="' + h(src['url'], quote=True) +
            '" target="_blank" rel="noopener">Read original source</a>' +
            '<a href="/articles/' + h(slug) + '/">Read ' + h(articles_by_slug[slug]['title']) + '</a></div></li>'
        )
    templates = ''.join(
        '<li><h3>' + h(label) + '</h3><p>' + h(description) + '</p>' +
        '<a href="' + h(path, quote=True) + '" download>Download blank Markdown template</a></li>'
        for label, path, description in TEMPLATES
    )
    stages = [
        ('01', 'Prepare', 'Describe the research question and relevant cultural, linguistic and historical context. Ask about privacy and intended uses before recording.'),
        ('02', 'Document permission', 'Separate permission to make a recording, preserve it privately, let researchers access it, and publish or redistribute it.'),
        ('03', 'Review and restrict', 'Offer narrator review where possible, document corrections, remove unconsented third-party details and resolve rights for each media asset.'),
        ('04', 'Preserve or publish responsibly', 'Choose a suitable custodian. Only release approved versions and non-sensitive metadata with clear rights and correction arrangements.'),
    ]
    steps = ''.join(
        '<li><span class="heritage-step-number">' + h(n) + '</span><div><h3>' + h(title) + '</h3><p>' + h(description) +
        '</p></div></li>' for n, title, description in stages
    )
    count = len(DATA['records'])
    return (
        '<main id="main" class="wrap section heritage-hub">' +
        heading('COMMUNITY MEMORY / PRESERVATION', 'Everyday voices belong in history.',
                'Explore attributed public heritage sources, find research methods and prepare a private first draft. No new personal testimony is collected or published here.') +
        '<div class="heritage-intro"><div><span class="eyebrow">THE PUBLIC SOURCE INDEX</span>' +
        '<h2>Look beyond monuments.</h2><p>Assyrian history includes migration, language, local institutions, family recipes, music, remembered villages and the way stories move between generations. ' +
        'This index links to material already published by its custodians. These are sourced examples, not recordings deposited with this project.</p></div>' +
        '<aside><strong>' + str(count) + '</strong><span>External reference entries</span>' +
        '<p>No original audio, transcripts, family photographs or private contact details are held in this catalogue.</p></aside></div>' +
        '<section class="heritage-section" aria-labelledby="heritage-index-title"><div class="heritage-section-head">' +
        '<div><span class="eyebrow">PUBLISHED LEADS / FOUR THEMES</span><h2 id="heritage-index-title">Discover living heritage.</h2></div>' +
        '<div class="heritage-filter"><label for="heritage-category">Filter by theme</label><select id="heritage-category" aria-controls="heritage-results">' +
        options + '</select><p id="heritage-count" role="status" aria-live="polite">Showing ' + str(count) +
        ' external references</p></div></div>' +
        '<ul id="heritage-results" class="heritage-records">' + ''.join(records) + '</ul>' +
        '<p id="heritage-empty" hidden>No entries match that selection.</p></section>' +
        '<section class="heritage-section" aria-labelledby="heritage-method-title"><div class="heritage-section-head">' +
        '<div><span class="eyebrow">A PRIVATE-FIRST METHOD</span><h2 id="heritage-method-title">From memory to a usable record.</h2></div></div>' +
        '<ol class="heritage-steps">' + steps + '</ol><p class="heritage-source-note">Guided by ' +
        '<a href="https://oralhistoryaustralia.org.au/guide-ethical-practice/" target="_blank" rel="noopener">Oral History Australia</a> ' +
        'and the <a href="https://www.library.gov.au/services/copyright-library-collections/rights-and-oral-history-and-folklore-collection" target="_blank" rel="noopener">National Library of Australia\'s rights guidance</a>. ' +
        'The published policies of these institutions do not confer consent to reuse an individual interview.</p></section>' +
        '<section class="heritage-section" aria-labelledby="heritage-download-title"><div class="heritage-section-head">' +
        '<div><span class="eyebrow">BLANK FILES / LOCAL DOWNLOAD</span><h2 id="heritage-download-title">Prepare, without submitting.</h2></div></div>' +
        '<p class="heritage-note">Download these original blank Markdown worksheets to your device. Do not put completed private forms, recordings or family documents into a public Git repository. ' +
        'The downloads do not send anything to this website and are not legal releases or proof of consent.</p>' +
        '<ul class="heritage-templates">' + templates + '</ul></section>' +
        '<div class="heritage-final"><span class="eyebrow">CONTRIBUTE WITH CARE</span>' +
        '<h2>Have a story, a correction or a heritage lead?</h2>' +
        '<p>The existing contribution form makes a Markdown draft on your device only. There is no public upload, submission, approval or automated publication service. ' +
        'Only consider an authorised delivery method after securing necessary permissions.</p>' +
        '<a href="/contribute/">Prepare a local contribution draft</a> ' +
        '<a href="/articles/heritage-consent-and-access/">Read the consent and access guide</a></div></main>'
    )
