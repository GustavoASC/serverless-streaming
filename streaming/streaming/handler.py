import os, base64, io
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus, parse_qsl
from pydub import AudioSegment

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
# Utilities
# --------------------------------------------------------------

def util_parse_query_params():
    query_string_env = os.getenv('Http_Query')
    query_parsed = parse_qsl(query_string_env)
    query_string_dict = dict(query_parsed)
    return query_string_dict

def convert_bytes_to_song(song_bytes):
    bytesio = io.BytesIO(song_bytes)
    return AudioSegment.from_mp3(bytesio)

# --------------------------------------------------------------
# Base64 encoding/decoding
# --------------------------------------------------------------

def encode_bytes_to_base64_string(bytes):
    base64_bytes = base64.b64encode(bytes)
    return base64_bytes.decode("ascii")
    
def decode_base64_string_to_bytes(base64_string):
    base64_bytes = base64_string.encode("ascii")
    return base64.b64decode(base64_bytes)

# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------

def crud_find_song_base64_pk(id):
    collection = db_get_collection()
    db_music = collection.find_one({"_id": ObjectId(id)})
    return db_music[u'song_base64']

def slice_song(song_base64, initial_ms, final_ms):
    decoded_bytes = decode_base64_string_to_bytes(song_base64)
    song = convert_bytes_to_song(decoded_bytes)
    return song[initial_ms:final_ms]

# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    query_params = util_parse_query_params()
    if "id" not in query_params:
        return "error id not found"
    elif "initial_ms" not in query_params:
        return "error initial_ms not found"
    elif "final_ms" not in query_params:
        return "error final_ms not found"

    id = query_params["id"]
    initial_ms = query_params["initial_ms"]
    initial_ms = int(initial_ms)
    final_ms = query_params["final_ms"]
    final_ms = int(final_ms)

    song_base64 = crud_find_song_base64_pk(id)
    sliced_song = slice_song(song_base64, initial_ms, final_ms)

    
    output_bytes = io.BytesIO()
    sliced_song.export(output_bytes)

    encoded_sliced = encode_bytes_to_base64_string(output_bytes.getvalue())
    return encoded_sliced









if __name__ == "__main__":
    os.environ["gateway_hostname"] = "192.168.0.111"
    os.environ["Http_Query"] = "id=60a14a57dd64e7d93157e7c6&initial_ms=55000&final_ms=65000"
    res = handle("")


    from pydub.playback import play
    base64_string = res
    base64_bytes = base64_string.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    bytesio = io.BytesIO(sample_string_bytes)
    song = AudioSegment.from_mp3(bytesio)
    play(song)





    print(res)
