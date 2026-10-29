"""Historical source-comparison room for Samaria and the Assyrian succession."""
from html import escape as H


def render(heading, stages, cases, report, note):
    timeline = "".join(
        '<li><button type="button" data-samaria-filter="' + H(s["id"]) + '" aria-pressed="false">' +
        '<strong>' + H(s["title"]) + '</strong><small>' + H(s["date"]) +
        '</small><span>' + H(s["focus"]) + '</span></button></li>' for s in stages)
    cards = []
    for c in cases:
        bible = "".join('<li><a href="' + H(p["url"], quote=True) + '">' + H(p["label"]) +
                        '</a></li>' for p in c["bible_links"])
        source_kind = "Direct royal inscription edition" if c["mode"] == "edition" else "Specialist synthesis - not a royal inscription"
        edition = ('<p><strong>Edition:</strong> ' + H(c["edition"]) + '</p><p><strong>Passage:</strong> ' +
                   H(c["location"]) + '</p>') if c["mode"] == "edition" else (
                   '<p><strong>Record status:</strong> No surviving siege annal from Shalmaneser V is asserted.</p>')
        cards.append(
            '<article class="samaria-case" id="case-' + H(c["id"]) + '" data-samaria-stage="' + H(c["stage"]) + '">' +
            '<header><span class="eyebrow">' + H(c["year"]) + ' / ' + H(c["actors"]) + '</span>' +
            '<h2>' + H(c["heading"]) + '</h2><p class="samaria-kind">' + H(source_kind) + '</p></header>' +
            '<div class="samaria-witnesses"><section><h3>Assyrian historical witness</h3>' +
            '<p class="samaria-object">' + H(c["object"]) + '</p>' + edition + '<p>' + H(c["royal"]) +
            '</p><a href="' + H(c["source_url"], quote=True) +
            '" target="_blank" rel="noopener noreferrer">Examine the cited edition or specialist study</a></section>' +
            '<section><h3>Scriptural witness</h3><ul>' + bible + '</ul><p>' + H(c["scripture"]) +
            '</p></section></div>' +
            '<div class="samaria-analysis"><div><h3>Shared setting</h3><p>' + H(c["meeting"]) +
            '</p></div><div><h3>Limits of comparison</h3><p>' + H(c["limits"]) +
            '</p></div><div><h3>Outstanding uncertainty</h3><p>' + H(c["uncertainty"]) +
            '</p></div></div><footer><span>Evidence classification: ' + H(c["class"].replace("-", " ")) +
            '. Specialist review outstanding.</span><a href="/articles/' + H(c["article"]) +
            '/">Read full historical dossier</a></footer></article>')
    return (
        '<main id="main" class="wrap section samaria-room">' +
        heading("RESEARCH / NORTHERN ISRAEL", "Samaria: succession, siege and aftermath.",
                "Eight documented source comparisons following tribute, changing kings, the disputed siege and Assyrian resettlement claims.") +
        '<div class="samaria-method"><p><strong>Scripture is the primary record for the biblical account.</strong> '
        'Surviving Assyrian inscriptions independently document what successive kings chose to claim. '
        'Their testimony is not combined into an imaginary single royal eyewitness.</p><p>' +
        H(note) + '</p><p><strong>' + str(report["cases"]) + ' comparisons</strong>, ' +
        str(report["distinct_edition_ids"]) + ' named original editions, ' +
        str(report["bible_routes"]) + ' Bible reading routes. No original-language retranslation or '
        'independently approved historical reconstruction is claimed.</p></div>' +
        '<nav class="samaria-filters" aria-label="Filter historical phases"><h2>Follow the evidence through time</h2>'
        '<div class="samaria-reset"><button type="button" data-samaria-filter="all" aria-pressed="true">All phases</button></div>' +
        '<ol>' + timeline + '</ol><p class="samaria-filter-count" role="status" aria-live="polite">' +
        str(report["cases"]) + ' studies displayed</p></nav>' +
        '<div class="samaria-cases">' + "".join(cards) + '</div>' +
        '<section class="samaria-conclusion"><h2>Why attribution remains disputed</h2>'
        '<p>The biblical record names Shalmaneser V at the siege, whereas Sargon II later claims the capture, deportation '
        'and provincial reorganisation. The two statements must be attributed to their own authors and texts. '
        'A case may describe an earlier siege, a later action, royal appropriation of a predecessor\'s success, '
        'or another reconstruction. These alternatives cannot be settled solely by direct links to the editions.</p>'
        '<p>The Assyrian deportation figures are imperial claims, and the copies do not preserve a single uncontested '
        'number. The archive protects this distinction in its <a href="/about/evidence/">claim-review queue</a>, '
        '<a href="/royal-witnesses/">other royal evidence comparisons</a>, and '
        '<a href="/about/#next-chapters">Next Chapters roadmap</a>.</p></section></main>')
