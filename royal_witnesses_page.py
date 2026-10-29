"""Direct reference and Bible comparison cards for named royal source witnesses."""
from html import escape as H


def render(heading, cases, report):
    cards = []
    for case in cases:
        bible_links = "".join('<li><a href="' + H(p["url"], quote=True) + '">' + H(p["label"]) + '</a></li>'
                              for p in case["bible_links"])
        kind = "Royal inscription - edited Akkadian" if case["kind"] == "royal-inscription" else "Royal palace relief - visual object"
        reference = ('<strong>Edition and location:</strong> ' + H(case["edition_id"]) + ' / ' + H(case["lines"])
                     if case["kind"] == "royal-inscription" else
                     '<strong>Museum object:</strong> physical relief, no cuneiform inscription line claimed')
        cards.append('<article class="royal-case" id="witness-' + H(case["id"]) + '">' +
                     '<header><span class="eyebrow">' + H(case["ruler"]) + ' / ' + H(kind) + '</span>' +
                     '<h2>' + H(case["title"]) + '</h2><p>' + H(case["event_date"]) + '</p></header>' +
                     '<div class="royal-two"><section aria-label="Assyrian royal evidence"><h3>Assyrian record</h3>' +
                     '<p class="royal-meta">' + H(case["object_id"]) + '</p><p>' + reference + '</p><p>' +
                     H(case["royal"]) + '</p><a href="' + H(case["source_url"], quote=True) +
                     '" target="_blank" rel="noopener noreferrer">Inspect original edition or museum catalogue</a></section>' +
                     '<section aria-label="Biblical evidence"><h3>Biblical passages</h3><ul>' + bible_links + '</ul><p>' +
                     H(case["scripture"]) + '</p></section></div>' +
                     '<div class="royal-assessment"><div><h3>Shared historical frame</h3><p>' +
                     H(case["shared"]) + '</p></div><div><h3>Different assertions</h3><p>' +
                     H(case["difference"]) + '</p></div><div><h3>What remains uncertain</h3><p>' +
                     H(case["uncertainty"]) + '</p></div></div>' +
                     '<footer><span>Classification: ' + H(case["status"].replace("-", " ")) +
                     ' / editorial analysis, specialist review pending</span><a href="/articles/' +
                     H(case["article"]) + '/">Read the fuller research dossier</a></footer></article>')
    index = "".join('<li><a href="#witness-' + H(c["id"]) + '">' + H(c["title"]) + '</a></li>' for c in cases)
    return ('<main id="main" class="wrap section royal-room">' +
            heading("RESEARCH / ORIGINAL ROYAL RECORDS", "Two witnesses. One careful comparison.",
                    "Explore six source-bound comparisons of the royal records of Shalmaneser III, Sargon II and Sennacherib with Scripture.") +
            '<div class="royal-intro"><p><strong>The Bible is primary for the biblical narrative.</strong> '
            'An Assyrian inscription is primary for the words and claims that its ruler commissioned. '
            'They are independent and differently motivated witnesses, not substitutes for one another.</p><p>' +
            str(report["comparisons"]) + ' curated comparisons / ' + str(report["inscription_comparisons"]) +
            ' source-edition cases / ' + str(report["museum_comparisons"]) + ' accessioned relief case / ' +
            str(report["bible_routes"]) + ' exact biblical reading routes. No local reproduction of scholarly translation text '
            'or unverified new cuneiform readings. All editorial conclusions remain pending independent specialist review.</p></div>' +
            '<nav class="royal-index" aria-label="Royal witness comparisons"><h2>Compare the evidence</h2><ol>' + index +
            '</ol></nav><div class="royal-cases">' + "".join(cards) + '</div>' +
            '<section class="royal-method"><h2>Read the conflict, not just the agreement</h2>'
            '<p>The Hezekiah tribute sources name the same gold figure but report different silver amounts. '
            'This register preserves both numbers rather than inventing a reconciliation. The account of Jerusalem also has '
            'distinct claims and silences that neither source resolves on its own. Check the '
            '<a href="/identity-register/">name and identity register</a>, '
            '<a href="/dossiers/">historical evidence dossiers</a> and '
            '<a href="/governance/">review requirements</a>.</p></section></main>')
