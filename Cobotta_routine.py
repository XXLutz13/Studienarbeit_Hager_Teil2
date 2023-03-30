#----------------------------------------------------------------------------------------------------------------
#   Main script for an automated imaging tool for AI services
#
#   Author: Lutz Hager 
#   Date: 29.03.23
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

#----------------------------------------------------------------------------------------------------------------
#   Class for the data creation process -> Singleton approche (only one instance can be created)
#   Inputs: number of Images: num_images
#           Label of the data: name
#   Outputs: status: is_running
#----------------------------------------------------------------------------------------------------------------
#
class COBOTTA_ROUTINE:
    _instance = None

    def __new__(cls, label, num_img):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(COBOTTA_ROUTINE, cls).__new__(cls)

            # initialize global variables
            cls.name = label
            cls.num_images = num_img

            # create motorkit object
            cls.kit = MotorKit() 

            # establish Cobotta connection
            cls.client, cls.RC8 = COBOTTA_ROUTINE.connect_Cobotta('10.50.12.87')
            # open camera connection
            cls.CAM = CAMERA(client=cls.client, IP='10.50.12.88')

            # initialize variable access handlers 
            cls.I90_access = cls.client.controller_getvariable(cls.RC8, "I90", "")   # Object for variable access
            cls.I91_access = cls.client.controller_getvariable(cls.RC8, "I91", "")   # Object for variable access
            cls.P90_access = cls.client.controller_getvariable(cls.RC8, "P90", "")   # Object to post new Coordinates

            # calculate arrays with roboter coordinates
            Objekt_cords = [190, -40, 120]
            cls.cords, cls.motorStepps = coordinates(cls.num_images, Objekt_cords) 
    
        return cls._instance
    

    #----------------------------------------------------------------------------------------------------------------
    #   establish connection to Cobotta
    #   Input: IP_adress: IP
    #   Output: bcapclient: client
    #           RC8 controller: RC8 
    #----------------------------------------------------------------------------------------------------------------
    def connect_Cobotta(self, IP):
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

                cv_image = convert_image(image_buff)    # -> check img formate -> if usable byte, then directly encode to base64 
                # save image to file
                image_name = 'Images/{}{}.png'
                cv2.imwrite(image_name.format(datetime.now().strftime("%Y%m%d_%H:%M:%S"), name), cv_image)
            except:
                raise RuntimeError("faild to capture image")
            

    def __del__(self):
        # finish script on cobotta
        I90 = 0   # new value
        self.client.variable_putvalue(self.I90_access, I90) # write I90 value

        self.client.variable_release(self.I90_access) # close connection
        self.client.variable_release(self.I91_access) # close connection
        self.client.variable_release(self.P90_access) # close connection
        self.client.service_stop() # stop bcapclient

        self.kit.stepper1.release()

        raise Exception("service stoped!")



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