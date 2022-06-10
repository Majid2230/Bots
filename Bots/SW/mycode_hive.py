from api import API
from qpyou import QPYOU
from tools import Tools


if __name__ == "__main__":
    my_email='@gmail.com'
    my_hivelogin=''
    my_password='Test@test123'
    uid,did,sessionkey=QPYOU().hiveLogin(my_hivelogin,my_password)
    a=API(uid,did,my_hivelogin,my_email,sessionkey)
    a.setRegion('eu')
    a.setIDFA(Tools().rndDeviceId())
    a.getServerStatus()
    a.getVersionInfo()
    a.CheckLoginBlock()
    a.login()
    a.doMission(1,1,1)#garen forest outskirts
    a.doMission(1,2,1)#garen forest south
    a.doMission(1,3,1)#garen forest east
    a.doMission(1,4,1)#garen forest paths
