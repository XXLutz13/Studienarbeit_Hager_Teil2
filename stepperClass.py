from adafruit_motorkit import MotorKit  # library for motor control board
from adafruit_motor import stepper


class STEPPER_TEST:
    def __init__(self):
        # create motorkit object
        self.kit = MotorKit() 
        print("created object")
        
    # moves stepper motor
    def stepper_worker(self, numsteps, direction):
        for x in range(numsteps):
            if direction == 'FORWARD':
                print("Moving forward")
                self.kit.stepper1.onestep(direction=stepper.FORWARD)
            elif direction == 'BACKWARD':
                print("Moving backward")
                self.kit.stepper1.onestep(direction=stepper.BACKWARD)
