import logging
from newspaper import Article

logger = logging.getLogger(__name__)


def from_url(url: str):
    article = Article(url)
    article.download()
    article.parse()
    return {
        'url': url,
        'text': article.text,
        'title': article.title,
        'publish_date': article.publish_date,
        'top_image_url': article.top_image,
        'authors': article.authors,
    }
