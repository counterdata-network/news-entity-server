import os
import requests
import zipfile
import logging
from elasticsearch import Elasticsearch

from urllib.parse import urlparse
from helpers.geo.geonames import GEONAMES_URLS
from helpers.geo import INDEX_NAME
from helpers.geo.index import create_elasticsearch_index, index_geonames_data


logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s][%(levelname)s] %(name)s %(filename)s | %(message)s")
logger = logging.getLogger(__name__)


def download_and_extract(geonames_url: str) -> str:
    temp_dir = os.path.join(os.getcwd(), "tmp")
    logger.debug(f"  Using tmp directory: {temp_dir}")

    # Parse the URL to get the filename
    parsed_url = urlparse(geonames_url)
    filename = os.path.basename(parsed_url.path)
    zip_path = os.path.join(temp_dir, filename)

    # Download if not there already
    if not os.path.exists(zip_path):
        logging.info(f"  Downloading {geonames_url}...")
        response = requests.get(geonames_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"  Download complete: {zip_path}")
    else:
        logger.debug("  Using existing zip file")

    extracted_filename = filename.replace('.zip', '.txt')

    if not os.path.exists(os.path.join(temp_dir, extracted_filename)):
        logger.debug(f"  Extracting to {temp_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        logger.debug("  Extraction complete")
    else:
        logger.debug("  Using existing .txt file")

    return os.path.join(temp_dir, extracted_filename)


if __name__ == "__main__":
    try:
        logger.info("Fetching GeoNames data...")
        downloaded_file_path = download_and_extract(GEONAMES_URLS)
        logger.info(f"  data at: {downloaded_file_path}")
        logger.info("Creating index...")
        es_client = Elasticsearch([os.getenv("ES_SERVER")])
        create_elasticsearch_index(es_client, INDEX_NAME)
        logger.info(f"  empty index at f{INDEX_NAME}")
        logger.info("Indexing geonames data...")
        success, failed = index_geonames_data(es_client, INDEX_NAME, downloaded_file_path)
        logger.info(f"  indexed f{success}, f{len(failed)} failed")
    except Exception as e:
        logger.exception(e)
