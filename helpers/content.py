import logging
from abc import ABC, abstractmethod
from newspaper import Article
from goose3 import Goose
import typing
import requests
from bs4 import BeautifulSoup
from boilerpy3 import extractors as bp3_extractors
import readability
import trafilatura
import regex as re

logger = logging.getLogger(__name__)

MINUMUM_CONTENT_LENGTH = 200  # less than this and it doesn't count as working extraction (experimentally determined)

METHOD_NEWSPAPER_3k = 'newspaper3k'
METHOD_GOOSE_3 = 'goose3'
METHOD_BEAUTIFUL_SOUP_4 = 'beautifulsoup4'
METHOD_BOILER_PIPE_3 = 'boilerpipe3'
METHOD_DRAGNET = 'dragnet'
METHOD_READABILITY = 'readability'
METHOD_TRIFILATURA = 'trifilatura'


def _default_headers() -> typing.Dict:
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }


def from_url(url: str) -> typing.Dict:
    """
    Try a series of extractors to pull content out of the HTML at a URL. The idea is to try as hard as can to get
    good content, but fallback to at least get something useful. The writeup at this site was very helpful:
    https://adrien.barbaresi.eu/blog/evaluating-text-extraction-python.html
    :param url: the webpage to try and parse
    :return: a dict of with url, text, title, publish_date, top_image_url, authors, and extraction_method keys
    """
    order = [  # based by findings from trifilatura paper, but customized to performance on EN and ES sources (see test)
        ReadabilityExtractor,
        TrifilaturaExtractor,
        BoilerPipe3Extractor,
        GooseExtractor,
        Newspaper3kExtractor,
        RawHtmlExtractor  # this one should never fail (if there is any content at all) because it just parses HTML
    ]
    for extractor_class in order:
        try:
            extractor = _extract(url, extractor_class)
            if extractor.worked():
                return extractor.content
        except Exception as e:
            # if the extractor fails for any reason, just continue on to the next one
            pass
    raise RuntimeError("Tried all the extractors and none worked!")


class AbstractExtractor(ABC):

    def __init__(self):
        self.content = None

    @abstractmethod
    def extract(self, url: str):
        pass

    def worked(self) -> bool:
        return (self.content is not None) and (len(self.content['text']) > MINUMUM_CONTENT_LENGTH)


def _extract(url: str, extract_implementation) -> AbstractExtractor:
    extractor = extract_implementation()
    extractor.extract(url)
    return extractor


class Newspaper3kExtractor(AbstractExtractor):

    def extract(self, url):
        doc = Article(url)
        doc.download()
        doc.parse()
        self.content = {
            'url': url,
            'text': doc.text,
            'title': doc.title,
            'publish_date': doc.publish_date,
            'top_image_url': doc.top_image,
            'authors': doc.authors,
            'extraction_method': METHOD_NEWSPAPER_3k,
        }


class GooseExtractor(AbstractExtractor):

    def extract(self, url):
        g = Goose({'browser_user_agent': 'Mozilla'})
        g3_article = g.extract(url=url)
        self.content = {
            'url': url,
            'text': g3_article.cleaned_text,
            'title': g3_article.title,
            'publish_date': g3_article.publish_date,
            'top_image_url': g3_article.top_image.src if g3_article.top_image else None,
            'authors': g3_article.authors,
            'extraction_method': METHOD_GOOSE_3,
        }


class BoilerPipe3Extractor(AbstractExtractor):

    def extract(self, url: str):
        extractor = bp3_extractors.ArticleExtractor()
        bp_doc = extractor.get_doc_from_url(url)
        self.content = {
            'url': url,
            'text': bp_doc.content,
            'title': bp_doc.title,
            'publish_date': None,
            'top_image_url': None,
            'authors': None,
            'extraction_method': METHOD_BOILER_PIPE_3,
        }


class TrifilaturaExtractor(AbstractExtractor):

    def extract(self, url: str):
        downloaded = trafilatura.fetch_url(url)
        # don't fallback to readability/justext because we have our own hierarchy of things to try
        text = trafilatura.extract(downloaded, no_fallback=True)
        self.content = {
            'url': url,
            'text': text,
            'title': None,
            'publish_date': None,
            'top_image_url': None,
            'authors': None,
            'extraction_method': METHOD_TRIFILATURA,
        }


class ReadabilityExtractor(AbstractExtractor):

    def extract(self, url: str):
        response = requests.get(url, headers=_default_headers())
        if response.status_code != 200:
            return
        doc = readability.Document(response.text)
        self.content = {
            'url': url,
            'text': re.sub('<[^<]+?>', '', doc.summary()),  # need to remove any tags
            'title': doc.title(),
            'publish_date': None,
            'top_image_url': None,
            'authors': None,
            'extraction_method': METHOD_READABILITY,
        }


class RawHtmlExtractor(AbstractExtractor):

    def extract(self, url: str):
        res = requests.get(url, headers=_default_headers())
        if res.status_code != 200:
            return
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)
        output = ''
        remove_list = [
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head',
            'input',
            'script',
        ]
        for t in text:
            if t.parent.name not in remove_list:
                output += '{} '.format(t)
        self.content = {
            'url': url,
            'text': output,
            'title': None,
            'publish_date': None,
            'top_image_url': None,
            'authors': None,
            'extraction_method': METHOD_BEAUTIFUL_SOUP_4,
        }
