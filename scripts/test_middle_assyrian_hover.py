"""Middle Assyrian reading tiles must share Explore's hover and theme behaviour."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from middle_assyrian_page import render
from middle_assyrian_content import ARTICLES

STYLES = (ROOT / "static/styles.css").read_text(encoding="utf-8")
MIDDLE = (ROOT / "static/middle-assyrian.css").read_text(encoding="utf-8")
THEME = (ROOT / "static/theme.css").read_text(encoding="utf-8")
GENERATOR = (ROOT / "generate.py").read_text(encoding="utf-8")


def declarations(styles, selector):
    without_comments = re.sub(r"/\*.*?\*/", "", styles, flags=re.S)
    for selectors, declaration_text in re.findall(r"([^{}]+)\{([^{}]*)\}", without_comments):
        if selector in [item.strip() for item in selectors.split(",")]:
            return {
                key.strip(): value.strip()
                for item in declaration_text.split(";")
                if ":" in item
                for key, value in [item.split(":", 1)]
            }
    raise AssertionError("Missing stylesheet selector: " + selector)


class MiddleAssyrianTileHoverTests(unittest.TestCase):
    def test_hub_has_nine_full_tile_links(self):
        html = render(lambda kicker, title, intro: "<div>Middle Assyrian</div>")
        self.assertEqual(len(ARTICLES), 9)
        self.assertEqual(html.count('class="middle-card"'), len(ARTICLES))
        self.assertEqual(html.count('class="middle-number"'), len(ARTICLES))
        self.assertIn('class="middle-grid"', html)

    def test_hover_and_keyboard_focus_match_explore_motion(self):
        explore = declarations(STYLES, ".article-card:hover")
        middle_hover = declarations(MIDDLE, ".middle-card:hover")
        middle_focus = declarations(MIDDLE, ".middle-card:focus-within")
        for mode in (middle_hover, middle_focus):
            self.assertEqual(mode.get("transform"), explore.get("transform"))
            self.assertEqual(mode.get("box-shadow"), explore.get("box-shadow"))
            self.assertNotIn("background", mode)
            self.assertNotIn("background-color", mode)
        self.assertIn("box-shadow", declarations(MIDDLE, ".middle-card")["transition"])
        self.assertIn("transform", declarations(MIDDLE, ".middle-card")["transition"])

    def test_tile_surfaces_stay_theme_aware_and_text_is_readable(self):
        self.assertEqual(declarations(MIDDLE, ".middle-card").get("background"),
                         declarations(STYLES, ".article-card").get("background"))
        self.assertEqual(declarations(MIDDLE, ".middle-card").get("background"), "var(--white)")
        self.assertIn("--white:#1a2926", THEME)
        self.assertNotIn("#eae9dd", MIDDLE)
        self.assertNotIn("#eae9df", MIDDLE)
        self.assertEqual(declarations(MIDDLE, ".middle-card p").get("color"), "var(--muted)")
        self.assertEqual(declarations(MIDDLE, ".middle-card>a").get("flex"), "1")

    def test_middle_css_is_loaded_after_shared_styles_before_theme(self):
        self.assertIn("middle-assyrian.css", GENERATOR)
        self.assertLess(GENERATOR.index('href="/styles.css"'),
                        GENERATOR.index('{extra}<link rel="stylesheet" href="/theme.css"'))
        self.assertIn('href="/middle-assyrian.css"', GENERATOR)
        self.assertIn(".middle-card", MIDDLE)


if __name__ == "__main__":
    unittest.main()
