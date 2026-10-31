"""Check every article has a traceable media candidate without invented licences."""
import unittest
import json
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import article_media
from archive_support import MediaCollector
import generate


class MediaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = []
        self.images = []
        self.references = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "data-article-media" in a:
            self.sections.append(a)
        if tag == "img":
            self.images.append(a)
        if tag == "a" and a.get("href", "").startswith("https://"):
            self.references.append(a["href"])


class ArticleMediaTests(unittest.TestCase):
    def test_every_article_has_an_explicit_media_research_slot(self):
        self.assertGreater(len(generate.ARTICLES), 372)
        for article in generate.ARTICLES:
            with self.subTest(slug=article["slug"]):
                markup = article_media.render(article, generate.SM, generate.REFERENCE_MEDIA)
                parser = MediaParser()
                parser.feed(markup)
                self.assertEqual(len(parser.sections), 1)
                self.assertTrue(parser.sections[0].get("data-media-page"))
                self.assertIn(parser.sections[0].get("data-media-relation"),
                              ("subject", "context", "candidate"))
                self.assertEqual(len(parser.images), 1)
                self.assertTrue(any(link.startswith("https://commons.wikimedia.org/")
                                    for link in parser.references))
                self.assertTrue(any(link.startswith("https://en.wikipedia.org/wiki/")
                                    for link in parser.references))

    def test_retained_source_images_include_captions_and_skip_tiny_icons(self):
        parser = MediaCollector()
        parser.feed(
            '<a href="/wiki/File:Small_icon.png"><img alt="icon" width="20" height="20"></a>'
            '<figure><a href="/wiki/File:Palace_relief.jpg">'
            '<img alt="Palace relief" data-file-width="600" data-file-height="400"></a>'
            '<figcaption>Relief from the northern palace.</figcaption></figure>'
        )
        self.assertEqual(parser.items, [
            {"file": "Palace relief.jpg", "alt": "Palace relief",
             "caption": "Relief from the northern palace."}
        ])

    def test_preserved_source_media_is_extracted_from_original_snapshot(self):
        article = next(a for a in generate.REFERENCES if a["title"] == "Assyria")
        self.assertGreater(len(article["media_candidates"]), 0)
        html = article_media.render(article, generate.SM, generate.REFERENCE_MEDIA)
        parser = MediaParser()
        parser.feed(html)
        self.assertEqual(json.loads(parser.sections[0]["data-media-candidates"]),
                         article["media_candidates"][:8])

    def test_original_reference_title_matches_its_preserved_source(self):
        sample = next(a for a in generate.REFERENCES if a["title"] == "Ashurbanipal")
        title, relation = article_media.wikipedia_title(sample, generate.SM)
        self.assertEqual(title, "Ashurbanipal")
        self.assertEqual(relation, "subject")

    def test_html_escape_prevents_injecting_titles_into_markup(self):
        article = {"slug": "test", "title": '<script>alert("x")</script>',
                   "sources": [], "category": "History & archaeology"}
        markup = article_media.render(article, {})
        self.assertNotIn("<script>", markup)
        self.assertIn("&lt;script&gt;", markup)

    def test_media_audit_distinguishes_slots_from_confirmed_images(self):
        report = article_media.report(generate.ARTICLES, generate.SM, generate.REFERENCE_MEDIA)
        self.assertEqual(report["total_articles"], len(generate.ARTICLES))
        self.assertEqual(report["articles_with_discovery_slots"], len(generate.ARTICLES))
        self.assertGreater(report["articles_with_retained_media_candidates"], 0)
        self.assertEqual(report["licensed_dynamic_images_verified_at_build"], 0)
        self.assertEqual(len(report["coverage"]), len(generate.ARTICLES))
        self.assertEqual(len({row["slug"] for row in report["coverage"]}),
                         len(generate.ARTICLES))
        self.assertFalse(any(row["image_licence_confirmed_at_build"]
                             for row in report["coverage"]))


if __name__ == "__main__":
    unittest.main()
