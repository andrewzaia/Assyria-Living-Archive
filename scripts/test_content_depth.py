"""Coverage, source immutability and exact primary text for the content review."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from html import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import ARTICLES
from biblical_content import ARTICLES as BIBLE_ARTICLES
from depth_content import DATA, expand
from content_review import DECISIONS
from bible_pages import passage_panel
from bible_support import load_bible
import case_files


class ContentDepthTests(unittest.TestCase):
    def test_every_original_article_has_one_explicit_decision(self):
        decisions = {x['slug']: x for x in DECISIONS['articles']}
        self.assertEqual(set(decisions), {a['slug'] for a in ARTICLES + BIBLE_ARTICLES})
        self.assertEqual(len(decisions), len(DECISIONS['articles']))
        self.assertEqual({s for s, x in decisions.items() if x['status'] == 'expanded'}, set(DATA))
        self.assertTrue(all(x['reason'].strip() for x in decisions.values()))

    def test_expansion_preserves_input_and_original_anchors(self):
        original = [dict(slug='test', sources=['a'], sections=[dict(title='First', text='Anchored sentence.')])]
        saved = copy.deepcopy(original)
        with patch.dict(DATA, {'test': dict(sources=['b'], sections=[dict(title='New', text='Explanation.')])}):
            result = expand(original)
        self.assertEqual(original, saved)
        self.assertEqual(result[0]['sections'][0], original[0]['sections'][0])
        self.assertEqual(result[0]['sources'], ['a', 'b'])

    def test_every_added_explanation_renders_with_a_source_trail(self):
        from section_evidence import DATA as trails
        articles = {a['slug']: a for a in ARTICLES + BIBLE_ARTICLES}
        for slug, addition in DATA.items():
            article = articles[slug]
            sections = article['sections'][-len(addition['sections']):]
            for section, added in zip(sections, addition['sections']):
                with self.subTest(article=slug, section=section['title']):
                    self.assertIn(added['text'], section['text'])
                    evidence = trails[slug][section['title']]
                    self.assertTrue(evidence.get('sources') or evidence.get('passages'))
                    self.assertTrue(set(evidence.get('sources', [])) <= set(article['sources']))

    def test_case_metadata_is_not_mutated_by_article_expansion(self):
        self.assertTrue(all(len(x['sections']) == 4 for x in case_files.DATA))
        self.assertEqual(sum(len(x['sections']) for x in case_files.DATA), 36)
        for a in ARTICLES:
            if a['slug'] in case_files.BY_SLUG:
                self.assertIsNot(a, case_files.BY_SLUG[a['slug']])

    def test_every_biblical_guide_includes_exact_local_primary_words(self):
        bible = load_bible()
        for a in BIBLE_ARTICLES:
            with self.subTest(article=a['slug']):
                html = passage_panel(a)
                book, chapter, first, last = a['passages'][0]
                self.assertIn('class="scripture-excerpt"', html)
                for verse in range(first, min(last, first + 7) + 1):
                    self.assertIn(escape(bible['verses'][(book, chapter, verse)]['text']), html)
                self.assertNotIn('<iframe', html)

    def test_supplements_are_not_duplicate_filler(self):
        text = [s['text'] for entry in DATA.values() for s in entry['sections']]
        self.assertEqual(len(text), len(set(text)))
        self.assertFalse(any('TODO' in t or 'content coming soon' in t.lower() for t in text))


if __name__ == '__main__':
    unittest.main()
