#----------------------------------------------------------------------------------------------------------------
#   Main script for an automated imaging tool for AI services
#
#   Author: Lutz Hager 
#   Date: 05.11.22
#
#----------------------------------------------------------------------------------------------------------------
import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access


from adafruit_motorkit import MotorKit  # library for motor control board
from adafruit_motor import stepper

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
import cv2
import time
import numpy as np
from datetime import datetime

kit = MotorKit()    # MotorKit Object


#----------------------------------------------------------------------------------------------------------------
#   function for calculation of Roboter coordinates
#   Inputs: number of Images: num_images
#   Outputs: array of coordinats: cords
#            number of motor stepps: num_steps
#----------------------------------------------------------------------------------------------------------------
def coordinates(num_images, center):

    R = 80
    spacing = num_images//8

    # phi = np.linspace(0, 0.5 * np.pi, spacing)
    phi = np.linspace(0.5*np.pi, np.pi, spacing)
    X = []
    Y = center[1] + R * np.cos(phi)
    Z = center[2] + R * np.sin(phi)
    rx = []
    ry = []
    rz = []

    cords = []
    angle_x_increment = 90/(spacing-1)
    for i in range(spacing):
        X += [center[0]]
        rx += [180 - i*angle_x_increment]
        ry += [0]
        rz += [0]
        cords += [[X[i], float(-Y[i]), float(Z[i]), rx[i], ry[i], rz[i]]] 

    num_steps = []
    for x in range(8):
        num_steps += [50]
    
    return cords, num_steps


#----------------------------------------------------------------------------------------------------------------
#   establish connection to Cobotta
#   Input: IP_adress: IP
#   Output: bcapclient: client
#           RC8 controller: RC8 
#----------------------------------------------------------------------------------------------------------------
def connect_Cobotta(IP):

    # set IP Address , Port number and Timeout of connected RC8
    host = IP
    port = 5007
    timeout = 2000

    try:
        # Connection processing of tcp communication
        client = bcapclient.BCAPClient(host, port, timeout)

        # start b_cap Service
        client.service_start("")

        # set Parameter
        Name = ""
        Provider = "CaoProv.DENSO.VRC"
        Machine = host
        Option = ""

        # Connect to RC8 (RC8(VRC)provider)
        RC8 = client.controller_connect(Name, Provider, Machine, Option)

        print("Cobotta connected")
        return client, RC8

    except:
        raise RuntimeError("can't connect to Cobotta")

#----------------------------------------------------------------------------------------------------------------
#   cobotta camera class
#   Atributes: client = Cobotta connection
#              IP = camera IP-adress
#----------------------------------------------------------------------------------------------------------------
class CAMERA:
    def __init__(self, client, IP):
        try:
            # Get Camera Handler
            self.camera_handler = client.controller_connect('N10-W02', 'CaoProv.Canon.N10-W02', '', 'Conn=eth:'+ IP +', Timeout=3000')
            self.client = client
            # Get Variable ID
            self.variable_handler = self.client.controller_getvariable(self.camera_handler, 'IMAGE')
        except:
            raise RuntimeError("can't connect camera")

    def OneShot(self, name):
        try:
            # take and export image from Canon camera 
            self.client.controller_execute(self.camera_handler, 'OneShotFocus', '')
            image_buff = self.client.variable_getvalue(self.variable_handler)

            cv_image = convert_image(image_buff)
            # save image to file
            image_name = 'Images/{}{}.png'
            cv2.imwrite(image_name.format(datetime.now().strftime("%Y%m%d_%H:%M:%S"), name), cv_image)
        except:
            raise RuntimeError("faild to capture image")


def get_number_of_Images():
    num_images = int(input('Number of Images: ') or '100')
    print('User Input num_images: %s', num_images)
    return num_images

def get_name():
    return str(input('Label of Object: '))


# converts Cobotta image to usable numpy formate 
def convert_image(img):
    np_img = np.frombuffer(img , dtype=np.uint8)
    cv_image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    scale_percent = 40 # percent of original size
    width = int(cv_image.shape[1] * scale_percent / 100)
    height = int(cv_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(cv_image, dim, interpolation = cv2.INTER_AREA)

    return resized

# moves stepper motor
def stepper_worker(stepper, numsteps, direction):
    for x in range(numsteps):
        stepper.onestep(direction=direction)




# establish Cobotta connection
client, RC8 = connect_Cobotta('10.50.12.87')
# open camera connection
CAM = CAMERA(client=client, IP='10.50.12.88')

num_images = get_number_of_Images()
name = get_name()


# calculate arrays with roboter coordinates
Objekt_cords = [190, -40, 120]
cords, motorStepps = coordinates(num_images, Objekt_cords)


I90_access = client.controller_getvariable(RC8, "I90", "")   # Object for variable access
I91_access = client.controller_getvariable(RC8, "I91", "")   # Object for variable access
P90_access = client.controller_getvariable(RC8, "P90", "")   # Object to post new Coordinates

print(f"size of cords: {len(cords)}")
try:
    for rotation in range(8):
        for point in cords:
            
            new_coords = point
            client.variable_putvalue(P90_access, new_coords)    # write new coordinates

            # acctivate script on cobotta
            I90 = 1   # new value
            client.variable_putvalue(I90_access, I90) # write I90 value

            ready = 0
            # wait for robot to set I91
            while not ready:
                ready = client.variable_getvalue(I91_access)  # read I91
                time.sleep(0.1)

            # capturing image
            CAM.OneShot(name)

            # # evtl delay?
            # time.sleep(2)

            # finish script on cobotta
            I90 = 0   # new value
            client.variable_putvalue(I90_access, I90) # write I90 value

        stepper_worker(kit.stepper1, motorStepps[rotation], stepper.FORWARD)   # move stepper motor 
        print("Moving Stepper")
        cords.reverse()

except:
    # finish script on cobotta
    I90 = 0   # new value
    client.variable_putvalue(I90_access, I90) # write I90 value

    client.variable_release(I90_access) # close connection
    client.variable_release(I91_access) # close connection
    client.variable_release(P90_access) # close connection
    client.service_stop() # stop bcapclient

    kit.stepper1.release()

    raise Exception("service stoped!")





