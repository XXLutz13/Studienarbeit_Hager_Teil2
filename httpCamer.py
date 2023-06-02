import requests

class HttPCamera:
    def __init__(self, IP):
        self.IP = IP
        url = f'http://{IP}/-wvhttp-01-/open.cgi?type=admin'
        response = requests.get(url)

        if response.status_code == 200:
            content = response.text
            self.sessionID = content[0]
            # set exposure mode to manual
            self.setOption(param='c.1.exp', value='manual')
            print('started camera session')

        else:
            print('Request failed with status code', response.status_code)
    
    def setOption(self, param, value):
        url = f'http://{self.IP}/-wvhttp-01-/control.cgi?[s={self.sessionID}][&{param}={value}]'
        response = requests.get(url)
        
        if response.status_code == 200:
            content = response.text
            print(f'set {content[0]} to {content[1]}')
        else:
            print('failed to set Options with status code', response.status_code)

    def getImage(self):
        url = f'http://{self.IP}/-wvhttp-01-/image.cgi?v=jpg:1920x1080'
        response = requests.get(url)

        if response.status_code == 200 and response.headers.get('content-type') == 'image/jpeg':
            image_data = response.content
            print('got image')
            return image_data
        else:
            print('failed to get image with status code', response.status_code)


    def closeSession(self):
        url = f'http://{self.IP}/-wvhttp-01-/close.cgi?s={self.sessionID}'
        response = requests.get(url)

        if response.status_code == 200:
            print('closed camera session')
        else:
            print('closing session failed with status code', response.status_code)


IP = '10.50.12.88'
cam = HttPCamera(IP)
cam.setOption(param='c.1.me.gain', value=4)
jpeg_image = cam.getImage()
cam.closeSession()

urlTest = 'http://10.50.12.88/-wvhttp-01-/control.cgi?[s=de69-690e01f][&c.1.exp=manual]'
