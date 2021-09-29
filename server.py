import logging
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import ignore_logger

from helpers import VERSION
import helpers.content as content
import helpers.entities as entities
from helpers.request import form_fields_required, api_method


# setup logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s")
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# load in config from local file or environment variables
load_dotenv()

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)  # optional centralized logging to Sentry
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, release=VERSION,
                    integrations=[FlaskIntegration()])
    # make sure some errors we don't care about don't make it to sentry
    ignore_logger("helpers.request")
    ignore_logger("boilerpy3")
    ignore_logger("trafilatura.utils")
    ignore_logger("trafilatura.core")
    ignore_logger("readability.readability")
    logger.info("  SENTRY_DSN: {}".format(SENTRY_DSN))
else:
    logger.info("Not logging errors to Sentry")

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


def _parse_title_option(value: str):
    try:
        return int(value)
    except:
        return 0


@app.route("/entities/from-url", methods=['POST'])
@form_fields_required('url', 'language')
@api_method
def entities_from_url():
    article_info = content.from_url(request.form['url'])
    include_title = _parse_title_option(request.form.get('title', None))  # should be a 1 or a 0
    article_text = ""
    if include_title and (article_info['title'] is not None):
        article_text += article_info['title'] + " "
    article_text += article_info['text']
    return entities.from_text(article_text, request.form['language'])


@app.route("/content/from-url", methods=['POST'])
@form_fields_required('url')
@api_method
def content_from_url():
    return content.from_url(request.form['url'])


@app.route("/entities/from-content", methods=['POST'])
@form_fields_required('text', 'language')
@api_method
def entities_from_content():
    return entities.from_text(request.form['text'], request.form['language'])


if __name__ == "__main__":
    app.debug = True
    app.run()
