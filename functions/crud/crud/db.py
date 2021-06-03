# --------------------------------------------------------------
# Database operations
# --------------------------------------------------------------
from pymongo import MongoClient
from urllib.parse import quote_plus

DB_NAME = 'openfaas'
DB_HOST_PORT = '192.168.10.165:27017'

class Database:

    def _get_uri(self):
        host = DB_HOST_PORT
        password = "admin"
        username = "admin"
        return "mongodb://%s:%s@%s" % (quote_plus(username), quote_plus(password), host)

    def _get_mongo_client(self):
        uri = self._get_uri()
        return MongoClient(uri)

    def get_musics_collection(self):
        client = self._get_mongo_client()
        db = client[DB_NAME]
        return db.musics

    def get_chunks_collection(self):
        client = self._get_mongo_client()
        db = client[DB_NAME]
        return db.chunks

