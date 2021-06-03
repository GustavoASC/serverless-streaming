from .Database import Database
from .ChunksPersistence import ChunksPersistence
from bson.objectid import ObjectId, InvalidId
import json

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
