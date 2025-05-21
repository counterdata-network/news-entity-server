import spacy
from typing import List, Dict
import os
import csv

from helpers import ENGLISH, SPANISH, PORTUGUESE, FRENCH, GERMAN, KOREAN, SWAHILI, MODEL_MODE_SMALL, MODEL_MODE
import helpers.custom.ages as ages
import helpers.custom.dates as dates
from helpers.exceptions import UnknownLanguageException

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification


GEO_ENTITY_TYPES = ['GPE', 'NORP', 'LOC']

_token_type_overrides = None

def get_masakhaner_pipeline(hf_ner_model="Davlan/xlm-roberta-large-masakhaner"):
    tokenizer = AutoTokenizer.from_pretrained(hf_ner_model)
    model = AutoModelForTokenClassification.from_pretrained(hf_ner_model)
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
    for e in entities:
        e['synthetic'] = False
    entities += token_overrides(entities)

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
            "end_char": ent["end"],
        })
    return entities


def token_overrides(entities: List[Dict]) -> List[Dict]:
    """
    Add in any tokens that we want to force to interpret in a certain way. This can be helpful for things
    like
    :param entities:
    :return:
    """
    global _token_type_overrides
    if _token_type_overrides is None:
        _token_type_overrides = _get_type_overrides()
    additions = []
    for e in entities:
        desired_type = _token_type_overrides.get(e['text'], None)
        if desired_type:
            additions.append({**e, "type": desired_type, "synthetic": True, "original_type": e['type']})
    return additions


def _get_type_overrides() -> Dict[str, str]:
    """
    Return a list of strings and what type they should be replicated to. This can be helpful to make "Chelsea" shows up
    as both a PERSON and a GPE type.
    :return:
    """
    text2type = {}
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_dir, 'data', 'entity-type-forcing.csv')
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            token = row.get('token').strip()
            type = row.get('type').strip()
            text2type[token] = type
    return text2type
