from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for
from flask_sock import Sock
import json
import time, datetime
import threading
import secrets
from flask import current_app

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}


sock = Sock(app)

client_list = []
client_list_test = []

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

@app.route('/progress')
def send_progress():
    # send the state for the progress bar
    response = make_response('80%', 200)
    response.mimetype = "text/plain"
    return response


@sock.route('/image')
def clock(ws):
    client_list.append(ws)
    print(client_list)
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
                client.send(json.dumps({
                    'text': 'http://127.0.0.1:5000/static/images/Test_Images/Test.png'
                }))
            except:
                print("failed")
                client_list.remove(client)

# @sock.route('/testing')
# def clock(ws):
#     client_list_test.append(ws)

if __name__ == '__main__':
    t = threading.Thread(target=send_img)
    t.daemon = True
    t.start()
    app.run()
