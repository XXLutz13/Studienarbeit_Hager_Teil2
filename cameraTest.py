import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access
import cv2
import numpy as np
from datetime import datetime
import os

# set IP Address , Port number and Timeout of connected RC8
host = '10.50.12.87'
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

    print('connected')
    
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
            cv2.imwrite(f'ImageProcessing\{name}.png', cv_image)
            print(f'saved image: {name}')
            return cv_image
        except:
            raise RuntimeError("faild to capture image")
        

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

cam = CAMERA(client, '10.50.12.88')
cam.OneShot('TestCompressedImg')

