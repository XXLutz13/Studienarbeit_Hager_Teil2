import cv2
from flask import url_for, Flask, current_app
import secrets
import threading
import time
import os


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

def send_img():
    time.sleep(1)
    with app.app_context():
        root_path = current_app.root_path
    path = os.path.join(root_path, 'Test_green.png')
    print(path)
    image = cv2.imread(path)
    #image = cv2.imread("Test_green.png")
    print(type(image))

if __name__ == '__main__':
    t = threading.Thread(target=send_img)
    t.daemon = True
    t.start()
    app.run()
