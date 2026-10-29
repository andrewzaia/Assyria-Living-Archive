"""Verify the published website, including its design assets and reading routes."""
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request

CHECKS = {
    '/': ('A civilisation.', 'hero-copy', 'styles.css'),
    '/explore/': ('Follow your curiosity.', 'article-grid', 'reference-assyria'),
    '/about/': ('An archive with a long horizon.', 'next-chapters'),
    '/articles/reference-assyria/': ('Preserved reference', 'Wikipedia contributors', 'Download retained source JSON'),
    '/styles.css': ('--paper:', '.hero{'),
    '/app.js': ('searchGlobal', 'renderReading'),
    '/glossary/': ('A glossary for the journey.', 'Read the sourced entry'),
    '/bible/': ('Assyria in the Bible.', 'World English Bible', 'bible.js'),
    '/bible/passages/': ('Let the text speak.', 'bible-query', 'bible-entry'),
    '/bible/read/isa/19/': ('v-25', 'Assyria the work of my hands'),
    '/articles/bible-jonah/': ('Read the Scripture.', 'Jonah 3:1-10'),
    '/map/': ('A changing empire.', 'map-year', 'map.js'),
    '/map.js': ('map-territory', 'map-chapter-select'),
    '/archive/maps/assyria-atlas.json': ('schema_version', 'snapshots', 'bm-chronicle'),
    '/archive/maps/natural-earth-countries.geojson': ('FeatureCollection', 'MultiPolygon'),
    '/stewardship/': ('Make the archive recoverable.', 'preservation-manifest.json', 'Offsite backups:'),
    '/middle-assyrian/': ('An empire built by people.', 'middle-grid', 'Dūr-Katlimmu'),
    '/case-files/': ('Every object has a story.', 'case-files-grid', 'VAT 08971'),
    '/object-case-files.json': ('tablet-kaj-247-workers-temple', 'bm-21901-nineveh-chronicle-case', 'met-62-85-3-sealed-tablet'),
    '/articles/tablet-marv-1-12-guard-rations/': ('VAT 18012 and VAT 18088', 'Object record and edition'),
    '/articles/middle-assyrian-women-and-law/': ('Women, status and the Middle Assyrian Laws', 'Veiling as a marker of status'),
    '/preservation-manifest.json': ('hash_algorithm', 'sha256', 'file_count'),
}

def check(base_url):
    errors = []
    for path, markers in CHECKS.items():
        url = base_url.rstrip('/') + path
        request = urllib.request.Request(url, headers={
            'User-Agent': 'AssyriaLivingArchive-deployment-check',
            'Cache-Control': 'no-cache',
        })
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read().decode('utf-8')
                if response.status != 200:
                    raise ValueError(f'HTTP {response.status}')
            missing = [marker for marker in markers if marker not in body]
            if missing:
                errors.append(f'{path}: expected website content is missing')
        except (OSError, ValueError, urllib.error.URLError) as error:
            errors.append(f'{path}: {error}')
    try:
        url = base_url.rstrip('/') + '/preservation-manifest.json'
        with urllib.request.urlopen(urllib.request.Request(url, headers={
            'User-Agent': 'AssyriaLivingArchive-deployment-check',
            'Cache-Control': 'no-cache',
        }), timeout=15) as response:
            manifest = json.loads(response.read())
        if manifest.get('hash_algorithm') != 'sha256' or manifest.get('schema_version') != 1:
            raise ValueError('unsupported manifest')
        records = {record['path']: record for record in manifest['files']}
        for path in ('index.html', 'catalogue.json', 'editorial-revisions.json',
                     'archive/maps/assyria-atlas.json', 'stewardship/index.html'):
            if path not in records:
                raise ValueError('missing manifest entry: ' + path)
            with urllib.request.urlopen(urllib.request.Request(
                base_url.rstrip('/') + '/' + path, headers={
                    'User-Agent': 'AssyriaLivingArchive-deployment-check',
                    'Cache-Control': 'no-cache',
                }), timeout=15) as response:
                body = response.read()
            if len(body) != records[path]['bytes'] or hashlib.sha256(body).hexdigest() != records[path]['sha256']:
                raise ValueError('live file digest mismatch: ' + path)
    except (KeyError, TypeError, OSError, ValueError, urllib.error.URLError) as error:
        errors.append('Live preservation sample: ' + str(error))
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--attempts', type=int, default=12)
    parser.add_argument('--delay', type=float, default=5)
    args = parser.parse_args()
    for attempt in range(args.attempts):
        errors = check(args.base_url)
        if not errors:
            print(f'Live checks passed for {len(CHECKS)} website routes and assets.')
            return 0
        print(f'Live check {attempt + 1}/{args.attempts}: ' + '; '.join(errors), flush=True)
        if attempt + 1 < args.attempts:
            time.sleep(args.delay)
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
