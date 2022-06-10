from hashlib import sha1
import time

global ts
ts=int(time.time())

def CurrentupTime():
    v5=0x5A8EF52B
    v1=ts-v5
    tsu=22222
    return 1000 * v1 + ((274877907 * tsu >> 38) + ((274877907 * tsu) >> 63))
    
def PlayerServerConnectElapsedTime():
    global ts
    return ((0x5A92AD2B + ((((CurrentupTime() - 0xE86C29C) >> 3) * 0x20C49BA5E353F7CF >> 64) >> 4)) ^ 0x1C2F0688)
    
def getSmonChecker(reqbodyencrypted):
    FinalTS = str(PlayerServerConnectElapsedTime())
    key = '60e2e90bb43b37fb'
    enctxt = reqbodyencrypted
    testsign = key+enctxt+FinalTS
    signituresha1 = testsign.encode('utf-8')
    return sha1(signituresha1).hexdigest().upper()