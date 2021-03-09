import helpers.custom.ages as ages
from helpers import SPANISH, ENGLISH

test_string_es = """Hoy es 8/3/21, lunes. el mes es marzo, el próximo mes es abril 
    y más tarde hay septiembre, noviembre y diciembre. Algunas abreviaturas son 
    sep., Oct., Nov., nov., jul., ago, etc. Mis amigos tienen 22 y 24 años."""

test_string_en = "I am a 23-year-old and my friends are 22 and 24 years old."


def test_extract_ages_es():
    results = ages.extract_ages(test_string_es, SPANISH)
    assert len(results) == 1
    for r in results:
        assert r['type'] == ages.ENTITY_TYPE_C_AGE
        assert 'text' in r
        assert 'start_char' in r
        assert 'end_char' in r
    assert results[0]['text'] == '24 años'


def test_extract_ages_en():
    results = ages.extract_ages(test_string_en, ENGLISH)
    assert len(results) == 2
    for r in results:
        assert r['type'] == ages.ENTITY_TYPE_C_AGE
        assert 'text' in r
        assert 'start_char' in r
        assert 'end_char' in r
    assert results[0]['text'] == '23-year-old'
    assert results[1]['text'] == '24 years old'
