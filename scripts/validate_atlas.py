"""Offline checks for retained map files, chronology, citations and polygon quality."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate():
    folder = ROOT / 'archive/maps'
    data = json.loads((folder / 'assyria-atlas.json').read_text())
    assert data['schema_version'] == 2
    assert data['licence_url'] == 'https://creativecommons.org/licenses/by/4.0/'
    years = [s['year'] for s in data['snapshots']]
    assert years == sorted(set(years)), 'Snapshots must have unique increasing dates'
    assert all(year < 0 for year in years), 'This edition covers BCE dates'
    sources = {s['id'] for s in data['sources']}
    from content import ARTICLES as HISTORICAL_ARTICLES
    from biblical_content import ARTICLES as BIBLICAL_ARTICLES
    editorial = {article['slug']: article for article in HISTORICAL_ARTICLES + BIBLICAL_ARTICLES}
    titles = data.get('article_titles', {})
    assert titles, 'Atlas related-study directory must not be empty'
    assert set(titles) <= set(editorial), 'Atlas related-study entry has unknown article'
    for slug, title in titles.items():
        assert title == editorial[slug]['title'], f'Atlas article title has changed: {slug}'
    library = {s['id']: s for s in json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))}
    assert sources <= library.keys(), 'Atlas source missing from source library'
    for entry in data['sources']:
        assert library[entry['id']]['url'] == entry['url'], f'Source URL mismatch: {entry["id"]}'
    statuses = {'broad-reconstruction', 'highly-generalised', 'unmapped'}
    regions = {f['id']: f for f in data['regions']['features']}
    places = {p['id'] for p in data['places']}
    assert len(sources) == len(data['sources']), 'Duplicate source ID'
    assert len(regions) == len(data['regions']['features']), 'Duplicate region ID'
    assert len(places) == len(data['places']), 'Duplicate place ID'
    for snapshot in data['snapshots']:
        assert snapshot['sources'] and set(snapshot['sources']) <= sources
        assert set(snapshot['control'] + snapshot['influence']) <= regions.keys()
        assert snapshot['focus'] in places and set(snapshot['fallen']) <= places
        assert not set(snapshot['control']) & set(snapshot['influence']), 'Conflicting legend categories'
        assert snapshot['summary'] and snapshot['caution'], 'Missing historical context'
        reconstruction = snapshot.get('reconstruction', {})
        assert reconstruction.get('status') in statuses, 'Missing or invalid reconstruction category'
        for field in ('boundary_note', 'control_note', 'influence_note'):
            assert isinstance(reconstruction.get(field), str) and len(reconstruction[field].strip()) > 24, f'Missing stage-specific {field}'
        if reconstruction['status'] == 'unmapped':
            assert not snapshot['control'] and not snapshot['influence'], 'Unmapped stage must not draw territory'
        else:
            assert snapshot['control'], 'Mapped stage must describe at least one control region'
        articles = snapshot.get('article_slugs', [])
        assert articles and len(articles) == len(set(articles)), 'Missing or repeated chapter article links'
        assert set(articles) <= set(titles), 'Chapter points to an unregistered editorial guide'
        for slug in articles:
            assert slug in editorial and editorial[slug].get('kind') != 'preserved_reference'
        notes = snapshot.get('evidence_notes', [])
        assert notes and len(notes) == len(snapshot['sources']), 'Every source must have a chapter-specific role'
        note_ids = [n['source_id'] for n in notes]
        assert len(note_ids) == len(set(note_ids)) and set(note_ids) == set(snapshot['sources']), 'Chapter source roles are incomplete'
        assert all(isinstance(n.get('scope'), str) and len(n['scope'].strip()) > 30 for n in notes), 'Source role must describe its limitation'
    def orientation(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    def crosses(a,b,c,d):
        return orientation(a,b,c)*orientation(a,b,d) < 0 and orientation(c,d,a)*orientation(c,d,b) < 0
    for feature in regions.values():
        assert feature['geometry']['type'] == 'Polygon'
        for ring in feature['geometry']['coordinates']:
            assert len(ring) >= 4 and ring[0] == ring[-1], f'Open polygon {feature["id"]}'
            assert all(24 <= point[0] <= 54 and 22 <= point[1] <= 43 for point in ring)
            edges = list(zip(ring, ring[1:]))
            for i,(a,b) in enumerate(edges):
                for c,d in edges[i+1:]:
                    assert not crosses(a,b,c,d), f'Self-intersection: {feature["id"]}'
    for asset in data['basemap']['files']:
        path = folder / asset['path']
        assert path.parent == folder and path.is_file(), 'Map asset must remain local'
        raw = path.read_bytes()
        assert len(raw) == asset['bytes']
        assert hashlib.sha256(raw).hexdigest() == asset['sha256'], f'Changed retained asset: {path.name}'
        geo = json.loads(raw)
        assert geo['type'] == 'FeatureCollection' and geo['features']
    assert not re.search('[\u2010-\u2015\u2212]', json.dumps(data, ensure_ascii=False)), 'Non-ASCII dash in atlas text'
    return len(years), len(regions), len(sources)


if __name__ == '__main__':
    counts = validate()
    print(f'Validated {counts[0]} dated snapshots, {counts[1]} regional polygons, {counts[2]} source notes and retained basemap hashes.')
