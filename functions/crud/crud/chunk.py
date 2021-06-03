# --------------------------------------------------------------
# CRUD methods interacting with database
# --------------------------------------------------------------
import base64
from .split import MusicSplitter

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
