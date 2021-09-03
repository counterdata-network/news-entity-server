import spacy

from helpers import ENGLISH, SPANISH, PORTUGUESE
import helpers.custom.ages as ages
import helpers.custom.dates as dates

# lookup table that maps from language code to default spaCy NER model
language_nlp_lookup = {
    ENGLISH: spacy.load("en_core_web_lg"),
    SPANISH: spacy.load("es_core_news_lg"),
    PORTUGUESE: spacy.load("pt_core_news_lg")
}


class UnknownLanguageException(Exception):
    """Raised when the input language is invalid"""
    pass


def from_text(text, language_code):
    if language_code.lower() not in language_nlp_lookup.keys():
        raise UnknownLanguageException()
    nlp = language_nlp_lookup[language_code.lower()]
    doc = nlp(text)
    entities = _entities_as_dict(doc)
    # add in custom entity types we've added
    entities += ages.extract_ages(text, language_code)
    entities += dates.extract_dates(text, language_code)
    return entities


def _entities_as_dict(doc):
    entities = []
    for ent in doc.ents:
        entities.append({
            'text': ent.text.strip(),
            'type': ent.label_,
            'start_char': ent.start_char,
            'end_char': ent.end_char,
        })
    return entities

