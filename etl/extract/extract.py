import logging
from typing import Any, Dict, List

import requests

from etl.common.config import load_config
from etl.common.db import get_mongo_collection


log = logging.getLogger(__name__)


def fetch_makeup_products(api_url: str) -> List[Dict[str, Any]]:
    """
    Fetch makeup products from the public Makeup API.

    The API returns a list of product documents in JSON format.
    At this stage, the data is not transformed.
    """
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Expected the Makeup API response to be a list of products.")

    return data


def save_raw_products(products: List[Dict[str, Any]]) -> int:
    """
    Save raw makeup products into MongoDB.

    Each product is stored as it comes from the API. The product 'id' is used
    only as a lookup key to avoid duplicates when the script is executed again.
    """
    cfg = load_config()
    raw_collection = get_mongo_collection(cfg)

    saved_count = 0

    for product in products:
        product_id = product.get("id")

        if product_id is None:
            log.warning("Skipping product without id: %s", product.get("name"))
            continue

        raw_collection.replace_one(
            {"id": product_id},
            product,
            upsert=True,
        )
        saved_count += 1

    return saved_count


def extract_main() -> None:
    """
    Extract products from Makeup API and load them as RAW documents into MongoDB.
    """
    cfg = load_config()
    api_url = cfg["MAKEUP_API_URL"]

    log.info("Starting RAW ingestion from Makeup API.")
    products = fetch_makeup_products(api_url)

    if len(products) < 100:
        log.warning("The API returned only %d products. The PDF requires at least 100.", len(products))

    saved_count = save_raw_products(products)
    log.info("RAW ingestion finished. Saved %d products into MongoDB.", saved_count)