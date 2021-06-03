import json
import base64
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
from urllib.parse import quote_plus

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
EXTRA_PARAMS = ' -c:a libmp3lame -b:a 128k -map 0:0 -f segment -segment_time 10 -segment_list outputlist.m3u8 -segment_format mpegts output%03d.ts'
FULL_COMMAND = PROCESS_NAME + ' -i ' + MP3_FILENAME + EXTRA_PARAMS

class MusicSplitter:

    def split(self, binary_full_song):
        
        with open(MP3_FILENAME, 'wb') as file:
            file.write(binary_full_song)
        
        subprocess.run(FULL_COMMAND.split())
        return self._read_all_chunks()

    def _read_chunk_bytes(self, chunk_name):
        with open(chunk_name, 'rb') as chunk:
            current_bytes = chunk.read()
            return current_bytes

    def _read_all_chunks(self):
        all_chunks = {}
        files = glob("*.m3u8") + glob("*.ts")
        for current_filename in files:
            all_chunks[current_filename] = self._read_chunk_bytes(current_filename)

        return all_chunks


# --------------------------------------------------------------
# Database methods
# --------------------------------------------------------------
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

# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------
class ChunksPersistence:

    def __init__(self, db):
        self.chunks_col = db.get_chunks_collection()

    def _split_chunks(self, song_base64):
        song_bytes = song_base64.encode("ascii")
        song_bytes = base64.b64decode(song_bytes)
        return MusicSplitter().split(song_bytes)

    def _insert_chunk(self, music_id, name, bytes):
        data = {
            "music_id": str(music_id),
            "chunk_name": name,
            "chunk_bytes": bytes
        }
        self.chunks_col.insert_one(data)

    def insert_song_chunks(self, music_id, song_base64):
        chunks = self._split_chunks(song_base64)
        for key in chunks:
            self._insert_chunk(music_id,
                               key,
                               chunks[key])

    def delete_song_chunks(self, music_id):
        self.chunks_col.delete_many({"music_id": music_id})


class MusicCrud:

    def __init__(self):
        self.db = Database()
        self.musics_col = self.db.get_musics_collection()

    def _music_to_dict(self, db_music):
        res = {
            "id": str(db_music[u'_id']),
            "name": db_music[u'name'],
            "author": db_music[u'author']
        }
        return res

    def insert_update(self, name, author, song_base64):
        music = {
            "name": name,
            "author": author
        }
        music_id = self.musics_col.insert_one(music).inserted_id
        ChunksPersistence(self.db).insert_song_chunks(music_id, song_base64)
        return music_id

    def find_pk(self, music_id):
        try:
            music = self.musics_col.find_one({"_id": ObjectId(music_id)})
            if music is None:
                return "{}"
            else:
                return json.dumps(self._music_to_dict(music))
        except InvalidId:
            return "{}"

    def list(self):
        ret = []
        for db_music in self.musics_col.find():
            music = self._music_to_dict(db_music)
            ret.append(music)
        return json.dumps(ret)

    def delete(self, music_id):
        try:
            res = self.musics_col.delete_one({"_id": ObjectId(music_id)})
            ChunksPersistence(self.db).delete_song_chunks(music_id)
            return res.deleted_count
        except:
            return 0

# --------------------------------------------------------------
# Utilities
# --------------------------------------------------------------

def get_id_from_path(http_path):
    http_path = http_path.split("/")
    http_path = [string for string in http_path if string != ""]
    return http_path[0] if len(http_path) > 0 else None


# --------------------------------------------------------------
# HTTP methods implementation
# --------------------------------------------------------------

class HttpImpl:

    def __init__(self, path, body):
        self.path = path
        self.body = body
        self.crud = MusicCrud()

    def post(self):
        music = json.loads(self.body)
        id = self.crud.insert_update(music.get("name", ""),
                                     music.get("author", ""),
                                     music.get("song_base64", ""))
        return "Record inserted: {}".format(id)

    def get(self):
        id = get_id_from_path(self.path)
        if id is not None:
            return self.crud.find_pk(id)
        else:
            return self.crud.list()

    def delete(self):
        total_deleted = 0
        id = get_id_from_path(self.path)
        if id is not None:
            total_deleted = self.crud.delete(id)
        return "Total records deleted: {}".format(str(total_deleted))

# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------

def handle(event, context):
    try:

        method = event.method
        http = HttpImpl(event.path, event.body)
        
        result = ""
        if method == "POST":
            result = http.post()
        elif method == "GET":
            result = http.get()
        elif method == "DELETE":
            result = http.delete()
        else:
            result = "Method: {} not supported".format(method)

        return {
            "statusCode": 200,
            "headers": {
                "Content-type": "text/plain; charset=utf-8",
                "content-length": len(result),
                "access-control-allow-origin": "*"
            },
            "body": result
        }

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
    bin_content = open('/home/gustavo/Downloads/teste/songs/SkyFullOfStars/SkyFullOfStars.mp3', 'rb').read()
    base64_bytes = base64.b64encode(bin_content)
    base64_string = base64_bytes.decode("ascii")
    req = '{"name":"Sky Full of Stars", "author":"Coldplay", "song_base64": "' + base64_string + '"}'
    res = handle("", "")
    print(res)


