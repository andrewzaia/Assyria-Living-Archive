"""Regression checks for the source-attributed Assyrian persecution catalogue."""
import json
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from persecution_page import load_records, render


class CatalogueParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.cards = []
        self.links = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, attrs['id']
            self.ids.add(attrs['id'])
        if tag == 'article' and attrs.get('data-ap-id'):
            self.cards.append(attrs['data-ap-id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'img':
            self.images.append(attrs)


class PersecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_records()
        cls.records = cls.data['records']
        cls.markup = render()
        cls.parser = CatalogueParser()
        cls.parser.feed(cls.markup)

    def test_source_ids_dates_and_coordinate_precision(self):
        self.assertEqual(len(self.records), len(set(r['id'] for r in self.records)))
        self.assertGreaterEqual(len(self.records), 148)
        self.assertTrue(all(r['sources'] and r['summary'] for r in self.records))
        self.assertEqual({r['country'] for r in self.records},
                         {'Australia', 'Belgium', 'Georgia', 'Iran', 'Iraq',
                          'Sweden', 'Syria', 'Turkey', 'United States'})
        self.assertLess(min(r['year'] for r in self.records), 1900)
        self.assertGreaterEqual(max(r['year'] for r in self.records), 2026)
        self.assertTrue(all(r.get('scope') for r in self.records))
        self.assertTrue(all(r['sources'] and all(s['url'].startswith('https://')
                       for s in r['sources']) for r in self.records))
        self.assertTrue(any(r['lat'] is None and r['lon'] is None for r in self.records))
        self.assertTrue(all((r['lat'] is None) == (r['lon'] is None)
                            for r in self.records))

    def test_all_records_are_server_rendered_with_direct_references(self):
        self.assertCountEqual(self.parser.cards, [r['id'] for r in self.records])
        self.assertIn('/persecution-records.json', self.parser.links)
        self.assertTrue(all(s['url'] in self.parser.links
                            for r in self.records for s in r['sources']))
        self.assertIn('id="ap-map"', self.markup)
        self.assertIn('id="ap-reset"', self.markup)
        self.assertIn('id="ap-country"', self.markup)
        self.assertIn('id="ap-data"', self.markup)
        self.assertEqual(self.markup.count('Community covered:</strong>'), len(self.records))
        self.assertIn('1843 - 2026', self.markup)
        self.assertIn('United States', self.markup)
        self.assertIn('Vandalism', self.markup)
        self.assertIn('Cultural destruction', self.markup)

    def test_2018_antwerp_source_lead_and_related_cases_are_preserved(self):
        by_id = {r['id']: r for r in self.records}
        self.assertEqual(len(by_id), len(self.records))
        antwerp2018 = by_id['AP-0081']
        self.assertEqual(antwerp2018['year'], 2018)
        self.assertEqual(antwerp2018['country'], 'Belgium')
        self.assertIn('14-15 January', antwerp2018['date'])
        self.assertIn('AP-0081', by_id['AP-0077']['related_ids'])
        self.assertIn('AP-0077', antwerp2018['related_ids'])
        self.assertNotEqual(antwerp2018['place'], by_id['AP-0077']['place'])
        self.assertEqual(by_id['AP-0082']['year'], 2023)
        self.assertEqual(by_id['AP-0082']['country'], 'Belgium')
        self.assertIn('Jette', by_id['AP-0082']['place'])
        self.assertNotIn('AP-0082', by_id['AP-0077'].get('related_ids', []))
        for r in self.records:
            for other in r.get('related_ids', []):
                self.assertIn(other, by_id)
                self.assertIn('#' + other.lower(), self.parser.links)
        self.assertIn('data-ap-related="AP-0081"', self.markup)
        js = (ROOT / 'static/persecution.js').read_text(encoding='utf-8')
        self.assertIn('a[data-ap-related]', js)
        self.assertIn('cards.get(link.dataset.apRelated).hidden', js)

    def test_source_audit_tracks_each_new_entry_and_deferred_leads(self):
        audit = json.loads((ROOT / 'data/persecution-source-audit.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['schema_version'], 1)
        self.assertGreaterEqual(len(audit['sources']), 15)
        by_id = {r['id']: r for r in self.records}
        captured = set()
        for entry in audit['sources']:
            self.assertIn(entry['review_status'], ('reviewed', 'partial'))
            self.assertTrue(entry['notes'] and entry['url'].startswith('https://'))
            self.assertTrue(entry['captured_record_ids'])
            for id_ in entry['captured_record_ids']:
                self.assertIn(id_, by_id)
                self.assertTrue(any(ref['url'] == entry['url'] for ref in by_id[id_]['sources']))
                captured.add(id_)
        self.assertEqual(captured, {r['id'] for r in self.records if int(r['id'][3:]) >= 81})
        self.assertTrue(audit['excluded_or_pending'])
        self.assertTrue(all(e['status'] in ('pending', 'excluded') and e['reason']
                            for e in audit['excluded_or_pending']))
        self.assertTrue(any(e['status'] == 'excluded' for e in audit['excluded_or_pending']))

    def test_new_locally_supported_cases_and_aggregation_are_preserved(self):
        by_id = {r['id']: r for r in self.records}
        self.assertEqual(by_id['AP-0125']['year'], 2005)
        self.assertIn('Mar Giwargis', by_id['AP-0125']['title'])
        self.assertIn('Tel Jumaa', by_id['AP-0146']['title'])
        self.assertEqual(by_id['AP-0146']['country'], 'Syria')
        self.assertIsNone(by_id['AP-0146']['lat'])
        self.assertEqual(by_id['AP-0146']['evidence'], 'reported')
        self.assertTrue(any('Human Rights Watch' in s['title']
                            for s in by_id['AP-0133']['sources']))
        mosul_2010 = [r for r in self.records if 138 <= int(r['id'][3:]) <= 143]
        self.assertEqual(len(mosul_2010), 6)
        self.assertTrue(all(r['year'] == 2010 for r in mosul_2010))
        self.assertTrue(all('AP-0012' in r.get('related_ids', [])
                            for r in mosul_2010))
        self.assertIn('AP-0130', by_id['AP-0046']['related_ids'])
        self.assertNotIn('AP-0130', by_id['AP-0011']['related_ids'])

    def test_world_geography_matches_catalogue_and_unlocated_cases(self):
        from persecution_page import COUNTRY_ALIASES
        features = json.loads((ROOT / 'archive/maps/natural-earth-countries.geojson').read_text(encoding='utf-8'))['features']
        names = {f['properties']['ADMIN'] for f in features}
        for record in self.records:
            self.assertIn(COUNTRY_ALIASES.get(record['country'], record['country']), names)
        js = (ROOT / 'static/persecution.js').read_text(encoding='utf-8')
        self.assertIn("'United States of America' ? 'United States'", js)
        self.assertIn('Number.isFinite(record.lon)', js)
        self.assertIn('Number.isFinite(record.lat)', js)

    def test_media_is_local_and_attributed(self):
        for image in self.parser.images:
            self.assertTrue(image['src'].startswith('/assets/archive-media/'))
            self.assertTrue(image.get('alt'))
        for record in self.records:
            if record.get('media'):
                self.assertIn(record['media']['source_url'], self.parser.links)
                self.assertTrue((ROOT / 'static' / record['media']['file'].lstrip('/')).exists())

    def test_page_is_integrated_with_the_generator_and_navigation(self):
        from navigation import NAV_PATHS, render_navigation
        self.assertIn('/persecution/', NAV_PATHS)
        self.assertIn('aria-current="page"', render_navigation('/persecution/'))
        source = (ROOT / 'generate.py').read_text(encoding='utf-8')
        self.assertIn("write('/persecution/index.html'", source)
        self.assertIn("'/map/', '/persecution/', '/glossary/'", source)
        self.assertIn('/persecution.js', source)
        self.assertIn('/persecution.css', source)

    def test_claim_scope_and_report_count_disclosures_remain_visible(self):
        for phrase in ('not people harmed', 'not a claim that all reports have been independently verified',
                       'coordinates are approximate', 'report counts, not victims'):
            self.assertIn(phrase.lower(), self.markup.lower() +
                          (ROOT / 'static/persecution.js').read_text(encoding='utf-8').lower())
        self.assertNotIn('<img src="http', self.markup)


if __name__ == '__main__':
    unittest.main()
