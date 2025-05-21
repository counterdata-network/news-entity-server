from unittest import TestCase
from . import ALL_COUNTRIES_FIXTURE_PATH
from ..geonames import parse_all_countries_file, matching_places
from ..locations import ResolvedLoc
from .. import INDEX_NAME, index_client


class GeonamesTest(TestCase):

    def setUp(self):
        self._es = index_client()

    def test_parse_all_countries_file(self):
        row_count = 0
        for row in parse_all_countries_file(ALL_COUNTRIES_FIXTURE_PATH, "temp_index_placeholder_name"):
            row_count += 1
            assert row['_index'] == 'temp_index_placeholder_name'
            assert row['_id']
            assert len(row["_source"]) == 20
        assert row_count == 100

    def test_real_index_has_uk(self):
        UK_GEONAMES_ID = '2635167'
        res = self._es.get(index=INDEX_NAME, id=UK_GEONAMES_ID)
        assert res["_source"]["geonameid"] == UK_GEONAMES_ID
        candidate = ResolvedLoc(**res["_source"])
        assert candidate.geoname_id == '2635167'
        assert candidate.admin1_code == '00'
        assert candidate.country_code == 'GB'
        assert candidate.feature_class == 'A'
        assert candidate.feature_code == 'PCLI'
        assert candidate.population > 0

    def test_europe(self):
        entity = {'text': 'Europe'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].feature_class == 'L'

    def test_exact_country_name(self):
        entity = {'text': 'Italian Republic'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].geoname_id == '3175395'
        entity = {'text': 'United Kingdom of Great Britain and Northern Ireland'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].geoname_id == '2635167'
        entity = {'text': 'Nigeria'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].geoname_id == '2328926'
        entity = {'text': 'French Republic'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].geoname_id == '3175395'

    def test_exact_city_name(self):
        entity = {'text': 'London'}
        candidates = matching_places(self._es, entity)
        assert len(candidates) > 0
        assert candidates[0].geoname_id == '2643743'
