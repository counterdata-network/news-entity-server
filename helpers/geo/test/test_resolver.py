from unittest import TestCase
import os
import json
import helpers.entities as entities
from ..resolver import resolve

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestResolver(TestCase):

    def test_simple_countries(self):
        country_tests = json.load(open(os.path.join(this_dir, 'fixtures', 'simple-countries.json')))
        for c in country_tests[1:2]:
            entity_list = entities.from_text(c['text'], 'en')
            assert len(entity_list) > 0
            geo_entities = [entity for entity in entity_list if entity['type'] in ['GPE', 'NORP', 'LOC']]
            assert len(geo_entities) > 0
            resolved_places = resolve(geo_entities)
            assert len(resolved_places) == 1
            assert resolved_places[0].country_code == c['expected']

    def test_simple(self):
        # get geo entities
        with open(os.path.join(this_dir, 'fixtures', 'sanctions_article.txt')) as f:
            article_text = f.read()
        entity_list = entities.from_text(article_text, 'en')
        assert len(entity_list) > 0
        geo_entities = [entity for entity in entity_list if entity['type'] in ['GPE', 'NORP', 'LOC']]
        assert len(geo_entities) > 0
        # call disambiguate
        candidates = resolve(geo_entities)
        assert len(candidates) > 0
