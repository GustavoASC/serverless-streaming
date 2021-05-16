import wave, os, requests

CHUNK = 1024


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    gateway_hostname = os.getenv("gateway_hostname", "gateway")
    r = requests.get("http://" + gateway_hostname + ":8080/function/sentimentanalysis")

    wf = wave.open(req.strip(), 'rb')
    
    result = ''
    
    data = wf.readframes(CHUNK)
    while data != b'':
        result += "".join(map(chr, data))
        data = wf.readframes(CHUNK)

    return result

