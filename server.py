from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from flask_cors import CORS  # ✅ Allow frontend requests

app = Flask(__name__, template_folder='templates')
CORS(app)  # ✅ Enable Cross-Origin Requests

# Create Main Database for Users
def create_main_database():
    conn = sqlite3.connect("skillhub_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
    conn.commit()
    conn.close()

create_main_database()

# Create User-Specific Database
def create_user_database(email):
    safe_email = email.replace('@', '_').replace('.', '_')  # ✅ Fix invalid filenames
    db_name = f"databases/user_{safe_email}.db"

    if not os.path.exists("databases"):
        os.makedirs("databases")  # ✅ Ensure directory exists

    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                interesting_language TEXT,
                known_language TEXT,
                level TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    return db_name

# Function to Register User
def register_user(email, password):
    try:
        conn = sqlite3.connect("skillhub_users.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        print(f"✅ User {email} registered successfully!")
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        print(f"⚠️ Error: Email {email} already exists!")
        return False, "Email already exists!"
    except Exception as e:
        print("⚠️ Database error:", str(e))
        return False, "Database error!"

# Function to Verify User
def verify_user(email, password):
    conn = sqlite3.connect("skillhub_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    conn.close()
    return row and row[0] == password

# Save Profile Data
@app.route("/save-profile", methods=["POST"])
def save_profile():
    try:
        data = request.json
        email = data.get("email")

        if not email:
            return jsonify({"success": False, "message": "Email is required!"}), 400

        db_path = create_user_database(email)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO profile (name, phone, address, interesting_language, known_language, level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["name"], data["phone"], data["address"], data["interestingLanguage"], data["knownLanguage"], data["level"]))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Profile saved successfully!"})
    
    except Exception as e:
        print(f"⚠️ Error saving profile: {e}")
        return jsonify({"success": False, "message": "Failed to save profile!"}), 500

# Fetch Profile Data
@app.route("/get-profile", methods=["GET"])
def get_profile():
    email = request.args.get("email")

    if not email:
        return jsonify({"success": False, "message": "Email is required!"}), 400

    db_path = create_user_database(email)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT name, phone, address, interesting_language, known_language, level FROM profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row:
        return jsonify({
            "success": True,
            "profile": {
                "name": row[0],
                "phone": row[1],
                "address": row[2],
                "interestingLanguage": row[3],
                "knownLanguage": row[4],
                "level": row[5]
            }
        })
    else:
        return jsonify({"success": False, "message": "Profile not found!"})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    success, message = register_user(data["email"], data["password"])
    return jsonify({"success": success, "message": message})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if verify_user(data["email"], data["password"]):
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials!"})

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

@app.route('/profile.html', methods=['GET'])
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)
