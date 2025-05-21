from typing import List, Dict

from helpers.geo.locations import ResolvedLoc

KINDA_POPULATED = 10000  # to help avoid picking tiny towns named same as big ones


def choose_city_over_admin(city: ResolvedLoc, admin: ResolvedLoc) -> bool:
    if city is None:
        return False
    if admin is None:
        return True
    return (city.population > admin.population) or (city.country_code == admin.country_code)


def same_country_and_admin1(candidates: List[ResolvedLoc], existing_choices: List[ResolvedLoc]) -> List[ResolvedLoc]:
    colocated = []
    for existing in existing_choices:
        for candidate in candidates:
            if is_same_country_and_admin1(existing, candidate) and candidate.population > KINDA_POPULATED:
                colocated.append(candidate)
    return colocated


def is_same_country_and_admin1(c1: ResolvedLoc, c2: ResolvedLoc) -> bool:
    return c1.admin1_code == c2.admin1_code



def in_same_country(candidates: List[ResolvedLoc], existing_choices: List[ResolvedLoc]) -> List[ResolvedLoc]:
    return [c for c in candidates if _in_same_country(c, existing_choices)]


def exact_or_admin1_matches(candidates: List[ResolvedLoc]) -> List[ResolvedLoc]:
    exact_or_admin1_candidates = []
    for candidate in candidates:
        if candidate.exact_match or candidate.exact_match_to_admin1_code():
            exact_or_admin1_candidates.append(candidate)
    return exact_or_admin1_candidates


def includes_populated_city_exact_match(candidates: List[ResolvedLoc]) -> bool:
    for candidate in candidates:
        if candidate.is_populated() and candidate.exact_match and candidate.is_city():
            return True
    return False


def first_city(candidates: List[ResolvedLoc]) -> ResolvedLoc | None:
    cities = [c for c in candidates if c.is_city() and c.is_populated()]
    # return the city with the top population
    return most_populated(cities)


def first_admin(candidates: List[ResolvedLoc]) -> ResolvedLoc | None:
    for candidate in candidates:
        if candidate.is_populated() and candidate.is_admin_region():
            return candidate
    return None


def first_country(candidates: List[ResolvedLoc], exact_match_required: bool = False) -> ResolvedLoc | None:
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


def biggest_country(candidates: List[ResolvedLoc], exact_match_required: bool = False) -> ResolvedLoc | None:
    countries = []
    for candidate in candidates:
        # skip large territories that appear ahead of countries in results (ie. Indian Subcontinent!)
        if candidate.is_large_territory():
            continue
        if candidate.is_country():
            if exact_match_required and candidate.exact_match:
                countries.append(candidate)
            elif not exact_match_required:
                countries.append(candidate)
    if len(countries) > 0:
        return most_populated(countries)
    return None


def most_populated(candidates: List[ResolvedLoc]) -> ResolvedLoc | None:
    if len(candidates) == 0:
        return None
    candidates.sort(key=lambda c: c.population, reverse=True)
    return candidates[0]


def _in_same_country(candidate: ResolvedLoc, best_candidates: List[ResolvedLoc]) -> bool:
    for best_candidate in best_candidates:
        if candidate.country_code == best_candidate.country_code:
            return True
    return False
