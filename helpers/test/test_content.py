import unittest

import helpers.content as content


class TestContentFromUrl(unittest.TestCase):

    def test_cnn(self):
        url = "https://www.cnn.com/2021/04/30/politics/mcconnell-1619-project-education-secretary/index.html"
        results = content.from_url(url)
        assert results['url'] == url
        assert len(results['text']) > 100
        assert "McConnell is calling on the education secretary to abandon the idea." in results['text']
        assert results['extraction_method'] == content.METHOD_READABILITY

    def test_from_url_informe_correintes(self):
        url = "http://www.informecorrientes.com/vernota.asp?id_noticia=44619"
        results = content.from_url(url)
        assert results['url'] == url
        assert len(results['text']) > 100
        assert "En este sentido se trabaja en la construcción de sendos canales a cielo abierto" in results['text']
        assert results['extraction_method'] == content.METHOD_READABILITY

    def test_from_url_página_12(self):
        url = "https://www.pagina12.com.ar/338796-coronavirus-en-argentina-se-registraron-26-053-casos-y-561-m"
        results = content.from_url(url)
        assert results['url'] == url
        assert len(results['text']) > 100
        assert "Por otro lado, fueron realizados en el día 84.085 tests" in results['text']
        assert results['extraction_method'] == content.METHOD_READABILITY

    def test_from_url_ahora_noticias(self):
        url = "https://www.ahoranoticias.com.uy/2021/03/son-falsas-las-afirmaciones-de-la-inmunologa-roxana-bruno-integrante-de-la-agrupacion-epidemiologos-argentinos/"
        results = content.from_url(url)
        assert results['url'] == url
        assert len(results['text']) > 100
        assert "Sobre el final de la entrevista Bruno mencionó a distintas" in results['text']
        # Readability returns !200 here, so it falls back to trifilatura
        assert results['extraction_method'] == content.METHOD_TRIFILATURA


if __name__ == "__main__":
    unittest.main()
