"""Verify citation integrity and safe paragraph rendering for revised articles."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import generate
import section_evidence
from middle_assyrian_content import ARTICLES

SOURCES = generate.SOURCES


class ArticleCitationTests(unittest.TestCase):
    def test_paragraphs_escape_content_and_keep_breaks(self):
        self.assertEqual(generate.article_paragraphs('First <script>.\n\nSecond & final.'),
                         '<p>First &lt;script&gt;.</p><p>Second &amp; final.</p>')

    def test_all_revised_sections_have_resolvable_citations(self):
        for article in ARTICLES:
            refs = {source: i + 1 for i, source in enumerate(article['sources'])}
            for section in article['sections']:
                with self.subTest(article=article['slug'], section=section['title']):
                    html = generate.section_reading_trail(article, section, refs)
                    self.assertIn('class="section-citations"', html)
                    mapped = section_evidence.trail(article, section['title'])
                    for source in mapped['sources']:
                        self.assertIn('href="#source-' + source + '"', html)
                    for locator in mapped.get('locations', {}).values():
                        self.assertIn(generate.H(locator), html)

    def test_locator_cannot_refer_to_an_uncited_source(self):
        original = section_evidence.DATA
        try:
            changed = copy.deepcopy(original)
            section = next(iter(changed[ARTICLES[0]['slug']].values()))
            section['locations']['nonexistent-source'] = 'p. 1'
            section_evidence.DATA = changed
            with self.assertRaisesRegex(ValueError, 'Invalid citation locator'):
                section_evidence.validate(generate.EDITORIAL_ARTICLES, SOURCES)
        finally:
            section_evidence.DATA = original

    def test_existing_guides_retain_standard_trails(self):
        article = next(a for a in generate.EDITORIAL_ARTICLES if a['slug'] == 'assyrian-identity')
        refs = {source: i + 1 for i, source in enumerate(article['sources'])}
        html = generate.section_reading_trail(article, article['sections'][0], refs)
        self.assertIn('class="section-reading-trail"', html)

    def test_biblical_references_stay_separate_and_legal_provisions_have_locations(self):
        article = next(a for a in ARTICLES if a['slug'] == 'middle-assyrian-women-and-law')
        mapped = section_evidence.DATA[article['slug']]
        veil = mapped['Veiling as a marker of status']
        self.assertIn('MAL A 40-41', veil['locations']['fales-veil-assyrian'])
        biblical = mapped['Marriage and remarriage in Deuteronomy']
        self.assertEqual(biblical['passages'], [['DEU', 24, 1, 4]])
        self.assertNotIn('passages', veil)


if __name__ == '__main__':
    unittest.main()
