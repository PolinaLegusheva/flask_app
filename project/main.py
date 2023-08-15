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
from PIL import Image
import time


main = Blueprint('main', __name__, template_folder='templates', static_folder='staticFiles')


@main.route('/profile')
@login_required
def profile():
    session['count'] = session.get('count', 0) + 1
    calculation = User()
    db.session.add(calculation)
    db.session.commit()
    return render_template('profile.html', name=current_user.name, count=session['count'])


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/home')
def home():
    return render_template('upload_display_img.html')


model = keras.models.load_model('/home/pl/Documents/practice_data/model')


def process_image(image):
    # Загрузите серое изображение
    img = Image.open(image).convert('L')
    img = img.resize((270, 210))
    # Произведите преобразование из серого в цветное
    img_array = np.array(img)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    # Расширьте размерность массива изображения
    img_array = np.expand_dims(img_array, axis=0)
    # Получите прогноз цветных значений пикселей
    prediction = model.predict(img_array/255.0)
    # Преобразуйте массив прогнозов в изображение
    processed_img = Image.fromarray(np.uint8(prediction[0]*255.0))

    return processed_img


@main.route('/home', methods=["POST"])
def uploadFile():
    image = request.files['image']
    processed_img = process_image(image)
    processed_img.save('staticFiles/uploads' + image.filename)
    return render_template('upload_display_img2.html', processed_img=image.filename)


@app.route('/processed/<filename>')
def processed(filename):
    return send_file('staticFiles/uploads' + filename, mimetype='image/png')


@app.route('/download/<filename>')
def download(filename):

    if filename:
        return send_file('staticFiles/uploads' + filename, as_attachment=True)
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