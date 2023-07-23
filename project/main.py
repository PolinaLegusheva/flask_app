from flask import Blueprint, render_template, request, session, Flask, redirect
from flask_login import login_required, current_user, LoginManager
from db import db
import os

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# WSGI Application
# Defining upload folder path
UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')

main = Blueprint('main', __name__, template_folder='templates', static_folder='staticFiles')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/')
def index():
    return render_template('upload_display_img.html')


@main.route('/', methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        # Upload file flask
        uploaded_img = request.files['uploaded-file']
        # Extracting uploaded data file name
        img_filename = secure_filename(uploaded_img.filename)
        # Upload file to database (defined uploaded folder in static path)
        uploaded_img.save(os.path.join(UPLOAD_FOLDER, img_filename))
        # Storing uploaded file path in flask session
        session['uploaded_img_file_path'] = os.path.join(UPLOAD_FOLDER, img_filename)

        return render_template('upload_display_img2.html')


@main.route('/show_image')
def displayImage():
    # Retrieving uploaded file path from session
    img_file_path = session.get('uploaded_img_file_path', None)
    # Display image in Flask application web page
    return render_template('show_img.html', user_image=img_file_path)


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)


app.register_blueprint(main)

import models

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)