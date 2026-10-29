"""Language heritage hub with Unicode-vetted script identifiers and attributed listening routes."""
import json
import re
import unicodedata
from html import escape as h
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent / 'data/syriac-letters.json').read_text(encoding='utf-8'))
LETTERS = [0x0710,0x0712,0x0713,0x0715,0x0717,0x0718,0x0719,0x071A,0x071B,0x071D,
           0x071F,0x0720,0x0721,0x0722,0x0723,0x0725,0x0726,0x0728,0x0729,0x072A,0x072B,0x072C]


def validate(articles, sources):
    known_articles = {item['slug'] for item in articles}
    known_sources = {item['id'] for item in sources}
    if DATA.get('schema_version') != 1 or not DATA.get('scope'):
        raise ValueError('Invalid language hub metadata')
    if len(DATA.get('letters', [])) != 22:
        raise ValueError('The Unicode character list must contain exactly 22 core Syriac letters')
    for letter, cp in zip(DATA['letters'], LETTERS):
        if letter['codepoint'] != 'U+' + format(cp, '04X') or letter['character'] != chr(cp):
            raise ValueError('Incorrect Unicode character: ' + str(letter))
        if letter['unicode_name'] != unicodedata.name(chr(cp)):
            raise ValueError('Incorrect official Unicode name: ' + letter['codepoint'])
    for name, ids, known in [
        ('reading_routes', DATA['reading_routes'], known_articles),
        ('recording_sources', DATA['recording_sources'], known_sources),
        ('script_sources', DATA['script_sources'], known_sources),
    ]:
        if not ids or len(set(ids)) != len(ids) or not set(ids) <= known:
            raise ValueError('Unknown or repeated language hub entry in ' + name)
    if DATA['unicode_source'] not in known_sources:
        raise ValueError('Missing Unicode name-list source')
    if DATA['unicode_source'] not in {a['id'] for a in sources if a['url'].startswith('https://www.unicode.org/')}:
        raise ValueError('Unicode name list must use its original publisher')
    return len(DATA['letters'])


def render(heading, articles, sources):
    validate(articles, sources)
    article_index = {a['slug']: a for a in articles}
    source_index = {s['id']: s for s in sources}
    tiles = []
    for letter in DATA['letters']:
        tiles.append(
            '<li class="lang-letter"><span class="lang-glyph" lang="syc" dir="rtl">' +
            h(letter['character']) + '</span><span class="lang-letter-name">' +
            h(letter['unicode_name'].replace('SYRIAC LETTER ', '').title()) +
            '</span><code>' + h(letter['codepoint']) + '</code></li>'
        )
    guides = []
    for slug in DATA['reading_routes']:
        article = article_index[slug]
        guides.append('<li><a href="/articles/' + h(slug) + '/"><strong>' + h(article['title']) +
                      '</strong><span>' + h(article['summary']) + '</span></a></li>')
    script_links = []
    for source_id, description in zip(DATA['script_sources'], (
        'Early Estrangela manuscript hands',
        'Serto forms and mixed hands',
        'East Syriac forms and marks',
    )):
        source = source_index[source_id]
        script_links.append('<li><a href="' + h(source['url'], quote=True) +
            '" target="_blank" rel="noopener">' + h(description) + '</a>' +
            '<small>Hill Museum & Manuscript Library / HMML School</small></li>')
    listening = []
    for source_id, label, note in [
        ('nena-urmi', 'Urmi, Christian', 'Christian Urmi fieldwork; recorded stories and grammatical description'),
        ('nena-alqosh', 'Alqosh', 'Locality-labelled narratives and linguistic analysis'),
        ('nena-ankawa', 'Ankawa', 'Locality-labelled oral account and grammatical features'),
    ]:
        source = source_index[source_id]
        listening.append('<li><strong>' + h(label) + '</strong><p>' + h(note) +
            '</p><a href="' + h(source['url'], quote=True) +
            '" target="_blank" rel="noopener">Listen with Cambridge NENA</a></li>')
    unicode_url = h(source_index[DATA['unicode_source']]['url'], quote=True)
    return (
        '<main id="main" class="wrap section narrow-page language-hub">' +
        heading('LANGUAGE & HERITAGE / READING ROOM', 'Many voices. Many written histories.',
                'Follow the evidence for Akkadian, Syriac and living Neo-Aramaic without confusing their periods, dialects or writing traditions.') +
        '<div class="language-intro prose"><h2>Start with the distinction.</h2>' +
        '<p><strong>Akkadian</strong> is an ancient Mesopotamian language with Assyrian and Babylonian varieties. ' +
        '<strong>Classical Syriac</strong> belongs to the Aramaic language tradition and developed a large literary history. ' +
        '<strong>Sureth and Surayt</strong> refer to living Neo-Aramaic traditions with their own local varieties. ' +
        'A shared script, a church tradition or a community name does not make these historically distinct forms interchangeable.</p>' +
        '<p>Use the linked studies below to check chronology, locality and source roles. No audio is generated on this site, ' +
        'and no displayed letter should be taken as a verified pronunciation.</p></div>' +
        '<section class="language-section" aria-labelledby="language-guide-heading"><div class="language-section-head">' +
        '<span class="eyebrow">ORIGINAL EDITORIAL GUIDES</span><h2 id="language-guide-heading">Find a research path.</h2></div>' +
        '<ul class="language-guides">' + ''.join(guides) + '</ul></section>' +
        '<section class="language-section" aria-labelledby="language-alphabet-heading"><div class="language-section-head">' +
        '<span class="eyebrow">UNICODE REFERENCE / NOT PRONUNCIATION</span>' +
        '<h2 id="language-alphabet-heading">The 22 core Syriac letters.</h2></div>' +
        '<p class="language-note">' + h(DATA['scope']) + ' ' +
        '<a href="' + unicode_url + '" target="_blank" rel="noopener">Official Unicode name list</a>.</p>' +
        '<ol class="language-letters">' + ''.join(tiles) + '</ol>' +
        '<details class="language-explainer"><summary>Why can the same letter look different?</summary>' +
        '<p>Unicode encodes the character, not a manuscript-era calligraphic hand. Fonts and writing conventions give a letter ' +
        'different forms in Estrangela, Serto and East Syriac traditions. Actual manuscripts require dated examples and specialist ' +
        'palaeographic comparison. A device without Syriac font support may display empty boxes or incorrect joins.</p></details></section>' +
        '<section class="language-section" aria-labelledby="language-manuscripts-heading"><div class="language-section-head">' +
        '<span class="eyebrow">SCRIPT HISTORY / MANUSCRIPT EXAMPLES</span>' +
        '<h2 id="language-manuscripts-heading">Study the hands in context.</h2></div>' +
        '<ul class="language-source-links">' + ''.join(script_links) + '</ul>' +
        '<p class="language-note">These links open the custodians\' teaching resources. The archive does not reproduce ' +
        'their manuscript photographs or claim rights to redistribute them.</p></section>' +
        '<section class="language-section" aria-labelledby="language-audio-heading"><div class="language-section-head">' +
        '<span class="eyebrow">REAL RECORDED VOICES / EXTERNAL LINKS</span>' +
        '<h2 id="language-audio-heading">Listen to named local varieties.</h2></div>' +
        '<ul class="language-audio-links">' + ''.join(listening) + '</ul>' +
        '<p class="language-note">The Cambridge NENA records identify distinct documented varieties and speakers. ' +
        'The linked recordings and transcripts remain on the provider website under its access terms. ' +
        'They are neither downloaded nor presented as a universal Assyrian pronunciation standard.</p></section>' +
        '<div class="language-bottom prose"><h2>What still needs specialist participation?</h2>' +
        '<p>Locally reviewed transcriptions, permission-cleared audio, speaker and locality metadata, ' +
        'dialect-specific transliteration keys, and published corrections. These are named future research tasks, ' +
        'not features claimed to be complete. <a href="/about/#next-chapters">Follow the Next Chapters roadmap</a>.</p></div></main>'
    )
