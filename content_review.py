"""Route inventory and explicit editorial decisions, separate from historical peer review."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
DECISIONS = json.loads((ROOT / 'data/content-review-decisions.json').read_text(encoding='utf-8'))
PURPOSES = {
 'index.html': 'Introduces the collection with explanations and routes into history, language and living culture.',
 'explore/index.html': 'Searchable and filterable collection index with summaries and local article routes.',
 'reading-list/index.html': 'Local saved-reading utility with instructions; an empty saved list is an intentional state.',
 'about/index.html': 'Explains the project, scope, statistics and maintained Next Chapters roadmap.',
 'about/expansion/index.html': 'Explains collection growth, baselines and the difference between original and preserved content.',
 'about/evidence/index.html': 'Explains source relationships, section traceability and pending claim review.',
 'glossary/index.html': 'Provides definitions and linked local explanations of relevant terms.',
 'languages/index.html': 'Provides a local letter reference and explanations of language, script and learning resources.',
 'heritage/index.html': 'Explains public heritage records, preservation practice and contributor rights.',
 'governance/index.html': 'Explains corrections, editorial responsibility and the revision record.',
 'stewardship/index.html': 'Explains preservation, recovery and the limits of integrity checks.',
 'audit/index.html': 'Explains source metadata and accessibility audit results and their limits.',
 'dossiers/index.html': 'Introduces local historical comparisons and their subject-specific reading routes.',
 'middle-assyrian/index.html': 'Introduces nine substantive local studies of institutions and everyday life.',
 'case-files/index.html': 'Introduces accessioned objects with provenance, summaries and local explanatory studies.',
 'text-comparisons/index.html': 'Provides local ancient-text excerpts, translations and explanations of uncertainty.',
 'concordance/index.html': 'Provides searchable terms with context, source relationships and local reading paths.',
 'identity-register/index.html': 'Explains particular name and identity disambiguation cases.',
 'royal-witnesses/index.html': 'Explains particular royal inscription comparisons with biblical passages.',
 'samaria-succession/index.html': 'Provides a staged historical account of Samaria and Assyrian succession.',
 'exile-provinces/index.html': 'Explains exile, settlement and provincial life through specific comparative records.',
 'bible/index.html': 'Introduces the biblical collection, its primary text and thematic local guides.',
 'bible/passages/index.html': 'Provides a local searchable verse index and instructions for its use.',
 'map/index.html': 'Provides an interactive dated historical atlas with local explanations and reconstruction limits.',
 'privacy/index.html': 'Explains data handling, local storage and the current contribution arrangement.',
 'contribute/index.html': 'Explains and provides a local contribution-draft form; it does not imply an active inbox.',
 'sources/index.html': 'Source index with publisher, role, dates and reciprocal local reading links; a bibliography serves a different purpose from an article.',
 'timeline/index.html': 'Explains selected historical stages and links them to local reading and evidence.',
 'credits/index.html': 'Provides attribution, licensing and reuse information.',
 '404.html': 'Explains a missing route and provides a route back into the collection.',
}

class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.skip = 0
        self.text = []
    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.in_main = True
        if tag in {'script', 'style'}: self.skip += 1
    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
        if tag in {'script', 'style'}: self.skip -= 1
    def handle_data(self, data):
        if self.in_main and not self.skip: self.text.append(data)


def build(out, articles):
    by_slug = {a['slug']: a for a in articles}
    original = {a['slug'] for a in articles if a.get('kind') != 'preserved_reference'}
    decisions = {r['slug']: r for r in DECISIONS['articles']}
    if set(decisions) != original or len(decisions) != len(DECISIONS['articles']):
        raise ValueError('Every original article requires one review decision')
    if any(r['status'] not in {'expanded', 'reviewed-retained'} or not r['reason'].strip() for r in decisions.values()):
        raise ValueError('Incomplete review decision')
    routes = []
    for path in sorted(out.rglob('*.html')):
        relative = path.relative_to(out).as_posix()
        html = path.read_text(encoding='utf-8')
        reader = MainText(); reader.feed(html)
        if not ''.join(reader.text).strip():
            raise ValueError('No local main content: ' + relative)
        if re.search(r'<meta[^>]+http-equiv=["\x27]refresh', html, re.I):
            raise ValueError('Unexpected redirect: ' + relative)
        slug = relative.split('/')[1] if relative.startswith('articles/') else None
        if slug in decisions:
            kind, status, reason = 'original-article', decisions[slug]['status'], decisions[slug]['reason']
        elif slug in by_slug:
            kind, status = 'preserved-reference', 'full-local-text-retained'
            reason = 'Complete retained text with original authorship and licence. Not independently re-authored or fact-checked.'
            if 'preserved-text' not in html: raise ValueError('Missing local source text: ' + relative)
        elif relative.startswith('bible/read/'):
            kind, status = 'primary-chapter-reader', 'complete-local-chapter'
            reason = 'Complete local primary chapter, with verse anchors; exact wording checked by Bible validation.'
        else:
            if relative not in PURPOSES: raise ValueError('Route requires purpose review: ' + relative)
            kind, status, reason = 'index-research-or-utility', 'purpose-reviewed', PURPOSES[relative]
        routes.append(dict(path='/' + relative, kind=kind, disposition=status, reason=reason,
                           main_words=len(re.findall(r'\b\w+\b', ' '.join(reader.text)))))
    return dict(schema_version=1, reviewed_on=DECISIONS['reviewed_on'], scope=DECISIONS['scope'],
                route_count=len(routes), kinds=dict(Counter(r['kind'] for r in routes)),
                editorial_dispositions=dict(Counter(r['status'] for r in decisions.values())), routes=routes,
                limitation='Local-text checks and editorial decisions are not independent historical peer review. Word counts are descriptive, not quality thresholds.')
