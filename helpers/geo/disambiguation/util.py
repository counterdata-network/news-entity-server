from typing import List, Dict

from helpers.geo.models import LocationCandidate


def choose_city_over_admin(city: LocationCandidate, admin: LocationCandidate) -> bool:
    if city is None:
        return False
    if admin is None:
        return True
    return (city.population > admin.population) or (city.country_code == admin.country_code)


def same_country_and_admin1(candidates: List[LocationCandidate], existing_choices: List[LocationCandidate]) -> List[LocationCandidate]:
    colocated = []
    for existing in existing_choices:
        for candidate in candidates:
            if is_same_country_and_admin1(existing, candidate):
                colocated.append(candidate)
    return colocated


def is_same_country_and_admin1(c1: LocationCandidate, c2: LocationCandidate) -> bool:
    return c1.admin1_code == c2.admin1_code



def in_same_country(candidates: List[LocationCandidate], existing_choices: List[LocationCandidate]) -> List[LocationCandidate]:
    return [c for c in candidates if _in_same_country(c, existing_choices)]


def exact_or_admin1_matches(candidates: List[LocationCandidate]) -> List[LocationCandidate]:
    exact_or_admin1_candidates = []
    for candidate in candidates:
        if candidate.exact_match or candidate.exact_match_to_admin1_code():
            exact_or_admin1_candidates.append(candidate)
    return exact_or_admin1_candidates


def includes_populated_city_exact_match(candidates: List[LocationCandidate]) -> bool:
    for candidate in candidates:
        if candidate.is_populated() and candidate.exact_match and candidate.is_city():
            return True
    return False


def first_city(candidates: List[LocationCandidate]) -> LocationCandidate | None:
    for candidate in candidates:
        if candidate.is_populated() and candidate.is_city():
            return candidate
    return None


def first_admin(candidates: List[LocationCandidate]) -> LocationCandidate | None:
    for candidate in candidates:
        if candidate.is_populated() and candidate.is_admin_region():
            return candidate
    return None


def first_country(candidates: List[LocationCandidate], exact_match_required: bool = False) -> LocationCandidate | None:
    for candidate in candidates:
        # skip large territories that appear ahead of countries in results (ie. Indian Subcontinent!)
        if candidate.is_large_territory():
            continue
        if candidate.is_country():
            if exact_match_required and candidate.exact_match:
                return candidate
            elif not exact_match_required:
                return candidate
    return None


def _in_same_country(candidate: LocationCandidate, best_candidates: List[LocationCandidate]) -> bool:
    for best_candidate in best_candidates:
        if candidate.country_code == best_candidate.country_code:
            return True
    return False
