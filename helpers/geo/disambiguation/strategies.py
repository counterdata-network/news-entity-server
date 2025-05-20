from typing import List
import logging

import helpers.geo.disambiguation.util as util
from ..models import LocationCandidate

logger = logging.getLogger(__name__)

def top_preferring_colocated_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    for entity_candidates in all_candidates:
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in best_candidates]
            if not found_one and [candidate.country_code in best_candidate_countries]:
                best_candidates.append(candidate)
                logger.debug(f"top_preferring_colocated_pass same-country: picked {candidate}")
                found_one = True
        if not found_one:
            for candidate in entity_candidates:
                if not found_one and candidate.is_city():
                    best_candidates.append(candidate)
                    logger.debug(f"top_preferring_colocated_pass city: picked {candidate}")
                    found_one = True
        # just pick something!
        if not found_one:
            candidate = entity_candidates[0]
            best_candidates.append(candidate)
            logger.debug(f"top_preferring_colocated_pass last-ditch: picked {candidate}")


def top_admin_populated_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    # Logic is now to compare the City place with the Admin/State place.
    # If City has larger population then choose it. If the City and State are in the same country,
    # then choose the city (this will favor Paris the city over Paris the district in France).
    # If the City has lower population and is not in same country then choose the state.
    for entity_candidates in all_candidates:
        exact_matches = [c for c in entity_candidates if c.exact_match]
        if len(exact_matches) == 0:
            city = util.first_city(exact_matches)
            admin = util.first_admin(entity_candidates)
        else:
            city = util.first_city(entity_candidates)
            admin = util.first_admin(entity_candidates)
        if util.choose_city_over_admin(city, admin):
            best_candidates.append(city)
            logger.debug(f"top_admin_populated_pass city: picked {city}")
        elif admin:
            best_candidates.append(admin)
            logger.debug(f"top_admin_populated_pass admin: picked {admin}")


def top_colocations_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    for entity_candidates in all_candidates:
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in best_candidates]
            if (not found_one) and (candidate.feature_class in ['A', 'P']) and (candidate.country_code in best_candidate_countries):
                best_candidates.append(candidate)
                logger.debug(f"top_colocations_pass: picked {candidate}")
                found_one = True


def exact_colocations_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    if len(best_candidates) == 0:
        return
    for entity_candidates in all_candidates:
        to_pick = None
        populated_exact_cities = [c for c in entity_candidates if c.is_populated() and c.is_city() and c.exact_match]
        colocated_cities = util.in_same_country(populated_exact_cities, best_candidates)
        if len(colocated_cities) == 1:
            to_pick = colocated_cities[0]
        elif len(colocated_cities) > 1:
            share_country_and_admin1 = util.same_country_and_admin1(colocated_cities, best_candidates)
            if len(share_country_and_admin1) > 0:
                to_pick = share_country_and_admin1[0]
            else:
                to_pick = colocated_cities[0]
        if to_pick:
            best_candidates.append(to_pick)
            logger.debug(f"exact_colocations_pass: picked {to_pick}")


def large_area_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    for entity_candidates in all_candidates:
        found_one = False
        for candidate in entity_candidates:
            if ((not found_one) and candidate.exact_match and (candidate.country_code is None)
                    and candidate.is_large_area()):
                best_candidates.append(candidate)
                logger.debug(f"large_area_pass: picked {candidate}")
                found_one = True


def fuzzy_matched_countries_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    for entity_candidates in all_candidates:
        country_candidate = util.first_country(entity_candidates)
        if country_candidate:
            best_candidates.append(country_candidate)
            logger.debug(f"fuzzy_matched_countries_pass: picked {country_candidate}")


def exact_admin1_match_pass(all_candidates: List[List[LocationCandidate]], best_candidates: List[LocationCandidate]) -> None:
    for entity_candidates in all_candidates:
        if util.includes_populated_city_exact_match(entity_candidates):
            continue
        exact_match_candidates = util.exact_or_admin1_matches(entity_candidates)
        if len(exact_match_candidates):
            first = exact_match_candidates[0]
            if first.is_populated() and first.is_admin1():
                best_candidates.append(first)
                logger.debug(f"exact_admin1_match_pass: picked {first}")
