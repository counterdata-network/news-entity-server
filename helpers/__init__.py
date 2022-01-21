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

MODEL_MODE_EFFICIENCY = 'efficiency'
MODEL_MODE_ACCURACY = 'accuracy'
MODEL_MODES = [MODEL_MODE_EFFICIENCY, MODEL_MODE_ACCURACY]

load_dotenv()

VERSION = '1.5.0'

# setup logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s")
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

MODEL_MODE = os.environ.get('MODEL_MODE', None)
if MODEL_MODE not in MODEL_MODES:
    sys.exit("invalid model mode - must be one of [{}]".format(", ".join(MODEL_MODES)))
logger.info("Starting {}, with '{}' models".format(VERSION, MODEL_MODE))

