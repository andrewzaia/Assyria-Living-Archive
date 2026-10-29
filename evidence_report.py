"""Traceable source relationships, not a historical accuracy score."""
from collections import defaultdict
from claim_review import build as build_claim_reviews, render as render_claim_reviews


def build(editorial, preserved, sources):
    """Return deterministic, machine-readable article and curated section relationships."""
    from section_evidence import trail
    source_ids = {source['id'] for source in sources}
    usage = defaultdict(list)
    entries = []
    for article in editorial:
        cited = list(article['sources'])
        if not cited or any(source_id not in source_ids for source_id in cited):
            raise ValueError('Missing or unknown sources: ' + article['slug'])
        if len(set(cited)) != len(cited):
            raise ValueError('Repeated source IDs: ' + article['slug'])
        for source_id in cited:
            usage[source_id].append(article['slug'])
        sections = [
            {
                'section_number': index,
                'title': section['title'],
                'source_ids': trail(article, section['title']).get('sources', []),
                'passages': trail(article, section['title']).get('passages', []),
            }
            for index, section in enumerate(article['sections'], 1)
            if trail(article, section['title'])
        ]
        entries.append({
            'slug': article['slug'],
            'title': article['title'],
            'category': article['category'],
            'source_ids': cited,
            'section_count': len(article['sections']),
            'mapped_section_count': len(sections),
            'mapped_sections': sections,
            'biblical_passage_count': len(article.get('passages', [])),
            'source_granularity': 'partial section mapping' if sections else 'article-level',
            'specialist_review': 'not recorded',
        })
    entries.sort(key=lambda entry: entry['title'].casefold())
    mapped = sum(entry['mapped_section_count'] for entry in entries)
    total = sum(entry['section_count'] for entry in entries)
    return {
        'method': 'Article and section bibliographies are distinct from claim-level source mappings. The initial claim queue identifies text and sources without asserting independent historical verification. No specialist review has yet been recorded.',
        'summary': {
            'editorial_entries': len(editorial),
            'preserved_references': len(preserved),
            'source_records': len(sources),
            'sources_cited_by_editorial': len(usage),
            'editorial_source_links': sum(len(entry['source_ids']) for entry in entries),
            'biblical_guides': sum(bool(article.get('bible_group')) for article in editorial),
            'total_sections': total,
            'mapped_sections': mapped,
            'unmapped_sections': total - mapped,
            'articles_with_section_trails': sum(bool(entry['mapped_sections']) for entry in entries),
            'section_source_links': sum(len(section['source_ids']) for entry in entries for section in entry['mapped_sections']),
            'section_bible_passage_links': sum(len(section['passages']) for entry in entries for section in entry['mapped_sections']),
        },
        'claim_reviews': build_claim_reviews(editorial, sources),
        'editorial_entries': entries,
        'source_usage': {source_id: sorted(slugs) for source_id, slugs in sorted(usage.items())},
    }


def render(heading, escape, report):
    summary = report['summary']
    cards = [
        ('Editorial guides', summary['editorial_entries'], 'Original introductions and biblical reading guides'),
        ('Source records', summary['source_records'], 'Bibliography records, including retained external sources'),
        ('Editorial citations', summary['editorial_source_links'], 'Article-to-source relationships, not verified claims'),
        ('Sections with reading trails', summary['mapped_sections'], 'Of ' + str(summary['total_sections']) + ' original editorial sections'),
        ('Preserved texts', summary['preserved_references'], 'Externally authored texts, kept separately from editorial guides'),
        ('Claim review records', report['claim_reviews']['summary']['claim_records'], 'Text-anchored claims queued for independent review'),
    ]
    stats = ''.join(
        '<article class="expansion-stat"><span class="expansion-stat-label">' + escape(title) +
        '</span><strong>' + f'{value:,}' + '</strong><p>' + escape(description) + '</p></article>'
        for title, value, description in cards
    )
    rows = []
    for entry in report['editorial_entries']:
        references = ' '.join(
            '<a href="/sources/#source-' + escape(source_id) + '">' + escape(source_id) + '</a>'
            for source_id in entry['source_ids']
        )
        rows.append(
            '<tr><th scope="row"><a href="/articles/' + escape(entry['slug']) + '/">' +
            escape(entry['title']) + '</a></th><td>' + escape(entry['category']) +
            '</td><td>' + str(len(entry['source_ids'])) + '</td><td>' + str(entry['mapped_section_count']) + '/' + str(entry['section_count']) + '</td><td>' + references + '</td></tr>'
        )
    return (
        '<main id="main" class="wrap section narrow-page">' +
        heading('RESEARCH / EVIDENCE REGISTER', 'Follow the references.', 
                'A transparent index of which editorial guides cite which sources, with the limits of that relationship clearly stated.') +
        '<section class="expansion-dashboard" aria-labelledby="evidence-summary-title"><div class="expansion-dashboard-heading">'
        '<div><span class="eyebrow">MEASURED FROM THE REPOSITORY</span><h2 id="evidence-summary-title">What the archive records.</h2></div>'
        '</div><div class="expansion-stats">' + stats + '</div>'
        '<p class="expansion-caveat">Citation counts measure documentation, not accuracy, research quality or specialist approval.</p></section>'
        '<div class="prose"><h2>Understand the evidence</h2>'
        '<p><strong>Scripture for biblical accounts:</strong> The <a href="/bible/">biblical guides</a> begin with named passages and the local Bible reader. Separate historical or archaeological identifications need their own evidence.</p>'
        '<p><strong>Editorial guides:</strong> Some sections now have curated links to specific Scripture passages and additional sources. Most articles still also use an article-level bibliography. None of these links claims that every statement in a section has been independently verified. No specialist review is recorded.</p>'
        '<p><strong>Preserved texts:</strong> Locally retained external reference material is credited to its original authors. Preservation does not mean that its contents are endorsed, verified or exclusively about Assyrians.</p>'
        '<p><strong>Source dates:</strong> The <a href="/sources/">source library</a> displays each record\'s recorded consultation or retrieval date. It is not a promise that a live external page remains unchanged.</p>'
        '</div>' + render_claim_reviews(report['claim_reviews']) + '<div class="prose"><h2>Editorial source register</h2><p>Use these direct links to inspect a guide and follow the references it names. '
        'The section trail column shows which guides have selected section references. Research, interpretation and specialist review are ongoing; unlinked sections are not automatically considered unsupported or proven.</p></div>'
        '<div class="expansion-table-wrap evidence-register-table"><table><thead><tr><th scope="col">Editorial guide</th>'
        '<th scope="col">Collection</th><th scope="col">Sources</th><th scope="col">Section trails</th><th scope="col">Source IDs</th>'
        '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
        '<div class="prose"><p><a href="/evidence-index.json" download>Download the machine-readable evidence index</a>'
        ' or <a href="/contribute/">prepare a sourced correction</a>. Neither route is a substitute for specialist review.</p></div></main>'
    )
