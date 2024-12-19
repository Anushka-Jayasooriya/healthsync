from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "health")

class Database:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            cls.client = MongoClient(MONGO_URL)
            cls.db = cls.client[DB_NAME]
        return cls.db

    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.connect()
        return db[collection_name]