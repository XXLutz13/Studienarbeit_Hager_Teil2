import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access


#
class COBOTTA_ROUTINE:
    _instance = None

    def __new__(cls, label, num_img):
        if cls._instance is None:
            cls._instance = super(COBOTTA_ROUTINE, cls).__new__(cls)

            # initialize global variables
            cls.name = label
            cls.num_images = num_img

            # establish Cobotta connection
            cls.client, cls.RC8 = COBOTTA_ROUTINE.connect_Cobotta(cls._instance, '10.50.12.87')
            # open camera connection
            cls.CAM =COBOTTA_ROUTINE.CAMERA(client=cls.client, IP='10.50.12.88')


            print("created COBOTTA_ROUTINE object")

        return cls._instance,  cls.CAM
    

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

            camera_handler = client.controller_connect('N10-W02', 'CaoProv.Canon.N10-W02', '', 'Conn=eth:'+ IP +', Timeout=3000')
            print("Cobotta connected")
            return client, RC8
            
        except:
            print("can't connect to Cobotta")
            raise RuntimeError("can't connect to Cobotta")

    class CAMERA:
        def __init__(self, client, IP):
            try:
                # Get Camera Handler
                self.camera_handler = client.controller_connect('N10-W02', 'CaoProv.Canon.N10-W02', '', 'Conn=eth:'+ IP +', Timeout=3000')
                self.client = client
                # Get Variable ID
                self.variable_handler = self.client.controller_getvariable(self.camera_handler, 'IMAGE')
                print("connected to camera")
            except:
                print("can't connect camera")
                raise RuntimeError("can't connect camera")

        def OneShot(self, name):
            try:
                # take and export image from Canon camera 
                self.client.controller_execute(self.camera_handler, 'OneShotFocus', '')
                image_buff = self.client.variable_getvalue(self.variable_handler)

                # save image to file
                print("captured image")
                return image_buff
            except:
                print("faild to capture image")
                raise RuntimeError("faild to capture image")
            

dataLabel = "test"
numImages = 100
backend, cam = COBOTTA_ROUTINE(dataLabel, numImages)
print("initialized backend")

img = cam.OneShot(dataLabel)
print(type(img))
print("finished")
