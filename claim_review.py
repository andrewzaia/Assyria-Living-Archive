"""Claim-level evidence queue - source mapping is not historical verification."""
import json
import re
from datetime import date
from html import escape as H
from pathlib import Path
from bible_support import load_bible, reference_label, reference_url

DATA = json.loads((Path(__file__).resolve().parent / 'data/claim-reviews.json').read_text(encoding='utf-8'))
STATUSES = {'awaiting-independent-review', 'under-independent-review', 'independently-reviewed'}
KINDS = {'biblical-text', 'historical-record'}


def build(articles, sources):
    by_slug = {a['slug']: a for a in articles}
    known_sources = {s['id'] for s in sources}
    verses = load_bible()['verses']
    entries, seen = [], set()
    if DATA.get('schema_version') != 1 or not DATA.get('method'):
        raise ValueError('Invalid claim review metadata')
    for item in DATA['claims']:
        ident, slug = item['id'], item['article']
        if not re.fullmatch(r'CL-[0-9]{3,}', ident) or ident in seen:
            raise ValueError('Invalid or repeated claim ID: ' + ident)
        seen.add(ident)
        if slug not in by_slug:
            raise ValueError('Unknown claim article: ' + slug)
        article = by_slug[slug]
        sections = [s['title'] for s in article['sections']]
        if item['section'] not in sections:
            raise ValueError('Unknown claim section: ' + ident)
        source_text = article['sections'][sections.index(item['section'])]['text']
        if len(item['anchor']) < 12 or item['anchor'] not in source_text:
            raise ValueError('Claim anchor missing from source text: ' + ident)
        if not item['claim'].strip() or not item['limitation'].strip() or item['kind'] not in KINDS:
            raise ValueError('Claim is incomplete: ' + ident)
        evidence = item['evidence_sources']
        context = item['context_sources']
        if len(evidence + context) != len(set(evidence + context)):
            raise ValueError('Repeated or ambiguous claim source: ' + ident)
        if any(s not in known_sources or s not in article['sources'] for s in evidence + context):
            raise ValueError('Claim source is not in article bibliography: ' + ident)
        if not item['passages'] and not evidence:
            raise ValueError('Claim has no direct cited evidence: ' + ident)
        if item['kind'] == 'biblical-text' and not item['passages']:
            raise ValueError('Biblical claim has no primary passage: ' + ident)
        if item['kind'] == 'historical-record' and not evidence:
            raise ValueError('Historical claim has no direct evidence source: ' + ident)
        passages_seen = set()
        for ref in item['passages']:
            if not isinstance(ref, list) or len(ref) != 4:
                raise ValueError('Malformed Bible passage: ' + ident)
            book, chapter, first, last = ref
            if not isinstance(book, str) or any(type(n) is not int for n in (chapter, first, last)) or min(chapter, first, last) < 1 or first > last:
                raise ValueError('Invalid Bible passage: ' + ident)
            if tuple(ref) in passages_seen or (book, chapter, first) not in verses or (book, chapter, last) not in verses:
                raise ValueError('Duplicate or missing Bible passage: ' + ident)
            passages_seen.add(tuple(ref))
            if not any(book == b and chapter == ch and low <= first <= last <= high for b, ch, low, high in article.get('passages', [])):
                raise ValueError('Claim passage not recorded in article: ' + ident)
        review = item['review']
        if review['status'] not in STATUSES:
            raise ValueError('Unknown claim review status: ' + ident)
        reviewer, reviewed_on = review.get('reviewer'), review.get('date')
        if review['status'] == 'independently-reviewed':
            if not reviewer or not reviewed_on or not review.get('review_note'):
                raise ValueError('Reviewed status requires named reviewer, date and review note: ' + ident)
            date.fromisoformat(reviewed_on)
        elif reviewer or reviewed_on:
            raise ValueError('Unreviewed claim must not imply completed review: ' + ident)
        entries.append(dict(item, article_title=article['title'], section_number=sections.index(item['section']) + 1))
    return {'method': DATA['method'], 'curated_on': DATA['curated_on'], 'summary': {
        'claim_records': len(entries),
        'awaiting_review': sum(i['review']['status'] == 'awaiting-independent-review' for i in entries),
        'under_review': sum(i['review']['status'] == 'under-independent-review' for i in entries),
        'independently_reviewed': sum(i['review']['status'] == 'independently-reviewed' for i in entries),
    }, 'claims': entries}


def render(report):
    out = ['<section aria-labelledby="claim-register-title"><div class="prose"><h2 id="claim-register-title">Claim-level review register</h2>',
           '<p>' + H(report['method']) + '</p>',
           '<p><strong>' + str(report['summary']['claim_records']) + ' records, ' +
           str(report['summary']['awaiting_review']) + ' awaiting independent review.</strong> These are editorial mappings, not a verified-claim count.</p></div>',
           '<ol class="source-list claim-review-list">']
    for item in report['claims']:
        readings = ['<a href="' + H(reference_url(ref)) + '">' + H(reference_label(ref)) + '</a>' for ref in item['passages']]
        direct = ['<a href="/sources/#source-' + H(s) + '">' + H(s) + '</a>' for s in item['evidence_sources']]
        context = ['<a href="/sources/#source-' + H(s) + '">' + H(s) + '</a>' for s in item['context_sources']]
        label = 'Biblical account' if item['kind'] == 'biblical-text' else 'Historical source record'
        out += ['<li class="source-item" id="claim-' + H(item['id'].lower()) + '"><span class="source-no">' + H(item['id']) + '</span><div>',
                '<span class="eyebrow">' + H(label) + ' / Awaiting specialist review</span><h3>' + H(item['claim']) + '</h3>',
                '<p><a href="/articles/' + H(item['article']) + '/#section-' + str(item['section_number']) + '">' +
                H(item['article_title']) + ' / ' + H(item['section']) + '</a></p>']
        if readings: out.append('<p><strong>Scripture:</strong> ' + ', '.join(readings) + '</p>')
        if direct: out.append('<p><strong>Direct source:</strong> ' + ', '.join(direct) + '</p>')
        if context: out.append('<p><strong>Comparison or context only:</strong> ' + ', '.join(context) + '</p>')
        out.append('<p><strong>Review limitation:</strong> ' + H(item['limitation']) + '</p></div></li>')
    out.append('</ol></section>')
    return ''.join(out)
