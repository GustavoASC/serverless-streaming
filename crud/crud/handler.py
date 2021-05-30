import os
import json
import base64
from types import TracebackType
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
from urllib.parse import quote_plus

DB_NAME = 'openfaas'
DB_HOST_PORT = '192.168.10.165:27017'

# --------------------------------------------------------------
#
# Para ver a senha: sudo cat /var/lib/faasd/secrets/basic-auth-password
#
# Para iniciar o container do mongodb: docker run -d -p 27017:27017 -p 28017:28017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo
#
# Para tratar esses parâmetros deve manipular como JSON.
# Exemplo com curl: curl -X POST --header "Content-Type: application/json" --data '{"name":"Teste", "author":"Alok"}' http://192.168.10.165:8080/function/crud
# O que vem em 'req' fica {"name":"Teste", "author":"Alok"}
#
# Para fazer o deploy desta função é necessário instalar o ffmpeg no Linux.
# Não é a biblioteca do Python, é no Linux mesmo.
#
# Para isso usar a command-line abaixo:
#
# faas-cli up -f crud.yml --build-arg ADDITIONAL_PACKAGE=ffmpeg
# --------------------------------------------------------------


## ------------------------------------
## Class to split song into multiple chunks
## ------------------------------------
import subprocess
from glob import glob

MP3_FILENAME = 'music.mp3'
PROCESS_NAME = 'ffmpeg'
FULL_COMMAND = PROCESS_NAME + ' -i ' + MP3_FILENAME + ' -c:a libmp3lame -b:a 128k -map 0:0 -f segment -segment_time 10 -segment_list outputlist.m3u8 -segment_format mpegts output%03d.ts'

class MusicSplitter:

    def split(self, binary_full_song):
        
        with open(MP3_FILENAME, 'wb') as file:
            file.write(binary_full_song)
        
        subprocess.run(FULL_COMMAND.split())

        all_chunks = {}
        files = glob("*.m3u8") + glob("*.ts")
        for current_filename in files:
            with open(current_filename, 'rb') as chunk:
                current_bytes = chunk.read()
                all_chunks[current_filename] = current_bytes

        return all_chunks




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

def db_get_musics_collection():
    client = db_get_mongo_client()
    db = client[DB_NAME]
    return db.musics

def db_get_chunks_collection():
    client = db_get_mongo_client()
    db = client[DB_NAME]
    return db.chunks

# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------

def crud_music_to_dict(db_music):
    res = {
        "id": str(db_music[u'_id']),
        "name": db_music[u'name'],
        "author": db_music[u'author']
    }
    return res


def crud_insert_update(name, author):
    collection = db_get_musics_collection()
    music = {
        "name": name,
        "author": author
    }
    res = collection.insert_one(music)
    return res.inserted_id


def crud_find_pk(id):
    collection = db_get_musics_collection()
    try:
        db_music = collection.find_one({"_id": ObjectId(id)})
        if db_music is not None:
            dict_music = crud_music_to_dict(db_music)
            return json.dumps(dict_music)
        else:
            return "{}"
    except InvalidId:
        return "{}"


def crud_list():
    collection = db_get_musics_collection()
    ret = []
    for db_music in collection.find():
        music = crud_music_to_dict(db_music)
        ret.append(music)
    return json.dumps(ret)


def crud_delete(id):
    collection = db_get_musics_collection()
    try:
        res = collection.delete_one({"_id": ObjectId(id)})
        return res.deleted_count
    except:
        return 0

# --------------------------------------------------------------
# Utilities
# --------------------------------------------------------------

def parse_http_path():
    http_path = os.getenv('Http_Path')
    http_path = http_path.split("/")
    http_path = [string for string in http_path if string != ""]
    return http_path

def get_id_from_path():
    http_path = os.getenv('Http_Path')
    http_path = http_path.split("/")
    http_path = [string for string in http_path if string != ""]
    return http_path[0] if len(http_path) > 0 else None


# --------------------------------------------------------------
# HTTP methods implementation
# --------------------------------------------------------------

def http_post(req):

    music = json.loads(req)

    song_base64 = music.get("song_base64", "")
    song_bytes = song_base64.encode("ascii")
    song_bytes = base64.b64decode(song_bytes)
    music_chunks = MusicSplitter().split(song_bytes)


    name = music.get("name", "")
    author = music.get("author", "")
    id = crud_insert_update(name, author)

    chunks_collection = db_get_chunks_collection()
    for key in music_chunks:
        chunk = {
            "music_id": str(id),
            "chunk_name": key,
            "chunk_bytes": music_chunks[key]
        }
        chunks_collection.insert_one(chunk)
        
    return "Record inserted: {}".format(id)



def http_get(req):
    id = get_id_from_path()
    if id is not None:
        return crud_find_pk(id)
    else:
        return crud_list()

def http_delete(req):
    total_deleted = 0
    id = get_id_from_path()
    if id is not None:
       total_deleted = crud_delete(id)
    return "Total records deleted: {}".format(str(total_deleted))

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
        return str(err)








if __name__ == "__main__":
    # --------------
    # Requisição GET (chamando diretamente a função)
    # --------------
    # os.environ["Http_Method"] = "DELETE"
    # os.environ["Http_Path"] = "/60b3914bd78ebfe0fe29ae51"
    # res = handle("")
    # res = json.loads(res)
    # print(res)

    # --------------
    # Requisição POST
    # --------------
    os.environ["Http_Method"] = "POST"
    bin_content = open('/home/gustavo/Downloads/teste/songs/SkyFullOfStars/SkyFullOfStars.mp3', 'rb').read()
    base64_bytes = base64.b64encode(bin_content)
    base64_string = base64_bytes.decode("ascii")
    req = '{"name":"Sky Full of Stars", "author":"Coldplay", "song_base64": "' + base64_string + '"}'
    res = handle(req)
    print(res)


