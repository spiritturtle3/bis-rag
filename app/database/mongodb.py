import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "bis_rag")


if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not configured")


client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,
)

db = client[MONGODB_DATABASE]


def check_connection() -> bool:
    """
    Verify that MongoDB is reachable.
    """
    client.admin.command("ping")
    return True