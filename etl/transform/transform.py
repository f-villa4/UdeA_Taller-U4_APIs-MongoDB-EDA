import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from etl.common.config import load_config
from etl.common.db import get_mongo_collection


log = logging.getLogger(__name__)


def _clean_text(value: Any, default: str = "unknown") -> str:
    """
    Convert a value to clean text.

    Empty values are replaced with a default label so categorical analysis
    becomes easier in Pandas.
    """
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _to_float(value: Any) -> float | None:
    """
    Convert API numeric values to float.

    Makeup API often returns price as text, so this helper makes it usable
    for numerical analysis.
    """
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _count_items(value: Any) -> int:
    """
    Count items when the value is a list.
    """
    if isinstance(value, list):
        return len(value)
    return 0


def _join_tags(value: Any) -> str:
    """
    Convert a list of tags into a readable text column.
    """
    if not isinstance(value, list):
        return ""

    clean_tags = [str(item).strip() for item in value if str(item).strip()]
    return ", ".join(clean_tags)


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert one raw Makeup API product into a flat analytical record.

    This does not modify MongoDB. It only creates a simplified representation
    for CSV export and EDA.
    """
    return {
        "id": product.get("id"),
        "brand": _clean_text(product.get("brand")),
        "name": _clean_text(product.get("name")),
        "product_type": _clean_text(product.get("product_type")),
        "category": _clean_text(product.get("category"), default="uncategorized"),
        "price": _to_float(product.get("price")),
        "rating": _to_float(product.get("rating")),
        "currency": _clean_text(product.get("currency")),
        "tag_count": _count_items(product.get("tag_list")),
        "color_count": _count_items(product.get("product_colors")),
        "tags": _join_tags(product.get("tag_list")),
    }


def transform_products(products: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transform raw product documents into a Pandas DataFrame.
    """
    rows = [normalize_product(product) for product in products]
    return pd.DataFrame(rows)


def transform_main() -> None:
    """
    Read RAW products from MongoDB, transform them, and export a CSV file.
    """
    cfg = load_config()
    raw_collection = get_mongo_collection(cfg)

    log.info("Reading RAW products from MongoDB.")
    products = list(raw_collection.find({}, {"_id": 0}))

    if not products:
        raise RuntimeError("No RAW documents found. Run 'python ingesta.py' first.")

    df = transform_products(products)

    output_path = Path(cfg["TRANSFORMED_CSV_PATH"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, encoding="utf-8")

    log.info("Transformation finished. Exported %d rows to %s.", len(df), output_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    transform_main()