"""Verify the published website, including its design assets and reading routes."""
import argparse
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
    '/map/': ('A changing empire.', 'map-year', 'map.js'),
    '/map.js': ('map-territory', 'map-chapter-select'),
    '/archive/maps/assyria-atlas.json': ('schema_version', 'snapshots', 'bm-chronicle'),
    '/archive/maps/natural-earth-countries.geojson': ('FeatureCollection', 'MultiPolygon'),
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
