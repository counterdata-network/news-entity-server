from unittest import TestCase
from elasticsearch import Elasticsearch
import time
from ..index import create_elasticsearch_index, index_geonames_data
import os

geo_test_basedir = os.path.dirname(__file__)


class IndexTest(TestCase):

    INDEX_NAME = "test_geonames"

    def setUp(self):
        self._es = Elasticsearch([os.getenv("ES_SERVER")])
        create_elasticsearch_index(self._es, self.INDEX_NAME)

    def test_es(self):
        try:
            if not self._es.ping():
                assert False
            else:
                assert True
        except Exception as e:
            assert False

    def test_index_create(self):
        assert self._es.indices.exists(index=self.INDEX_NAME)

    def test_index_geonames_data(self):
        all_countries_fixture_path = os.path.join(geo_test_basedir, "fixtures", "allCountries.txt")
        success, failed = index_geonames_data(self._es, self.INDEX_NAME, all_countries_fixture_path)
        assert success == 100
        assert len(failed) == 0
        # test search by id
        GEONAMES_ID = '3038838'
        res = self._es.get(index=self.INDEX_NAME, id=GEONAMES_ID)
        assert res["_source"]["geonameid"] == GEONAMES_ID
        time.sleep(1)
        # test search by name
        PLACE_NAME = "Costa Verda"
        # search for the matching docs where "name" is PLACE_NAME
        res = self._es.search(index=self.INDEX_NAME, body={
            "query": {
                "match": {
                    "name": PLACE_NAME
                }
            }
        })
        assert len(res['hits']['hits']) == 5
        assert res['hits']['hits'][0]['_source']['geonameid'] == GEONAMES_ID
        time.sleep(1)
        # search for the matching docs where "alternate" is PLACE_NAME
        ALERTNATE_PLACE_ID = '3038886'
        ALERTNATE_PLACE_NAME = "Pic de Tristagne"
        res = self._es.search(index=self.INDEX_NAME, body={
            "query": {
                "match": {
                    "alternatenames": ALERTNATE_PLACE_NAME
                }
            }
        })
        assert len(res['hits']['hits']) == 7
        assert res['hits']['hits'][0]['_source']['geonameid'] == ALERTNATE_PLACE_ID

    def tearDown(self):
        self._es.indices.delete(index=self.INDEX_NAME)
