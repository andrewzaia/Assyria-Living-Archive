"""Offline media validation for every editorial article and preserved reference."""
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import article_media
import generate
from archive_support import MediaCollector
from scripts.ingest_media import eligible, normalise_licence_url


class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.sources = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs.get('src', ''))
        if tag == 'a' and attrs.get('href', '').startswith('https://'):
            self.sources.append(attrs['href'])


class LocalMediaTests(unittest.TestCase):
    def test_every_saved_image_is_verified_and_local(self):
        self.assertTrue(article_media.validate_library(generate.MEDIA_LIBRARY))
        for article in generate.ARTICLES:
            with self.subTest(slug=article['slug']):
                markup = article_media.render(article, generate.MEDIA_LIBRARY)
                parser = ImageParser()
                parser.feed(markup)
                self.assertNotIn('upload.wikimedia.org', markup)
                self.assertNotIn('data-media-candidates', markup)
                self.assertTrue(all(src.startswith('/assets/archive-media/') for src in parser.images))
                self.assertEqual(len(parser.images), len(generate.MEDIA_LIBRARY['articles'].get(article['slug'], [])))

    def test_coverage_report_cannot_count_missing_images(self):
        report = article_media.report(generate.ARTICLES, generate.MEDIA_LIBRARY)
        self.assertEqual(report['total_articles'], len(generate.ARTICLES))
        self.assertEqual(report['articles_without_local_image'] +
                         report['articles_with_any_local_image'], len(generate.ARTICLES))
        self.assertEqual(report['locally_archived_licensed_files'], len(generate.MEDIA_LIBRARY['assets']))
        self.assertEqual(len(report['unillustrated_articles']), report['articles_without_local_image'])

    def test_original_source_metadata_is_not_automatically_a_licence(self):
        preserved = next(a for a in generate.REFERENCES if a['title'] == 'Assyria')
        self.assertGreater(len(preserved.get('media_candidates', [])), 0)
        if not generate.MEDIA_LIBRARY['articles'].get(preserved['slug']):
            self.assertEqual(article_media.render(preserved, generate.MEDIA_LIBRARY), '')

    def test_source_image_extraction_preserves_original_unicode_filename(self):
        collector = MediaCollector()
        collector.feed(
            '<figure><a href="/wiki/File:Relief_%E2%80%93_Ashur.jpg">'
            '<img alt="Royal relief" data-file-width="800" data-file-height="500"></a>'
            '<figcaption>Royal monument.</figcaption></figure>'
        )
        self.assertEqual(collector.items[0]['file'], 'Relief \u2013 Ashur.jpg')
        self.assertEqual(collector.items[0]['caption'], 'Royal monument.')

    def test_wikimedia_licence_links_are_canonical_https(self):
        self.assertEqual(
            normalise_licence_url('//creativecommons.org/licenses/by-sa/4.0/'),
            'https://creativecommons.org/licenses/by-sa/4.0/')
        self.assertEqual(
            normalise_licence_url('http://creativecommons.org/licenses/by/3.0/'),
            'https://creativecommons.org/licenses/by/3.0/')
        self.assertEqual(normalise_licence_url('https://malicious.example/license'), '')
        self.assertEqual(normalise_licence_url('javascript:alert(1)'), '')

    def test_eligible_image_normalises_licence_and_rejects_bad_hosts(self):
        info = {
            'mime': 'image/jpeg',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Assyrian_relief.jpg',
            'thumburl': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/x.jpg',
            'extmetadata': {
                'Artist': {'value': 'Museum photographer'},
                'LicenseShortName': {'value': 'CC BY-SA 4.0'},
                'LicenseUrl': {'value': '//creativecommons.org/licenses/by-sa/4.0/'},
            },
        }
        rights = eligible(info)
        self.assertIsNotNone(rights)
        self.assertEqual(rights['licence_url'],
                         'https://creativecommons.org/licenses/by-sa/4.0/')
        info['extmetadata']['LicenseUrl']['value'] = 'https://malicious.example/foo'
        self.assertIsNone(eligible(info))

    def test_invalid_stored_licence_is_rejected_even_with_local_path(self):
        registry = {
            'schema_version': 1,
            'articles': {},
            'assets': {'0123456789abcdef01234567': {
                'file': '/assets/archive-media/0123456789abcdef01234567.webp',
                'source_url': 'https://commons.wikimedia.org/wiki/File:Test.jpg',
                'creator': 'Test creator',
                'licence': 'CC BY 4.0',
                'licence_url': 'http://creativecommons.org/licenses/by/4.0/',
                'sha256': 'a' * 64,
                'original_title': 'File:Test.jpg',
            }},
        }
        with self.assertRaisesRegex(ValueError, 'Unverified image licence URL'):
            article_media.validate_library(registry, check_files=False)

    def test_source_candidates_never_become_hotlinks(self):
        article = {'slug': 'example', 'category': 'People & diaspora', 'title': 'Person',
                   'kind': 'preserved_reference',
                   'record': {'source_url': 'https://en.wikipedia.org/wiki/Ashurbanipal'},
                   'media_candidates': [{'file': 'Unverified.jpg', 'alt': 'Portrait', 'caption': ''}]}
        self.assertEqual(article_media.render(article, {'schema_version': 1, 'assets': {}, 'articles': {}}), '')
        title, relation = article_media.wikipedia_title(article, {})
        self.assertEqual((title, relation), ('Ashurbanipal', 'subject'))


if __name__ == '__main__':
    unittest.main()
