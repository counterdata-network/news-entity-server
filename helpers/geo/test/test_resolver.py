from unittest import TestCase
import os
import json
import csv
import helpers.entities as entities
import helpers.geo.resolver as resolver

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestResolver(TestCase):

    def test_simple_countries(self):
        country_tests = json.load(open(os.path.join(this_dir, 'fixtures', 'simple-countries.json')))
        for c in country_tests[1:2]:
            entity_list = entities.from_text(c['text'], 'en')
            assert len(entity_list) > 0
            resolved_places = resolver.resolve(entity_list)
            assert len(resolved_places) == 1
            assert resolved_places[0].is_country()
            assert resolved_places[0].country_code == c['expected']

    def test_europe(self):
        article_text = "It is a lovely time of year to visit Europe, even though it can get crowded."
        entity_list = entities.from_text(article_text, 'en')
        assert len(entity_list) == 1
        candidates = resolver.resolve(entity_list)
        assert len(candidates) == 1
        assert candidates[0].geoname_id == '6255148'

    def test_guardian_article(self):
        # https://www.theguardian.com/world/2025/may/20/sanctions-russia-uk-europe-putin-trump-call
        self._test_manually_coded(
            os.path.join(this_dir, 'fixtures', 'sanctions_article.txt'),
            os.path.join(this_dir, 'fixtures', 'sanctions_article.csv')
        )

    def _test_manually_coded(self, filepath, results_filepath):
        with open(os.path.join(this_dir, 'fixtures', filepath)) as f:
            article_text = f.read()
        with open(os.path.join(this_dir, 'fixtures', results_filepath), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            manually_coded = [row for row in reader]
        entity_list = entities.from_text(article_text, 'en')
        assert len(entity_list) > 0
        resolved_locs = resolver.resolve(entity_list)
        resolved_ids = [resolved_loc.geoname_id for resolved_loc in resolved_locs]
        assert len(manually_coded) == len(resolved_ids)
        for item in manually_coded:
            assert item['geoname_id'] in resolved_ids, f"Missing geoname_id: {item['geoname_id']}"

    def test_substitution_map(self):
        subs = resolver._load_custom_substitutions()
        assert len(subs.values()) > 0
        assert 'uk' in subs
        assert subs.get('uk') == 'United Kingdom of Great Britain and Northern Ireland'

    def test_demonyms(self):
        subs = resolver._load_demomnyms()
        assert len(subs.values()) > 0
        assert 'russians' in subs
        assert subs.get('russians') == 'Russian Federation'
        assert 'ukrainian' in subs
        assert subs.get('ukrainian') == 'Ukraine'


"""
    # doesn't work yet
    def test_mass_article(self):
        self._test_manually_coded(
            os.path.join(this_dir, 'fixtures', 'mass_article.txt'),
            os.path.join(this_dir, 'fixtures', 'mass_article.csv')
        )
"""
