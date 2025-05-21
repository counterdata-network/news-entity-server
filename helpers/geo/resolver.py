from typing import List, Dict
import os
import csv
from .locations import ResolvedLoc, ResolvedCandidates
from .disambiguation import disambiguate
from .geonames import matching_places
from typing import Dict
from .import index_client
from helpers.entities import GEO_ENTITY_TYPES

_replacements = None


def resolve(entities: List[Dict]) -> List[ResolvedLoc]:
    geo_entities = geo_entities = [entity for entity in entities if entity['type'] in GEO_ENTITY_TYPES]
    if len(geo_entities) == 0:
        return []

    index = index_client()
    all_candidates = []
    substitutions = replacement_map()
    for entity in geo_entities:
        replacement = substitutions.get(entity['text'].lower(), None)
        if replacement:
            entity['substitution'] = True
            entity['original_text'] = entity['text']
            entity['text'] = replacement
        else:
            entity['substitution'] = False
        candidates = matching_places(index, entity)
        all_candidates.append(ResolvedCandidates(entity, candidates))

    best_candidates = disambiguate(all_candidates)

    return best_candidates


def replacement_map() -> Dict[str, str]:
    global _replacements
    if _replacements is None:  # load it like a singleton
        subs = _load_custom_substitutions()
        demonyms = _load_demomnyms()
        _replacements = {**subs, **demonyms}
    return _replacements


def _load_demomnyms() -> Dict[str, str]:
    replacement_map = {}
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_dir, 'data', 'country-adjectivals-demonyms.csv')
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row.get('Country').strip()
            adjectives = row.get('Adjectival').split(',') if row.get('Adjectival') else ""
            demonyms = row.get('Demonym').split(',') if row.get('Demonym') else ""
            for adjective in adjectives:
                if adjective:
                    replacement_map[adjective.lower().strip()] = country
            for demonym in demonyms:
                if demonym:
                    replacement_map[demonym.lower().strip()] = country
    return replacement_map


def _load_custom_substitutions() -> Dict[str, str]:
    replacement_map = {}
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_dir, 'data', 'custom-substitutions.csv')
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name')
            replacement = row.get('replacement')
            if name and replacement:
                replacement_map[name.lower().strip()] = replacement.strip()
    return replacement_map