import time
from six.moves.urllib.request import urlopen
import json
import threading

from DoorMotor import DoorMotor
from IRSensors import IRSensors

coopId = 1


def main():

    global chickens
    global maxChickens
    global doorIsOpen

    maxChickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getTotalChickens/" + str(coopId)).read())[0]['totalChicken']
    chickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getChickensInside/" + str(coopId)).read())[0]['presentChicken']
    doorIsOpen = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getDoorTimes/" + str(coopId)).read())[0]['doorIsOpen']

    print("start:")
    IRThread = threading.Thread(target=IRSensorsLoop, args=())
    DoorThread = threading.Thread(target=DoorLoop, args=())

    IRThread.start()
    DoorThread.start()


def IRSensorsLoop():
    global chickens
    irSensors = IRSensors()
    while True:
        diff = irSensors.checkSensors()
        if diff != 0:
            chickens = min(chickens + 1, maxChickens) if diff == 1 else max(0, chickens - 1)
            urlThread = threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setChickensInside/" + str(chickens) + "/" + str(coopId),))
            urlThread.start()
            print(chickens)
        time.sleep(0.2)


def DoorLoop():
    global doorIsOpen
    doorMotor = DoorMotor()
    while True:
        doorTimes = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getDoorTimes/" + str(coopId)).read())[0]

        openTime = int(doorTimes['openTime'][0:2])+(int(doorTimes['openTime'][3:5])/60)
        closeTime = int(doorTimes['closeTime'][0:2])+(int(doorTimes['closeTime'][3:5])/60)
        doorIsOpenPrevious = doorIsOpen
        doorIsOpen = doorTimes['doorIsOpen']
        now = int(time.strftime("%H", time.localtime()))+int(time.strftime("%M", time.localtime()))/60

        if doorIsOpen == 0 and now == openTime:  # open door in the morning
            thread = threading.Thread(target=doorMotor.moveDoor, args=(1,))
            thread.start()
            doorIsOpen = 1
            thread2 = threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setDoorIsOpen/1/" + str(coopId),))
            thread2.start()
        elif doorIsOpen == 1 and now >= closeTime and chickens == maxChickens:  # close door in the evening
            thread = threading.Thread(target=doorMotor.moveDoor, args=(-1,))
            thread.start()
            doorIsOpen = 0
            thread2 = threading.Thread(target=urlopen, args=("https://studev.groept.be/api/a23ib2d05/setDoorIsOpen/0/" + str(coopId),))
            thread2.start()
        elif doorIsOpen != doorIsOpenPrevious:  # check if door was opened/closed manually
            thread = threading.Thread(target=doorMotor.moveDoor, args=(1 if doorIsOpen == 0 else -1,))
            thread.start()
        time.sleep(2)


if __name__ == '__main__':
    main()
