from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
from flask_cors import CORS
import bcrypt

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = "super_secret_key"
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class stude_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    education = db.Column(db.String(200))
    skillI = db.Column(db.String(200))  # Skill I
    skillC = db.Column(db.String(200))  # Skill C
    password = db.Column(db.String(100), nullable=True)  # Optional
    student_type = db.Column(db.String(20))  # Add student_type column

    def __init__(self, name, email, phone, address, education, skillI, skillC, student_type, password=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.education = education
        self.skillI = skillI
        self.skillC = skillC
        self.student_type = student_type  # Add student_type to the constructor
        self.password = password


with app.app_context():
    db.create_all()
    
# Routes
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already exists")

        new_user = User(name=name, email=email, password=password)  # Will be hashed in model
        db.session.add(new_user)
        db.session.commit()
        session['email'] = new_user.email
        return redirect('/dashboard_1.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard_1.html')
        else:
            return render_template('form.html', error='Invalid email or password')

    return render_template('form.html')

@app.route('/dashboard_1.html')
def dashboard():
    if session.get('email'):
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard_1.html', user=user)
    
    return redirect('/login')




# Make sure this appears only once in your code


# Static pages
@app.route('/aboutus.html')
def about():
    return render_template('aboutus.html')

@app.route('/contactus.html')
def contact():
    return render_template('contactus.html')

@app.route('/form.html')
def form():
    return render_template('form.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/index1.html')
def index1():
    return render_template('index1.html')

@app.route('/teacher.html')
def teacher():
    return render_template('teacher.html')

@app.route('/aboutus - Copy.html')
def about_copy():
    return render_template('aboutus - Copy.html')

@app.route('/contactus - Copy.html')
def contactus_copy():
    return render_template('contactus - Copy.html')

@app.route('/teacher - Copy.html')
def teacher_copy():
    return render_template('teacher - Copy.html')

@app.route('/michael.html')
def michael():
    return render_template('michael.html')

@app.route('/shradha.html')
def shradha():
    return render_template('shradha.html')

@app.route('/cwh.html')
def cwh():
    return render_template('cwh.html')

@app.route('/Jenny.html')
def Jenny():
    return render_template('Jenny.html')

@app.route('/Emma.html')
def Emma():
    return render_template('Emma.html')

@app.route('/Lisa.html')
def Lisa():
    return render_template('Lisa.html')

@app.route('/info', methods=['GET', 'POST'])
def stud_info():
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        education = request.form['education']
        skillI = request.form['skillI']
        skillC = request.form['skillC']
        student_type = request.form['studentType']  # Ensure this matches your form input name

        # Create new student record
        new_user = stude_info(
            name=name,
            email=email,
            phone=phone,
            address=address,
            education=education,
            skillI=skillI,
            skillC=skillC,
            student_type=student_type  # Pass student_type as a keyword argument
        )

        # Add to database and commit
        db.session.add(new_user)
        db.session.commit()

        # Redirect after successful form submission
        return redirect('/teacher.html')

    # For GET request, render the form page
    return render_template('info.html')


@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/index.html')

if __name__ == '__main__':
    if not os.path.exists("databases"):
        os.makedirs("databases")
    app.run(debug=True)