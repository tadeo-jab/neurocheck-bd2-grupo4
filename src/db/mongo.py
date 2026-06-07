from pymongo import MongoClient
from pymongo.database import Database


class MongoService:
    def __init__(self, uri: str, database: str = "neurocheck"):
        self.uri = uri
        self.database_name = database
        self._client: MongoClient | None = None
        self.db: Database | None = None

    def connect(self):
        self._client = MongoClient(self.uri)
        self.db = self._client[self.database_name]

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None
            self.db = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()
