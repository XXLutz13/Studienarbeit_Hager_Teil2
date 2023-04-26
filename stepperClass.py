from adafruit_motorkit import MotorKit  # library for motor control board
from adafruit_motor import stepper


class STEPPER_TEST:
    def __init__(self):
        # create motorkit object
        self.kit = MotorKit() 

    # moves stepper motor
    def stepper_worker(self, numsteps, direction):
        for x in range(numsteps):
            self.kit.onestep(direction=direction)