import unittest
import pytest
import time
import mcmetadata.content
from fastapi.testclient import TestClient
import os
import json

from server import app
from helpers import ENGLISH, SPANISH, VERSION, FRENCH, KOREAN,GERMAN, MODEL_MODE_SMALL

ENGLISH_ARTICLE_URL = 'https://web.archive.org/web/20240329152732/https://apnews.com/article/belgium-racing-pigeon-fetches-million-9ae40c9f2e9e11699c42694250e012f7'
SPANISH_ARTICLE_URL = 'https://web.archive.org/web/20220809180347/https://elpais.com/economia/2020-12-03/la-salida-de-trump-zanja-una-era-de-unilateralismo-y-augura-un-cambio-de-paradigma-en-los-organismos-economicos-globales.html'

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestServer(unittest.TestCase):

    def setUp(self) -> None:
        # This initializes the base client used by all the other tests
        self._client = TestClient(app)

    def test_basic(self):
        url = "https://web.archive.org/web/20221228220125/https://www.bostonglobe.com/2022/12/28/metro/more-cancellations-delays-travelers-southwest-airlines/"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=ENGLISH))
        data = response.json()
        assert data['status'] == 'ok'

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
        response = self._client.post('/entities/from-url', data=dict(url=SPANISH_ARTICLE_URL, language=SPANISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) > 0
        assert data['results']['entities'][2]['text'] == 'Biden'
        assert data['results']['entities'][2]['type'] == 'PER'

    def test_entities_from_html_english(self):
        url = "https://web.archive.org/web/20240120194229/https://www.bostonglobe.com/2022/09/27/nation/cdc-makes-masking-optional-hospitals-nursing-homes-regions-without-high-covid-transmission/"
        html_text, _ = mcmetadata.webpages.fetch(url)
        response = self._client.post('/entities/from-html', data=dict(url=ENGLISH_ARTICLE_URL, html=html_text,
                                                                      language=ENGLISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert data['results']['entities'][0]['text'] == 'late Friday'
        assert data['results']['entities'][0]['type'] == 'DATE'

    def test_entities_from_url_english(self):
        response = self._client.post('/entities/from-url', data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert data['results']['entities'][0]['text'] == 'Belgian'
        assert data['results']['entities'][0]['type'] == 'NORP'
        assert len(data['results']['entities']) > 0
        response_with_title = self._client.post('/entities/from-url',
                                                data=dict(url=ENGLISH_ARTICLE_URL, language=ENGLISH, title=1))
        data_with_title = response_with_title.json()
        assert 'results' in data_with_title
        assert 'entities' in data_with_title['results']
        assert len(data['results']['entities']) < len(data_with_title['results']['entities'])

    def test_entities_from_url_korean(self):
        url = "https://web.archive.org/web/20230514220324/https://www.donga.com/news/Economy/article/all/20230503/119113986/1"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=KOREAN))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert 'modelMode' in data
        if data['modelMode'] == MODEL_MODE_SMALL:
            assert len(data['results']['entities']) == 177
        else:
            assert len(data['results']['entities']) == 171

    def test_entities_from_url_french(self):
        url = "https://web.archive.org/web/20220407064224/https://www.letelegramme.fr/soir/alain-souchon-j-ai-un-modele-mick-jagger-05-11-2021-12861556.php"
        response = self._client.post('/entities/from-url', data=dict(url=url, language=FRENCH))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert 'modelMode' in data
        if data['modelMode'] == MODEL_MODE_SMALL:
            assert len(data['results']['entities']) == 253
        else:
            assert len(data['results']['entities']) == 94

    def test_entities_from_url_german(self):
            url = "https://web.archive.org/web/20241009131438/https://musikderzeit.de/"
            response = self._client.post('/entities/from-url', data=dict(url=url, language=GERMAN))
            data = response.json()
            assert 'results' in data
            assert 'entities' in data['results']
            
            assert len(data['results']['entities']) > 0
            assert data['results']['entities'][2]['text'] == 'Gare du Nord Basel'
            assert data['results']['entities'][2]['type'] == 'LOC'
            
            assert 'modelMode' in data
            if data['modelMode'] == MODEL_MODE_SMALL:
                assert len(data['results']['entities']) == 54
            else:
                assert len(data['results']['entities']) >= 54
            

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
        assert len(data['results']['entities']) == 23
        assert 'domain_name' in data['results']
        assert data['results']['domain_name'] == 'europapress.es'

    def test_error_from_url(self):
        response = self._client.post('/entities/from-url', data=dict(
            url="https://app.clickup.com/t/3ymrcbv", language="ES"
        ))
        data = response.json()
        assert 'results' in data
        assert 'entities' in data['results']
        assert len(data['results']['entities']) == 1
        assert data['results']['entities'][0]['text'] == 'ClickUp'
    @pytest.fixture(autouse=True)
    def slow_down_tests(self):
        yield
        time.sleep(1)

if __name__ == "__main__":
    unittest.main()
