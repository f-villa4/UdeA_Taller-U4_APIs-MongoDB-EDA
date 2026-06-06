from typing import Tuple
from urllib.parse import unquote, urlparse

import pymysql
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def get_mongo_client(mongo_uri: str) -> MongoClient:
    """
    Create and return a MongoDB client.
    """
    return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)


def get_mongo_database(cfg: dict) -> Database:
    """
    Return the MongoDB database configured for the project.
    """
    client = get_mongo_client(cfg["MONGO_URI"])
    return client[cfg["MONGO_DB"]]


def get_mongo_collection(cfg: dict, collection_name: str | None = None) -> Collection:
    """
    Return a MongoDB collection.
    """
    db = get_mongo_database(cfg)
    target_collection = collection_name or cfg["MONGO_RAW_COLLECTION"]
    return db[target_collection]


def ping_mongo(cfg: dict) -> bool:
    """
    Check if MongoDB is reachable.
    """
    client = get_mongo_client(cfg["MONGO_URI"])
    client.admin.command("ping")
    client.close()
    return True


def _parse_mysql_url(database_url: str) -> Tuple[str, str, str, int, str]:
    """
    Parse a mysql+pymysql URL into connection parts.

    Expected format:
    mysql+pymysql://user:password@host:port/database
    """
    parsed = urlparse(database_url)

    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    host = parsed.hostname or "localhost"
    port = int(parsed.port or 3306)
    database = (parsed.path or "/").lstrip("/") or "makeup_etl_db"

    return user, password, host, port, database


def ensure_mysql_database(database_url: str) -> None:
    """
    Create the MySQL database if it does not exist.
    """
    user, password, host, port, database = _parse_mysql_url(database_url)

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset="utf8mb4",
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
    finally:
        connection.close()


def get_mysql_connection(cfg: dict) -> pymysql.connections.Connection:
    """
    Return a MySQL connection using the DATABASE_URL config value.
    """
    database_url = cfg["DATABASE_URL"]
    user, password, host, port, database = _parse_mysql_url(database_url)

    ensure_mysql_database(database_url)

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database,
        charset="utf8mb4",
        autocommit=False,
    )