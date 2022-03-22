import os
import sys
from dotenv import load_dotenv
import logging

ENGLISH = 'en'
SPANISH = 'es'
PORTUGUESE = 'pt'
FRENCH = 'fr'
GERMAN = 'de'

LANGUAGES = [ENGLISH, SPANISH, PORTUGUESE, FRENCH, GERMAN]

MODEL_MODE_SMALL = 'small'
MODEL_MODE_LARGE = 'large'
MODEL_MODES = [MODEL_MODE_SMALL, MODEL_MODE_LARGE]

load_dotenv()

VERSION = '2.0.2'

# setup logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s")
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

MODEL_MODE = os.environ.get('MODEL_MODE', MODEL_MODE_SMALL)
if MODEL_MODE not in MODEL_MODES:
    sys.exit("invalid model mode - must be one of [{}]".format(", ".join(MODEL_MODES)))
logger.info("Starting {}, with '{}' models".format(VERSION, MODEL_MODE))

