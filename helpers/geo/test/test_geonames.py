from unittest import TestCase
from . import ALL_COUNTRIES_FIXTURE_PATH
from ..geonames import parse_all_countries_file, matching_places
from .. import index_client


class GeonamesTest(TestCase):

    def test_parse_all_countries_file(self):
        row_count = 0
        for row in parse_all_countries_file(ALL_COUNTRIES_FIXTURE_PATH, "temp_index_placeholder_name"):
            row_count += 1
            assert row['_index'] == 'temp_index_placeholder_name'
            assert row['_id']
            assert len(row["_source"]) == 20
        assert row_count == 100

    def test_matching_places(self):
        es = index_client()
        entity = {
            'text': 'Alabama'
        }
        candidates = matching_places(es, entity)
        assert len(candidates) > 0
        name_candidates = [c for c in candidates if c.name_match]
        assert len(name_candidates) > 0
        alternate_name_candidates = [c for c in candidates if c.alternate_name_match]
        assert len(alternate_name_candidates) > 0
        exact_match_candidates = [c for c in candidates if c.exact_match]
        assert len(exact_match_candidates) > 0
