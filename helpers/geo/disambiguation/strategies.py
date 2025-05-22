from typing import List, Dict
import logging

import helpers.geo.disambiguation.util as util
from ..locations import ResolvedLoc, ResolvedCandidates

logger = logging.getLogger(__name__)


def large_area_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    """
    Pull out any large areas, like Europe, Asia, etc. These have a low frequency of occurence, but high rate
    of false positives on names, so we want to pick them first.
    """
    stage_name = "large_area_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        found_one = False
        for candidate in entity_candidates:
            if ((not found_one) and candidate.exact_match and (len(candidate.country_code) == 0)
                    and candidate.is_large_area()):
                _add_or_increment(entity_candidate_set.entity, candidate, resolved_locs, stage_name)
                to_remove.append(entity_candidate_set)
                logger.debug(f"large_area_pass: picked {candidate}")
                found_one = True
    _remove(to_remove, all_candidate_lists)


def fuzzy_matched_countries_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    """
    Countries are mentioned a _lot_ in the text, so pull them out by exact match.
    """
    stage_name = "fuzzy_matched_countries_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        country_candidate = util.first_country(entity_candidates[:3])  # subjective threshold of top 3
        if country_candidate:
            logger.debug(f"fuzzy_matched_countries_pass: picked {country_candidate}")
            _add_or_increment(entity_candidate_set.entity, country_candidate, resolved_locs, stage_name)
            to_remove.append(entity_candidate_set)
    _remove(to_remove, all_candidate_lists)


def exact_admin1_match_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    """
    If we find a city that matches, then pick it because the requently occur.
    """
    stage_name = "exact_admin1_match_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        if util.includes_populated_city_exact_match(entity_candidates):
            continue
        exact_match_candidates = util.exact_or_admin1_matches(entity_candidates)
        if len(exact_match_candidates):
            first = exact_match_candidates[0]
            if first.is_populated() and first.is_admin1():
                _add_or_increment(entity_candidate_set.entity, first, resolved_locs, stage_name)
                to_remove.append(entity_candidate_set)
                logger.debug(f"exact_admin1_match_pass: picked {first}")
    _remove(to_remove, all_candidate_lists)


def exact_colocations_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    if len(resolved_locs) == 0:
        return
    stage_name = "exact_colocations_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        to_pick = None
        populated_exact_cities = [c for c in entity_candidates if c.is_populated() and c.is_city() and c.exact_match]
        colocated_cities = util.in_same_country(populated_exact_cities, resolved_locs)
        if len(colocated_cities) == 1:
            to_pick = colocated_cities[0]
        elif len(colocated_cities) > 1:
            share_country_and_admin1 = util.same_country_and_admin1(colocated_cities, resolved_locs)
            if len(share_country_and_admin1) > 0:
                to_pick = share_country_and_admin1[0]
            else:
                to_pick = colocated_cities[0]
        if to_pick:
            _add_or_increment(entity_candidate_set.entity, to_pick, resolved_locs, stage_name)
            to_remove.append(entity_candidate_set)
            logger.debug(f"exact_colocations_pass: picked {to_pick}")
    _remove(to_remove, all_candidate_lists)


def top_colocations_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    stage_name = "top_colocations_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in resolved_locs]
            if (not found_one) and (candidate.feature_class in ['A', 'P']) and (candidate.country_code in best_candidate_countries):
                _add_or_increment(entity_candidate_set.entity, candidate, resolved_locs, stage_name)
                to_remove.append(entity_candidate_set)
                logger.debug(f"top_colocations_pass: picked {candidate}")
                found_one = True
    _remove(to_remove, all_candidate_lists)


def top_admin_populated_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    # Logic is now to compare the City place with the Admin/State place.
    # If City has larger population then choose it. If the City and State are in the same country,
    # then choose the city (this will favor Paris the city over Paris the district in France).
    # If the City has lower population and is not in same country then choose the state.
    stage_name = "top_admin_populated_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        exact_matches = [c for c in entity_candidates if c.exact_match]
        if len(exact_matches) == 0:
            city = util.most_populated(exact_matches)
            admin = util.most_populated(entity_candidates)
        else:
            city = util.most_populated(entity_candidates)
            admin = util.most_populated(entity_candidates)
        if util.choose_city_over_admin(city, admin):
            _add_or_increment(entity_candidate_set.entity, city, resolved_locs, stage_name)
            to_remove.append(entity_candidate_set)
            logger.debug(f"top_admin_populated_pass city: picked {city}")
        elif admin:
            _add_or_increment(entity_candidate_set.entity, admin, resolved_locs, stage_name)
            to_remove.append(entity_candidate_set)
            logger.debug(f"top_admin_populated_pass admin: picked {admin}")
    _remove(to_remove, all_candidate_lists)


def top_preferring_colocated_pass(all_candidate_lists: List[ResolvedCandidates], resolved_locs: List[ResolvedLoc]) -> None:
    stage_name = "top_preferring_colocated_pass"
    to_remove = []
    for entity_candidate_set in all_candidate_lists:
        entity_candidates = entity_candidate_set.candidates
        if len(entity_candidates) == 0:
            continue
        found_one = False
        for candidate in entity_candidates:
            best_candidate_countries = [c.country_code for c in resolved_locs]
            if not found_one and [candidate.country_code in best_candidate_countries]:
                _add_or_increment(entity_candidate_set.entity, candidate, resolved_locs, stage_name)
                logger.debug(f"top_preferring_colocated_pass same-country: picked {candidate}")
                found_one = True
        if not found_one:
            for candidate in entity_candidates:
                if not found_one and candidate.is_city():
                    _add_or_increment(entity_candidate_set.entity, candidate, resolved_locs, stage_name)
                    logger.debug(f"top_preferring_colocated_pass city: picked {candidate}")
                    found_one = True
        # just pick something!
        if not found_one:
            candidate = entity_candidates[0]
            _add_or_increment(entity_candidate_set.entity, candidate, resolved_locs, stage_name)
            logger.debug(f"top_preferring_colocated_pass last-ditch: picked {candidate}")
        to_remove.append(entity_candidate_set)
    _remove(to_remove, all_candidate_lists)


def _add_or_increment(entity: Dict, picked_loc: ResolvedLoc, all_resolved: List[ResolvedLoc], stage_name: str = None):
    """
    Centrally locate function that adds a choosen resolution to the list of resolved ones
    """
    for loc in all_resolved:
        if loc.geoname_id == picked_loc.geoname_id:
            loc.usage_count += 1
            loc.add_entity_and_stage(entity, stage_name)
            return
    picked_loc.usage_count += 1
    picked_loc.add_entity_and_stage(entity, stage_name)
    all_resolved.append(picked_loc)


def _remove(candidate_list_to_remove: List[ResolvedCandidates], all_candidate_lists: List[ResolvedCandidates]):
    """
    Remove to_remove from all_items. Call this at the end of each pass to remove the item
    that thas been resolved so it doesn't trigger a re-attempt to resolve in the subequent pass.
    """
    for item_to_remove in candidate_list_to_remove:
        all_candidate_lists.remove(item_to_remove)
