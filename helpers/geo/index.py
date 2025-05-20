#from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging

from .geonames import parse_all_countries_file

logger = logging.getLogger(__name__)


def create_elasticsearch_index(es_client, index_name):
    """
    Creates an Elasticsearch index with appropriate mappings for GeoNames data.

    Args:
        es_client: Elasticsearch client
        index_name (str): Name of the index to create
    """
    logger.info("Creating ES Index")
    # Define mappings based on GeoNames columns
    mappings = {
        "properties": {
            "geonameid": {"type": "keyword"},
            "name": {"type": "text", "fields": {"raw": { "type": "keyword" }}},
            "asciiname": {"type": "text"},
            "alternatenames": {"type": "text", "fields": {"raw": { "type": "keyword" }}},
            "latitude": {"type": "float"},
            "longitude": {"type": "float"},
            "location": {"type": "geo_point"},
            "feature_class": {"type": "text"},
            "feature_code": {"type": "text"},
            "country_code": {"type": "text"},
            "cc2": {"type": "text"},
            "admin1_code": {"type": "text"},
            "admin2_code": {"type": "text"},
            "admin3_code": {"type": "text"},
            "admin4_code": {"type": "text"},
            "population": {"type": "long"},
            "elevation": {"type": "integer"},
            "dem": {"type": "integer"},
            "timezone": {"type": "text"},
            "modification_date": {"type": "date", "format": "yyyy-MM-dd"},
        }
    }

    # Check if index exists and delete if it does
    if es_client.indices.exists(index=index_name):
        logger.info(f"  Deleting existing index: {index_name}")
        es_client.indices.delete(index=index_name)

    # Create the index with mappings
    logger.info(f"Creating index: {index_name}")
    es_client.indices.create(
        index=index_name,
        mappings=mappings,
        settings={
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "lowercase": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase"]
                    }
                }
            }
        }
    )
    logger.info(f"  Index {index_name} created successfully")


def index_geonames_data(es_client, index_name, file_path):
    logger.info(f"Indexing data from {file_path} into {index_name}")

    # Count total lines for progress reporting
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)

    # Stream documents to Elasticsearch
    success, failed = bulk(
        es_client,
        parse_all_countries_file(file_path, index_name),
        chunk_size=1000,
        max_retries=3,
        request_timeout=60
    )

    logger.info(f"Indexing complete: {success} documents indexed, {len(failed)} failed")
    return success, failed
