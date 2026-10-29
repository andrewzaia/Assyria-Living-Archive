"""Museum and cuneiform edition case-file index, preserving period and genre limits."""
from html import escape as H
from case_files import DATA


def render(heading):
    items = []
    for number, case in enumerate(DATA, start=1):
        category = "Middle Assyrian original" if case["period"] == "middle" else "Later Babylonian comparative record"
        items.append(
            '<li class="case-file-card"><a href="/articles/' + H(case["slug"]) + '/">' +
            '<span class="case-file-index">CASE ' + str(number).zfill(2) + ' / ' + H(category) + '</span>' +
            '<h2>' + H(case["title"]) + '</h2><p>' + H(case["summary"]) + '</p>' +
            '<dl><div><dt>Object</dt><dd>' + H(case["catalogue"]) + '</dd></div>' +
            '<div><dt>Findspot</dt><dd>' + H(case["findspot"]) + '</dd></div>' +
            '<div><dt>Edition</dt><dd>' + H(case["edition"]) + '</dd></div></dl>' +
            '<span class="case-file-more">Read object case file</span></a></li>'
        )
    return (
        '<main id="main" class="wrap section case-files-room">' +
        heading('RESEARCH / INDIVIDUAL OBJECTS', 'Every object has a story. And a limit.',
                'Nine individually identified clay tablets and archaeological objects, with collection numbers, editions, provenances and careful interpretation.') +
        '<div class="case-files-intro"><p><strong>What this adds:</strong> the discussion now begins with a real record that can be looked up by ' +
        'an institutional number, edition or CDLI identifier. Entries explain what the text or catalogue reports, and what it cannot tell us about individual lives. ' +
        'Case files are editorial study guides, not newly discovered inscriptions or independent philological editions.</p>' +
        '<p><strong>Chronology matters:</strong> eight Middle Assyrian objects belong in the social-history research pathway. ' +
        'The Babylonian Chronicle is a <em>later</em> comparative case concerning Nineveh and its destruction. ' +
        'Its surviving copy date differs from the year of the events it describes. The biblical account remains primary for what its own passages say.</p></div>' +
        '<section class="case-files-library" aria-labelledby="case-files-heading"><span class="eyebrow">CATALOGUED EVIDENCE</span>' +
        '<h2 id="case-files-heading">Browse the objects.</h2>' +
        '<ol class="case-files-grid">' + ''.join(items) + '</ol></section>' +
        '<section class="case-files-method" aria-labelledby="case-files-method-heading"><span class="eyebrow">CHECK THE RECORD</span>' +
        '<h2 id="case-files-method-heading">The identifiers travel with every claim.</h2>' +
        '<p>Begin with the catalogue or CDLI ID, the physical object's provenance and date, and the line range of the edited text. ' +
        'Check damage, uncertain signs, archaeological context, translation choices and the difference between an official assertion and an observed outcome. ' +
        'The <a href="/about/evidence/">Evidence Register</a> provides section-level source trails; the ' +
        '<a href="/about/evidence/#claim-register-title">claim review queue</a> documents what still needs qualified independent verification.</p>' +
        '<p><a href="/middle-assyrian/">Explore Middle Assyrian everyday life</a> or ' +
        '<a href="/dossiers/">compare biblical and Assyrian records</a>. ' +
        'See <a href="/governance/">editorial review policy</a> for corrections and specialist sign-off requirements.</p></section></main>'
    )
