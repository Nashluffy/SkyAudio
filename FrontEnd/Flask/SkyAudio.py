from flask import send_file, Flask, flash, redirect, send_from_directory, render_template, url_for, request, Response
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from nameko.standalone.rpc import ClusterRpcProxy
from flask_cors import CORS
import os, boto3, wave
import logging

SERVER_IP = os.environ.get('SERVER_IP')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS')


#UPLOAD_FOLDER = '/home/ec2-user/SkyAudio/SkyAudio/FrontEnd/Flask/tmp/'
UPLOAD_FOLDER = 'tmp/SkyAudio/'
ALLOWED_EXTENSIONS = set(
    ['txt', 'mp3', 'wav', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
AMQP_URI = 'amqp://' + str(RABBITMQ_USER) + ':' + \
    str(RABBITMQ_PASS) + '@' + str(SERVER_IP)
CONFIG = {'AMQP_URI': "amqp://dev_user:dev_pass@34.227.109.165:5672"}
#CONFIG = {'AMQP_URI': AMQP_URI}
application = Flask(__name__)
Bootstrap(application)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(application)


s3_client = boto3.client('s3')


@application.route("/home", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        #First, we need to get the selected effect from the request
        selectedItem = request.form.get('effectHolder')
        print('Selected Effect is: ' + selectedItem)
        
        #Next, we need to get the blob file
        if 'blob' in request.files:
            file = request.files['blob']
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], 'download.ogg'))
        else:
            print('No file found!')

        #Then, we need to process the file depending on the selected effect
        if selectedItem == 'reverbSmallRoom':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.reverbSmallRoom()
        elif selectedItem == 'reverbCaveEffect':
           with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.reverbReflectiveCave()
        elif selectedItem == 'reverbConcertHall':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.reverbConcertHall()
        elif selectedItem == 'miscReverseSong':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.miscReverseSong()
        elif selectedItem == 'phaserDefault':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.phaserDefault()
        elif selectedItem == 'phaserSpaceEffect':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.phaserSpaceEffect()
        elif selectedItem == 'phaserSubtle':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.phaserSubtle()
        elif selectedItem == 'miscSpeedUp2x':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.miscSpeedUp2x()
        elif selectedItem == 'miscSlowDownHalf':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.miscSlowDownHalf()
        elif selectedItem == 'miscReset':
            with ClusterRpcProxy(CONFIG) as rpc:
                result = rpc.SigProc.miscSlowDownHalf()
        #Then, return the file
        return send_file(os.path.join(application.config['UPLOAD_FOLDER'], 'processed.ogg'))
        
     

    elif request.method == 'GET':
        return render_template('index.html', title='Testing')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route('/download', methods=['GET'])
def download_file():
    if request.method == 'GET':
        filename = request.form['file']
        s3_client.download_file(
            bucket, filename, UPLOAD_FOLDER + '/' + filename)
        file = UPLOAD_FOLDER + '/' + filename
        return send_file(file)

#@application.route('/', methods=['POST'])
#def upload_file():
#    if request.method == 'POST':
#        file = request.files['file']
#        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
#            response = s3_client.upload_file(UPLOAD_FOLDER + '/' + filename, bucket, file.filename)
#            os.remove(UPLOAD_FOLDER + '/' + filename)
#        return 'Successfully uploaded to S3'
@application.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(application.config['UPLOAD_FOLDER'],
                               filename)


@application.route("/")
def home():
    return render_template('login.html', title='Login')


@application.route("/register")
def register():
    return render_template('register.html', title='Register New')


@application.route("/forgot-password")
def forgot():
        return render_template('forgot-password.html', title='Password')


@application.route("/record")
def record():
    return render_template('record.html', title='Record')


# @application.route("/uploader" , methods = ['GET', 'POST'])
# def upload_file():
#	if request.method == 'POST':
#		f = request.files['file']
#		f.save(secure_filename(f.filename))
#		return "file uploaded successfully"


if __name__ == '__main__':
    application.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)
