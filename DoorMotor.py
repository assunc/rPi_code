import time
import RPi.GPIO as GPIO


class DoorMotor:
    step_sleep = 0.002
    step_count = 2*4096  # 5.625*(1/64) per step, 4096 steps is 360°

    # defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
    step_sequence = [[1, 0, 0, 1],
                     [1, 0, 0, 0],
                     [1, 1, 0, 0],
                     [0, 1, 0, 0],
                     [0, 1, 1, 0],
                     [0, 0, 1, 0],
                     [0, 0, 1, 1],
                     [0, 0, 0, 1]]

    motor_pins = [6, 13, 19, 26]
    motor_step_counter = 0

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self.motor_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def moveDoor(self, direction):
        for i in range(self.step_count):
            for pin in range(len(self.motor_pins)):
                GPIO.output(self.motor_pins[pin], self.step_sequence[self.motor_step_counter][pin])
            self.motor_step_counter = (self.motor_step_counter + direction) % 8
            time.sleep(self.step_sleep)