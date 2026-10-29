"""Navigation coverage and accessible column markup regression tests."""
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from navigation import NAV_COLUMNS, NAV_GROUPS, NAV_PATHS, render_navigation, validate_nav_columns


class NavParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = []
        self.groups = []
        self.columns = []
        self.summaries = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('class') == 'nav-destination':
            self.links.append(attrs.get('href'))
            if attrs.get('aria-current'):
                self.current.append(attrs.get('href'))
        elif tag == 'details':
            self.groups.append(attrs)
        elif tag == 'section' and attrs.get('class') == 'nav-column':
            self.columns.append(attrs.get('aria-label'))
        elif tag == 'summary' and attrs.get('class') == 'nav-trigger':
            self.summaries.append(attrs)


class NavigationTests(unittest.TestCase):
    def parse(self, path):
        p = NavParser()
        p.feed(render_navigation(path))
        return p

    def test_categories_are_complete_and_balanced(self):
        validate_nav_columns()
        self.assertEqual([len(p) for _, p in NAV_COLUMNS['Research']], [5, 4, 4])
        self.assertEqual([len(p) for _, p in NAV_COLUMNS['Explore']], [4, 3])
        for group, cols in NAV_COLUMNS.items():
            all_targets = [x for _, destinations in cols for x in destinations]
            original = [p for name, links in NAV_GROUPS if name == group for _, p, _ in links]
            self.assertCountEqual(all_targets, original)

    def test_every_public_link_present_once(self):
        p = self.parse('/samaria-succession/')
        self.assertCountEqual(p.links, NAV_PATHS)
        self.assertEqual(len(p.links), len(set(p.links)))
        self.assertEqual(len(p.groups), 4)
        self.assertEqual(len(p.summaries), 4)
        self.assertEqual(len(p.columns), 5)
        self.assertEqual(p.current, ['/samaria-succession/'])

    def test_every_navigation_group_has_native_disclosure(self):
        p = self.parse('/about/')
        self.assertEqual([x.get('data-nav-group') for x in p.groups],
                         ['Explore', 'Scripture', 'Research', 'Project'])
        self.assertEqual(p.current, ['/about/'])
        self.assertEqual(p.columns, [
            'Discover', 'Culture and language', 'Sources and texts',
            'Historical comparisons', 'Review and stewardship'])

    def test_no_stale_links_on_unnamed_article_route(self):
        p = self.parse('/articles/samaria-assyrian-chronology/')
        self.assertEqual(p.current, [])
        self.assertEqual(len(p.links), len(NAV_PATHS))

    def test_css_desktop_columns_and_mobile_reflow(self):
        css = (ROOT / 'static/styles.css').read_text(encoding='utf-8')
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))', css)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))', css)
        self.assertIn('.mobile-nav .nav-panel--columns{display:block}', css)
        self.assertIn('.desktop-nav .nav-panel{top:100%', css)

    def test_pointer_hover_is_desktop_only_and_close_is_scoped(self):
        js = (ROOT / 'static/app.js').read_text(encoding='utf-8')
        self.assertIn("$$('details.nav-group')", js)
        self.assertIn("(min-width: 801px) and (hover: hover) and (pointer: fine)", js)
        self.assertIn("group.addEventListener('pointerenter'", js)
        self.assertIn("group.addEventListener('pointerleave'", js)
        self.assertIn("group.open=false;", js)
        self.assertIn("group.contains(document.activeElement)", js)
        self.assertIn("event.key!=='Escape'", js)


if __name__ == '__main__':
    unittest.main()
