import spacy
from typing import List, Dict

from helpers import ENGLISH, SPANISH, PORTUGUESE, FRENCH, GERMAN, KOREAN, SWAHILI, MODEL_MODE_SMALL, MODEL_MODE
import helpers.custom.ages as ages
import helpers.custom.dates as dates
from helpers.exceptions import UnknownLanguageException

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

def get_masakhaner_pipeline():
    tokenizer = AutoTokenizer.from_pretrained("Davlan/xlm-roberta-large-masakhaner")
    model = AutoModelForTokenClassification.from_pretrained("Davlan/xlm-roberta-large-masakhaner")
    return pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# lookup table that maps from language code to default spaCy or HuggingFace NER model
language_nlp_lookup = {
    ENGLISH: spacy.load("en_core_web_sm" if MODEL_MODE == MODEL_MODE_SMALL else "en_core_web_lg"),
    SPANISH: spacy.load("es_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "es_core_news_lg"),
    PORTUGUESE: spacy.load("pt_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "pt_core_news_lg"),
    FRENCH: spacy.load("fr_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "fr_core_news_lg"),
    GERMAN: spacy.load("de_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "de_core_news_lg"),
    KOREAN: spacy.load("ko_core_news_sm" if MODEL_MODE == MODEL_MODE_SMALL else "ko_core_news_lg"),
    SWAHILI: get_masakhaner_pipeline() 
}


def from_text(text: str, language_code: str) -> List[Dict]:
    lang = language_code.lower()

    if lang not in language_nlp_lookup:
        raise UnknownLanguageException()

    nlp = language_nlp_lookup[lang]

    if lang == SWAHILI:
        ner_results = nlp(text)
        entities = _huggingface_entities_as_dict(ner_results)
    else:
        doc = nlp(text)
        entities = _entities_as_dict(doc)

    entities += ages.extract_ages(text, lang)
    entities += dates.extract_dates(text, lang)
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


def _huggingface_entities_as_dict(ner_results) -> List[Dict]:
    entities = []
    for ent in ner_results:
        entities.append({
            "text": ent["word"],
            "type": ent["entity_group"],
            "start_char": ent["start"],
            "end_char": ent["end"]
        })
    return entities

