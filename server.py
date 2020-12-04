import logging
from dotenv import load_dotenv
from flask import Flask, request, render_template

import helpers.content as content
import helpers.entities as entities
from helpers.request import arguments_required, form_fields_required, api_method

# setup logging
logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s")
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# load in config from local file or environment variables
load_dotenv()

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


@app.route("/entities/from-url", methods=['POST'])
@form_fields_required('url', 'language')
@api_method
def entities_from_url():
    article_info = content.from_url(request.form['url'])
    return entities.from_text(article_info['text'], request.form['language'])


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
