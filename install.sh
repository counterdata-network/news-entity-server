#!/bin/sh

python -m spacy download en_core_web_sm
python -m spacy download en_core_web_trf

python -m spacy download es_core_news_sm
python -m spacy download es_core_news_lg

python -m spacy download pt_core_news_sm
python -m spacy download pt_core_news_lg

python -m spacy download fr_core_news_sm
python -m spacy download fr_core_news_lg

python -m spacy download de_core_news_sm
python -m spacy download de_core_news_md
