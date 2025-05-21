from typing import List, Dict
import logging

import helpers.geo.disambiguation.util as util
from ..locations import ResolvedLoc, ResolvedCandidates

logger = logging.getLogger(__name__)


def top_preferring_colocated_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        if len(entity_candidates) == 0:
            continue
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in best_candidates]
            if not found_one and [candidate.country_code in best_candidate_countries]:
                _add_or_increment(entity_candidate_set.entity, candidate, best_candidates)
                logger.debug(f"top_preferring_colocated_pass same-country: picked {candidate}")
                found_one = True
        if not found_one:
            for candidate in entity_candidates:
                if not found_one and candidate.is_city():
                    _add_or_increment(entity_candidate_set.entity, candidate, best_candidates)
                    logger.debug(f"top_preferring_colocated_pass city: picked {candidate}")
                    found_one = True
        # just pick something!
        if not found_one:
            candidate = entity_candidates[0]
            _add_or_increment(entity_candidate_set.entity, candidate, best_candidates)
            logger.debug(f"top_preferring_colocated_pass last-ditch: picked {candidate}")
        to_remove.append(entity_candidate_set)
    _remove(to_remove, all_candidates)


def top_admin_populated_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    # Logic is now to compare the City place with the Admin/State place.
    # If City has larger population then choose it. If the City and State are in the same country,
    # then choose the city (this will favor Paris the city over Paris the district in France).
    # If the City has lower population and is not in same country then choose the state.
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        exact_matches = [c for c in entity_candidates if c.exact_match]
        if len(exact_matches) == 0:
            city = util.most_populated(exact_matches)
            admin = util.most_populated(entity_candidates)
        else:
            city = util.most_populated(entity_candidates)
            admin = util.most_populated(entity_candidates)
        if util.choose_city_over_admin(city, admin):
            _add_or_increment(entity_candidate_set.entity, city, best_candidates)
            to_remove.append(entity_candidate_set)
            logger.debug(f"top_admin_populated_pass city: picked {city}")
        elif admin:
            _add_or_increment(entity_candidate_set.entity, admin, best_candidates)
            to_remove.append(entity_candidate_set)
            logger.debug(f"top_admin_populated_pass admin: picked {admin}")
    _remove(to_remove, all_candidates)


def top_colocations_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in best_candidates]
            if (not found_one) and (candidate.feature_class in ['A', 'P']) and (candidate.country_code in best_candidate_countries):
                _add_or_increment(entity_candidate_set.entity, candidate, best_candidates)
                to_remove.append(entity_candidate_set)
                logger.debug(f"top_colocations_pass: picked {candidate}")
                found_one = True
    _remove(to_remove, all_candidates)


def exact_colocations_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    if len(best_candidates) == 0:
        return
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
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
            _add_or_increment(entity_candidate_set.entity, to_pick, best_candidates)
            to_remove.append(entity_candidate_set)
            logger.debug(f"exact_colocations_pass: picked {to_pick}")
    _remove(to_remove, all_candidates)


def large_area_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        found_one = False
        for candidate in entity_candidates:
            if ((not found_one) and candidate.exact_match and (len(candidate.country_code) == 0)
                    and candidate.is_large_area()):
                _add_or_increment(entity_candidate_set.entity, candidate, best_candidates)
                to_remove.append(entity_candidate_set)
                logger.debug(f"large_area_pass: picked {candidate}")
                found_one = True
    _remove(to_remove, all_candidates)


def fuzzy_matched_countries_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        country_candidate = util.first_country(entity_candidates)
        if country_candidate:
            logger.debug(f"fuzzy_matched_countries_pass: picked {country_candidate}")
            _add_or_increment(entity_candidate_set.entity, country_candidate, best_candidates)
            to_remove.append(entity_candidate_set)
    _remove(to_remove, all_candidates)


def exact_admin1_match_pass(all_candidates: List[ResolvedCandidates], best_candidates: List[ResolvedLoc]) -> None:
    to_remove = []
    for entity_candidate_set in all_candidates:
        entity_candidates = entity_candidate_set.candidates
        if util.includes_populated_city_exact_match(entity_candidates):
            continue
        exact_match_candidates = util.exact_or_admin1_matches(entity_candidates)
        if len(exact_match_candidates):
            first = exact_match_candidates[0]
            if first.is_populated() and first.is_admin1():
                _add_or_increment(entity_candidate_set.entity, first, best_candidates)
                to_remove.append(entity_candidate_set)
                logger.debug(f"exact_admin1_match_pass: picked {first}")
    _remove(to_remove, all_candidates)


def _add_or_increment(entity: Dict, candidate: ResolvedLoc, candidates: List[ResolvedLoc]):
    for c in candidates:
        if c.geoname_id == candidate.geoname_id:
            c.usage_count += 1
            c.add_entity(entity)
            return
    candidate.usage_count += 1
    candidate.add_entity(entity)
    candidates.append(candidate)


def _remove(to_remove: List[ResolvedCandidates], all_items: List[ResolvedCandidates]):
    for item_to_remove in to_remove:
        all_items.remove(item_to_remove)
