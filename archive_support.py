"""Offline loading and conservative sanitisation of attributed reference snapshots."""
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'archive'
DASHES = str.maketrans({c: '-' for c in '\u2010\u2011\u2012\u2013\u2014\u2015\u2212'})

def normalise(value):
    return value.translate(DASHES)

def words(value):
    return len(re.findall(r"\b[\w'-]+\b", value, flags=re.UNICODE))

def title_key(value):
    return unquote(value).replace('_', ' ').strip().casefold()

class Reader(HTMLParser):
    """Remove executable content, media embeds and navigation from a source copy."""
    allowed = set('p h2 h3 h4 h5 h6 ul ol li dl dt dd div section span table caption thead tbody tfoot tr th td blockquote q pre code em strong b i u s small sup sub br hr a cite'.split())
    void = {'br', 'hr', 'img', 'meta', 'link', 'input', 'source', 'wbr', 'area', 'embed', 'param', 'col', 'track'}
    skip_tags = {'script', 'style', 'iframe', 'object', 'form', 'button', 'svg', 'math', 'figure', 'audio', 'video', 'noscript', 'map'}
    skip_classes = {'navbox', 'vertical-navbox', 'sidebar', 'metadata', 'ambox', 'hatnote', 'mw-editsection', 'mw-empty-elt', 'sistersitebox', 'shortdescription', 'noprint', 'mw-indicators'}

    def __init__(self, source_url, title_routes):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.routes = title_routes
        self.stack = []
        self.skipping = 0
        self.output = []
        self.text = []
        self.ids = set()
        self.headings = []
        self.heading = None
        self.heading_text = []
        self.paragraph = None
        self.lead = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get('class', '').split())
        blocked = tag in self.skip_tags or bool(classes & self.skip_classes)
        # A source notice remains in the untouched API snapshot; it is not article prose.
        emitted = tag in self.allowed and not self.skipping and not blocked
        if tag not in self.void:
            self.stack.append((tag, emitted, blocked))
            if blocked:
                self.skipping += 1
        if not emitted:
            return
        safe = []
        identifier = attrs.get('id')
        if identifier and identifier not in self.ids:
            self.ids.add(identifier)
            safe.append(('id', 'reference-' + identifier))
        for key in ('lang', 'dir', 'scope'):
            if key in attrs:
                safe.append((key, attrs[key]))
        for key in ('colspan', 'rowspan'):
            if attrs.get(key, '').isdigit() and int(attrs[key]) <= 100:
                safe.append((key, attrs[key]))
        if tag == 'a':
            href = attrs.get('href', '')
            if href.startswith('#'):
                safe.append(('href', '#reference-' + href[1:]))
            elif href:
                resolved = urljoin(self.source_url, href)
                parsed = urlsplit(resolved)
                if parsed.scheme in ('http', 'https') and 'action=edit' not in parsed.query:
                    target = self.routes.get(title_key(parsed.path[6:])) if parsed.netloc == 'en.wikipedia.org' and parsed.path.startswith('/wiki/') else None
                    safe.append(('href', '/articles/' + target + '/' if target else resolved))
                    if not target:
                        safe.extend([('target', '_blank'), ('rel', 'noopener noreferrer')])
        attributes = ''.join(f' {key}="{html.escape(value, quote=True)}"' for key, value in safe)
        self.output.append('<' + tag + attributes + '>')
        if tag in {'p', 'li', 'dt', 'dd', 'h2', 'h3', 'h4', 'tr', 'br'}:
            self.text.append('\n')
        if tag == 'p':
            self.paragraph = []
        if tag in {'h2', 'h3'}:
            self.heading = identifier
            self.heading_text = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.void:
            return
        # MediaWiki produces balanced HTML. Recover conservatively if a wrapper differs.
        index = next((i for i in range(len(self.stack)-1, -1, -1) if self.stack[i][0] == tag), None)
        if index is None:
            return
        closed = self.stack[index:]
        self.stack = self.stack[:index]
        for name, emitted, blocked in reversed(closed):
            if emitted:
                self.output.append('</' + name + '>')
            if blocked:
                self.skipping -= 1
        if tag == 'p' and self.paragraph is not None:
            paragraph = re.sub(r'\s+', ' ', ''.join(self.paragraph)).strip()
            if not self.lead and words(paragraph) > 18:
                self.lead = paragraph
            self.paragraph = None
        if tag in {'h2', 'h3'}:
            label = re.sub(r'\s+', ' ', ''.join(self.heading_text)).strip()
            if self.heading and label:
                self.headings.append(dict(id='reference-' + self.heading, title=label))
            self.heading = None
        if tag in {'p', 'li', 'dt', 'dd', 'h2', 'h3', 'h4', 'tr'}:
            self.text.append('\n')

    def handle_data(self, data):
        if self.skipping:
            return
        value = normalise(data)
        self.output.append(html.escape(value))
        self.text.append(value)
        if self.paragraph is not None:
            self.paragraph.append(value)
        if self.heading is not None:
            self.heading_text.append(value)

    def finish(self):
        for name, emitted, _ in reversed(self.stack):
            if emitted:
                self.output.append('</' + name + '>')
        plain = re.sub(r'[ \t]+', ' ', ''.join(self.text))
        plain = re.sub(r'\n\s*\n+', '\n\n', plain).strip()
        rendered = normalise(''.join(self.output))
        ids = set(re.findall(r' id="([^"]+)"', rendered))
        rendered = re.sub(r' href="#([^"]+)"', lambda m: m.group(0) if m.group(1) in ids else '', rendered)
        return rendered, plain

def load_references():
    path = ARCHIVE / 'references.json'
    if not path.exists():
        return []
    manifest = json.loads(path.read_text(encoding='utf-8'))
    records = manifest['records']
    routes = {title_key(label): r['slug'] for r in records for label in (r['title'], r['requested_title'])}
    articles = []
    for record in records:
        raw = (ARCHIVE / record['raw_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Snapshot checksum mismatch: ' + record['id'])
        source = json.loads(raw)['parse']
        if source['revid'] != record['revision_id']:
            raise ValueError('Snapshot revision mismatch: ' + record['id'])
        reader = Reader(record['source_url'], routes)
        reader.feed(source['text'])
        clean, plain = reader.finish()
        lead = reader.lead or plain[:400]
        summary = ' '.join(lead.split()[:48])
        if len(lead.split()) > 48:
            summary += '...'
        articles.append(dict(
            slug=record['slug'], title=normalise(record['title']), category=record['category'],
            summary=summary, sections=[dict(title='Preserved reference text', text=plain)],
            sources=[record['id']], related=[], image=None, note=None, kind='preserved_reference',
            word_count=words(plain), html=clean, headings=reader.headings, record=record,
        ))
    return articles

def reference_sources(articles):
    return [dict(id=a['record']['id'], title=a['title'], publisher='Wikipedia contributors',
                 url=a['record']['revision_url'], type='Preserved encyclopaedia reference',
                 access='Full text retained locally under CC BY-SA 4.0',
                 checked=a['record']['retrieved_at'][:10], licence='CC BY-SA 4.0',
                 local_url='/articles/' + a['slug'] + '/') for a in articles]

def corpus_metrics(guides, references):
    baseline = json.loads((ROOT / 'data/expansion-baseline.json').read_text())
    editorial_words = sum(words(s['text']) for a in guides for s in a['sections'])
    preserved_words = sum(a['word_count'] for a in references)
    return dict(baseline=baseline, editorial_articles=len(guides), preserved_references=len(references),
                editorial_words=editorial_words, preserved_words=preserved_words,
                total_readable_words=editorial_words+preserved_words,
                expansion_ratio=round((editorial_words+preserved_words)/baseline['editorial_body_words'], 2),
                categories=dict(Counter(a['category'] for a in references)),
                method='Readable article section text, excluding interface and source JSON. Preserved reference text includes its notes and bibliography; original editorial guides are counted separately.')
