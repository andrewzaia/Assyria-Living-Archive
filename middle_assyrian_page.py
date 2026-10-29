"""Public Middle Assyrian social-history reading room and method limitations."""
from html import escape as h
from middle_assyrian_content import ARTICLES, validate

def render(heading):
    validate()
    cards = []
    for index, article in enumerate(ARTICLES, 1):
        readings = ' / '.join([str(len(article['sources'])) + ' curated sources', str(len(article['sections'])) + ' original sections'])
        if article['passages']:
            readings += ' / ' + str(len(article['passages'])) + ' comparison passages'
        cards.append(
            '<li class="middle-card"><a href="/articles/' + h(article['slug']) + '/">' +
            '<span class="middle-number">STUDY ' + str(index).zfill(2) + ' / ' + str(len(ARTICLES)).zfill(2) + '</span>' +
            '<h2>' + h(article['title']) + '</h2><p>' + h(article['summary']) + '</p>' +
            '<span class="middle-meta">' + h(readings) + '</span></a></li>'
        )
    return (
        '<main id="main" class="wrap section middle-room">' +
        heading('HISTORY / PEOPLE AND EVERYDAY LIFE', 'An empire built by people.',
                'Nine source-mapped guides exploring Middle Assyrian institutions, families, food, law, labour, religion and exchange.') +
        '<section class="middle-intro" aria-label="Research approach"><p><strong>Look beyond royal announcements.</strong> ' +
        'Clay tablets, laws, seal impressions, excavated contexts and specialist editions help reconstruct some of the work and relationships ' +
        'that sustained Middle Assyrian communities. But official documents are selective. A law is a prescription, not proof of enforcement; ' +
        'a list is an administrative record, not an entire person\'s life.</p>' +
        '<p>These studies focus on Middle Assyria, with attention to Aššur, Dūr-Katlimmu and nearby provincial settlements. ' +
        'The Bible remains primary for statements about its own narrative and teachings. Comparisons involving Genesis, Deuteronomy or Kings ' +
        'are carefully labelled and do not turn a later biblical reference into contemporary proof for a thirteenth-century tablet.</p></section>' +
        '<section class="middle-collection" aria-labelledby="middle-studies"><div class="middle-header"><span class="eyebrow">ORIGINAL RESEARCH GUIDES</span>' +
        '<h2 id="middle-studies">Nine paths into the Middle Assyrian world.</h2></div>' +
        '<ol class="middle-grid">' + ''.join(cards) + '</ol></section>' +
        '<section class="middle-method" aria-labelledby="middle-method-heading"><span class="eyebrow">READ THE EVIDENCE</span>' +
        '<h2 id="middle-method-heading">How much can a tablet really tell us?</h2>' +
        '<p>Every chapter includes section-by-section source trails tied to the archive\'s <a href="/about/evidence/">Evidence Register</a>. ' +
        'Individually anchored propositions appear in the <a href="/about/evidence/#claim-register-title">independent review queue</a>. ' +
        'The main <a href="/sources/">Source Library</a> links institutional catalogues and scholarly research. ' +
        'The <a href="/dossiers/">Bible and historical artefact dossiers</a> deal chiefly with later Assyrian rulers and are a separate period.</p>' +
        '<p>The texts are original editorial introductions, not a newly excavated archive or completed Assyriological peer review. ' +
        'The available documents privilege scribes, officials, estates and courts; children, marginalised workers and private beliefs ' +
        'often remain difficult to recover without specialist scrutiny.</p></section></main>'
    )
