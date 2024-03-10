import RPi.GPIO as GPIO
import time

in1 = 5
in2 = 6
in3 = 13
in4 = 19

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.5

step_count = 4096  # 5.625*(1/64) per step, 4096 steps is 360°

direction = -1  # -1 for clockwise, +1 for counter-clockwise

# defining stepper motor sequence
step_sequence = [[1, 0, 0, 1],
                 [1, 0, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 1],
                 [0, 0, 0, 1]]

motor_pins = [in1, in2, in3, in4]

# setting up, initializing
GPIO.setmode(GPIO.BCM)
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

motor_step_counter = 0


def cleanup():
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()


# the meat
try:
    i = 0
    for i in range(step_count):
        for pin in range(len(motor_pins)):
            GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
        motor_step_counter = (motor_step_counter + direction) % 8
        time.sleep(step_sleep)

except KeyboardInterrupt:
    cleanup()
    exit(1)

cleanup()
exit(0)
