from flask import Flask, render_template,Flask, request, jsonify
import sqlite3

app = Flask(__name__, template_folder='templates')

def insert_user(name, phone, address, interesting_language, known_language, level):
    conn = sqlite3.connect("skillhub.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, phone, address, interesting_language, known_language, level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, address, interesting_language, known_language, level))
        
        conn.commit()
        return True, "Profile saved successfully!"
    except sqlite3.IntegrityError:
        return False, "Phone number already exists!"
    finally:
        conn.close()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/aboutus.html')
def about():
    return render_template('aboutus.html')

@app.route('/contactus.html')
def contact():
    return render_template('contactus.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/form.html')
def form():
    return render_template('form.html')

@app.route('/signin.html')
def signin():
    return render_template('signin.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route("/save-profile", methods=["POST"])
def save_profile():
    data = request.json
    success, message = insert_user(
        data["name"], data["phone"], data["address"],
        data["interestingLanguage"], data["knownLanguage"], data["level"]
    )
    return jsonify({"success": success, "message": message})


if __name__ == '__main__':
    app.run(debug=True)
