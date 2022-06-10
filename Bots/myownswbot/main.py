import swrequest
import base64
import request2

if __name__ == "__main__":
    strnum = input('how many times you want to reapet : ')
    num = int(strnum)
    avarageenergy = num*9
    maxtimemins = num*2.5
    maxtimehours = 0.041666*num
    print('this will cost you around : '+str(avarageenergy)+' energy \n and it will take  : '+str(maxtimemins)+' minuts at max \n or : '+str(maxtimehours)+' hours')
    for x in range(num):
        print(request2.request2())