"""Automated accessible-markup smoke checks on representative site journeys.

This is not a WCAG conformance audit. Manual screen-reader, keyboard-only,
touch target, contrast, zoom and Syriac shaping tests remain necessary.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "/", "/explore/", "/map/", "/languages/", "/heritage/", "/governance/",
    "/stewardship/", "/bible/", "/bible/passages/", "/reading-list/",
    "/contribute/", "/sources/", "/about/", "/glossary/", "/middle-assyrian/", "/case-files/", "/text-comparisons/", "/articles/reading-cuneiform-transliteration/",
)


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.skip = []
        self.mains = 0
        self.main_id = False
        self.h1s = 0
        self.ids = set()
        self.labels = set()
        self.controls = []
        self.buttons = []
        self.button_stack = []
        self.label_depth = 0
        self.images_missing_alt = 0
        self.search_dialog_label = False
        self.nav_toggle = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "main":
            self.mains += 1
            self.main_id |= a.get("id") == "main"
        if tag == "h1":
            self.h1s += 1
        if a.get("id"):
            if a["id"] in self.ids:
                raise ValueError("duplicate id: " + a["id"])
            self.ids.add(a["id"])
        if tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.labels.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") != "hidden":
            self.controls.append((tag, a, self.label_depth > 0))
        if tag == "button":
            self.button_stack.append({"attributes": a, "text": []})
        if tag == "img" and "alt" not in a:
            self.images_missing_alt += 1
        if tag == "a" and a.get("class", "").split().count("skip"):
            self.skip.append(a.get("href"))
        if tag == "dialog" and a.get("id") == "search-dialog":
            self.search_dialog_label = a.get("aria-labelledby") == "search-title"
        if tag == "button" and "menu-toggle" in a.get("class", "").split():
            self.nav_toggle = a.get("aria-expanded") == "false" and a.get("aria-controls") == "mobile-site-nav"

    def handle_data(self, data):
        if self.button_stack:
            self.button_stack[-1]["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "button" and self.button_stack:
            self.buttons.append(self.button_stack.pop())
        if tag == "label" and self.label_depth:
            self.label_depth -= 1


def audit(path, site):
    html = (site / "index.html") if path == "/" else (site / path.lstrip("/") / "index.html")
    if not html.is_file():
        return [path + ": missing HTML page"]
    scan = Inspector()
    try:
        scan.feed(html.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [path + ": " + str(exc)]
    issues = []
    if scan.lang != "en-AU": issues.append("missing Australian English document language")
    if scan.skip != ["#main"]: issues.append("missing skip-to-content route")
    if scan.mains != 1 or not scan.main_id: issues.append("missing unique main landmark")
    if scan.h1s != 1: issues.append("expected one top-level heading")
    if scan.images_missing_alt: issues.append(str(scan.images_missing_alt) + " images missing alt attribute")
    if not scan.search_dialog_label or "search-title" not in scan.ids: issues.append("search dialog missing title relationship")
    if not scan.nav_toggle or "mobile-site-nav" not in scan.ids: issues.append("mobile navigation lacks disclosure state")
    for tag, a, nested in scan.controls:
        if nested or a.get("aria-label") or a.get("aria-labelledby") or (a.get("id") in scan.labels):
            continue
        issues.append(tag + " missing accessible label: " + str(a.get("id") or a.get("name") or "anonymous"))
    for button in scan.buttons:
        a = button["attributes"]
        if a.get("aria-label") or a.get("aria-labelledby") or a.get("title") or "".join(button["text"]).strip():
            continue
        issues.append("button missing accessible name: " + str(a.get("id") or a.get("class") or "anonymous"))
    return [path + ": " + issue for issue in issues]


def run(site):
    issues = []
    for path in PAGES:
        issues.extend(audit(path, site))
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    problems = run(args.site)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"Accessible-markup smoke checks passed for {len(PAGES)} representative pages; manual WCAG testing remains outstanding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
