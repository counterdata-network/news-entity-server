import re

from helpers import SPANISH, PORTUGUESE
from helpers.custom import matches_as_entities

ENTITY_TYPE_C_DATE = "C_DATE"

SPANISH_DATE_WORDS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
                      'Octubre', 'Noviembre', 'Diciembre',
                      r'Ene\.', r'Feb\.', r'Mar\.', r'Abr\.', r'Jun\.', r'Jul\.', r'Ago\.', r'Sep\.',
                      r'Oct\.', r'Nov\.', r'Dic\.',
                      'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

PORTUGUESE_DATE_WORDS = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 
                         'Outubro','Novembro', 'Dezembro', 
                         r'Jan\.', r'Fev\.', r'Mar\.', r'Abr\.', r'Jun\.', r'Jul\.', r'Ago\.', r'Set\.', r'Out\.', 
                         r'Nov\.', r'Dez\.', 
                         'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

def extract_dates(text, language_code):
    if language_code.lower() == SPANISH or language_code.lower() == PORTUGUESE:
        return _get_dates_custom(text, language_code)
    return []

def _get_dates_custom(article_text, language_code):
    """
    Function to pull out ages from article text. It gets strings corresponding to Spanish or Portuguese days of the week
    and months (including month abbreviations), or strings of the form dd/dd/dd (slashes may be replaced
    with hypens, month & day can be 1 or 2 digits, and the year can be 2 or 4 digits).
    :param article_text: string
    :return: List of strings corresponding to dates contained in the text.
    """
    all_dates = []
    if language_code.lower() == SPANISH: 
        custom_date_words = SPANISH_DATE_WORDS
    elif language_code.lower() == PORTUGUESE: 
        custom_date_words = PORTUGUESE_DATE_WORDS
    else: return []

    for word in custom_date_words:
        found = matches_as_entities(word, article_text, ENTITY_TYPE_C_DATE, flags=re.IGNORECASE)
        all_dates.extend(found)
    numerical_date_regexp = re.compile(r'(?:\d{2}|\d{1})[-/](?:\d{2}|\d{1})[-/](?:\d{4}|\d{2})')
    found_numerical_dates = matches_as_entities(numerical_date_regexp, article_text, ENTITY_TYPE_C_DATE)
    all_dates.extend(found_numerical_dates)
    return all_dates
