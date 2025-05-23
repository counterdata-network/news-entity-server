import logging
import os
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import ignore_logger
from typing import Optional, Dict
from fastapi import FastAPI, Form
import mcmetadata
import uvicorn

import helpers
import helpers.entities as entities
from helpers.request import api_method
from helpers.exceptions import UnknownLanguageException

logger = logging.getLogger(__name__)

app = FastAPI(
    title="News Entity Server",
    description="Extract entities from online news in multiple languages",
    version=helpers.VERSION,
    license_info={
        "name": "The MIT License"
    },
    contact={
        "name": "Rahul Bhargava",
        "email": "r.bhargava@northeastern.edu",
        "url": "https://dataculture.northeastern.edu"
    },
)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)  # optional centralized logging to Sentry
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, release=helpers.VERSION,
                    ignore_errors=[UnknownLanguageException])
    # make sure some errors we don't care about don't make it to sentry
    ignore_logger("boilerpy3")
    ignore_logger("trafilatura.utils")
    ignore_logger("trafilatura.core")
    ignore_logger("readability.readability")
    logger.info("  SENTRY_DSN: {}".format(SENTRY_DSN))
    try:
        app.add_middleware(SentryAsgiMiddleware)
    except Exception:
        # pass silently if the Sentry integration failed
        pass
else:
    logger.info("Not logging errors to Sentry")


# HACK: ovveride mcmetadata timeout to be longer
mcmetadata.webpages.DEFAULT_TIMEOUT_SECS = 60*5


@app.get("/version")
@api_method
def version():
    return {}


@app.get("/languages")
@api_method
def supported_languages():
    return helpers.LANGUAGES


@app.post("/entities/from-url")
@api_method
def entities_from_url(url: str = Form(..., description="A publicly accessible web url of a news story."),
                      title: Optional[int] = Form(None, description="Optional 1 or 0 indicating if the title should be prefixed the content before checking for entities.",)):
    """
    Return all the entities found in content extracted from the URL.
    """
    article_info = mcmetadata.extract(url)
    include_title = title == 1 if title is not None else False
    article_text = ""
    if include_title and (article_info['article_title'] is not None):
        article_text += article_info['article_title'] + " "
    article_text += article_info['text_content']
    found_entities = entities.from_text(article_text, article_info['language'])
    results = article_info | dict(entities=found_entities)
    results = _backwards_compatible_results(results)
    del results['text']
    return results


@app.post("/content/from-url")
@api_method
def content_from_url(url: str = Form(..., description="A publicly accessible web url of a news story.")):
    """
    Return the content found at the URL. This uses a fallback mechanism to iterate through a list of 3rd party content
    extractors. It will try each until it finds one that succeeds.
    """
    results = mcmetadata.extract(url)
    results = _backwards_compatible_results(results)
    # for backwards compatability
    return results


def _backwards_compatible_results(results: Dict) -> Dict:
    results['text'] = results['text_content']
    del results['text_content']
    results['title'] = results['article_title']
    del results['article_title']
    results['url'] = results['original_url']
    del results['original_url']
    results['domain_name'] = results['canonical_domain']
    del results['canonical_domain']
    return results


@app.post("/entities/from-content")
@api_method
def entities_from_content(text: str = Form(..., description="Raw text to check for entities."),
                          language: str = Form(..., description="One of the supported two-letter language codes.", length=2),
                          url: Optional[str] = Form(..., description="Helpful for some metadata if you pass in the original URL (optional).")):
    """
    Return all the entities found in content passed in.
    """
    results = dict(
        entities=entities.from_text(text, language),
        domain_name=mcmetadata.urls.canonical_domain(url) if url is not None else None,
        url=url
    )
    return results


@app.post("/entities/from-html")
@api_method
def entities_from_html(html: str = Form(..., description="Raw HTML to check for entities."),
                       language: str = Form(..., description="One of the supported two-letter language codes.", length=2),
                       url: Optional[str] = Form(..., description="Helpful for some metadata if you pass in the original URL (optional).")):
    """
    Return all the entities found in content from HTML passed in.
    """
    content = mcmetadata.content.from_html(url, html)
    results = dict(
        entities=entities.from_text(content['text'], language),
        domain_name=mcmetadata.urls.canonical_domain(url) if url is not None else None,
        url=url
    )
    return results


@app.post("/domains/from-url")
@api_method
def domain_from_url(url: str = Form(..., description="A publicly accessible web url of a news story.")):
    """
    Return the useful "canonical" domain for a url
    """
    results = dict(
        domain_name=mcmetadata.urls.canonical_domain(url),
        url=url,
    )
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
