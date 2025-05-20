import csv
import logging
from .models import LocationCandidate
from typing import Dict, List
from . import INDEX_NAME

logger = logging.getLogger(__name__)

GEONAMES_URLS = "https://download.geonames.org/export/dump/allCountries.zip"
RESULT_COUNT = 100


def parse_all_countries_file(file_path, index_name):
    columns = [
        "geonameid",  "name",  "asciiname",  "alternatenames",  "latitude",  "longitude",  "feature_class",
        "feature_code",  "country_code",  "cc2",  "admin1_code",  "admin2_code",  "admin3_code",  "admin4_code",
        "population",  "elevation",  "dem",  "timezone",  "modification_date"
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        # Skip header if present
        # Checking if the first line contains column headers
        first_line = f.readline().strip()
        f.seek(0)  # Reset file pointer to the beginning

        has_header = all(col in first_line for col in ["ISO", "Country", "Capital"])

        reader = csv.reader(f, delimiter='\t')
        if has_header:
            next(reader)  # Skip header

        for i, row in enumerate(reader):
            if len(row) != len(columns):
                logger.warning(f"Row {i} has {len(row)} columns instead of {len(columns)}, skipping")
                continue

            doc = dict(zip(columns, row))

            # Convert numeric fields
            try:
                doc['latitude'] = float(doc['latitude'])
                doc['longitude'] = float(doc['longitude'])
                doc['alternatenames'] = doc['alternatenames'].split(",") if doc.get('alternatenames') else []
                doc['location'] = [doc['longitude'], doc['latitude']]
                doc['population'] = int(doc['population']) if doc.get('population') else None
                doc['elevation'] = int(doc['elevation']) if doc.get('elevation') else None
            except ValueError:
                pass  # Keep as string if conversion fails

            # Use geonameid as document ID
            yield {
                "_index": index_name,
                "_id": doc["geonameid"],
                "_source": doc
            }


def matching_places(index, entity: Dict) -> List[LocationCandidate]:
    entity_name = entity['text'].strip().lower()
    if len(entity_name) == 0:
        return []

    candidates = []
    # search for exact match
    res = index.search(index=INDEX_NAME, body={
        "size": RESULT_COUNT,
        "query": {
            "match": {
                "name": {
                    "query": entity_name,
                    "analyzer": "lowercase"
                }
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
            {"population": {"order": "desc"}}
        ]
    })
    if res['hits']['total']['value'] > 0:
        for hit in res['hits']['hits']:
            candidate = LocationCandidate(**hit['_source'], name_match=True, score=hit['_score'],
                                          exact_match=hit['_source']['name'].lower() == entity_name.lower())
            candidates.append(candidate)
    # search for the matching docs where "alternate" is PLACE_NAME
    res = index.search(index=INDEX_NAME, body={
        "size": RESULT_COUNT,
        "query": {
            "match": {
                "alternatenames": {
                    "query": entity_name,
                    "analyzer": "lowercase"
                }
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
            {"population": {"order": "desc"}}
        ]
    })
    if res['hits']['total']['value'] > 0:
        for hit in res['hits']['hits']:
            lowercase_alternate_names = [name.lower() for name in hit['_source']['alternatenames']]
            candidate = LocationCandidate(**hit['_source'], alternate_name_match=True, score=hit['_score'],
                                          exact_match=entity_name.lower() in lowercase_alternate_names)
            candidates.append(candidate)
    return candidates
