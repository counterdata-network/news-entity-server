import pytest
import json

from server import app
from helpers import ENGLISH, SPANISH, VERSION
from helpers.custom.dates import ENTITY_TYPE_C_DATE

ENGLISH_ARTICLE_URL = 'https://apnews.com/article/belgium-racing-pigeon-fetches-million-9ae40c9f2e9e11699c42694250e012f7'
SPANISH_ARTICLE_URL = 'https://elpais.com/economia/2020-12-03/la-salida-de-trump-zanja-una-era-de-unilateralismo-y-augura-un-cambio-de-paradigma-en-los-organismos-economicos-globales.html'
SPANISH_ARTICLE_URL_2 = 'https://www.notigape.com/el-papa-francisco-prepara-viaje-a-hungria-en-septiembre-/229666'


@pytest.fixture
def client():
    # This initializes the base client used by all the other tests
    # do any setup here
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # do any cleanup here


def test_api_metadata(client):
    response = client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'ok'
    assert 'duration' in data
    assert data['duration'] > 0
    assert 'version' in data
    assert data['version'] == VERSION


def test_entities_from_url_spanish(client):
    response = client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL_2, language=SPANISH))
    data = json.loads(response.data)
    assert 'results' in data
    assert len(data['results']) > 18
    assert data['results'][17]['text'] == 'septiembre'
    assert data['results'][17]['type'] == ENTITY_TYPE_C_DATE
    response = client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL, language=SPANISH))
    data = json.loads(response.data)
    assert 'results' in data
    assert len(data['results']) > 0
    assert data['results'][0]['text'] == 'EE UU'
    assert data['results'][0]['type'] == 'LOC'


def test_entities_from_url_english(client):
    response = client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
    data = json.loads(response.data)
    response_with_title = client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH, title=1))
    data_with_title = json.loads(response_with_title.data)
    assert 'results' in data
    assert len(data['results']) > 0
    assert 'results' in data
    assert data['results'][0]['text'] == 'Pipa'
    assert data['results'][0]['type'] == 'ORG'
    assert len(data['results']) < len(data_with_title['results'])


def test_content_from_url(client):
    response = client.post('/content/from-url', data=dict(url=ENGLISH_ARTICLE_URL))
    data = json.loads(response.data)
    assert 'results' in data
    assert 'url' in data['results']
    assert data['results']['url'] == ENGLISH_ARTICLE_URL
    assert 'text' in data['results']
    assert len(data['results']['text']) > 0
    assert 'title' in data['results']
    assert len(data['results']['title']) > 0
    assert 'publish_date' in data['results']
    assert data['results']['publish_date'] == 'Sun, 15 Nov 2020 12:40:17 GMT'
    assert 'authors' in data['results']
    assert len(data['results']['authors']) == 1
