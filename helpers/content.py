import logging
from newspaper import Article

logger = logging.getLogger(__name__)


def from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return {
        'url': url,
        'text': article.text,
        'publish_date': article.publish_date,
        'top_image_url': article.top_image,
        'authors': article.authors,
    }
