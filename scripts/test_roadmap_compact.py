"""Keep all About > The Next Chapters cards concise and traceable."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from project_roadmap import DATA, MAX_DELIVERED, MAX_NEXT, render, validate


class CompactRoadmapTests(unittest.TestCase):
    def test_all_milestones_retained_and_summaries_short(self):
        items = validate()
        self.assertEqual(len(items), 25)
        self.assertEqual(items[0]['id'], 'foundation')
        self.assertEqual(items[-1]['id'], 'assyrian-persecution')
        self.assertTrue(all(len(m['delivered']) <= MAX_DELIVERED and
                            len(m['next']) <= MAX_NEXT for m in items))
        self.assertLess(sum(len(m['delivered']) + len(m['next']) for m in items), 6500)
        self.assertEqual({m['status'] for m in items}, {'available', 'in-progress', 'on-hold'})
        self.assertEqual(next(m['status'] for m in items if m['id'] == 'submission'), 'on-hold')

    def test_renderer_retains_each_title_status_and_two_fields(self):
        markup = render()
        self.assertEqual(markup.count('<strong>Delivered:</strong>'), 25)
        self.assertEqual(markup.count('<strong>Next:</strong>'), 25)
        self.assertEqual(markup.count('class="roadmap-status"'), 25)
        for item in DATA['milestones']:
            self.assertIn('id="milestone-' + item['id'] + '"', markup)

    def test_persecution_milestone_tracks_live_catalogue(self):
        counts = json.loads((ROOT / 'static/persecution-records.json').read_text(encoding='utf-8'))
        item = next(m for m in DATA['milestones'] if m['id'] == 'assyrian-persecution')
        self.assertIn(str(len(counts['records'])), item['delivered'])
        self.assertIn('heat map', item['delivered'])
        self.assertIn('Audit', item['next'])


if __name__ == '__main__':
    unittest.main()
