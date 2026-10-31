"""Check every article has a traceable media candidate without invented licences."""
import unittest
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import article_media
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
                markup = article_media.render(article, generate.SM)
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
        report = article_media.report(generate.ARTICLES, generate.SM)
        self.assertEqual(report["total_articles"], len(generate.ARTICLES))
        self.assertEqual(report["articles_with_discovery_slots"], len(generate.ARTICLES))
        self.assertEqual(report["licensed_dynamic_images_verified_at_build"], 0)
        self.assertEqual(len(report["coverage"]), len(generate.ARTICLES))
        self.assertEqual(len({row["slug"] for row in report["coverage"]}),
                         len(generate.ARTICLES))
        self.assertFalse(any(row["image_licence_confirmed_at_build"]
                             for row in report["coverage"]))


if __name__ == "__main__":
    unittest.main()
