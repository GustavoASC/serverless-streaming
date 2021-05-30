import requests, base64, json

FUNCTION_URL = "http://192.168.10.247:8080/function/crud"

class MusicApi:

    def insert(self, author, music_name, song_path):        
        payload = {
            "author": author,
            "name": music_name,
            "song_base64": self._load_song_base64(song_path)
            # "song_base64": "abc"
        }
        json_payload = json.dumps(payload)
        return requests.post(FUNCTION_URL, data=json_payload).text

    def remove(self, music_id):
        final_url = FUNCTION_URL + "/" + music_id
        return requests.delete(final_url).text

    def get(self, music_id):
        final_url = FUNCTION_URL + "/" + music_id
        return requests.get(final_url).text

    def list(self):
        return requests.get(FUNCTION_URL).text

    ### Utility methods

    def _load_song_base64(self, song_path):
        song_binary_content = open(song_path, 'rb').read()
        return self._convert_binary_base64(song_binary_content)

    def _convert_binary_base64(self, binary_content):
        base64_bytes = base64.b64encode(binary_content)
        return base64_bytes.decode("ascii")


if __name__ == "__main__":

    res = MusicApi().insert("Teste", "Musica teste", '/home/gustavo/Downloads/Music.mp3')
    print(res)
