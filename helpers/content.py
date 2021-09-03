import logging
from abc import ABC, abstractmethod
import configparser
import newspaper
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

# wait only this many seconds for a server to respond with content. important to keep in sync with central server
DEFAULT_TIMEOUT_SECS = 3

METHOD_NEWSPAPER_3k = 'newspaper3k'
METHOD_GOOSE_3 = 'goose3'
METHOD_BEAUTIFUL_SOUP_4 = 'beautifulsoup4'
METHOD_BOILER_PIPE_3 = 'boilerpipe3'
METHOD_DRAGNET = 'dragnet'
METHOD_READABILITY = 'readability'
METHOD_TRIFILATURA = 'trifilatura'


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
        TrafilaturaExtractor,
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
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        self.timeout_secs = DEFAULT_TIMEOUT_SECS

    def _fetch_content_via_requests(self, url):
        response = requests.get(url, headers={'User-Agent': self.user_agent}, timeout=self.timeout_secs)
        if response.status_code != 200:
            raise RuntimeError("Webpage didn't return content ({}) from {}".format(response.status_code, url))
        if "text/html" not in response.headers["content-type"]:
            raise RuntimeError("Webpage didn't return html content ({}) from {}".format(
                response.headers["content-type"], url))
        return response.text

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
        config = newspaper.Config()
        config.browser_user_agent = self.user_agent
        config.request_timeout = self.timeout_secs
        doc = newspaper.Article(url)
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
        html_text = self._fetch_content_via_requests(url)
        g = Goose()
        g3_article = g.raw_html(html_text)
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
        html_text = self._fetch_content_via_requests(url)
        bp_doc = extractor.get_content(html_text)
        self.content = {
            'url': url,
            'text': bp_doc.content,
            'title': bp_doc.title,
            'publish_date': None,
            'top_image_url': None,
            'authors': None,
            'extraction_method': METHOD_BOILER_PIPE_3,
        }


class TrafilaturaExtractor(AbstractExtractor):

    def extract(self, url: str):
        config = configparser.ConfigParser()
        config['[DEFAULT]'] = dict(USER_AGENTS=self.user_agent,)
        html_text = self._fetch_content_via_requests(url)
        # don't fallback to readability/justext because we have our own hierarchy of things to try
        text = trafilatura.extract(html_text, no_fallback=True)
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
        html_text = self._fetch_content_via_requests(url)
        doc = readability.Document(html_text)
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

    def __init__(self):
        super(RawHtmlExtractor, self).__init__()
        self.is_html = None

    def worked(self) -> bool:
        if self.is_html:
            return super().worked()
        return False

    def extract(self, url: str):
        html_text = self._fetch_content_via_requests(url)
        soup = BeautifulSoup(html_text, 'html.parser')
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
