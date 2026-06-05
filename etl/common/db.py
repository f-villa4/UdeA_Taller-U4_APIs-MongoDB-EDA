from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def get_mongo_client(mongo_uri: str) -> MongoClient:
    """
    Create and return a MongoDB client.

    The client represents the connection between Python and the MongoDB server.
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

    If no collection name is provided, the RAW collection from the config is used.
    """
    db = get_mongo_database(cfg)
    target_collection = collection_name or cfg["MONGO_RAW_COLLECTION"]
    return db[target_collection]


def ping_mongo(cfg: dict) -> bool:
    """
    Check if MongoDB is reachable.

    MongoDB only creates databases and collections when data is inserted,
    so this function verifies the connection without creating documents.
    """
    client = get_mongo_client(cfg["MONGO_URI"])
    client.admin.command("ping")
    client.close()
    return True