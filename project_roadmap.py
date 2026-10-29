"""Maintained, data-driven next-chapters roadmap."""
import json
import re
from html import escape as H
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent / 'data/project-roadmap.json').read_text(encoding='utf-8'))
STATUSES = {'available', 'in-progress', 'planned', 'on-hold'}
REQUIRED = {'foundation', 'navigation', 'scripture', 'encyclopaedia', 'atlas', 'source-trails',
            'claims', 'language', 'community', 'submission', 'governance', 'publication'}


def validate():
    items = DATA['milestones']
    ids = [item['id'] for item in items]
    if DATA.get('schema_version') != 1 or len(set(ids)) != len(ids) or not REQUIRED.issubset(set(ids)):
        raise ValueError('Invalid or undocumented roadmap milestone IDs')
    for item in items:
        if not re.fullmatch(r'[a-z][a-z0-9-]+', item['id']) or item['status'] not in STATUSES:
            raise ValueError('Invalid roadmap milestone status or ID: ' + item['id'])
        if not all(isinstance(item.get(field), str) and item[field].strip() for field in ('title','delivered','next')):
            raise ValueError('Roadmap milestone is incomplete: ' + item['id'])
    return items


def render():
    items = validate()
    cards = []
    for n, item in enumerate(items, 1):
        label = item['status'].replace('-', ' ').upper()
        cards.append('<div id="milestone-' + H(item['id']) + '"><span class="phase">' +
                     str(n).zfill(2) + ' / ' + label + '</span><h3>' + H(item['title']) + '</h3>' +
                     '<p><strong>Delivered:</strong> ' + H(item['delivered']) + '</p>' +
                     '<p><strong>Next:</strong> ' + H(item['next']) + '</p>' +
                     '<span class="roadmap-status">' + H(label) + '</span></div>')
    return '<div class="roadmap">' + ''.join(cards) + '</div>'
