"""Comparable encyclopaedia growth measurements, excluding the retained Bible."""
import json
from pathlib import Path
from collections import Counter

def measure(articles):
    baseline = json.loads((Path(__file__).parent / 'data/encyclopaedia-round-two-baseline.json').read_text())
    current = dict(
        articles=len(articles),
        references=sum(a.get('kind') == 'preserved_reference' for a in articles),
        article_body_words=sum(len(s['text'].split()) for a in articles for s in a['sections'])
    )
    return dict(
        baseline=baseline,
        current=current,
        article_factor=round(current['articles'] / baseline['articles'], 3),
        word_factor=round(current['article_body_words'] / baseline['article_body_words'], 3),
        category_entries=dict(Counter(a['category'] for a in articles)),
        method=baseline['method'],
        review_note='Preserved references are externally authored, attributed and licence-labelled. Text volume does not imply independent verification or specialist review.'
    )

def render(heading, h, report):
    before = report['baseline']
    after = report['current']
    rows = ''.join(
        f'<tr><th scope="row">{label}</th><td>{before[key]:,}</td><td>{after[key]:,}</td></tr>'
        for key, label in [
            ('articles', 'Reading entries'),
            ('references', 'Preserved references'),
            ('article_body_words', 'Article body words')
        ]
    )
    largest = max(report['category_entries'].values(), default=1)
    categories = ''.join(
        '<li><span class="expansion-category-label">' + h(name) +
        '</span><span class="expansion-category-track"><span style="width:' +
        str(round(number / largest * 100, 1)) +
        '%"></span></span><strong>' + f'{number:,}' + '</strong></li>'
        for name, number in report['category_entries'].items()
    )
    entry_change = after['articles'] - before['articles']
    word_change = after['article_body_words'] - before['article_body_words']
    return (
        '<main id="main" class="wrap section narrow-page">'
        + heading('THE ENCYCLOPAEDIA / EXPANSION RECORD', 'More knowledge. A visible record.',
                  'Explore the measurable growth of the encyclopaedia, with the underlying figures and limitations kept in view.')
        + '<section class="expansion-dashboard" aria-labelledby="expansion-dashboard-title">'
        + '<div class="expansion-dashboard-heading"><div><span class="eyebrow">THE ARCHIVE IN NUMBERS</span>'
        + '<h2 id="expansion-dashboard-title">A growing body of knowledge.</h2></div>'
        + '<span class="expansion-live"><span aria-hidden="true"></span> Measured from the archive</span></div>'
        + '<div class="expansion-stats">'
        + '<article class="expansion-stat expansion-stat-featured"><span class="expansion-orbit" aria-hidden="true"></span>'
        + '<span class="expansion-stat-icon" aria-hidden="true">&#10022;</span><span class="expansion-stat-label">Article body words</span>'
        + '<strong>' + f'{after["article_body_words"]:,}' + '</strong>'
        + '<p>Measured editorial and preserved reading text, excluding the Bible reader and interface.</p>'
        + '<div class="expansion-feature-meta"><span>+' + f'{word_change:,}' + ' words</span>'
        + '<span>' + f'{report["word_factor"]:.2f}' + 'x the baseline</span></div>'
        + '<a href="/encyclopaedia-growth.json" download>Explore the data <span aria-hidden="true">&#8599;</span></a></article>'
        + '<article class="expansion-stat"><span class="expansion-stat-icon" aria-hidden="true">&#9638;</span>'
        + '<span class="expansion-stat-label">Reading entries</span><strong>' + f'{after["articles"]:,}' + '</strong>'
        + '<p>Editorial entries and preserved references together.</p></article>'
        + '<article class="expansion-stat"><span class="expansion-stat-icon" aria-hidden="true">&#9672;</span>'
        + '<span class="expansion-stat-label">Editorial entries</span><strong>' + f'{after["articles"] - after["references"]:,}' + '</strong>'
        + '<p>Locally authored article introductions and guides.</p></article>'
        + '<article class="expansion-stat"><span class="expansion-stat-icon" aria-hidden="true">&#9830;</span>'
        + '<span class="expansion-stat-label">Preserved references</span><strong>' + f'{after["references"]:,}' + '</strong>'
        + '<p>Externally authored sources, credited and identified.</p></article>'
        + '<article class="expansion-stat"><span class="expansion-stat-icon" aria-hidden="true">&#8599;</span>'
        + '<span class="expansion-stat-label">Growth since baseline</span><strong>' + f'{report["article_factor"]:.2f}' + 'x</strong>'
        + '<p>' + f'{entry_change:+,}' + ' additional reading entries.</p></article>'
        + '</div><div class="expansion-dashboard-footer"><span><strong>'
        + str(len(report['category_entries'])) + '</strong> topic collections</span>'
        + '<span><strong>' + f'{before["articles"]:,}' + '</strong> baseline entries</span>'
        + '<span><strong>' + f'{after["articles"]:,}' + '</strong> current entries</span></div>'
        + '<p class="expansion-caveat">These are coverage and text-volume measures, not measures of historical certainty or peer review.</p>'
        + '</section>'
        + '<div class="prose expansion-detail"><h2>Before and after</h2>'
        + '<p>The same counting method is used for both editions. This table supplies the exact figures behind the dashboard.</p>'
        + '<div class="expansion-table-wrap"><table><thead><tr><th scope="col">Measure</th><th scope="col">Before</th>'
        + '<th scope="col">Now</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        + '<h2>Coverage across the collection</h2>'
        + '<p>Entries per topic in the current edition. Bars are scaled against the largest topic, not against a research-completeness target.</p>'
        + '<ul class="expansion-categories">' + categories + '</ul>'
        + '<h2>What is counted</h2><p>' + h(report['method']) +
        ' Preserved reference text includes its notes and bibliography. This measures available reading volume, not a count of independently verified facts. Source book files, duplicate Bible chapter text and interface copy do not inflate the total.</p>'
        + '<h2>The next chapters, in progress</h2><p>The retained collection expands biographies, women'
        + '&#39;s histories, regional communities, ancient evidence, languages and literature. Some contextual entries concern shared traditions, neighbouring societies or related churches; inclusion does not identify every subject as Assyrian.</p>'
        + '<h2>What still requires people</h2><p>' + h(report['review_note']) +
        ' Preserved references are not substitutes for original research, specialist review, community testimony or permissions for new media. Missing source pages produce no placeholder articles. Revision, author-history and licence links accompany each retained reference.</p>'
        + '<p><a href="/explore/">Browse the expanded encyclopaedia</a> / <a href="/glossary/">Read the introductory glossary</a> / <a href="/encyclopaedia-growth.json" download>Download the comparison data</a></p></div></main>'
    )
