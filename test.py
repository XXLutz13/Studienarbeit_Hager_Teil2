from flask import Flask, render_template, flash, request, make_response, send_file, redirect, url_for, current_app
import secrets
from datetime import datetime
import os
import cv2


# create flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}


dataLabel = ""
numImages = 0
active = False
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
            test_file(dataLabel)
            # return redirect(url_for('running'))
            
    if active:
        return redirect(url_for('running'))
    else:
        return render_template('index.html')


#----------------------------------------------------------------------------------------------------------------
#   websocket for sending image 
#----------------------------------------------------------------------------------------------------------------
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

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000) 

