import spacy
from typing import List, Dict

from helpers import ENGLISH, SPANISH, PORTUGUESE, FRENCH, GERMAN, KOREAN, MODEL_MODE_SMALL, MODEL_MODE
import helpers.custom.ages as ages
import helpers.custom.dates as dates
from helpers.exceptions import UnknownLanguageException

# lookup table that maps from language code to default spaCy NER model
language_nlp_lookup = {
    ENGLISH: spacy.load("en_core_web_sm" if MODEL_MODE == MODEL_MODE_SMALL else "en_core_web_lg"),
    SPANISH: spacy.load("es_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "es_core_news_lg"),
    PORTUGUESE: spacy.load("pt_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "pt_core_news_lg"),
    FRENCH: spacy.load("fr_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "fr_core_news_lg"),
    GERMAN: spacy.load("de_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "de_core_news_lg"),
    KOREAN: spacy.load("ko_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "ko_core_news_lg")
}


def from_text(text: str, language_code: str) -> List[Dict]:
    if language_code.lower() not in language_nlp_lookup.keys():
        raise UnknownLanguageException()
    nlp = language_nlp_lookup[language_code.lower()]
    doc = nlp(text)
    entities = _entities_as_dict(doc)
    # add in custom entity types we've added
    entities += ages.extract_ages(text, language_code)
    entities += dates.extract_dates(text, language_code)
    return entities


def _entities_as_dict(doc) -> List[Dict]:
    entities = []
    for ent in doc.ents:
        entities.append({
            'text': ent.text.strip(),
            'type': ent.label_,
            'start_char': ent.start_char,
            'end_char': ent.end_char,
        })
    return entities

