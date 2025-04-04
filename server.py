from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
app.secret_key = "super_secret_key"
CORS(app)

# Database initialization
def init_db():
    if not os.path.exists("databases"):
        os.makedirs("databases")

    conn = sqlite3.connect("skillhub_users.db")
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

init_db()

def create_user_db(email):
    safe_email = email.replace('@', '_').replace('.', '_')
    db_path = f"databases/user_{safe_email}.db"

    if not os.path.exists("databases"):
        os.makedirs("databases")

    conn = sqlite3.connect(db_path)
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
    return db_path

# Routes
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")
@app.route("/register", methods=["POST"])
def register():
    conn = None
    try:
        data = request.get_json()
        app.logger.info(f"Register data received: {data}")

        if not data or not data.get("email") or not data.get("password") or not data.get("name"):
            return jsonify({"success": False, "message": "Name, email and password are required!"}), 400

        conn = sqlite3.connect("skillhub_users.db")
        cursor = conn.cursor()

        # Add 'name' column if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")

        cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                       (data["email"], data["password"], data["name"]))
        conn.commit()

        create_user_db(data["email"])

        return jsonify({"success": True, "message": "Registration successful!"})
    
    except sqlite3.IntegrityError as ie:
        app.logger.warning(f"Email already exists: {str(ie)}")
        return jsonify({"success": False, "message": "Email already exists!"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "message": "Registration failed. Please try again."}), 500
    
    finally:
        if conn:
            conn.close()

@app.route("/login", methods=["POST"])
def login():
    conn = None
    try:
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"success": False, "message": "Email and password are required!"}), 400

        conn = sqlite3.connect("skillhub_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (data["email"],))
        user = cursor.fetchone()

        if user and user[0] == data["password"]:
            session['email'] = data["email"]
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "email": data["email"]
            })
        else:
            return jsonify({"success": False, "message": "Invalid credentials!"}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route("/dashboard.html")
def dashboard():
    if 'email' in session and 'name' in session:
        return render_template("dashboard.html", email=session['email'], name=session['name'])
    else:
        return redirect(url_for('index1'))
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

# Debug endpoint
@app.route("/debug/user/<email>")
def debug_user(email):
    conn = None
    try:
        conn = sqlite3.connect("skillhub_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return jsonify({
            "exists": bool(user),
            "email_in_db": user[0] if user else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    if not os.path.exists("databases"):
        os.makedirs("databases")
    app.run(debug=True)