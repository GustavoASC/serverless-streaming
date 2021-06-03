# --------------------------------------------------------------
# HTTP methods implementation
# --------------------------------------------------------------

import json
from .MusicCrud import MusicCrud

class HttpImpl:

    def __init__(self, path, body):
        self.path = path
        self.body = body
        self.crud = MusicCrud()

    def _get_id_from_path(self):
        http_path = self.path.split("/")
        http_path = [string for string in http_path if string != ""]
        return http_path[0] if len(http_path) > 0 else None

    def post(self):
        music = json.loads(self.body)
        id = self.crud.insert_update(music.get("name", ""),
                                     music.get("author", ""),
                                     music.get("song_base64", ""))
        return "Record inserted: {}".format(id)

    def get(self):
        id = self._get_id_from_path()
        if id is not None:
            return self.crud.find_pk(id)
        else:
            return self.crud.list()

    def delete(self):
        total_deleted = 0
        id = self._get_id_from_path()
        if id is not None:
            total_deleted = self.crud.delete(id)
        return "Total records deleted: {}".format(str(total_deleted))
