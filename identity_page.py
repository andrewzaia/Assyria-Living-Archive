"""Publish carefully attributed name comparisons and unresolved identities."""
from html import escape as H


def render(heading, cases, counts):
    cards = []
    for item in cases:
        citations = "".join(
            '<li><a href="' + H(ref["url"], quote=True) + '">' + H(ref["label"]) + '</a>'
            '<span class="identity-kind">' + ("Object record" if ref["kind"] == "object" else "Biblical passage") + '</span>'
            '<p>' + H(ref["note"]) + ' <a href="' + H(ref["term_url"], quote=True) + '">Concordance: '
            + H(ref["term_label"]) + '</a></p></li>'
            for ref in item["evidence"]
        )
        cards.append('<article class="identity-case" id="identity-' + H(item["id"]) + '">'
                     '<div class="identity-case-head"><span class="eyebrow">' + H(item["type"].upper())
                     + ' / ' + H(item["decision"].replace("-", " ")) + '</span>'
                     '<h2>' + H(item["title"]) + '</h2>'
                     '<p class="identity-forms">Indexed forms: ' + H(", ".join(item["forms"])) + '</p>'
                     '<p><strong>Research question:</strong> ' + H(item["question"]) + '</p></div>'
                     '<div class="identity-case-body"><div><h3>What the source supports</h3><p>' + H(item["finding"]) + '</p>'
                     '<h3>What remains unproved</h3><p>' + H(item["limit"]) + '</p>'
                     '<h3>Next verification</h3><p>' + H(item["next"]) + '</p></div>'
                     '<section class="identity-evidence" aria-label="Cited source routes"><h3>Primary reading routes</h3>'
                     '<ul>' + citations + '</ul>'
                     '<p class="identity-pending">Independent specialist review pending</p></section></div></article>')
    index = "".join('<li><a href="#identity-' + H(item["id"]) + '">' + H(item["title"]) + '</a></li>' for item in cases)
    return ('<main id="main" class="wrap section identity-room">' +
            heading("RESEARCH / IDENTITY EVIDENCE", "Names need context, not just a match.",
                    "Source-scoped comparisons distinguish text, language, original records and unresolved historical identities.") +
            '<div class="identity-intro"><p><strong>Identical spelling is not identical identity.</strong> '
            'A tablet findspot, a damaged personal name and a biblical passage have different evidentiary roles. '
            'Each reference below resolves to an existing <a href="/concordance/">concordance</a> citation, '
            'not an invented identification.</p><p>' + str(counts["cases"]) + ' researched cases / ' +
            str(counts["evidence_links"]) + ' checked source links. Scripture is primary for what its text says; '
            'historical object identities require independent material evidence. All cases remain awaiting specialist review.</p></div>' +
            '<nav class="identity-index" aria-label="Identity case index"><h2>Browse research cases</h2><ol>' + index +
            '</ol></nav><div class="identity-cases">' + "".join(cards) + '</div>' +
            '<section class="identity-outro"><h2>Before claiming an identification</h2><p>Require an accession or '
            'edition identifier, a precise passage or line, chronology, provenanced source, manuscript uncertainty and '
            'a documented specialist assessment. Until then, an apparent parallel stays a research lead. '
            'Review the <a href="/about/evidence/">evidence register</a> and '
            '<a href="/governance/">editorial policy</a>.</p></section></main>')
