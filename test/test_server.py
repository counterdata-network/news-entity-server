import unittest
from fastapi.testclient import TestClient
import os
import json

from server import app
from helpers import ENGLISH, SPANISH, VERSION, FRENCH, GERMAN
from helpers.custom.dates import ENTITY_TYPE_C_DATE

ENGLISH_ARTICLE_URL = 'https://apnews.com/article/belgium-racing-pigeon-fetches-million-9ae40c9f2e9e11699c42694250e012f7'
SPANISH_ARTICLE_URL = 'https://elpais.com/economia/2020-12-03/la-salida-de-trump-zanja-una-era-de-unilateralismo-y-augura-un-cambio-de-paradigma-en-los-organismos-economicos-globales.html'
SPANISH_ARTICLE_URL_2 = 'https://www.notigape.com/el-papa-francisco-prepara-viaje-a-hungria-en-septiembre-/229666'

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestServer(unittest.TestCase):

    def setUp(self) -> None:
        # This initializes the base client used by all the other tests
        self._client = TestClient(app)

    def test_too_many_redirects(self):
        url = "https://mepublic.tarrantcounty.com/default.aspx?AspxAutoDetectCookieSupport=1"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=ENGLISH))
        data = response.json()
        assert data['status'] == 'error'
        assert data['statusCode'] == 400

    def test_bad_url(self):
        url = "https://mystupiddomain.doesnotexist"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=ENGLISH))
        data = response.json()
        assert data['status'] == 'error'
        assert data['statusCode'] == 400

    def test_api_metadata(self):
        response = self._client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'ok'
        assert 'duration' in data
        assert data['duration'] > 0
        assert 'version' in data
        assert data['version'] == VERSION

    def test_entities_from_url_spanish(self):
        response = self._client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL_2, language=SPANISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) == 20
        assert data['results']['entities'][17]['text'] == 'marzo'
        assert data['results']['entities'][17]['type'] == ENTITY_TYPE_C_DATE
        response = self._client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL, language=SPANISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) > 0
        assert data['results']['entities'][0]['text'] == 'EE UU'
        assert data['results']['entities'][0]['type'] == 'LOC'

    def test_entities_from_url_english(self):
        response = self._client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert data['results']['entities'][0]['text'] == 'HALLE'
        assert data['results']['entities'][0]['type'] == 'ORG'
        assert len(data['results']['entities']) > 0
        response_with_title = self._client.post('/entities/from-url',
                                                data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH, title=1))
        data_with_title = response_with_title.json()
        assert 'results' in data_with_title
        assert 'entities' in data_with_title['results']
        assert len(data['results']['entities']) < len(data_with_title['results']['entities'])

    def test_entities_from_url_french(self):
        url = "https://www.letelegramme.fr/soir/alain-souchon-j-ai-un-modele-mick-jagger-05-11-2021-12861556.php?utm_source=rss_telegramme&utm_medium=rss&utm_campaign=rss&xtor=RSS-20"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=FRENCH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) == 94

    def test_domain_from_url(self):
        response = self._client.post('/content/from-url', data=dict(url=ENGLISH_ARTICLE_URL))
        data = response.json()
        assert 'results' in data
        assert 'url' in data['results']
        assert data['results']['url'] == ENGLISH_ARTICLE_URL
        assert 'domain_name' in data['results']
        assert data['results']['domain_name'] == 'apnews.com'

    def test_content_from_url(self):
        response = self._client.post('/content/from-url', data=dict(url=ENGLISH_ARTICLE_URL))
        data = response.json()
        assert 'results' in data
        assert 'url' in data['results']
        assert 'domain_name' in data['results']
        assert data['results']['url'] == ENGLISH_ARTICLE_URL
        assert 'text' in data['results']
        assert len(data['results']['text']) > 0

    def test_entities_from_text(self):
        story = json.load(open(os.path.join(this_dir, 'fixtures', '1952688847.json')))
        response = self._client.post('/entities/from-content', data=dict(
            text=story['story_text'], language=story['language'], url=story['url']
        ))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) == 24
        assert 'domain_name' in data['results']
        assert data['results']['domain_name'] == 'europapress.es'


if __name__ == "__main__":
    unittest.main()
