import os
from typing import Any, Dict

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """
    Load project configuration from the .env file.

    The values here define the API source, the MongoDB RAW storage,
    and the output path for transformed data.
    """
    load_dotenv()

    return {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "taller4_db"),
        "MONGO_RAW_COLLECTION": os.getenv("MONGO_RAW_COLLECTION", "raw_data"),
        "MAKEUP_API_URL": os.getenv(
            "MAKEUP_API_URL",
            "https://makeup-api.herokuapp.com/api/v1/products.json",
        ),
        "TRANSFORMED_CSV_PATH": os.getenv(
            "TRANSFORMED_CSV_PATH",
            "data/transformed/makeup_products.csv",
        ),
        "DATABASE_URL": os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root:root@localhost:3306/makeup_etl_db",
        ),
    }