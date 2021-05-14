import wave

CHUNK = 1024

def handle(audio_name):

    wf = wave.open(audio_name.strip(), 'rb')
    
    result = ''
    
    data = wf.readframes(CHUNK)
    while data != b'':
        result += "".join(map(chr, data))
        data = wf.readframes(CHUNK)

    return result
