import unittest
from fastapi.testclient import TestClient

from server import app
from helpers import ENGLISH, SPANISH, VERSION, FRENCH, GERMAN
from helpers.custom.dates import ENTITY_TYPE_C_DATE

ENGLISH_ARTICLE_URL = 'https://apnews.com/article/belgium-racing-pigeon-fetches-million-9ae40c9f2e9e11699c42694250e012f7'
SPANISH_ARTICLE_URL = 'https://elpais.com/economia/2020-12-03/la-salida-de-trump-zanja-una-era-de-unilateralismo-y-augura-un-cambio-de-paradigma-en-los-organismos-economicos-globales.html'
SPANISH_ARTICLE_URL_2 = 'https://www.notigape.com/el-papa-francisco-prepara-viaje-a-hungria-en-septiembre-/229666'


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
        assert len(data['results']) == 22
        assert data['results'][19]['text'] == 'marzo'
        assert data['results'][19]['type'] == ENTITY_TYPE_C_DATE
        response = self._client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL, language=SPANISH))
        data = response.json()
        assert 'results' in data
        assert len(data['results']) > 0
        assert data['results'][0]['text'] == 'EE UU'
        assert data['results'][0]['type'] == 'LOC'

    def test_entities_from_url_english(self):
        response = self._client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
        data = response.json()
        response_with_title = self._client.post('/entities/from-url',
                                                data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH, title=1))
        data_with_title = response_with_title.json()
        assert 'results' in data
        assert len(data['results']) > 0
        assert 'results' in data
        assert data['results'][0]['text'] == 'HALLE'
        assert data['results'][0]['type'] == 'ORG'
        assert len(data['results']) < len(data_with_title['results'])

    def test_entities_from_url_french(self):
        url = "https://www.letelegramme.fr/soir/alain-souchon-j-ai-un-modele-mick-jagger-05-11-2021-12861556.php?utm_source=rss_telegramme&utm_medium=rss&utm_campaign=rss&xtor=RSS-20"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=FRENCH))
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 229

    def test_content_from_url(self):
        response = self._client.post('/content/from-url', data=dict(url=ENGLISH_ARTICLE_URL))
        data = response.json()
        assert 'results' in data
        assert 'url' in data['results']
        assert data['results']['url'] == ENGLISH_ARTICLE_URL
        assert 'text' in data['results']
        assert len(data['results']['text']) > 0


if __name__ == "__main__":
    unittest.main()
