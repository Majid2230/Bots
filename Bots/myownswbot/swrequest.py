import requests
import swcrypt
import zlib
import base64
from numpy import random
from time import sleep
import summonerchecker
from requests_toolbelt.utils import dump

def GB12(hashed_data,SmonTmVal,SmonChecker):
    SmonTmVal = SmonTmVal
    SmonChecker = SmonChecker
    cookies = {"advertising_id":"96E43F82-1CC8-4B83-A3B1-F239252313E8", "analytics_id":"fMHZGMhcTaWxJWDNm8r7xg%3D%3D", "appid":"com.com2us.smon.normal.freefull.apple.kr.ios.universal", "device":"iPhone8%2C1", "deviceLanguage":"en", "device_country":"SA", "did":"1028215380", "enable_cookie":"no", "hive_config_language":"en_US", "hive_config_nationality":"SA", "inquiry_language":"en_US", "native_version":"Hub+v.2.8.8", "osversion":"14.4", "peppermint":"Na49rrQNH7i6uw%2BURB6Le5AdGB8DmHUfRnsyUwgxIBm%2FVFzfEbvAa6ynmtNMKjFI1WQCrQB7SDNRg10mPTwwm6H2H2igZFCuegQZLRRQNH5NxC%2FAGMKCqDaNRf30AQw7Bk5Pu88aQOOPcp%2BUD8%2BxiawXKiZ0lu3t2a0M3pXmLBy5KPsT3hCVWMnbYVfYYVzcKGyF4i0X%2BqXgYtN6B%2BALcg%3D%3D", "platform":"ios", "server_id":"1", "vendor_id":"F485640C-352D-465A-B632-182447B5E01D", "pmt_auth":"IZltyWbbu1MpGlI%2BP7awy10t6zTuZvQIL0vgmklpWWdKVEmJVdRLtN9C7TUZKA8QgV1P4ipqgJ5Dj105qK3cxGCbqnLfda8Uy7KzbE%2BiO0QNfVO1q7SPH%2F8wxLvgsPY7"}
    headers={"Content-Type":"application/octet-stream","SmonTmVal" : str(SmonTmVal),"SmonChecker" :SmonChecker,  "User-Agent" : "Summoners%20War/6.3.3.63304 CFNetwork/1220.1 Darwin/20.3.0", "Accept-Language":"en-us","Accept-Encoding":"gzip, deflate, br"}
    response = requests.post("https://summonerswar-gb-lb.qpyou.cn/api/gateway_c2.php",cookies=cookies, headers=headers ,data=hashed_data)
    datara = dump.dump_all(response)
    return response.text


def finalenc(data):
    key = base64.b64decode('R3I0UzJlaU5sN3pxNU1yVQ==')
    aesiv =  base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==')
    cryptme = swcrypt.AESCipher(key)
    ctrypetstring = cryptme.encrypt(data)
    finalenct = ctrypetstring.decode("utf-8")
    return finalenct
    
def finaldec():
    key = base64.b64decode('R3I0UzJlaU5sN3pxNU1yVQ==')
    aesiv =  base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==')
    cryptme = swcrypt.AESCipher(key)
    sleeptime = random.uniform(5, 10)
    sleep(sleeptime)
    SmonTmVal = summonerchecker.PlayerServerConnectElapsedTime()
    unhashed_data= '{\n"command":\t"BattleDungeonStart",\n"wizard_id":\t34930554,\n"session_key":\t"2e59a4265ae402c6ce2a8f23ff9c38b32da117c3",\n"proto_ver":\t11940,\n"infocsv":\t"4.02.90_PrC2jk3L",\n"channel_uid":\t228387750,\n"ts_val":\t'+str(SmonTmVal)+',\n"dungeon_id":\t8001,\n"stage_id":\t12,\n"helper_list":\t[],\n"mentor_helper_list":\t[],\n"npc_friend_helper_list":\t[],\n"unit_id_list":\t[{\n"unit_id":\t18046986190\n}, {\n"unit_id":\t18031090789\n}, {\n"unit_id":\t18043822232\n}, {\n"unit_id":\t18064404469\n}, {\n"unit_id":\t18490311990\n}],\n"cash_used":\t0,\n"retry":\t0,\n"is_rooting":\t0,\n"auto_repeat":\t0\n}'
    hashed_data = finalenc(unhashed_data)
    SmonChecker = summonerchecker.getSmonChecker(hashed_data)
    requesttat = GB12(hashed_data,SmonTmVal,SmonChecker)
    decrypted = cryptme.decrypt(requesttat)
    return decrypted

#if __name__ == "__main__":