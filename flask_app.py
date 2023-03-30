from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for, current_app
from flask_sock import Sock
import json
import time
import threading
import secrets
import base64
import cv2
import os
# from Cobotta_routine import COBOTTA_ROUTINE

# create flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

# create websocket
sock = Sock(app)
sock_progress = Sock(app)

# global variables
client_list = []
client_list_progress = []
dataLabel = ""
numImages = 0
headerLink = 'index'
active = False
routine_active = False

#----------------------------------------------------------------------------------------------------------------
#   index page
#----------------------------------------------------------------------------------------------------------------
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        global dataLabel
        global numImages
        dataLabel = request.form['dataLabel']
        numImages = request.form['numImages']

        if not dataLabel:
            print('Label is required!')
            flash('Label is required!', category="error")
        else:  
            print(dataLabel)
            print(numImages)
            global active
            active = True
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
    # counter an bildern oder bool running einführen im main script -> wenn fertig, dann reder Template index
    # if finished -> index + headerLink = "index"
    # evtl. import send_img und send_progress im Backend script? -> keine Datenübergabe nötig
    # if not routine_active:
    # start backend routine
    # backend = COBOTTA_ROUTINE(dataLabel, numImages)
    # routine = threading.Thread(target=backend.start_routine)
    # routine.daemon = True
    # routine.start()

    print("in running")

    global active
    if active:
        return render_template('running.html')  
    else:
        return redirect(url_for('index'))

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
    while True:
        time.sleep(1) # -> muss nicht zyklisch aufgerufen werden, sonder nur wenn ein neues Bild gemacht wurde
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

    # noch weg machen weil die Funktion später vom main skript aufgerufen wird
    while True:
        time.sleep(1)
        
        clients = client_list_progress.copy()
        for client in clients:
            try:
                client.send(json.dumps({'progress' : progress}))
            except:
                print("failed to send progress")
                client_list_progress.remove(client)


if __name__ == '__main__':
    # no need for threads in final app -> remove while True + sleep!
    t = threading.Thread(target=send_img)
    t.daemon = True
    t.start()

    t2 = threading.Thread(target=send_progress, args=['77%'])
    t2.daemon = True
    t2.start()

    app.run(host='0.0.0.0', port=5000) # threaded?
