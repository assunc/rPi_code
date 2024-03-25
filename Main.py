import time
from six.moves.urllib.request import urlopen
import json
import threading
from gpiozero import MCP3008, Servo

from DoorMotor import DoorMotor
from IRSensors import IRSensors

coopId = 1


def main():

    global chickens
    global maxChickens
    global doorIsOpen
    global now

    maxChickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getTotalChickens/" + str(coopId)).read())[0]['totalChicken']
    chickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getChickensInside/" + str(coopId)).read())[0]['presentChicken']
    doorIsOpen = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getDoorTimes/" + str(coopId)).read())[0]['doorIsOpen']
    now = int(time.strftime("%H", time.localtime()))+int(time.strftime("%M", time.localtime()))/60


    print("start:")
    threading.Thread(target=UpdateTime, args=()).start()
    threading.Thread(target=IRSensorsLoop, args=()).start()
    threading.Thread(target=DoorLoop, args=()).start()
    threading.Thread(target=WeightSensorLoop, args=()).start()
    threading.Thread(target=FeederLoop, args=()).start()


def IRSensorsLoop():
    global chickens
    irSensors = IRSensors()
    while True:
        # print(chickens)
        # if doorIsOpen == 1:
        if True:  
            diff = irSensors.checkSensors()
            if diff != 0:
                chickens = min(chickens + 1, maxChickens) if diff == 1 else max(0, chickens - 1)
                threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setChickensInside/" + str(chickens) + "/" + str(coopId),)).start()
                print(chickens)
        time.sleep(0.2)

def WeightSensorLoop():
    sensor = MCP3008(0)
    global weight
    max = 0
    min = 100
    while True:
        weight = sensor.value

     #   print(weight)
        # if(weight > max):
        #     max = weight
        
        # if(weight < min):
        #     min = weight

        # print("----------")
        # print("Max value is:",max)


        # print("Min value is:",min)

        threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setFood/"+str(int(weight))+"/1",)).start()
        time.sleep(1)

def DoorLoop():
    global doorIsOpen
    doorMotor = DoorMotor()
    while True:
        doorTimes = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getDoorTimes/" + str(coopId)).read())[0]

        openTime = timeToFloat(doorTimes['openTime'])
        closeTime = timeToFloat(doorTimes['closeTime'])
        doorIsOpenPrevious = doorIsOpen
        doorIsOpen = doorTimes['doorIsOpen']

        if doorIsOpen == 0 and now == openTime:  # open door in the morning
            threading.Thread(target=doorMotor.moveDoor, args=(1,)).start()
            doorIsOpen = 1
            threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setDoorIsOpen/1/" + str(coopId),)).start()
        elif doorIsOpen == 1 and now >= closeTime and chickens == maxChickens:  # close door in the evening
            threading.Thread(target=doorMotor.moveDoor, args=(-1,)).start()
            doorIsOpen = 0
            threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setDoorIsOpen/0/" + str(coopId),)).start()
        elif doorIsOpen != doorIsOpenPrevious:  # check if door was opened/closed manually
            threading.Thread(target=doorMotor.moveDoor, args=(1 if doorIsOpen == 0 else -1,)).start()
        time.sleep(2)

def FeederLoop():
    servo = Servo(17)
    servo.max()
    while True:
        feedingTimes = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getFeedingTimes/" + str(coopId)).read())
        for feeding in feedingTimes:
            if now == timeToFloat(feeding['time']):
                # while weight < feeding['weight']:
                servo.min()
                time.sleep(2)
                servo.max()
                time.sleep(60)
        time.sleep(3)
        # servo.min()
        # servo.max()
        # time.sleep(3)

def UpdateTime():
    global now
    global maxChickens
    while True:
        now = timeToFloat(time.strftime("%H:%M", time.localtime()))
        maxChickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getTotalChickens/" + str(coopId)).read())[0]['totalChicken']
        time.sleep(10)

def timeToFloat(timeStr: str) -> float:
    return int(timeStr.split(':')[0])+(int(timeStr.split(':')[1])/60)

if __name__ == '__main__':
    main()
