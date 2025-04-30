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
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()
    
# Routes
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/dashboard_1.html')



    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard_1.html')
        else:
            return render_template('form.html',error='Invalid user')

    return render_template('login')

@app.route('/dashboard_1.html')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard_1.html',user=user)
    
    return redirect('/login')


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

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/index.html')

if __name__ == '__main__':
    if not os.path.exists("databases"):
        os.makedirs("databases")
    app.run(debug=True)