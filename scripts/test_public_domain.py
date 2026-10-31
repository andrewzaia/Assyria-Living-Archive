"""Verify that production output uses only the canonical public hostname."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://www.assyrialivingarchive.org'
config = json.loads((ROOT / 'site.config.json').read_text(encoding='utf-8'))
assert config == {'site_url': DOMAIN, 'base_path': '', 'allow_indexing': True}, config
index = (ROOT / 'dist' / 'index.html').read_text(encoding='utf-8')
assert '<link rel="canonical" href="' + DOMAIN + '/">' in index
assert '<meta name="robots" content="index,follow">' in index
assert 'andrewzaia.github.io' not in index
robots = (ROOT / 'dist' / 'robots.txt').read_text(encoding='utf-8')
assert DOMAIN + '/sitemap.xml' in robots, robots
sitemap = (ROOT / 'dist' / 'sitemap.xml').read_text(encoding='utf-8')
assert '<loc>' + DOMAIN + '/</loc>' in sitemap
assert 'andrewzaia.github.io' not in sitemap
worker = json.loads((ROOT / 'worker' / 'wrangler.jsonc').read_text(encoding='utf-8'))
assert worker.get('workers_dev') is False, 'Contribution Worker must not expose a workers.dev hostname'
print('Public domain, indexing and sitemap checks passed.')
