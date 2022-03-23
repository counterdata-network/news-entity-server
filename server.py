import logging
import os
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import ignore_logger
from typing import Optional
from fastapi import FastAPI, Form
import mcmetadata

import helpers
import helpers.entities as entities
from helpers.request import api_method

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
        "url": "http://dataculturegroup.org"
    },
)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)  # optional centralized logging to Sentry
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, release=helpers.VERSION)
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
                      language: str = Form(..., description="One of the supported two-letter language codes.", length=2),
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
    found_entities = entities.from_text(article_text, language)
    del article_info['text_content']
    results = article_info | dict(entities=found_entities)
    # for backwards compatability
    results['title'] = results['article_title']
    return results


@app.post("/content/from-url")
@api_method
def content_from_url(url: str = Form(..., description="A publicly accessible web url of a news story.")):
    """
    Return the content found at the URL. This uses a fallback mechanism to iterate through a list of 3rd party content
    extractors. It will try each until it finds one that succeeds.
    """
    return mcmetadata.extract(url)['text_content']


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
        domain_name=mcmetadata.domains.from_url(url) if url is not None else None,
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
        domain_name=mcmetadata.domains.from_url(url),
        url=url,
    )
    return results
