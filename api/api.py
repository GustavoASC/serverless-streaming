import requests, base64, json

FUNCTION_URL = "http://192.168.10.247:8080/function/crud"

class MusicApi:

    def insert(self, author, music_name, song_path):        
        payload = {
            "author": author,
            "name": music_name,
            "song_base64": self._load_song_base64(song_path)
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

    def _load_song_base64(self, song_path):
        song_binary_content = open(song_path, 'rb').read()
        return self._convert_binary_base64(song_binary_content)

    def _convert_binary_base64(self, binary_content):
        base64_bytes = base64.b64encode(binary_content)
        return base64_bytes.decode("ascii")


if __name__ == "__main__":

    import json

    api = MusicApi()

    print("Adding musics...")
    print(api.insert("Madonna", "Like a Prayer", '/home/gustavo/Downloads/Like_A_Prayer.mp3'))
    print(api.insert("Coldplay", "Sky Full of Stars", '/home/gustavo/Downloads/teste/songs/SkyFullOfStars/SkyFullOfStars.mp3'))
    print(api.insert("Erasure", "A Little Respect", '/home/gustavo/Downloads/A_Little_Respect.mp3'))
    print(api.insert("a-ha", "Take on me", '/home/gustavo/Downloads/TakeOnMe.mp3'))

    print()
    print("Listing musics...")
    all_musics = json.loads(api.list())
    for music in all_musics:
        print(music)

    print()
    print("Printing specific music data...")
    for music in all_musics:
        print(api.get(music["id"]))

    print()
    print("Printing data which does not exist...")
    print(api.get("11111"))
    print(api.get("22222"))
    print(api.get("33333"))

    print()
    print("Deleting musics...")
    for music in all_musics:
        print(api.remove(music["id"]))

    print()
    print("Listing musics...")
    all_musics = json.loads(api.list())
    for music in all_musics:
        print(music)

