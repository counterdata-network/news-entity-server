from unittest import TestCase

from . import ALL_COUNTRIES_FIXTURE_PATH
from ..geonames import parse_all_countries_file


class GeonamesTest(TestCase):

    def test_parse_all_countries_file(self):
        row_count = 0
        for row in parse_all_countries_file(ALL_COUNTRIES_FIXTURE_PATH, "temp_index_placeholder_name"):
            row_count += 1
            assert row['_index'] == 'temp_index_placeholder_name'
            assert row['_id']
            assert len(row["_source"]) == 20
        assert row_count == 100
