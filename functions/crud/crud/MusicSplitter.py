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
