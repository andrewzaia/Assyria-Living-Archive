"""Accessible source-linked original language and translation-comparison reading room."""
from html import escape as H
from case_files import DATA as CASES
from text_comparisons import BY_SLUG, DATA, render_lines


def render(heading):
    sections=[]
    for index, case in enumerate(CASES,1):
        rec=BY_SLUG[case["slug"]]
        status=("Short edition excerpts" if rec["status"]=="excerpted" else "No verified line edition")
        sections.append(
            '<li class="text-room-item" id="comparison-' + H(case["slug"]) + '"><details' +
            (' open' if index==1 else '') + '><summary><span class="text-room-number">' +
            str(index).zfill(2) + ' / ' + H(status) + '</span><strong>' +
            H(case["title"]) + '</strong><span class="text-room-edition">' +
            H(case["edition"]) + '</span></summary><div class="text-room-content">' +
            '<p class="text-room-scope"><strong>Evidence scope:</strong> ' +
            H(rec["editorial_scope"]) + '</p>' + render_lines(case,include_heading=False) +
            '<p class="text-room-article"><a href="/articles/' + H(case["slug"]) +
            '/">Read the full archaeological case file</a></p></div></details></li>'
        )
    return (
        '<main id="main" class="wrap section text-room">' +
        heading("RESEARCH / TEXT AND TRANSLATION", "The evidence is in the signs.",
                "Compare short credited transliterations, original English reading cues and recorded textual uncertainty for individually identified cuneiform objects.") +
        '<div class="text-room-intro"><p><strong>Side-by-side rather than a seamless translation.</strong> ' +
        'Seven edited Middle Assyrian tablet records supply short, clearly credited sign sequences and editorial reading cues. ' +
        'Two museum or chronicle records remain catalogue-only: they are not given invented cuneiform text, normalized Akkadian or a translation.</p>' +
        '<p>The snippets come from the <a href="https://oracc.museum.upenn.edu/tcma/" rel="noopener noreferrer" target="_blank">ATMAP/TCMA project</a> ' +
        'and are credited to the scholarly editor under the stated CC BY-SA 3.0 edition licence. English cues are newly written ' +
        'editorial summaries, not replacement scholarly translations. See <a href="/articles/reading-cuneiform-transliteration/">the reading methods guide</a> ' +
        'for damage, restoration, uncertain signs and the difference between transliteration and transcription.</p></div>' +
        '<section aria-labelledby="text-room-heading"><span class="eyebrow">VERIFIABLE EDITION ROUTES</span>' +
        '<h2 id="text-room-heading">Read the named line before the interpretation.</h2>' +
        '<ol class="text-room-list">' + ''.join(sections) + '</ol></section>' +
        '<section class="text-room-method" aria-labelledby="text-room-method-heading">' +
        '<h2 id="text-room-method-heading">What this release cannot yet certify.</h2>' +
        '<p>Matching a digital edition and preserving its notation does not mean we independently examined clay signs, confirmed ' +
        'the original-language reading, assessed rival translations or acquired rights to reproduce an entire scholarly edition. ' +
        'All source-specific historical propositions remain pending qualified specialist review. ' +
        '<a href="/about/evidence/">See the evidence register</a>, <a href="/governance/">the editorial standards</a> and ' +
        '<a href="/case-files/">the physical-object collection</a>.</p></section></main>'
    )
