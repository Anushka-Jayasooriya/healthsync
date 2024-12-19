from pymongo import MongoClient
from .config import settings

class Database:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            cls.client = MongoClient(settings.MONGO_URL)
            cls.db = cls.client[settings.DB_NAME]
        return cls.db

    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.connect()
        return db[collection_name]