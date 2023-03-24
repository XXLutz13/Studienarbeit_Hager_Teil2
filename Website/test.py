from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for
from flask_sock import Sock
import json
import time, datetime
import threading
import secrets
import base64
import cv2
from PIL import Image

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}


sock = Sock(app)
sock_progress = Sock(app)

client_list = []
client_list_progress = []

headerLink = 'index'


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        dataLabel = request.form['dataLabel']
        numImages = request.form['numImages']

        if not dataLabel:
            print('Label is required!')
            flash('Label is required!', category="error")
        else:  
            print(dataLabel)
            print(numImages)
            return redirect(url_for('running'))
            # start backend routine
        
    return render_template('index.html')

@app.route('/about', methods=('GET','POST'))
def about(): 
    return render_template('about.html', link=headerLink) 

@app.route('/runnnig', methods=('GET','POST')) 
def running():
    global headerLink
    headerLink = 'running'
    # counter an bildern oder bool running einführen im main script -> wenn fertig, dann reder Template index
    # if finished -> index + headerLink = "index"
    return render_template('running.html')  


@sock.route('/image')
def clock(ws):
    client_list.append(ws)
    while True:
        data = ws.receive()
        if data == 'stop':
            break
    client_list.remove(ws)

def send_img():
    # link = url_for('static', filename= 'images/Test_Images/Test.png') -> Working outside of application context.
    while True:
        time.sleep(1) # -> muss nicht zyklisch aufgerufen werden, sonder nur wenn ein neues Bild gemacht wurde
        clients = client_list.copy()
        for client in clients:
            try:
                image = cv2.imread("green.png")
                # Encode the image data as base64
                image_data = image.tobytes()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                img_data_url = f'data:image/png;base64,{image_base64}'
                # 'http://127.0.0.1:5000/static/images/Test_Images/Test.png'
                client.send(json.dumps({
                    'img_src': img_data_url
                }))
            except:
                print("failed to send img src")
                client_list.remove(client)


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
    t = threading.Thread(target=send_img)
    t.daemon = True
    t.start()

    t2 = threading.Thread(target=send_progress, args=['77%'])
    t2.daemon = True
    t2.start()

    app.run()
