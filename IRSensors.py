from gpiozero import MCP3008
from enum import Enum


class IRSensors:
    State = Enum('State', ['IDLE', 'ENTER_IN', 'MIDDLE_IN', 'EXIT_IN',
                           'ENTER_OUT', 'MIDDLE_OUT', 'EXIT_OUT'])

    upThresh = 0.115
    downThresh = 0.1

    sensorIn = MCP3008(1)
    sensorOut = MCP3008(2)

    def __init__(self):
        self.curr_state = self.State.IDLE
        self.next_state = self.State.IDLE


    def checkSensors(self) -> int:
        diff = 0
        vIn = self.sensorIn.value
        vOut = self.sensorOut.value
        self.next_state = self.curr_state
        if self.curr_state == self.State.IDLE:
            if vIn < self.downThresh:
                self.next_state = self.State.ENTER_IN
            elif vOut < self.downThresh:
                self.next_state = self.State.ENTER_OUT

        elif self.curr_state == self.State.ENTER_IN:
            if vIn > self.upThresh:
                self.next_state = self.State.IDLE
            elif vOut < self.downThresh:
                self.next_state = self.State.MIDDLE_IN

        elif self.curr_state == self.State.MIDDLE_IN:
            if vIn > self.upThresh:
                self.next_state = self.State.EXIT_IN
            elif vOut > self.upThresh:
                self.next_state = self.State.ENTER_IN

        elif self.curr_state == self.State.EXIT_IN:
            if vIn < self.downThresh:
                self.next_state = self.State.MIDDLE_IN
            elif vOut > self.upThresh:
                self.next_state = self.State.IDLE
                diff = -1

        elif self.curr_state == self.State.ENTER_OUT:
            if vOut > self.upThresh:
                self.next_state = self.State.IDLE
            elif vIn < self.downThresh:
                self.next_state = self.State.MIDDLE_OUT

        elif self.curr_state == self.State.MIDDLE_OUT:
            if vIn > self.upThresh:
                self.next_state = self.State.ENTER_OUT
            elif vOut > self.downThresh:
                self.next_state = self.State.EXIT_OUT

        elif self.curr_state == self.State.EXIT_OUT:
            if vIn > self.upThresh:
                self.next_state = self.State.IDLE
                diff = 1
            elif vOut < self.downThresh:
                self.next_state = self.State.MIDDLE_OUT

        self.curr_state = self.next_state
        # print(round(vIn, 4), round(vOut, 4), self.curr_state)
        return diff
    
