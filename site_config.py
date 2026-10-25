"""Build settings for a root domain or a GitHub Pages project path."""
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
STATIC = ROOT / 'static'
SETTINGS = json.loads((ROOT / 'site.config.json').read_text(encoding='utf-8'))

SITE_URL = os.environ.get('SITE_URL', SETTINGS.get('site_url', '')).strip().rstrip('/')
BASE_PATH = os.environ.get('BASE_PATH', SETTINGS.get('base_path', '')).strip().rstrip('/')
raw_indexing = os.environ.get('ALLOW_INDEXING', SETTINGS.get('allow_indexing', False))
if isinstance(raw_indexing, bool):
    ALLOW_INDEXING = raw_indexing
elif isinstance(raw_indexing, str) and raw_indexing.lower() in ('true', 'false'):
    ALLOW_INDEXING = raw_indexing.lower() == 'true'
else:
    raise ValueError('allow_indexing / ALLOW_INDEXING must be true or false')

if not re.fullmatch(r'(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*', BASE_PATH):
    raise ValueError('base_path / BASE_PATH must be empty or an absolute path such as /Assyria')
if SITE_URL:
    parsed = urlsplit(SITE_URL)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname
            or parsed.username or parsed.password or parsed.path
            or parsed.query or parsed.fragment or any(c.isspace() for c in SITE_URL)):
        raise ValueError('site_url / SITE_URL must be an origin such as https://example.com, without a path')
if ALLOW_INDEXING and not SITE_URL:
    raise ValueError('Set site_url / SITE_URL before enabling indexing')

def public_url(path):
    return SITE_URL + BASE_PATH + path if SITE_URL else ''

def prefix_html(text):
    """Prefix local root links only. Leave external URLs and fragment links intact."""
    if not BASE_PATH:
        return text
    return re.sub(r'\b(href|src)=([' + '"\'' + r'])/(?!/)',
                  lambda match: match.group(1) + '=' + match.group(2) + BASE_PATH + '/', text)
