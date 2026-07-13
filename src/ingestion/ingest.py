"""
ingest.py
Downloads Inside Airbnb data files for a configured city.

"""

import logging
import time
import yaml
import requests
from pathlib import Path
from datetime import datetime

# ---------- Setup ----------

def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_logging(log_dir: str) -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # also prints to terminal
        ]
    )
    return logging.getLogger(__name__)


# ---------- Core download logic ----------

def download_file(url: str, dest_path: Path, retries: int, delay: int, logger: logging.Logger) -> bool:
    """Downloads a single file with retry logic. Returns True on success."""
    if url == "PASTE_URL_HERE" or not url:
        logger.warning(f"Skipping {dest_path.name}: no URL configured.")
        return False

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Downloading {dest_path.name} (attempt {attempt}/{retries})...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # raises an error if status code is 4xx/5xx

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(response.content)

            size_kb = dest_path.stat().st_size / 1024
            logger.info(f"Saved {dest_path.name} ({size_kb:.1f} KB)")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {attempt} failed for {dest_path.name}: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All {retries} attempts failed for {dest_path.name}. Giving up.")
                return False


# ---------- Main pipeline ----------

def run_ingestion(config: dict, logger: logging.Logger) -> dict:
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    retries = config["pipeline"]["retry_attempts"]
    delay = config["pipeline"]["retry_delay_seconds"]

    files_to_download = {
        "listings.csv.gz": config["city"]["listings_url"],
        "calendar.csv.gz": config["city"]["calendar_url"],
        "reviews.csv.gz": config["city"]["reviews_url"],
        "neighbourhoods.csv": config["city"]["neighbourhoods_url"],
        "neighbourhoods.geojson": config["city"]["neighbourhoods_geojson_url"],
    }

    logger.info(f"Starting ingestion for city: {city}")
    results = {}
    for filename, url in files_to_download.items():
        dest = raw_dir / filename
        success = download_file(url, dest, retries, delay, logger)
        results[filename] = "SUCCESS" if success else "FAILED/SKIPPED"

    logger.info("Ingestion run complete. Summary:")
    for filename, status in results.items():
        logger.info(f"  {filename}: {status}")

    return results


if __name__ == "__main__":
    config = load_config()
    logger = setup_logging(config["paths"]["log_dir"])
    run_ingestion(config, logger)