import helpers.custom.dates as dates
from helpers import SPANISH, ENGLISH

test_string_es = """Hoy es 8/3/21, lunes. el mes es marzo, el próximo mes es abril 
    y más tarde hay septiembre, noviembre y diciembre. Algunas abreviaturas son 
    sep., Oct., Nov., nov., jul., ago, etc. Mis amigos tienen 22 y 24 años."""


def test_extract_dates_es():
    results = dates.extract_dates(test_string_es, SPANISH)
    assert len(results) is 13
    assert results[0]['text'] == 'marzo'
    assert results[12]['text'] == '8/3/21'


def test_extract_dates_en():
    results = dates.extract_dates("This happend on 8/3/21", ENGLISH)
    assert len(results) is 0
