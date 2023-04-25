from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for, current_app
import secrets
from datetime import datetime
from flask_sock import Sock
import os
import cv2
import base64
import json
import time
import threading

# create flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

# create websocket
sock = Sock(app)
sock_progress = Sock(app)


dataLabel = ""
numImages = 0
active = False
headerLink = 'index'
client_list = []
routine_active = False
client_list_progress = []

#----------------------------------------------------------------------------------------------------------------
#   index page
#----------------------------------------------------------------------------------------------------------------
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        global dataLabel
        global numImages
        dataLabel = request.form['dataLabel']
        numImages = int(request.form['numImages'])

        if not dataLabel:
            print('Label is required!')
            flash('Label is required!', category="error")
        # elif not numImages:
        #     print('Number of images is required!')
        #     flash('Number of images is required!', category="error")
        else:  
            print(dataLabel)
            print(numImages)
            global active
            active = True
            # test_file(dataLabel)
            return redirect(url_for('running'))
            
    if active:
        return redirect(url_for('running'))
    else:
        return render_template('index.html')

#----------------------------------------------------------------------------------------------------------------
#   about page
#----------------------------------------------------------------------------------------------------------------
@app.route('/about', methods=('GET','POST'))
def about(): 
    return render_template('about.html', link=headerLink) 

#----------------------------------------------------------------------------------------------------------------
#   running page
#----------------------------------------------------------------------------------------------------------------
@app.route('/runnnig', methods=('GET','POST')) 
def running():
    global headerLink
    headerLink = 'running'
    # if finished -> index + headerLink = "index"
    global routine_active
    if not routine_active:
    # start backend routine
        routine_active = True
        routine = threading.Thread(target=start_routine)
        routine.daemon = True
        routine.start()

    if routine_active:
        return render_template('running.html', finished=0)  
    else:
        render_template('running.html', finished=1)  

#----------------------------------------------------------------------------------------------------------------
#   websocket for sending image 
#----------------------------------------------------------------------------------------------------------------
@sock.route('/image')
def clock(ws):
    client_list.append(ws)
    while True:
        data = ws.receive()
        if data == 'stop':
            break
    client_list.remove(ws)

def send_img():
    clients = client_list.copy()
    for client in clients:
        try:
            with app.app_context():
                root_path = current_app.root_path

            # Load the image data
            image = open(os.path.join(root_path, 'Test_green.png'), "rb").read()
            # Encode the image data as base64
            image_base64 = base64.b64encode(image).decode('ascii')
            # Generate a data URL for the image
            data_url = f'data:image/png;base64,{image_base64}'

            client.send(json.dumps({'img_src': data_url}))
            print("image send")
        except:
            print("failed to send img src")
            client_list.remove(client)

#----------------------------------------------------------------------------------------------------------------
#   websocket for sending routine progress 
#----------------------------------------------------------------------------------------------------------------
@sock_progress.route('/progress')
def progress(ws):
    client_list_progress.append(ws)
    while True:
        data = ws.receive()
        if data == 'stop':
            break
    client_list_progress.remove(ws)

def send_progress(progress):
    clients = client_list_progress.copy()
    for client in clients:
        try:
            client.send(json.dumps({'progress' : progress}))
        except:
            print("failed to send progress")
            client_list_progress.remove(client)


def test_file(dataLabel):
    with app.app_context():
        root_path = current_app.root_path

    # Load the image data
    image = open(os.path.join(root_path, 'Test_green.png'), "rb").read()
    # try saving it on the external hard drive
    parent_dir  = '/exdisk'
    directory = dataLabel + str(datetime.now().strftime("%Y%m%d_%H:%M:%S"))
    print(directory)
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)

    img_path = os.path.join(path, directory)
    cv2.imwrite(img_path, image)

def start_routine():
    send_progress(progress="0%")
    send_img()
    time.sleep(1)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000) 

