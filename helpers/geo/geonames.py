import csv
import logging
from .locations import ResolvedLoc
from typing import Dict, List

logger = logging.getLogger(__name__)

GEONAMES_URLS = "https://download.geonames.org/export/dump/allCountries.zip"
RESULT_COUNT = 10
INDEX_NAME = "news-geonames"


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


def matching_places(index, entity: Dict) -> List[ResolvedLoc]:
    entity_name = entity['text'].strip().lower()
    if len(entity_name) == 0:
        return []

    candidates = []
    # Combined search: match entity_name in both 'name' and 'alternatenames', boost 'name' matches higher
    res = index.search(index=INDEX_NAME, body={
        "size": RESULT_COUNT,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "name": {
                                        "query": entity_name,
                                        "analyzer": "lowercase",
                                    }
                                }
                            },
                            {
                                "term": {
                                    "name.keyword": {
                                        "value": entity_name,
                                        "boost": 10  # High boost for exact match
                                    }
                                }
                            }
                        ]
                    }
                },
                "boost_mode": "sum",
                "score_mode": "sum",
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "population",
                            "factor": 1,
                            "modifier": "log1p",
                            "missing": 0
                        }
                    },
                    {
                        "filter": {
                            "term": {
                                "admin1_code": "00"
                            }
                        },
                        "weight": 2  # Adjust this weight as needed for the boost
                    },
                    {
                        "filter": {
                            "terms": {
                                "feature_class": ["P", "A"]
                            }
                        },
                        "weight": 1.5  # Slight boost for feature_class P or A
                    }
                ]
            }
        }
    })
    if res['hits']['total']['value'] > 0:
        for hit in res['hits']['hits']:
            src = hit['_source']
            name_match = src['name'].lower() == entity_name.lower()
            alternate_name_match = entity_name.lower() in [n.lower() for n in src.get('alternatenames', [])]
            candidate = ResolvedLoc(
                **src,
                name_match=name_match,
                alternate_name_match=alternate_name_match,
                score=hit['_score'],
                exact_match=name_match or alternate_name_match
            )
            candidates.append(candidate)
    return candidates


def by_id(index, geoname_id: str) -> ResolvedLoc:
    res = index.get(index=INDEX_NAME, id=geoname_id)
    if res['found']:
        return res["_source"]
    return None
