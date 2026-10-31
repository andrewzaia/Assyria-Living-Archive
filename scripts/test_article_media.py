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

    def test_public_domain_requires_consistent_commons_evidence(self):
        info = {
            'mime': 'image/jpeg',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Ashurnasipal_with_official.jpg',
            'thumburl': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/da/test.jpg/1000px-test.jpg',
            'extmetadata': {
                'Credit': {'value': 'ChrisO (Own work)'},
                'LicenseShortName': {'value': 'Public domain'},
                'Copyrighted': {'value': 'False'},
                'UsageTerms': {'value': 'Public domain'},
            },
        }
        rights = eligible(info)
        self.assertIsNotNone(rights)
        self.assertEqual(rights['licence'], 'Public domain')
        self.assertEqual(
            rights['licence_url'],
            'https://commons.wikimedia.org/wiki/Commons:Licensing#Material_in_the_public_domain'
        )
        info['extmetadata']['Copyrighted']['value'] = 'True'
        self.assertIsNone(eligible(info))
        info['extmetadata']['Copyrighted']['value'] = 'False'
        info['extmetadata']['UsageTerms']['value'] = 'All rights reserved'
        self.assertIsNone(eligible(info))
        info['extmetadata']['UsageTerms']['value'] = 'Public domain'
        info['thumburl'] = 'https://untrusted.example/test.jpg'
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

    def test_unsuitable_preserved_figures_fall_back_to_source_lead(self):
        from unittest.mock import patch
        from tempfile import TemporaryDirectory
        from scripts import ingest_media
        article = {'slug': 'sample-person', 'kind': 'preserved_reference',
                   'title': 'Historical person', 'category': 'People & diaspora',
                   'record': {'source_url': 'https://en.wikipedia.org/wiki/Historical_person'},
                   'media_candidates': [{'file': 'Unlicensed.jpg', 'alt': 'Unknown',
                                         'caption': 'Unlicensed image'}]}
        rights = {
            'mime': 'image/jpeg',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Person.jpg',
            'thumburl': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/x.jpg',
            'extmetadata': {'Artist': {'value': 'Photographer'},
                            'LicenseShortName': {'value': 'CC BY 4.0'},
                            'LicenseUrl': {'value': 'https://creativecommons.org/licenses/by/4.0/'}}
        }
        calls = []
        def candidates(titles, _delay):
            calls.append(tuple(titles))
            return {'file:person.jpg': rights} if titles == ['Person.jpg'] else {}
        counters = dict(previously_archived=0, new_article_images=0,
                        lookup_failures=0, without_eligible_licence=0, no_source_images=0)
        library = {'schema_version': 1, 'assets': {}, 'articles': {}}
        with TemporaryDirectory() as tmp:
            with patch.object(ingest_media, 'ROOT', Path(tmp)), \
                 patch.object(ingest_media, 'candidate_info', side_effect=candidates), \
                 patch.object(ingest_media, 'fallback', return_value=[
                     {'file': 'Person.jpg', 'alt': 'Related period portrait',
                      'caption': 'Source lead picture'}]), \
                 patch.object(ingest_media, 'read_url', return_value=b'source-image'), \
                 patch.object(ingest_media, 'optimise', return_value=b'RIFFwebp-test'):
                ingest_media.ingest_article(article, library, 0.5, 2, counters)
            self.assertEqual(len(library['assets']), 1)
            self.assertEqual(len(library['articles']['sample-person']), 1)
            self.assertEqual(counters['new_article_images'], 1)
            self.assertEqual(calls, [('Unlicensed.jpg',), ('Person.jpg',)])

    def test_cached_images_are_reused_without_network_access(self):
        from unittest.mock import patch
        from scripts import ingest_media
        title = 'File:Preserved image.jpg'
        media_id = 'f' * 24
        registry = {'schema_version': 1,
                    'assets': {media_id: {'original_title': title}},
                    'articles': {}}
        article = {'slug': 'a-source', 'kind': 'preserved_reference',
                   'media_candidates': [{'file': 'Preserved_image.jpg',
                                         'alt': 'Historical illustration',
                                         'caption': 'Source photo'}]}
        counters = dict(previously_archived=0, new_article_images=0,
                        lookup_failures=0, no_source_images=0, without_eligible_licence=0)
        with patch.object(ingest_media, 'candidate_info') as candidate_info, \
             patch.object(ingest_media, 'read_url') as read_url, \
             patch.object(ingest_media, 'fallback') as fallback:
            ingest_media.ingest_article(article, registry, 0.5, 2, counters)
        candidate_info.assert_not_called()
        read_url.assert_not_called()
        fallback.assert_not_called()
        self.assertEqual(registry['articles']['a-source'][0]['asset_id'], media_id)

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
