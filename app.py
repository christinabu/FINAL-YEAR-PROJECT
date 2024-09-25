from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import pyrebase
import json
from calendar import monthrange
from datetime import datetime, timedelta

app = Flask(__name__)

#-----------------------------------------------------Home page--------------------------------------------------------------
@app.route('/')
def home():
    return render_template('landingpage.html')

#-------------------------------------------------------signup page----------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']  # Capture username from the form
        
        try:
            # Create user with email and password
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user['localId']
            # Update profile with display name
            auth.update_profile(user['idToken'], {'displayName': username})
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "An error occurred while creating your account."
            return redirect(url_for('dashboard'))
    return render_template('signup.html')


#-------------------------------------------------------Sign in page-----------------------------------------------------------
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Clear session when user visits sign-in page
    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            
            # Retrieve user data
            user_info = auth.get_account_info(user['idToken'])
            # Extract username
            username = user_info['users'][0].get('displayName', "Admin")

            # Store the username in the session
            session['username'] = username

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "Authentication failed. Please check your email and password."
            return render_template('error.html', error=error)
    return render_template('signup.html')

#----------------------------------------------forgot password-----------------------------------------------------

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            return "Password reset email sent. Check your inbox."
        except Exception as e:
            return "An error occurred: " + str(e)
    # Render a simple form with an input field for email
    return render_template('Passreset.html')

#-------------------------------------------------Dashboard page--------------------------------------------------

def get_current_dates():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_start_date = f"{current_year}-{current_month:02d}-01"
    current_end_date = f"{current_year}-{current_month:02d}-{monthrange(current_year, current_month)[1]}"
    
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    prev_start_date = f"{prev_year}-{prev_month:02d}-01"
    prev_end_date = f"{prev_year}-{prev_month:02d}-{monthrange(prev_year, prev_month)[1]}"
    
    return current_start_date, current_end_date, prev_start_date, prev_end_date



def calculate_total_amount(ref):
    total = 0
    if ref:
        for item in ref.each():
            total += float(item.val()['amount'])
    return total


def fetch_category_data(user_id):
    expenditure_data = db.child("users").child(user_id).child("expenditure").get().val()
    category_totals = {}
    for key, item in expenditure_data.items():
        category = item['category']
        amount = float(item['amount'])
        category_totals[category] = category_totals.get(category, 0) + amount

    category_labels = list(category_totals.keys())
    category_amounts = list(category_totals.values())
    return category_labels, category_amounts

def fetch_monthly_income_data(user_id, start_date, end_date):
    incomes_ref = db.child("users").child(user_id).child("income") \
        .order_by_child("date").start_at(start_date).end_at(end_date).get()
    
    monthly_income = {}
    for item in incomes_ref.each():
        date = item.val()['date']
        amount = float(item.val()['amount'])
        month_year = date[:7]  # Extracting YYYY-MM format
        
        if month_year in monthly_income:
            monthly_income[month_year] += amount
        else:
            monthly_income[month_year] = amount
            
    # Sort the monthly income data by month_year
    sorted_monthly_income = dict(sorted(monthly_income.items()))
    
    return list(sorted_monthly_income.keys()), list(sorted_monthly_income.values())


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_id = session['user']
        username = session.get('username', 'admin')
        
        # Get current month and year  and Calculate start and end dates of the current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_start_date = f"{current_year}-{current_month:02d}-01"
        current_end_date = f"{current_year}-{current_month:02d}-{monthrange(current_year, current_month)[1]}"
        

        # Calculate start and end dates of the previous month
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        prev_start_date = f"{prev_year}-{prev_month:02d}-01"
        prev_end_date = f"{prev_year}-{prev_month:02d}-{monthrange(prev_year, prev_month)[1]}"
        
        # Query Firebase to fetch expenditures for the current month
        expenditures_ref = db.child("users").child(user_id).child("expenditure") \
            .order_by_child("date").start_at(current_start_date).end_at(current_end_date).get()

        # Calculate total expenditure for the current month
        total_expenditure = 0
        if expenditures_ref:
            for exp in expenditures_ref.each():
                total_expenditure += float(exp.val()['amount'])
        
        # Query Firebase to fetch incomes for the current month
        incomes_ref = db.child("users").child(user_id).child("income") \
            .order_by_child("date").start_at(current_start_date).end_at(current_end_date).get()
        
        # Calculate total income for the current month
        total_income = 0
        if incomes_ref:
            for inc in incomes_ref.each():
                total_income += float(inc.val()['amount'])
        
        profit = total_income - total_expenditure

        #print("*****************************************************************",total_income,total_expenditure,profit)


        # Query Firebase to fetch expenditures for the previous month
        prev_expenditures_ref = db.child("users").child(user_id).child("expenditure") \
            .order_by_child("date").start_at(prev_start_date).end_at(prev_end_date).get()
        
        # Calculate total expenditure for the previous month
        prev_total_expenditure = 0
        if prev_expenditures_ref:
            for exp in prev_expenditures_ref.each():
                prev_total_expenditure += float(exp.val()['amount'])
        
        # Query Firebase to fetch incomes for the previous month
        prev_incomes_ref = db.child("users").child(user_id).child("income") \
            .order_by_child("date").start_at(prev_start_date).end_at(prev_end_date).get()
        
        # Calculate total income for the previous month
        prev_total_income = 0
        if prev_incomes_ref:
            for inc in prev_incomes_ref.each():
                prev_total_income += float(inc.val()['amount'])
        
        prev_profit = prev_total_income - prev_total_expenditure

        # Calculate percentage change in income
        # Calculate percentage change in income
        income_change = round(((total_income - prev_total_income) / prev_total_income) * 100, 1) if prev_total_income != 0 else 0

        # Calculate percentage change in expenditure
        expenditure_change = round(((total_expenditure - prev_total_expenditure) / prev_total_expenditure) * 100, 1) if prev_total_expenditure != 0 else 0

        # Calculate percentage change in profit
        profit_change = round(((profit - prev_profit) / prev_profit) * 100, 1) if prev_total_income != 0 else 0

        #------------------------------pie chart------------------------------------
        
        # Query Firebase to fetch expenditure data
        expenditure_data = db.child("users").child(user_id).child("expenditure").get().val()

        # Initialize dictionary to store total expenditure for each category
        category_totals = {}

    # Process the data to calculate total expenditure for each category
        for key, item in expenditure_data.items():
            category = item['category']
            amount = float(item['amount'])
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        # Convert the data into lists for rendering in the template
        category_labels = list(category_totals.keys())
        category_amounts = list(category_totals.values())     
        
          
        return render_template(
            'dashboard.html', 
                           username=username, 
                           total_expenditure=total_expenditure, 
                           total_income=total_income, 
                           income_change=income_change, 
                           expenditure_change=expenditure_change, 
                           profit=profit, 
                           profit_change=profit_change,
                           category_labels=category_labels,
                           category_amounts=category_amounts,
        )
    else:
        # If user is not in session, redirect to sign-in page
        return redirect(url_for('signin'))
#-------------------------------------------------logout page------------------------------------------------------
@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('user', None)
    # Redirect to the signin page
    return redirect(url_for('signin'))

#-------------------------------------------------Livestock data page----------------------------------------------
# Function to check if the cow ID already exists for the user
def check_cow_id(user_id, cow_id):
    livestock_data = db.child("users").child(user_id).child("livestock").get()
    if livestock_data:
        for cow in livestock_data.each():
            if cow.val().get("cow_id") == cow_id:
                return True  # Cow ID already exists for the user
    return False  # Cow ID doesn't exist for the user

# Route for adding livestock information
@app.route('/livestock', methods=['GET', 'POST'])
def livestock():
    if 'user' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in page if user is not authenticated

    user_id = session['user']
    if request.method == 'POST':
        # Handle form submission
        cow_id = request.form['cow_id']
        breed = request.form['breed']
        dob = request.form['dob']
        avg_milk = request.form['avg_milk']
        buying_price = request.form['buying_price']

        # Check if the cow ID already exists for the user
        existing_cows = db.child("users").child(user_id).child("livestock").get().val()
        if existing_cows and any(cow['cow_id'] == cow_id for cow in existing_cows.values()):
            return render_template('error.html', error="Cow ID already exists. Please choose a different ID.")

        # Push livestock data to Firebase under the user's node
        try:
            db.child("users").child(user_id).child("livestock").push({
                "cow_id": cow_id,
                "breed": breed,
                "dob": dob,
                "avg_milk": avg_milk,
                "buying_price": buying_price
            })
        except Exception as e:
            return render_template('error.html', error=str(e))

    # Fetch the keys (child paths) under the "livestock" node
    livestock_data = db.child("users").child(user_id).child("livestock").order_by_child("cow_id").get().val()
    return render_template('livestock.html', livestock_data=livestock_data)

#-----------------------------------------------Expenditure page------------------------------------------------
@app.route('/expenditure', methods=['GET', 'POST'])
def expenditure():
    if 'user' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in page if user is not authenticated

    user_id = session['user']

    if request.method == 'POST':
        # Handle form submission
        date = request.form['date']
        category = request.form['category']
        description = request.form['description']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        supplier = request.form['supplier']
        invoice_number = request.form['invoice_number']

        expenditure_data = {
            "date": date,
            "category": category,
            "description": description,
            "amount": amount,
            "payment_method": payment_method,
            "supplier": supplier,
            "invoice_number": invoice_number,
        }

        # Store the expenditure data into Firebase under the user's node
        try:
            db.child("users").child(user_id).child("expenditure").push(expenditure_data)
        except Exception as e:
            return render_template('error.html', error=str(e))

        # Redirect to a different URL after form submission to prevent resubmission
        return redirect(url_for('expenditure'))

    # Fetch expenditure data for the user
    expenditures = db.child("users").child(user_id).child("expenditure").order_by_child("date").get().val()

    # Convert the dictionary of expenditure data to a list of dictionaries
    expenditure_list = []
    if expenditures:
        for key, value in reversed(expenditures.items()):
            value['key'] = key  # Include the key in each expenditure entry for identification
            expenditure_list.append(value)

    return render_template('expenditure.html', expenditures=expenditure_list)

    # Fetch expenditure data for the user
    #expenditure_data = db.child("users").child(user_id).child("expenditure").order_by_child("date").get().val()
    #return render_template('expenditure.html')

#---------------------------------------------Income Page---------------------------------------------------------
@app.route('/income', methods=['GET', 'POST'])
def add_income():
    if 'user' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in page if user is not authenticated
    
    user_id = session['user']
    
    if request.method == 'POST':
        date = request.form['date']
        source = request.form['source']
        description = request.form['description']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        
        income_data = {
            "date": date,
            "source": source,
            "description": description,
            "amount": amount,
            "payment_method": payment_method
        }
        
        try:
            db.child("users").child(user_id).child("income").push(income_data)
        except Exception as e:
            return render_template('error.html', error=str(e))
        
        # Redirect to prevent form resubmission
        return redirect(url_for('add_income'))
    
    # Fetch income data for the user
    income_data = db.child("users").child(user_id).child("income").order_by_child("date").get().val()
    income_list = []  # Convert income data to a list for rendering
    if income_data:
        for key, value in reversed(income_data.items()):
            value['key'] = key  # Include the key for identification if needed
            income_list.append(value)
    # Render the income.html template with income data
    return render_template('income.html', income_data=income_list)


#------------------------------------------------Machine learning integration--------------------------------------

# Specify the upload folder inside the static directory
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Specify the allowed extensions for file uploads
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Load the pre-trained model
loaded_model = load_model(r'C:\Users\proma\Desktop\FINAL YEAR PROJECT\final_model.h5')

# Function to check if the file has allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function for contrast stretching
def contrast_stretching(img):
    if img.shape[-1] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    min_val, max_val, _, _ = cv2.minMaxLoc(img)
    stretched_img = np.uint8((img - min_val) / (max_val - min_val) * 255)

    if len(stretched_img.shape) == 2:
        stretched_img = cv2.cvtColor(stretched_img, cv2.COLOR_GRAY2BGR)

    return stretched_img

# Function to preprocess the image
def preprocess_image(img_path):
    img = cv2.imread(img_path)

    if img is None:
        print(f"Error: Unable to load image from {img_path}")
        return None

    img = contrast_stretching(img)

    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.resnet50.preprocess_input(img)

    return img

# Function to predict the image
def predict_image(model, preprocessed_image):
    predictions = model.predict(preprocessed_image)
    return predictions

@app.route('/disease_prediction')
def disease_prediction():
    return render_template('disease_prediction.html') 

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template('error.html', error='No file found')

    file = request.files['file']

    if file.filename == '':
        return render_template('error.html', error='No file found')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = url_for('static', filename='uploads/' + filename)
        preprocessed_image = preprocess_image(file_path)

        if preprocessed_image is not None:
            predictions = predict_image(loaded_model, preprocessed_image)
            predicted_class = (predictions > 0.65).astype(int).flatten()[0]

            if predicted_class == 0:
                xem = (predictions > 0.5).astype(int).flatten()[0]
                if xem == 1:
                    prediction_result = "The cow may have an infection"
                else:
                    prediction_result = "The uploaded image is predicted to be healthy."
            else:
                prediction_result = "The uploaded image is predicted to be infected."

            return render_template('prediction_result.html', prediction=prediction_result, image_url=image_url)
        else:
            return render_template('error.html', error="Error in image preprocessing.")
    else:
        return render_template('error.html', error="File type not allowed")

#-------------------------------------------------config-------------------------------------------------------
if __name__ == '__main__':

    # Set the secret key for session management
    app.secret_key = '1a3f6c9e47b8d2f10e5a7b3c8f9d0e2a'
    
    # Firebase configuration
    firebaseConfig = {
        "apiKey": "AIzaSyA8Q8619M2fOJpjpqMUoqlP_l7MxBJT2y0",
        "authDomain": "s8project-e9096.firebaseapp.com",
        "databaseURL": "https://s8project-e9096-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "s8project-e9096",
        "storageBucket": "s8project-e9096.appspot.com",
        "messagingSenderId": "105612683914",
        "appId": "1:105612683914:4:web:f6629fc45d8873c5a85b73"
    }

    # Initialize Firebase app
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()  # Initialize the Firebase database

    app.run(debug=True)
