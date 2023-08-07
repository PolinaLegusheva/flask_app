import cv2
import numpy as np
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user, LoginManager
from tensorflow import keras
from run import app
from models import db
import os
from models import User
from auth import auth as auth_blueprint
from flask import send_file
from werkzeug.utils import secure_filename

# WSGI Application
# Defining upload folder path
UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
main = Blueprint('main', __name__, template_folder='templates', static_folder='staticFiles')
last_uploaded_file = None


@main.route('/profile')
@login_required
def profile():
    session['count'] = session.get('count', 0) + 1
    calculation = User(count=session['count'])
    db.session.add(calculation)
    db.session.commit()
    return render_template('profile.html', name=current_user.name, count=session['count'])


@main.route('/')
def index():
    return render_template('upload_display_img.html')


model = keras.models.load_model('/home/pl/Documents/practice_data/model')


def process_image(image_path):
    # Открытие изображения
    image = cv2.imread(UPLOAD_FOLDER)
    # Обработка изображения
    processed_image = np.expand_dims(cv2.resize(image, (270, 210)), 0)
    # Предсказание с помощью модели
    prediction = model.predict(processed_image)

    return prediction


@main.route('/', methods=("POST", "GET"))
def uploadFile():

    if request.method == 'POST':
        global last_uploaded_file
        # Upload file flask
        uploaded_img = request.files['uploaded-file']
        # Extracting uploaded data file name
        img_filename = secure_filename(uploaded_img.filename)
        # Upload file to database (defined uploaded folder in static path)
        uploaded_img.save(os.path.join(UPLOAD_FOLDER, img_filename))
        # Storing uploaded file path in flask session
        session['uploaded_img_file_path'] = os.path.join(UPLOAD_FOLDER, img_filename)
        last_uploaded_file = img_filename
        return render_template('upload_display_img2.html')


@main.route('/show_image')
def displayImage():
    # Retrieving uploaded file path from session
    img_file_path = session.get('uploaded_img_file_path', None)
    # Display image in Flask application web page
    return render_template('show_img.html', user_image=img_file_path)


@main.route('/download')
def download():
    global last_uploaded_file
    if last_uploaded_file:
        return send_file(os.path.join(UPLOAD_FOLDER, last_uploaded_file), as_attachment=True)
    else:
        return '<h1>No files uploaded yet</h1>'


db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_blueprint)
app.register_blueprint(main)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)