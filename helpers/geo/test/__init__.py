import os
import unittest

GEO_TEST_BASEDIR = os.path.dirname(__file__)

ALL_COUNTRIES_FIXTURE_PATH = os.path.join(GEO_TEST_BASEDIR, "fixtures", "allCountries.txt")


def skip_if_no_es_server(cls):
    if not os.environ.get('ES_SERVER'):
        return unittest.skip("ES_SERVER env var not set")(cls)
    return cls