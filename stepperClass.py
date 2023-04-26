from adafruit_motorkit import MotorKit  # library for motor control board
from adafruit_motor import stepper


class STEPPER_TEST:
    def __init__(self):
        # create motorkit object
        self.kit = MotorKit() 
        self.stepper = self.kit.stepper1()
        
    # moves stepper motor
    def stepper_worker(self, numsteps, direction):
        for x in range(numsteps):
            if direction == 'FORWARD':
                self.stepper.onestep(stepper.FORWARD)
            elif direction == 'BACKWARD':
                self.stepper.onestep(stepper.BACKWARD)
