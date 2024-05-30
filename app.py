import string
import bcrypt
from flask import Flask,flash , redirect, render_template, url_for, request, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
import requests
import numpy as np
import pandas as pd
import config
import pickle
import io
import sys
import json
import warnings
import torch
import re
from torchvision import transforms
from utils.fertilizer import fertilizer_dic

warnings.filterwarnings('ignore', message='.*SQLALCHEMY_TRACK_MODIFICATIONS.*')

# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

# Loading crop recommendation model
crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(
        open(crop_recommendation_model_path, 'rb'))  # The open() function is used to open the file in binary mode ('rb'), 
                                                    #which is necessary when working with pickle files.

# Load the Yield pickled model from yield.pkl
yield_model_path = 'models/yield.pkl'   # Same location as crop recommendation model
model = pickle.load(open(yield_model_path, 'rb'))

ohe_model_path = 'models/ohe.pkl'   # Same location as crop recommendation model
ohe = pickle.load(open(ohe_model_path, 'rb')) 

# Load the pickled Random Forest classifier
fert_type_rec_path = 'models/fRF.pkl'
fRF = pickle.load(open(fert_type_rec_path, 'rb'))

fert_type_path = 'models/fertilizer_type.pkl'
ferttype = pickle.load(open(fert_type_path, 'rb'))

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None


app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db' 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'thisissecretkey'

db = SQLAlchemy(app)

# initialization and configuration of a LoginManager object in a Flask application
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class UserAdmin(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=5,max=20)],render_kw={"placeholder":"username"})
    password=PasswordField(validators=[InputRequired(),Length(min=5,max=20)],render_kw={"placeholder":"password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exist.Please choose different one.")

    
class LoginForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=5,max=20)],render_kw={"placeholder":"username"})
    password=PasswordField(validators=[InputRequired(),Length(min=5,max=20)],render_kw={"placeholder":"password"})
    submit = SubmitField("Login")


class ContactUs(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    text = db.Column(db.String(900), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route("/")
def hello_world():
    return render_template("index.html")
    

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        text = request.form['text']
        contacts = ContactUs(name=name, email=email, text=text)
        db.session.add(contacts)
        db.session.commit()

        flash('Your message has been sent successfully!')

        return redirect(url_for('contact'))  # Redirect to the same page after POST

    return render_template("contact.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
         return redirect(url_for('dashboard'))

    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)

                flash('Login successful!', 'success')

                return redirect(url_for('dashboard'))
            
            else:
                 flash('Invalid username or password.', 'error')

    return render_template("login.html", form=form)


@ app.route('/dashboard',methods=['GET', 'POST'])
@login_required
def dashboard():
    title = 'dashboard'
    return render_template('dashboard.html',title=title)

@ app.route('/logout',methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()

    flash("You have been logged out successfully.")
    return redirect(url_for('hello_world'))


@app.route("/signup",methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("User registered successfully!")
        return redirect(url_for('login'))
    
    elif request.method == 'POST':
        flash("Registration failed. Please check your input.")

    return render_template("signup.html", form=form)

#admin login 
@app.route("/reg",methods=['GET', 'POST'])
def adminreg():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user_admin = UserAdmin(username=form.username.data, password=hashed_password)
        db.session.add(user_admin)
        db.session.commit()
        flash("Admin registered successfully!")
        return redirect(url_for('adminlogin'))
    
    elif request.method == 'POST':
        flash("Registration failed. Please check your input.")

    return render_template("reg.html", form=form)

@ app.route('/crop-recommend')
@login_required
def crop_recommend():
    title = 'crop-recommend - Crop Recommendation'
    return render_template('crop.html', title=title)

@ app.route('/fertilizer')
@login_required
def fertilizer_recommendation():
    title = '- Fertilizer Suggestion'
    return render_template('fertilizer.html', title=title)


@ app.route('/album')
def album():
    title = '- Album'
    return render_template('album.html', title=title)

# ===============================================================================================

@app.route("/display")
def querydisplay():
    alltodo = ContactUs.query.all()
    return render_template("display.html",alltodo=alltodo)

@app.route("/AdminLogin", methods=['GET', 'POST'])
def AdminLogin():

    form = LoginForm()
    if current_user.is_authenticated:
         return redirect(url_for('admindashboard'))

    elif form.validate_on_submit():
        user = UserAdmin.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('admindashboard'))
        else:
                flash('Invalid username or password.')
        
    return render_template("adminlogin.html", form=form)

# ===============================================================================================


# ===============================================================================================
# RENDER PREDICTION PAGES

# ===============================================================================================

# render crop recommendation result page


@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = '- Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title)

        else:

            return render_template('try_again.html', title=title)
        
# ===============================================================================================

# render fertilizer recommendation result page


@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = '- Fertilizer Suggestion'


    temp = int(request.form['temperature'])
    humi = int(request.form['humidity'])
    mois = int(request.form['moisture'])
    soil = int(request.form['soiltype'])
    crop = int(request.form['cropname'])
    nitro = int(request.form['nitrogen'])
    pota = int(request.form['pottasium'])
    phosp = int(request.form['phosphorous'])

    

    # Convert values to integers
    input_values = np.array([[temp, humi, mois, soil, crop, nitro , phosp, pota]])

    # Classify using the Random Forest classifier
    res = ferttype.classes_[fRF.predict(input_values)]
   

    crop_name = str(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    

    df = pd.read_csv('Data/fertilizer.csv')

    crop_df = df[df['Crop'] == crop_name]
    if not crop_df.empty:
        nr = crop_df['N'].iloc[0]
        pr = crop_df['P'].iloc[0]
        kr = crop_df['K'].iloc[0]
    else:
    # Handle the case when the DataFrame slice is empty
        crop_name = "maize"
        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]
    
    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = Markup(str(fertilizer_dic[key]))

    return render_template('fertilizer-result.html', recommendation=response, x=res ,title=title)

# ===============================================================================================
# render yield prediction result page

@app.route('/yield', methods=['GET', 'POST'])
@login_required
def yield_prediction():
    title = '- Yield Prediction'

    if request.method == 'POST':
        # Get the input parameters from the form data
        Jprovince = request.form['Jprovince']
        Jdistrict = request.form['Jdistrict']
        Jseason = request.form['Jseason']
        Jcrops = request.form['Jcrops']
        Jarea = request.form['Jarea']

        # Get the user inputs and store them in a numpy array
        user_input = np.array([[Jprovince, Jdistrict, Jseason, Jcrops, Jarea]])

        # Convert the categorical columns to one-hot encoding
        user_input_categorical = ohe.transform(user_input[:, :4])

        # Combine the one-hot encoded categorical columns and numerical columns
        user_input_final = np.hstack((user_input_categorical.toarray(), user_input[:, 4:].astype(float)))

        # Make the prediction
        prediction = model.predict(user_input_final)

        # Render the yield-result.html template with the prediction
        return render_template('yield-result.html', title=title, prediction=prediction[0])
    
    else:

     return render_template('yield.html', title=title)


# ===============================================================================================

     # return render_template("news.html")   
    
@app.route('/news')
def news():
    endpoint = "https://newsapi.org/v2/everything?q=agriculture%20Zimbabwe&sortBy=popularity&apiKey=e13c1810209a4e6ca7997d39b797152c"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        # Pass the first 10 Zimbabwean agricultural news articles to the template
        return render_template('news.html', news_data=data)
    except requests.exceptions.RequestException as error:
        return "There was a problem fetching data from the API: {}".format(error)
    
# return render_template("news.html") //more news

@app.route('/news/more')
def more_news():
    endpoint = "https://newsapi.org/v2/everything?q=agriculture%20Zimbabwe&sortBy=popularity&apiKey=e13c1810209a4e6ca7997d39b797152c"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        # Pass all the Zimbabwean agricultural news articles to the template
        return render_template('news.html', news_data=data)
    except requests.exceptions.RequestException as error:
        return "There was a problem fetching data from the API: {}".format(error)
    
 # ===============================================================================================
   
   # Define the get_weather_icon_class function
def get_weather_icon_class(weather_description):
    icons = {
        'clear': 'fa-sun text-yellow-500',
        'clouds': 'fa-cloud text-gray-500',
        'rain': 'fa-cloud-showers-heavy text-blue-500',
        'thunderstorm': 'fa-bolt text-purple-500',
        'snow': 'fa-snowflake text-white',
        'mist': 'fa-smog text-gray-500',
        # Add more weather descriptions and corresponding icons as needed
    }

    # Find a matching weather description and return the corresponding icon class
    for key, value in icons.items():
        if re.search(key, weather_description, re.IGNORECASE):
            return value

    # Return a default icon class if no match is found
    return 'fa-question text-gray-500'  # Default icon: question mark                            
                               
                              
# return render_template("weather.html") 

@app.route('/weather', methods=['POST', 'GET'])
def weather():
     # Pass the get_weather_icon_class function to the template environment
    template_env = app.jinja_env
    template_env.globals['get_weather_icon_class'] = get_weather_icon_class
    
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # Perform API request to retrieve weather data
            api_key = "870887df4d2b01335921fe396c69a360"  # Replace with your OpenWeatherMap API key
            api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&lang=en&units=metric&appid={api_key}"
            response = requests.get(api_url)
            data = response.json()

            # Check if the API response contains the weather data
            if 'list' in data:
                weather_forecast = []
                for forecast in data['list']:
                    # Access the weather data for each forecast
                    date = forecast['dt_txt']
                    temperature_max = forecast['main']['temp_max']
                    temperature_min = forecast['main']['temp_min']
                    weather_description = forecast['weather'][0]['main'] + ', ' + forecast['weather'][0]['description']
                    humidity = forecast['main']['humidity']
                    wind_speed = forecast['wind']['speed']

                    # Store the weather data in a dictionary
                    forecast_data = {
                        'date': date,
                        'temperature_max': temperature_max,
                        'temperature_min': temperature_min,
                        'weather_description': weather_description,
                        'humidity': humidity,
                        'wind_speed': wind_speed
                    }

                    # Add the forecast data to the forecast list
                    weather_forecast.append(forecast_data)

                return render_template('weather.html', weather_forecast=weather_forecast, city=city)
            else:
                return render_template('weather.html', error_message=f"No weather forecast available for {city}")
        else:
            return render_template('weather.html', error_message="Please enter a valid city.")
    else:
        return render_template('weather.html')
    
 # ===============================================================================================
       

@app.route("/admindashboard")
@login_required
def admindashboard():
    alltodo = ContactUs.query.all()
    alluser = User.query.all()
    return render_template("admindashboard.html",alltodo=alltodo, alluser=alluser)

# ===============================================================================================

@app.route("/reg",methods=['GET', 'POST'])
def reg():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = UserAdmin(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("User registered successfully!")
        return redirect(url_for('AdminLogin'))
    else:
        flash("Registration failed. Please check your input.")

    return render_template("reg.html", form=form)
 # ===============================================================================================


if __name__ == "__main__":
    db.create_all()

db.session.commit()

app.run(debug=True,port=8000)
