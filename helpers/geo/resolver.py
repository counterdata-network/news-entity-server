from typing import List, Dict
from .models import LocationCandidate
from .disambiguation import disambiguate
from .geonames import matching_places
from .import index_client


def resolve(geo_entities: List[Dict]) -> List[LocationCandidate]:
    index = index_client()
    if len(geo_entities) == 0:
        return []

    all_candidates = []
    for entity in geo_entities:
        candidates = matching_places(index, entity)
        all_candidates.append(candidates)

    best_candidates = disambiguate(all_candidates)

    unique_candidates = {}
    for c in best_candidates:
        if c.geoname_id not in unique_candidates:
            unique_candidates[c.geoname_id] = c
            unique_candidates[c.geoname_id].usage_count = 1
        else:
            unique_candidates[c.geoname_id].usage_count += 1

    return list(unique_candidates.values())
