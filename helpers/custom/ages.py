import re

from helpers import SPANISH, ENGLISH, PORTUGUESE
from helpers.custom import matches_as_entities

ENTITY_TYPE_C_AGE = "C_AGE"


def extract_ages(text, language_code):
    """
    Function to pull out ages from article text. It gets ages of the form "x(x) años" for Spanish, 
    "x(x) anos" for Portuguese, and "x(x)(-)year(s)(-)old" for English.
    :param text: string
    :param language_code: 'EN', 'ES' or 'PT'
    :return: List of strings corresponding to ages contained in the text.
    """
    if language_code.lower() == SPANISH:
        regexp = re.compile(r'[0-9]{1,2}\saños')
    elif language_code.lower() == ENGLISH:
        regexp = re.compile(r'[0-9]{1,2}(?:\s|-)(?:years|year)(?:\s|-)(?:old)')
    elif language_code.lower() == PORTUGUESE:
        regexp = re.compile(r'[0-9]{1,2}\sanos')
    else:
        regexp = None
    if regexp:
        return matches_as_entities(regexp, text, ENTITY_TYPE_C_AGE)
    return []
