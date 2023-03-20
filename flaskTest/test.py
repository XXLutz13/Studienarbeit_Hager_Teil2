from flask import Flask, render_template, send_file, make_response
from flask_sock import Sock
from werkzeug.exceptions import abort
from flask import request, flash, url_for, redirect
import secrets
import cv2
import numpy as np
from datetime import datetime
import time
import json
import threading

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

sock = Sock(app)

client_list = []

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
            # start backend routine
            return redirect(url_for('running'))
            
            # -> at the end of the image routine -> return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/about', methods=('GET','POST'))
def about(): 
    headerLink = 'index'
    # headerLink = 'running'
    return render_template('about.html', link=headerLink) 

@app.route('/runnnig', methods=('GET','POST')) 
def running():
    # counter an bildern oder bool running einführen im main script -> wenn fertig, dann reder Template index
    return render_template('running.html')  

@app.route('/imageupload')
def serve_image():
    # Send the image data to the client
    return send_file("./static/images/Test_Images/Test.png", mimetype='image/png')

@app.route('/progress')
def send_progress():
    # send the state for the progress bar
    response = make_response('80%', 200)
    response.mimetype = "text/plain"
    return response


def send_time():
    while True:
        time.sleep(1)
        clients = client_list.copy()
        for client in clients:
            try:
                client.send(json.dumps({
                    'text': datetime.datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')
                }))
            except:
                client_list.remove(client)


@sock.route('/clock')
def clock(ws):
    client_list.append(ws)
    while True:
        data = ws.receive()
        if data == 'stop':
            break
    client_list.remove(ws)


if __name__ == '__main__':
    t = threading.Thread(target=send_time)
    t.daemon = True
    t.start()
    app.run()

    # app.run(host='0.0.0.0' ,port=5000)

    
