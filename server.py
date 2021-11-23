import logging
import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import ignore_logger
from typing import Optional, Dict
import time

import helpers
import helpers.content as content
import helpers.entities as entities

from fastapi import FastAPI, Form

# setup logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s")
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# load in config from local file or environment variables
load_dotenv()

app = FastAPI(
    title="News Entity Server",
    description="Extract entities from online news in multiple langauges",
    version=helpers.VERSION,
    license_info={
        "name": "The MIT License"
    }
)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)  # optional centralized logging to Sentry
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, release=helpers.VERSION)
    # make sure some errors we don't care about don't make it to sentry
    ignore_logger("helpers.request")
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


def _as_api_results(data: Dict, start_time: float) -> Dict:
    return {
        'version': helpers.VERSION,
        'status': 'ok',
        'duration': int(round((time.time() - start_time) * 1000)),
        'results': data
    }


@app.get("/version")
def version():
    start_time = time.time()
    return _as_api_results({}, start_time)


@app.get("/languages")
def supported_languages():
    start_time = time.time()
    return _as_api_results(helpers.LANGUAGES, start_time)


@app.post("/entities/from-url")
def entities_from_url(url: str = Form(..., description="A publicly accessible web url of a news story."),
                      language: str = Form(..., description="One of the supported two-letter language codes.", length=2),
                      title: Optional[int] = Form(None, description="Optional 1 or 0 indicating if the title should be prefixed the content before checking for entities.",)):
    """
    Return all the entities found in content extracted from the URL.
    """
    start_time = time.time()
    article_info = content.from_url(url)
    include_title = title == 1 if title is not None else False
    article_text = ""
    if include_title and (article_info['title'] is not None):
        article_text += article_info['title'] + " "
    article_text += article_info['text']
    data = entities.from_text(article_text, language)
    return _as_api_results(data, start_time)


@app.post("/content/from-url")
def content_from_url(url: str = Form(..., description="A publicly accessible web url of a news story.")):
    """
    Return the content found at the URL. This uses a fallback mechanism to iterate through a list of 3rd party content
    extractors. It will try each until it finds one that succeeds.
    """
    start_time = time.time()
    data = content.from_url(url)
    return _as_api_results(data, start_time)


@app.post("/entities/from-content")
def entities_from_content(text: str = Form(..., description="Raw text to check for entities."),
                          language: str = Form(..., description="One of the supported two-letter language codes.", length=2)):
    """
    Return all the entities found in content passed in.
    """
    start_time = time.time()
    data = entities.from_text(text, language)
    return _as_api_results(data, start_time)
