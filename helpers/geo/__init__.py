from elasticsearch import Elasticsearch
import os

INDEX_NAME = "news-geonames"


def index_client() -> Elasticsearch:
    return Elasticsearch([os.getenv("ES_SERVER")])
