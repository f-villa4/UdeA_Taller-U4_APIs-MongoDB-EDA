import logging
from pathlib import Path
from typing import Any, List, Tuple

import pandas as pd

from etl.common.config import load_config
from etl.common.db import get_mysql_connection


log = logging.getLogger(__name__)


def _none_if_missing(value: Any) -> Any:
    """
    Convert Pandas missing values into None for MySQL.
    """
    if pd.isna(value):
        return None
    return value


def _ensure_schema(connection) -> None:
    """
    Create the MySQL table for transformed makeup products.
    """
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS makeup_products (
            id INT PRIMARY KEY,
            brand VARCHAR(150) NULL,
            name VARCHAR(255) NOT NULL,
            product_type VARCHAR(100) NULL,
            category VARCHAR(150) NULL,
            price DECIMAL(10, 2) NULL,
            rating DECIMAL(3, 2) NULL,
            currency VARCHAR(20) NULL,
            tag_count INT NULL,
            color_count INT NULL,
            tags TEXT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_sql)

    connection.commit()


def _build_rows(df: pd.DataFrame) -> List[Tuple]:
    """
    Convert a DataFrame into tuples ready for MySQL insertion.
    """
    rows = []

    for product in df.itertuples(index=False):
        rows.append(
            (
                int(product.id),
                _none_if_missing(product.brand),
                _none_if_missing(product.name),
                _none_if_missing(product.product_type),
                _none_if_missing(product.category),
                _none_if_missing(product.price),
                _none_if_missing(product.rating),
                _none_if_missing(product.currency),
                _none_if_missing(product.tag_count),
                _none_if_missing(product.color_count),
                _none_if_missing(product.tags),
            )
        )

    return rows


def _insert_rows(connection, rows: List[Tuple]) -> int:
    """
    Insert transformed products into MySQL using upsert logic.
    """
    if not rows:
        return 0

    insert_sql = """
        INSERT INTO makeup_products (
            id,
            brand,
            name,
            product_type,
            category,
            price,
            rating,
            currency,
            tag_count,
            color_count,
            tags
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            brand = VALUES(brand),
            name = VALUES(name),
            product_type = VALUES(product_type),
            category = VALUES(category),
            price = VALUES(price),
            rating = VALUES(rating),
            currency = VALUES(currency),
            tag_count = VALUES(tag_count),
            color_count = VALUES(color_count),
            tags = VALUES(tags);
    """

    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, rows)

    connection.commit()
    return len(rows)


def load_main() -> None:
    """
    Load the transformed CSV file into MySQL.
    """
    cfg = load_config()
    csv_path = Path(cfg["TRANSFORMED_CSV_PATH"])

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Transformed CSV not found at {csv_path}. Run 'python main.py transform' first."
        )

    log.info("Reading transformed CSV from %s.", csv_path)
    df = pd.read_csv(csv_path)

    connection = get_mysql_connection(cfg)

    try:
        _ensure_schema(connection)
        rows = _build_rows(df)
        inserted_count = _insert_rows(connection, rows)
        log.info("LOAD finished. Upserted %d rows into MySQL.", inserted_count)
    finally:
        connection.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    load_main()