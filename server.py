from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
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
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        conn = sqlite3.connect("skillhub_users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", 
                      (data["email"], data["password"]))
        conn.commit()
        create_user_db(data["email"])
        return jsonify({"success": True, "message": "Registration successful!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists!"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        conn = sqlite3.connect("skillhub_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (data["email"],))
        user = cursor.fetchone()
        
        if user and user[0] == data["password"]:
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "email": data["email"]
            })
        else:
            return jsonify({"success": False, "message": "Invalid credentials!"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/save-profile", methods=["POST"])
def save_profile():
    try:
        data = request.get_json()
        if not data.get("email"):
            return jsonify({"success": False, "message": "Email is required!"}), 400
            
        db_path = create_user_db(data["email"])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO profile (name, phone, address, interesting_language, known_language, level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["phone"],
            data["address"],
            data["interestingLanguage"],
            data["knownLanguage"],
            data["level"]
        ))
        
        conn.commit()
        return jsonify({"success": True, "message": "Profile saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/get-profile", methods=["GET"])
def get_profile():
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"success": False, "message": "Email is required!"}), 400
            
        db_path = create_user_db(email)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profile ORDER BY id DESC LIMIT 1")
        profile = cursor.fetchone()
        
        if profile:
            return jsonify({
                "success": True,
                "profile": {
                    "name": profile[1],
                    "phone": profile[2],
                    "address": profile[3],
                    "interestingLanguage": profile[4],
                    "knownLanguage": profile[5],
                    "level": profile[6]
                }
            })
        else:
            return jsonify({"success": False, "message": "Profile not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# Debug endpoint
@app.route("/debug/user/<email>")
def debug_user(email):
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
        conn.close()
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