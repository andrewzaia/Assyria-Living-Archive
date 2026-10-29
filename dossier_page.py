"""Evidence dossier reading room for biblical-primary, object-linked studies."""
from html import escape as h
from historical_evidence_content import ARTICLES

def render(heading):
    cards = []
    for i, article in enumerate(ARTICLES, 1):
        cited = len(article['sources'])
        verses = len(article['passages'])
        cards.append(
            '<li class="dossier-card"><a href="/articles/' + h(article['slug']) + '/">' +
            '<span class="dossier-number">' + str(i).zfill(2) + ' / DOCUMENTED COMPARISON</span>' +
            '<h2>' + h(article['title']) + '</h2><p>' + h(article['summary']) + '</p>' +
            '<div class="dossier-meta">' + str(len(article['sections'])) +
            ' research sections <span aria-hidden="true">/</span> ' + str(cited) +
            ' source records <span aria-hidden="true">/</span> ' + str(verses) +
            ' biblical reading routes</div></a></li>'
        )
    return (
        '<main id="main" class="wrap section dossier-room">' +
        heading('SCRIPTURE / HISTORICAL RECORDS', 'Compare what each witness says.',
                'Eight original evidence dossiers pair precise biblical passages with identifiable Assyrian monuments, royal records and chronicle sources.') +
        '<div class="dossier-intro"><p><strong>Scripture is primary for biblical testimony.</strong> The reader begins with the chapter and verse, ' +
        'then sees independent material with the object number, publisher and scholarly limitations retained. ' +
        'An inscription may corroborate a named ruler or campaign without confirming every reported detail or theological interpretation.</p>' +
        '<p>All dossiers are newly written introductions; their mapped sections are part of the ' +
        '<a href="/about/evidence/">Evidence Register</a>. ' +
        'Text-anchored claims are tracked in the <a href="/about/evidence/#claim-register-title">independent-review queue</a>, not presented as peer-reviewed conclusions. '
        'See the <a href="/royal-witnesses/">royal inscription comparison room</a> for directly identified edition lines, and the '
        '<a href="/samaria-succession/">fall of Samaria and succession room</a> for the debated eighth-century sequence.</p></div>' +
        '<section class="dossier-section" aria-labelledby="dossier-heading"><span class="eyebrow">EVIDENCE READING ROUTES</span>' +
        '<h2 id="dossier-heading">Eight connected research dossiers.</h2>' +
        '<ol class="dossier-list">' + ''.join(cards) + '</ol></section>' +
        '<div class="dossier-note"><h2>How to check a claim.</h2><p>Read the Bible passage first. Find the named object or corpus. ' +
        'Compare the ancient genres, chronology, translation and missing voices. If a royal inscription or museum record is cited ' +
        'only for context, do not silently treat it as a direct confirmation of a biblical assertion.</p>' +
        '<p><a href="/articles/historical-evidence-methods/">Study the comparison method</a> ' +
        'or <a href="/governance/">read the editorial review and correction policy</a>.</p></div></main>'
    )
