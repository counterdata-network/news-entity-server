#!/bin/bash
# Helper to startup a local elasticsearch instance with some reasonable defaults (for a MacBook Pro)

docker run -d --name es-geonames -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" docker.elastic.co/elasticsearch/elasticsearch:9.0.1
