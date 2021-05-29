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
DB_HOST_PORT = '192.168.0.110:27017'

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
    return db.musics

# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------

def crud_find_song_bytes(music_name, music_part):
    collection = db_get_collection()
    db_music = collection.find_one({"name": music_name, "part": music_part})
    return db_music[u'song_bytes']


def detect_content_type(music_part):
    return "application/octet-stream"


# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------

def handle(event, context):
    """handle a request to the function
    Args:
        req (str): request body
    """

    http_path = event.path.split("/")
    http_path = [string for string in http_path if string != ""]
    music_name = http_path[0]
    music_part = http_path[1]

    song_bytes = crud_find_song_bytes(music_name, music_part)
    song_bytes = bytes(song_bytes)
    return {
        "statusCode": 200,
        "headers": {
            "content-type": detect_content_type(music_part),
            "content-length": len(song_bytes),
            "access-control-allow-origin": "*"
        },
        "body": song_bytes
    }


if __name__ == "__main__":
    
    os.environ["gateway_hostname"] = "192.168.0.111"
    os.environ["Http_Path"] = "/BachGavotteShort/output019.ts"
    res = handle("", "")

    # import requests
    # res = requests.get('http://192.168.0.111:8080/function/streaming?id=60a14a57dd64e7d93157e7c6&initial_ms=30000&final_ms=70000').text

    # from pydub.playback import play
    # base64_string = res
    # base64_bytes = base64_string.encode("ascii")
    # music_bytes = base64.b64decode(base64_bytes)
    # music_bytes = res
    # bytesio = io.BytesIO(music_bytes)
    # song = AudioSegment.from_mp3(bytesio)
    # play(song)
    # print(res)
    