from unittest import TestCase
from . import ALL_COUNTRIES_FIXTURE_PATH
from ..geonames import parse_all_countries_file, matching_places, by_id
from ..locations import ResolvedLoc
from .. import index_client
from ..geonames import INDEX_NAME


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
        location = ResolvedLoc(**res["_source"])
        assert location.geoname_id == '2635167'
        assert location.admin1_code == '00'
        assert location.country_code == 'GB'
        assert location.feature_class == 'A'
        assert location.feature_code == 'PCLI'
        assert location.population > 0

    def test_europe(self):
        entity = {'text': 'Europe'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].feature_class == 'L'

    def test_exact_country_name(self):
        entity = {'text': 'Italian Republic'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].geoname_id == '3175395'
        entity = {'text': 'United Kingdom of Great Britain and Northern Ireland'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].geoname_id == '2635167'
        entity = {'text': 'Nigeria'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].geoname_id == '2328926'
        entity = {'text': 'French Republic'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].geoname_id == '3175395'

    def test_exact_city_name(self):
        entity = {'text': 'London'}
        locations = matching_places(self._es, entity)
        assert len(locations) > 0
        assert locations[0].geoname_id == '2643743'

    def test_by_id(self):
        loc = by_id(self._es, '2643743')
        assert loc['geonameid'] == '2643743'
        assert loc['name'] == 'London'
        assert loc['admin1_code'] == 'ENG'
        assert loc['country_code'] == 'GB'
        assert loc['feature_class'] == 'P'
        assert loc['feature_code'] == 'PPLC'
        assert loc['population'] > 0
