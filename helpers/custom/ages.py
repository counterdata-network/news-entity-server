import re

from helpers import SPANISH, ENGLISH
from helpers.custom import matches_as_entities

ENTITY_TYPE_C_AGE = "C_AGE"


def extract_ages(text, language_code):
    """
    Function to pull out ages from article text. It gets ages of the form "xx años" for Spanish,
    and "xx(-)year(s)(-)old" for English.
    :param text: string
    :param language_code: 'EN' or 'ES'
    :return: List of strings corresponding to ages contained in the text.
    """
    if language_code is SPANISH:
        regexp = re.compile(r'[0-9]{2}\saños')
    elif language_code is ENGLISH:
        regexp = re.compile(r'[0-9]{2}(?:\s|-)(?:years|year)(?:\s|-)(?:old)')
    else:
        regexp = None
    if regexp:
        return matches_as_entities(regexp, text, ENTITY_TYPE_C_AGE)
    return []
