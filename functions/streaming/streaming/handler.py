import os
from pymongo import MongoClient
from urllib.parse import quote_plus

# --------------------------------------------------------------
# Para fazer o deploy desta função é necessário instalar o ffmpeg no Linux.
# Não é a biblioteca do Python, é no Linux mesmo.
#
# Para isso usar a command-line abaixo:
#
# faas-cli up -f streaming.yml --build-arg ADDITIONAL_PACKAGE=ffmpeg
# --------------------------------------------------------------

DB_NAME = 'openfaas'
DB_HOST_PORT = '192.168.10.165:27017'

# --------------------------------------------------------------
# Database methods
# --------------------------------------------------------------

def db_get_uri():
    host = DB_HOST_PORT
    password = "admin"
    username = "admin"
    return "mongodb://%s:%s@%s" % (quote_plus(username), quote_plus(password), host)

def db_get_mongo_client():
    uri = db_get_uri()
    return MongoClient(uri)

def db_get_collection():
    client = db_get_mongo_client()
    db = client[DB_NAME]
    return db.chunks

# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------

def crud_find_song_bytes(music_id, chunk_name):
    collection = db_get_collection()
    db_music = collection.find_one({"music_id": music_id, "chunk_name": chunk_name})
    return db_music[u'chunk_bytes']

# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------

def handle(event, context):
    """handle a request to the function
    Args:
        req (str): request body
    """
    try:
        http_path = event.path
        http_path = http_path.split("/")
        http_path = [string for string in http_path if string != ""]
        music_id = http_path[0]
        chunk_name = http_path[1]

        song_bytes = crud_find_song_bytes(music_id, chunk_name)
        return {
            "statusCode": 200,
            "headers": {
                "Content-type": "application/octet-stream",
                "content-length": len(song_bytes),
                "access-control-allow-origin": "*"
            },
            "body": song_bytes
        }
    except Exception as err:
        return str(err)


if __name__ == "__main__":
    
    res = handle("", "")
    text_result = res["body"]
    print(text_result)
