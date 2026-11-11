"""Assyrian persecution catalogue and locally rendered incident records."""
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json

DATA_PATH = Path(__file__).resolve().parent / 'static' / 'persecution-records.json'
TYPES = ('Mass killing', 'Displacement', 'Abduction', 'Religious violence',
         'Property seizure', 'Institutional pressure', 'Cultural destruction',
         'Airstrikes', 'Vandalism', 'Land encroachment', 'Physical assault',
         'Harassment')
# The map provider uses a longer name than the editorial catalogue.
COUNTRY_ALIASES = {'United States': 'United States of America'}
EVIDENCE = ('historical', 'documented', 'reported')


def load_records():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    records = data['records']
    assert data['schema_version'] == 1 and len(records) > 0
    ids = {record['id'] for record in records}
    assert len(ids) == len(records)
    natural_earth = json.loads((Path(__file__).resolve().parent /
        'archive/maps/natural-earth-countries.geojson').read_text(encoding='utf-8'))
    map_countries = {feature['properties']['ADMIN'] for feature in natural_earth['features']}
    for record in records:
        assert record['id'].startswith('AP-')
        assert 1500 <= record['year'] <= 2100
        assert record['type'] in TYPES and record['evidence'] in EVIDENCE
        assert COUNTRY_ALIASES.get(record['country'], record['country']) in map_countries, record['country']
        assert record.get('scope') and len(record['scope']) < 160
        related = record.get('related_ids', [])
        assert isinstance(related, list) and len(related) == len(set(related)), record['id']
        assert all(other in ids and other != record['id'] for other in related), record['id']
        lat, lon = record['lat'], record['lon']
        assert (lat is None) == (lon is None), record['id']
        if lat is not None:
            assert isinstance(lat, (int, float)) and isinstance(lon, (int, float))
            assert -90 <= lat <= 90 and -180 <= lon <= 180
        assert all(record.get(k) for k in ('title', 'summary', 'place', 'date', 'actor', 'sources'))
        assert all(s.get('title') and urlsplit(s['url']).scheme == 'https'
                   and urlsplit(s['url']).netloc for s in record['sources'])
        if 'media' in record:
            media = record['media']
            assert media['file'].startswith('/assets/archive-media/')
            assert all(media.get(k) for k in ('alt', 'caption', 'creator', 'licence', 'source_url'))
            assert (Path(__file__).resolve().parent / 'static' / media['file'].lstrip('/')).is_file(), media['file']
    return data


def render():
    data = load_records()
    records = sorted(data['records'], key=lambda r: (-r['year'], r['id']))
    h = lambda value: escape(str(value), quote=True)
    countries = sorted({r['country'] for r in records})
    types = TYPES

    def card(r):
        media_html = ''
        if r.get('media'):
            m = r['media']
            media_html = ('<figure class="ap-photo"><img loading="lazy" decoding="async" src="' +
                          h(m['file']) + '" alt="' + h(m['alt']) + '"><figcaption>' +
                          h(m['caption']) + ' Photo: ' + h(m['creator']) + '. ' +
                          '<a href="' + h(m['source_url']) + '" target="_blank" rel="noopener noreferrer">' +
                          h(m['licence']) + ' - original and attribution</a>.</figcaption></figure>')
        links = ''.join('<li><a href="' + h(s['url']) +
                        '" target="_blank" rel="noopener noreferrer">' + h(s['title']) +
                        '</a></li>' for s in r['sources'])
        related_html = ''
        if r.get('related_ids'):
            related_html = ('<nav class="ap-related" aria-label="Related incident records"><strong>Related reports:</strong> ' +
                ' '.join('<a href="#' + h(other.lower()) + '" data-ap-related="' + h(other) + '">' +
                         h(other) + '</a>' for other in r['related_ids']) + '</nav>')
        return ('<article class="ap-case" id="' + h(r['id'].lower()) + '" data-ap-id="' +
                h(r['id']) + '" data-ap-year="' + str(r['year']) +
                '" data-ap-country="' + h(r['country']) + '" data-ap-type="' +
                h(r['type']) + '" data-ap-evidence="' + h(r['evidence']) +
                '" data-ap-search="' + h(' '.join(str(r[k]) for k in
                ('title', 'summary', 'place', 'country', 'date', 'actor', 'type', 'year', 'scope')).lower()) +
                '"><div class="ap-case-top"><span class="eyebrow">' + h(r['id']) +
                ' / ' + h(r['date']) + '</span><span class="ap-evidence ap-evidence-' +
                h(r['evidence']) + '">' + h({'historical':'Historical research',
                'documented':'Documented account','reported':'Reported account'}[r['evidence']]) +
                '</span></div><div class="ap-case-main"><div><h3>' + h(r['title']) +
                '</h3><p class="ap-case-place">' + h(r['place']) + ', ' +
                h(r['country']) + ' / ' + h(r['type']) + '</p>' +
                '<p class="ap-case-scope"><strong>Community covered:</strong> ' +
                h(r['scope']) + '</p><p>' + h(r['summary']) +
                '</p><p class="ap-actor"><strong>Reported actor or context:</strong> ' +
                h(r['actor']) + '</p></div>' + media_html + '</div>' + related_html +
                '<details class="ap-citations"><summary>Sources and references (' +
                str(len(r['sources'])) + ')</summary><ul>' + links + '</ul></details></article>')
    filters_country = '<option value="">All countries</option>' + ''.join(
        '<option value="' + h(country) + '">' + h(country) + '</option>' for country in countries)
    filters_type = '<option value="">All incident types</option>' + ''.join(
        '<option value="' + h(t) + '">' + h(t) + '</option>' for t in types)
    dataset = json.dumps({'updated_on': data['updated_on'], 'records': records}, ensure_ascii=True)
    dataset = dataset.replace('<', '\\u003c')
    return f'''<main id="main" class="wrap section ap-page" data-persecution>
<div class="page-heading ap-heading"><span class="eyebrow">HUMAN RIGHTS / HISTORICAL RECORD</span><h1>Assyrian persecution.</h1>
<p>An expandable record of mass violence, abductions, displacement, religious intimidation and property violations affecting Assyrian communities across history. Each entry identifies its evidence and links to the published account.</p></div>
<div class="ap-intro"><p>These are <strong>attributed source records</strong>, not a claim that all reports have been independently verified or that the catalogue is complete. A documented report may include unverified allegations. Reports from outside the homeland identify Assyrian diaspora institutions; these are not automatically findings of religious hate crime. Historical Assyrian communities appear across several church traditions; reports that only identify Christians or Syriac communities are labelled accordingly rather than silently assigning an ethnicity to every victim.</p>
<p><strong>Land rights and alleged Kurdish-actor abuses:</strong> The catalogue now separately identifies claimed encroachment by private individuals, actions of KRG authorities, arrests and physical assaults, and cases involving other Iraqi agencies. Community complaints do not by themselves establish legal ownership, motive or a criminal conviction. Court orders, subsequent releases and the authorities' recorded responses are included when available. The 2019 Assyrian Aid Society survey lists 94 land-claim rows, not 94 independently confirmed seizures; individual village entries are cross-linked to its regional overview. Some historical dispossession predates the KRG and must be attributed to the former Iraqi regime rather than contemporary authorities. It is inaccurate to attribute an individual or government action to Kurdish people collectively.</p>
<p>Map shading counts <strong>catalogue records</strong>, not people harmed, individual victims, unique incidents or the rate of persecution. Multiple records may concern related events. Place markers identify approximate localities; entries without a defensible locality remain on the country layer without a location pin. No unlisted location should be interpreted as safe or incident-free.</p></div>
<div class="ap-metrics" aria-label="Catalogue coverage">
<div><strong id="ap-total">{len(records)}</strong><span>Source-linked records</span></div>
<div><strong id="ap-countries">{len(countries)}</strong><span>Countries represented</span></div>
<div><strong id="ap-places">{len({(r['place'],r['country']) for r in records})}</strong><span>Named localities / regions</span></div>
<div><strong>{min(r['year'] for r in records)} - {max(r['year'] for r in records)}</strong><span>Years covered by this edition</span></div></div>
<section class="ap-map-section" aria-label="Interactive country heat map"><div class="ap-section-heading"><div><span class="eyebrow">GEOGRAPHIC RECORD</span><h2>Where persecution is recorded.</h2></div><div class="ap-map-actions" role="group" aria-label="Map view">
<button type="button" id="ap-world" class="button outline" aria-pressed="true">World</button>
<button type="button" id="ap-homeland" class="button outline" aria-pressed="false">Historic homeland</button>
<button type="button" id="ap-reset" class="button outline">Reset map and filters</button></div></div>
<div class="ap-map-frame"><svg id="ap-map" viewBox="0 0 1080 540" aria-labelledby="ap-map-title ap-map-desc" role="img"><title id="ap-map-title">Assyrian persecution catalogue heat map</title><desc id="ap-map-desc">Country shading displays the number of matching catalogue reports. Interactive countries also filter the records. The country selector below provides an equivalent keyboard-accessible method.</desc>
<rect width="1080" height="540" class="ap-sea"/><g id="ap-map-countries"></g><g id="ap-map-markers"></g></svg>
<div class="ap-map-watermark">NATURAL EARTH / LOCATIONS APPROXIMATE</div></div>
<p class="ap-map-help" id="ap-map-status" role="status" aria-live="polite">Loading locally stored map geography. The catalogue remains readable without the map.</p>
<div class="ap-legend" aria-label="Heat map legend"><span><i class="ap-level ap-level-0"></i> No catalogue entries</span><span><i class="ap-level ap-level-1"></i> 1-2</span><span><i class="ap-level ap-level-2"></i> 3-5</span><span><i class="ap-level ap-level-3"></i> 6-10</span><span><i class="ap-level ap-level-4"></i> 11+</span><span><i class="ap-pin-symbol"></i> Named place / region</span></div></section>
<section class="ap-catalogue" aria-labelledby="ap-catalogue-title"><div class="ap-section-heading"><div><span class="eyebrow">EVENT AND REPORT INDEX</span><h2 id="ap-catalogue-title">Browse the catalogue.</h2></div><a href="/persecution-records.json" class="text-link" download>Download source data (JSON)</a></div>
<div class="ap-filters"><label>Search records<input type="search" id="ap-search" placeholder="Place, event, year, actor or keyword" autocomplete="off"></label>
<label>Country<select id="ap-country">{filters_country}</select></label>
<label>Type<select id="ap-type">{filters_type}</select></label>
<label>Period<select id="ap-period"><option value="">All years</option><option value="before1900">Before 1900</option><option value="1900-1949">1900-1949</option><option value="1950-1999">1950-1999</option><option value="2000-2013">2000-2013</option><option value="2014-2019">2014-2019</option><option value="2020+">2020 onwards</option></select></label>
<label>Evidence<select id="ap-evidence"><option value="">All evidence categories</option><option value="historical">Historical research</option><option value="documented">Documented accounts</option><option value="reported">Reported accounts</option></select></label>
<label>Order<select id="ap-sort"><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label></div>
<p id="ap-results" class="ap-results" role="status" aria-live="polite">Showing all {len(records)} records.</p>
<div class="ap-case-list" id="ap-case-list">{''.join(card(r) for r in records)}</div>
<div class="empty-state" id="ap-empty" hidden><h3>No records match these filters.</h3><p>Reset the filters, or try a different location or date.</p></div></section>
<section class="ap-method" id="persecution-method"><span class="eyebrow">RESEARCH STANDARDS AND LIMITS</span><h2>How to interpret the catalogue.</h2>
<p><strong>Community covered</strong> distinguishes direct Assyrian cases from Syriac, church-linked and wider Christian accounts. Inclusion records a documented connection to Assyrian history or institutions; it does not assign one ethnicity to everyone affected. Incidents against Assyrian institutions abroad are recorded even when their motives are unresolved.</p>
<p><strong>Historical research</strong> denotes an event recorded in historical scholarship; <strong>documented account</strong> denotes a named published investigation or official record; <strong>reported account</strong> preserves the attribution of a report or allegation without independently adjudicating it. These labels describe evidence presentation, not a numerical reliability score.</p>
<p>When a source documents more than one relevant incident, each event is assessed separately. Related report links connect distinct records without merging their dates or counting one event twice. The maintained source-review register identifies source lists still awaiting further event extraction.</p>
<p>Selected historical campaigns are represented by regional entries, while modern cases may be individual attacks, testimony or country-level assessments. Event groups may overlap (for example, the 2014 Nineveh Plains offensive and town-specific attacks), so the total is a count of catalogue entries, not distinct events. Counts therefore must not be used to compare the prevalence or severity of persecution across countries or centuries. Coordinates are approximate and not intended for identifying victims, private property or exact attack sites.</p>
<p>Photographs appear only when a reuse-checked local archive file is available. Historical contextual photographs are explicitly labelled; no remotely hosted media is embedded. Links open the original published source and do not imply institutional endorsement. <a href="/governance/">Read the archive's corrections policy</a> or <a href="/contribute/">prepare a sourced addition</a>. Basemap: <a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noopener noreferrer">Natural Earth public-domain geography</a>, retained locally.</p>
<p><a href="/articles/sayfo/">Read about Sayfo</a> / <a href="/articles/simele/">Read about Simele</a> / <a href="/map/">Explore the historical atlas</a>.</p></section>
<noscript><p class="ap-noscript">The source-linked catalogue is available below. Enable JavaScript for interactive filters and the country heat map.</p></noscript>
<script type="application/json" id="ap-data">{dataset}</script></main>'''
