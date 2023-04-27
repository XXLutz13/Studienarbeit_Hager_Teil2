from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for, current_app
from flask_sock import Sock
import json
import time
import threading
import secrets
import base64
import cv2
import os
from Cobotta_routine import COBOTTA_ROUTINE

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

    return render_template('running.html')  



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

def send_img(image):
    clients = client_list.copy()
    for client in clients:
        try:
            # with app.app_context():
            #     root_path = current_app.root_path

            # # Load the image data
            # image = open(os.path.join(root_path, 'Test_green.png'), "rb").read()
            # Encode the image data as base64
            # Convert the image to base64 string
            retval, buffer = cv2.imencode('.png',image)  
            png_as_text = base64.b64encode(buffer).decode('utf-8')
            # image_base64 = base64.b64encode(image).decode('ascii')
            # Generate a data URL for the image
            data_url = f"data:image/png;base64,{png_as_text}"

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
    clients = client_list_progress.copy()
    for client in clients:
        try:
            client.send(json.dumps({'progress' : progress}))
        except:
            print("failed to send progress")
            client_list_progress.remove(client)


#----------------------------------------------------------------------------------------------------------------
#   main routine function
#   return val: Finished / Failed
#               progress (img_nun/total images in %)
#
#   ! function is blocking => use separate thread !              
#----------------------------------------------------------------------------------------------------------------
def start_routine():
    send_progress(progress="0%")
    try:
        backend, cords, motorStepps, cam = COBOTTA_ROUTINE(dataLabel, numImages)
        # initialize variable access handlers 
        I90_access = backend.get_variable_handler("I90")    # Object for variable access
        I91_access = backend.get_variable_handler("I91")    # Object for variable access
        P90_access = backend.get_variable_handler("P90")    # Object to post new Coordinates
        print("initialized backend")
    except:
        flash("faild to connect Cobotta", category="error")
        print("faild to connect Cobotta")   
        
    try:
        img_counter = 0
        for rotation in range(8):
            for point in cords:
                
                new_coords = point
                backend.write_value(P90_access, new_coords)    # write new coordinate

                # acctivate script on cobotta
                I90 = 1   # new value
                backend.write_value(I90_access, I90) # write I90 value

                ready = 0
                # wait for robot to set I91
                while not ready:
                    ready = backend.read_value(I91_access)  # read I91
                    time.sleep(0.1)

                # capturing image
                try:
                    img = cam.OneShot(dataLabel)   # poss. self parameter not needed
                except:
                    print("failed to capture image")

                send_img(img)
                img_counter = img_counter + 1
                # send progress in %
                progress = f"{(img_counter/numImages)*100}%"
                print(progress)
                send_progress(progress=progress)

                # finish script on cobotta
                I90 = 0   # new value
                backend.write_value(I90_access, I90) # write I90 value

            try:
                backend.stepper_worker(motorStepps[rotation], 'FORWARD')   # move stepper motor 
            except:
                print("Failed to move stepper")
                flash("Failed to move stepper", category="error")

            cords.reverse()
            print("reversed cords")

        global routine_active
        routine_active = False
        global active
        active = False
        # backend.__del__()
        print("Finished")
        return "Finished"

    except:
        flash("routine error", category="error")
        return "Failed"



if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000) 

