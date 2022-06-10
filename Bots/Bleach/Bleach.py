import mainBot
import klab
import pkcs7



if __name__ == "__main__":
    a = mainBot.API()
    a.completeTut()
    print a.completeQuest(3,0,{"101":{"1":8}},[3001])
