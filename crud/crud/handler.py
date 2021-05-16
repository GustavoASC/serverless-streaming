import os
import json
import base64
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus, parse_qsl

DB_NAME = 'openfaas'
DB_HOST_PORT = '192.168.0.110:27017'

# --------------------------------------------------------------
#
# Para ver a senha: sudo cat /var/lib/faasd/secrets/basic-auth-password
#
# Para iniciar o container do mongodb: docker run -d -p 27017:27017 -p 28017:28017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo
#
# Para tratar esses parâmetros deve manipular como JSON.
# Exemplo com curl: curl -X POST --header "Content-Type: application/json" --data '{"name":"Teste", "author":"Alok"}' http://192.168.10.247:8080/function/crud
# O que vem em 'req' fica {"name":"Teste", "author":"Alok"}
#
# --------------------------------------------------------------

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

def crud_music_to_dict(db_music):
    res = {
        "id": str(db_music[u'_id']),
        "name": db_music[u'name'],
        "author": db_music[u'author'],
        # "song_base64": db_music[u'song_base64']
    }
    return res


def crud_insert_update(name, author, song_base64):
    collection = db_get_collection()
    music = {
        "name": name,
        "author": author,
        "song_base64": song_base64
    }
    res = collection.insert_one(music)
    return "Record inserted: {}".format(res.inserted_id)


def crud_find_pk(id):
    collection = db_get_collection()
    db_music = collection.find_one({"_id": ObjectId(id)})
    dict_music = crud_music_to_dict(db_music)
    return json.dumps(dict_music)


def crud_list():
    collection = db_get_collection()
    ret = []
    for db_music in collection.find():
        music = crud_music_to_dict(db_music)
        ret.append(music)
    return json.dumps(ret)


def crud_delete(id):
    collection = db_get_collection()
    res = collection.delete_one({"_id": ObjectId(id)})
    return "Total records deleted: {}".format(res.deleted_count)

# --------------------------------------------------------------
# Utilities
# --------------------------------------------------------------

def util_parse_query_params():
    query_string_env = os.getenv('Http_Query')
    query_parsed = parse_qsl(query_string_env)
    query_string_dict = dict(query_parsed)
    return query_string_dict

# --------------------------------------------------------------
# HTTP methods implementation
# --------------------------------------------------------------

def http_post(req):
    music = json.loads(req)
    name = music.get("name", "")
    author = music.get("author", "")
    song_base64 = music.get("song_base64", "")
    return crud_insert_update(name, author, song_base64)


def http_get(req):
    query_params = util_parse_query_params()
    if "id" in query_params:
        id = query_params["id"]
        return crud_find_pk(id)
    else:
        return crud_list()


def http_delete(req):
    id = util_parse_query_params()["id"]
    return crud_delete(id)

# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    try:
        method = os.getenv("Http_Method")

        if method in ["POST", "PUT"]:
            return http_post(req)
        elif method == "GET":
            return http_get(req)
        elif method == "DELETE":
            return http_delete(req)
        else:
            return "Method: {} not supported".format(method)

    except Exception as err:
        return err.message


if __name__ == "__main__":
    # --------------
    # Requisição GET
    # --------------
    # os.environ["Http_Method"] = "GET"
    # os.environ["Http_Query"] = "id=60a11922c56144cd7d5b0d75"
    # res = handle("")
    # res = json.loads(res)
    # # print(res)

    # from pydub import AudioSegment
    # from pydub.playback import play
    # import io

    # if "song_base64" in res:
    #     base64_string = res["song_base64"]
    #     base64_bytes = base64_string.encode("ascii")
    #     sample_string_bytes = base64.b64decode(base64_bytes)
    #     bytesio = io.BytesIO(sample_string_bytes)
    #     song = AudioSegment.from_mp3(bytesio)
    #     play(song)3





    # --------------
    # Requisição POST
    # --------------
    os.environ["Http_Method"] = "POST"
    bin_content = open('/home/gustavo/Downloads/teste.mp3', 'rb').read()
    base64_bytes = base64.b64encode(bin_content)
    base64_string = base64_bytes.decode("ascii")
    req = '{"name":"Outro", "author":"Erasure", "song_base64": "' + base64_string + '"}'

    res = handle(req)
    print(res)

