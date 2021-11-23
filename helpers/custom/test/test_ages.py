import unittest
import helpers.custom.ages as ages
from helpers import SPANISH, ENGLISH, PORTUGUESE

test_string_es = """Mis amigos tienen 22 y 24 años. Mi hermana tiene 8 años. Tengo 3 gatos."""

test_string_pt = """Meus amigos têm 22 e 24 anos. Minha irmã tem 8 anos. Eu tenho 3 gatos."""

test_string_en = "I am a 23-year-old and my friends are 22 and 24 years old. My sister is 8 years old and I have 3 cats."

class TestCustomAgeExtraction(unittest.TestCase):

    def test_extract_ages_es(self):
        results = ages.extract_ages(test_string_es, SPANISH)
        assert len(results) == 2
        for r in results:
            assert r['type'] == ages.ENTITY_TYPE_C_AGE
            assert 'text' in r
            assert 'start_char' in r
            assert 'end_char' in r
        assert results[0]['text'] == '24 años'
        assert results[1]['text'] == '8 años'


    def test_extract_ages_pt(self):
        results = ages.extract_ages(test_string_pt, PORTUGUESE)
        assert len(results) == 2
        for r in results:
            assert r['type'] == ages.ENTITY_TYPE_C_AGE
            assert 'text' in r
            assert 'start_char' in r
            assert 'end_char' in r
        assert results[0]['text'] == '24 anos'
        assert results[1]['text'] == '8 anos'


    def test_extract_ages_en(self):
        results = ages.extract_ages(test_string_en, ENGLISH)
        assert len(results) == 3
        for r in results:
            assert r['type'] == ages.ENTITY_TYPE_C_AGE
            assert 'text' in r
            assert 'start_char' in r
            assert 'end_char' in r
        assert results[0]['text'] == '23-year-old'
        assert results[1]['text'] == '24 years old'
        assert results[2]['text'] == '8 years old'


if __name__ == "__main__":
    unittest.main()
