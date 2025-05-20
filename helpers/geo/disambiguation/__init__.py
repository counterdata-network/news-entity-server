from typing import List
from ..models import LocationCandidate
import helpers.geo.disambiguation.strategies as strategies


def disambiguate(all_candidates: List[List[LocationCandidate]]) -> List[LocationCandidate]:
    best_candidates = []  # one per entity
    strategies.large_area_pass(all_candidates, best_candidates)
    strategies.fuzzy_matched_countries_pass(all_candidates, best_candidates)
    strategies.exact_admin1_match_pass(all_candidates, best_candidates)
    strategies.exact_colocations_pass(all_candidates, best_candidates)
    strategies.top_colocations_pass(all_candidates, best_candidates)
    strategies.top_admin_populated_pass(all_candidates, best_candidates)
    strategies.top_preferring_colocated_pass(all_candidates, best_candidates)
    return best_candidates
