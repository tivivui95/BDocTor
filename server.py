from flask import Flask, render_template,request,redirect, url_for, send_from_directory
import os
from werkzeug import secure_filename
import cv2
from tensorflow.keras.models import load_model
from Detector import Detector
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
from predict import detection_on_image
# BlurPointTrackingPath ="modelblur_inf.h5"
# model = models.load_model(BlurPointTrackingPath, backbone_name='resnet50')
USERNAME = 'admin'
PASSWORD = 'admin'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
@app.route('/', methods=['GET', 'POST'])
# Signin
def get_signin():
    if request.method == 'POST':
        username = request.form['fname']
        password = request.form['fpass']
    else:
        return render_template('signin.html')
    if username == USERNAME and password == PASSWORD:
        return redirect('/chandoan')
    else:
        return redirect('/signin')
@app.route('/register', methods=['GET', 'POST'])
# Register
def get_register():
    return render_template('register.html')
# history
@app.route('/history', methods=['GET','POST'])
def history():
    return render_template('history.html')
#chandoan
@app.route('/chandoan')
def index():
    return render_template('index.html')
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2)]
    for image_path in TEST_IMAGE_PATHS:
    	img = cv2.imread(image_path)
    	draw = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    	kq= detection_on_image(image_path)
    	colors= kq[0]
    	b=kq[1]
    	caption = kq[2]
    	draw_box(draw, b, color=colors)
    	draw_caption(draw, b, caption)
    	detected_img =cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)

    	diachi ='uploads/'+filename
    	cv2.imwrite(diachi, detected_img)

    	
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
if __name__ == '__main__':
    app.run(debug=True,host='192.168.43.214',port=3000)