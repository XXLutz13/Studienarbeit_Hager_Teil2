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
import os
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
            cls._instance = super(COBOTTA_ROUTINE, cls).__new__(cls)

            # initialize global variables
            cls.name = label
            cls.num_images = num_img
            # create folder for the images
            cls.path = createDirectory(cls.name)
            logging.info(f"created directory {cls.path}")

            # create motorkit object
            cls.kit = MotorKit() 

            # establish Cobotta connection
            cls.client, cls.RC8 = COBOTTA_ROUTINE.connect_Cobotta(cls._instance, '10.50.12.87')
            # open camera connection
            cls.CAM =COBOTTA_ROUTINE.CAMERA(client=cls.client, IP='10.50.12.88')

            # calculate arrays with roboter coordinates
            Objekt_cords = [190, -40, 110]
            cls.cords, cls.motorStepps = coordinates(cls.num_images, Objekt_cords) 

            logging.info("created COBOTTA_ROUTINE object")

        return cls._instance, cls.cords, cls.motorStepps, cls.CAM
    

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

            logging.info("Cobotta connected")
            return client, RC8
            
        except:
            logging.error("can't connect to Cobotta")
            raise RuntimeError("can't connect to Cobotta")
        

    def get_variable_handler(self, id):
        try:
            handler = self.client.controller_getvariable(self.RC8, id, "")
            return handler
        except:
            logging.error("faild to get handler")
            raise RuntimeError("failed to get handler")
    
    def write_value(self, handler, value):
        try:
            self.client.variable_putvalue(handler, value)
        except:
            logging.error("faild to write value")
            raise RuntimeError("faild to write value")

    def read_value(self, handler):
        try:
            value = self.client.variable_getvalue(handler)
            return value
        except:
            logging.error("faild to read value")
            raise RuntimeError("faild to read value")

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
                logging.info("connected to camera")
            except:
                logging.error("can't connect camera")
                raise RuntimeError("can't connect camera")

        def OneShot(self, name):
            try:
                # take and export image from Canon camera 
                self.client.controller_execute(self.camera_handler, 'OneShotFocus', '')
                image_buff = self.client.variable_getvalue(self.variable_handler)

                cv_image = convert_image(image_buff)    # -> check img formate -> if usable byte, then directly encode to base64 
                # save image to file
                image_name = f'{name}{datetime.now().strftime("%Y%m%d_%H:%M:%S")}.png'
                img_path = os.path.join(COBOTTA_ROUTINE.path, image_name)
                cv2.imwrite(img_path, cv_image)
                return cv_image
            except:
                logging.error("faild to capture image")
                raise RuntimeError("faild to capture image")
            

    # moves stepper motor
    def stepper_worker(self, numsteps, direction):
        for x in range(numsteps):
            if direction == 'FORWARD':
                self.kit.stepper1.onestep(direction=stepper.FORWARD)
            elif direction == 'BACKWARD':
                self.kit.stepper1.onestep(direction=stepper.BACKWARD)
            

    def __del__(self):
        # finish script on cobotta
        I90 = 0   # new value
        self.client.variable_putvalue(self.I90_access, I90) # write I90 value

        self.client.variable_release(self.I90_access) # close connection
        self.client.variable_release(self.I91_access) # close connection
        self.client.variable_release(self.P90_access) # close connection
        self.client.service_stop() # stop bcapclient

        self.kit.stepper1.release()

        logging.info("service stoped!")




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
    phi = np.linspace(0.85*np.pi, 0.5*np.pi, spacing)
    X = [center[0]]*spacing
    Y = center[1] - R * np.cos(phi)
    Z = center[2] + R * np.sin(phi)
    rx = np.linspace(180, 90, 24)
    ry = [0]*spacing
    rz = [0]*spacing
    num_steps = [50]*8
    # type conversions
    rx = rx.tolist()
    Y = Y.tolist()
    Z = Z.tolist()

    cords = list(zip(X, Y, Z, rx, ry, rz))
    # Round every element in the list of tuples using list comprehension and round()
    cords = [(round(a, 4), round(b, 4), round(c, 4), round(d, 4), round(e, 4), round(f, 4)) for a,b,c,d,e,f in cords]
    
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

# creates a new directory on the external hard drive
def createDirectory(name):
    parent_dir  = '/exdisk'
    directory = name + str(datetime.now().strftime("%Y%m%d_%H:%M:%S"))
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)

    return path
