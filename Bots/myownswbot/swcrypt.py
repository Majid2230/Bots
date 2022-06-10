# base64 key R3I0UzJlaU5sN3pxNU1yVQ==
#base64 iv AAAAAAAAAAAAAAAAAAAAAA==
import zlib
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

global aeskey
global aesiv

class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key
    def encrypt(self, raw):
        aesiv =  base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==')
        raw = self._pad(raw)
        iv = aesiv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        aesiv =  base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==')
        enc = base64.b64decode(enc)
        iv = aesiv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        data = base64.b64encode(self._unpad(cipher.decrypt(enc))).decode('utf-8')
        return zlib.decompress(base64.b64decode(data)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
        
#if __name__ == "__main__":
#    key = base64.b64decode('R3I0UzJlaU5sN3pxNU1yVQ==')
#    aesiv =  base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==')
#    cryptme = AESCipher(key)
#    hashes = cryptme.encrypt('sad')
#    hashed = 'al+g2yzpK8QDYz1YNNHmQMzeCiH2Rv68Mz3323JheRvG/ok6GiRcQ4TJA4M2iMFT4re+2q7VxljRyJzZl/ZuO0Iswi4FxkGgxgv2GqOf/dvTnuGgzf4bCQhYepyy+HlfiK9y+dhjQOZJhCDT/Xxjc3lSc2CEeOXyjej0/DoHbsbb7ZClGj6I6GKv/9igjn0cxHNrkySc/wdXQwo/EPGI0AOEzNBMMuy/lU1OMRQ/aY3EhE1AKL06pyDTgjAtF3D+nH8eDc9ohq//ZHp1s+zPcau1HTI9ANfetQjTpH2uL4J3yL8Gor/79E/KeR1pSOClbD9BdOnGYnnxiWgTm9bPPNSEr8XudSpSpFVr2biZ9H/1+9j9suqKNqWAavPsYkdCm09uZtDGHhqQOIVc+8zB3MR/rfIeXjpZc3o0FHEAwRgOItmrqOXrcJUABOzkzKoQO5/F2LofhX06i16/8aHpd8v3ZaQUbpIt7O9LSXkrMC/yGT74iKbp0wL3f8HMi7bglsWe8wDBoE0edv/TIapWhbkHyKbUYWgtoJu3fHNFw2+ZIUXuiQD6/1dryl3ivk2SGdTsXGov6d+J3cx3qlkGkw=='
#    unhashed1 = cryptme.decrypt(hashed)
#    print(unhashed1)