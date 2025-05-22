from elasticsearch import Elasticsearch
import os


def index_client() -> Elasticsearch:
    return Elasticsearch([os.getenv("ES_SERVER")])
