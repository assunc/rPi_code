from gpiozero import MCP3008
from time import sleep
from enum import Enum
from six.moves.urllib.request import urlopen
import json

coopId = 1


def main():
    State = Enum('State', ['IDLE', 'ENTER_IN', 'MIDDLE_IN', 'EXIT_IN', 'ENTER_OUT', 'MIDDLE_OUT', 'EXIT_OUT'])
    curr_state = State.IDLE

    upThresh = 0.8
    downThresh = 0.5

    sensorIn = MCP3008(1)
    sensorOut = MCP3008(2)

    maxChickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getTotalChickens/" + str(coopId)).read())[0]['totalChicken']
    chickens = json.loads(urlopen("https://studev.groept.be/api/a23ib2d05/getChickensInside/" + str(coopId)).read())[0]['presentChicken']

    while True:
        vIn = sensorIn.value
        vOut = sensorOut.value
        next_state = curr_state
        if curr_state == State.IDLE:
            if vIn < downThresh:
                next_state = State.ENTER_IN
            elif vOut < downThresh:
                next_state = State.ENTER_OUT

        elif curr_state == State.ENTER_IN:
            if vIn > upThresh:
                next_state = State.IDLE
            elif vOut < downThresh:
                next_state = State.MIDDLE_IN

        elif curr_state == State.MIDDLE_IN:
            if vIn > upThresh:
                next_state = State.EXIT_IN
            elif vOut > upThresh:
                next_state = State.ENTER_IN

        elif curr_state == State.EXIT_IN:
            if vIn < downThresh:
                next_state = State.MIDDLE_IN
            elif vOut > upThresh:
                next_state = State.IDLE
                chickens = max(0, chickens - 1)
                urlopen("https://studev.groept.be/api/a23ib2d05/setChickensInside/" + str(chickens) + "/" + str(coopId))

        elif curr_state == State.ENTER_OUT:
            if vOut > upThresh:
                next_state = State.IDLE
            elif vIn < downThresh:
                next_state = State.MIDDLE_OUT

        elif curr_state == State.MIDDLE_OUT:
            if vIn > upThresh:
                next_state = State.ENTER_OUT
            elif vOut > downThresh:
                next_state = State.EXIT_OUT

        elif curr_state == State.EXIT_OUT:
            if vIn > upThresh:
                next_state = State.IDLE
                chickens = min(chickens + 1, maxChickens)
                urlopen("https://studev.groept.be/api/a23ib2d05/setChickensInside/" + str(chickens) + "/" + str(coopId))
            elif vOut < downThresh:
                next_state = State.MIDDLE_OUT

        print(round(vIn, 4), round(vOut, 4), curr_state, chickens)
        curr_state = next_state
        sleep(0.2)


if __name__ == '__main__':
    main()
