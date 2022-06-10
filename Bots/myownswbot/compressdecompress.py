import base64
import zlib

def compress(data):
    data_bytes = data.encode("utf-8")
    b = zlib.compress(data_bytes)
    c = base64.b64encode(b)
    return c.decode('utf-8')

def decompress(data):
    return zlib.decompress(base64.b64decode(data)).decode('utf-8')
    
