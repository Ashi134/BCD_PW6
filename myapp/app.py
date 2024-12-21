from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import register_keras_serializable
from tensorflow.keras.models import model_from_json
from keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import model_from_json
from tensorflow.keras.preprocessing.image import img_to_array, load_img

from PIL import Image
from io import BytesIO
from keras.preprocessing.image import img_to_array
import numpy as np
import io


app = Flask(__name__)
model = None
graph = tf.compat.v1.get_default_graph()

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/6thSem/project_4/PW4_BreastCancerDetector/myapp/database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def load_request_image(image):
    image = Image.open(io.BytesIO(image))
    image = image.resize((224, 224))  # Example: Resize to 224x224, adjust as needed
    image = np.array(image)  
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image
    # if image.mode != "RGB":
    #     image = image.convert("RGB")
    # image = image.resize((48, 48))
    # image = img_to_array(image)
    # image = preprocess_input(image)
    # image = np.expand_dims(image, axis=0)

    return image


def load_model():
    global model
    try:
        # Load model architecture
        with open('E:/6thSem/project_4/PW4_BreastCancerDetector/ipynb_checkpoints/model1.json', 'r') as json_file:
            model_json = json_file.read()
            model = model_from_json(model_json)
        # Load model weights
        model.load_weights('E:/6thSem/project_4/PW4_BreastCancerDetector/ipynb_checkpoints/bc_detect.h5.keras')
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

# def load_model():
#     global model  # Use the global variable

#     json_file = open('E:/6thSem/project_4/PW4_BreastCancerDetector/ipynb_checkpoints/model1.json', 'r')
#     model1_json = json_file.read()
#     json_file.close()
#     model = model_from_json(model1_json)
    # model_weights_path = 'E:/6thSem/project_4/PW4_BreastCancerDetector/ipynb_checkpoints/bc_detect.h5.keras'
    
    # try:
    #     model.load_weights(model_weights_path)
    # except Exception as e:
    #     print(f"Error loading weights: {e}")
    #model.load_weights('E:/6thSem/project_4/PW4_BreastCancerDetector/ipynb_checkpoints/bc_detect.h5.keras')

def predict_class(image_array):
    print('=========================')
    global model
    if model is None:  # Safety check to ensure the model is loaded
        load_model()
    print(model)
    classes = [ "Benign", "Malignant"]
    y_pred = model.predict(image_array, verbose=0)[0]
    print(y_pred)
    class_index = np.argmax(y_pred)
    confidence = y_pred[class_index]
    class_predicted = classes[class_index]
    print('-------------'+confidence)
    print('-------------'+class_predicted)
    return class_predicted, confidence
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])


class feedbackForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    feedback = StringField('Feedback', validators=[
                           InputRequired(), Length(min=4, max=400)])

# @app.route('/test_model', methods=['GET'])
# def test_model():
#     try:
#         load_model()
#         return "Model loaded successfully.", 200
#     except Exception as e:
#         return f"Error: {e}", 500
    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
#    print("class:malignant and confidence :0.856734521")
   try:
        #print("class:malignant and confidence :0.856734521")
        image = request.files["image"].read()
        image = load_request_image(image)
        #print(image)
        class_predicted, confidence = predict_class(image)
        #print(class_predicted)
        image_class = {"class": class_predicted, "confidence": str(confidence)}
        print("Response being sent:", image_class)
        return jsonify(image_class)
   except Exception as e:
        print("Error:", str(e)) 
        return jsonify({"error": str(e)}), 500


@app.route('/dashboard/feedback', methods=['GET', 'POST'])
def feedback():
    form = feedbackForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if (user.username == form.username.data) & (user.email == form.email.data):
                # login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or email</h1>'
    # if form.validate_on_submit():
    #     new_user = User(username=form.username.data,
    #                     email=form.email.data, feedback=form.feedback.data)
    #     db.session.add(new_user)
    #     db.session.commit()
        # return '<h1>Thank you for your feedback!</h1>'

    return render_template('feedback.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "app":
    load_model()