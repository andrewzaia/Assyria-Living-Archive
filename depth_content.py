"""Original explanations supplement existing articles without altering source records."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data/article-depth-expansions.json').read_text(encoding='utf-8'))


def expand(articles):
    result = copy.deepcopy(articles)
    for article in result:
        entry = DATA.get(article['slug'])
        if not entry:
            continue
        for source in entry['sources']:
            if source not in article['sources']:
                article['sources'].append(source)
        if entry.get('integration') == 'within-existing':
            for section, addition in zip(article['sections'][-2:], entry['sections']):
                section['text'] += '\n\n' + addition['text']
        else:
            article['sections'].extend(copy.deepcopy(entry['sections']))
        article['updated'] = '2026-10-30'
        article['inline_scripture'] = entry.get('inline_scripture', False)
    return result
