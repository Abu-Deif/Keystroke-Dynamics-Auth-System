import os
import sqlite3
import json
import joblib
import numpy as np
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from model import train_user_model

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

# Database setup

def get_db():
    conn = sqlite3.connect("project.db") 
    conn.row_factory = sqlite3.Row 
    return conn 

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE,
            password     TEXT,
            attempts     INTEGER DEFAULT 0,
            locked_until TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS keystrokes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            key          TEXT,
            press_time   REAL,
            release_time REAL,
            dwell        REAL,
            flight       REAL,
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS auth_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            result TEXT,
            svm_score REAL,
            iso_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT DEFAULT 'Unknown',
            user_agent TEXT DEFAULT 'Unknown'
        )
    """) 
    
    conn.commit()
    conn.close()

init_db()

# Auth & Pages Routes

@app.route("/register", methods=["GET", "POST"]) 
def register():
    message = ""
    if request.method == "POST": 
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            return render_template("register.html", message="Username and password are required.")
        
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, generate_password_hash(password)))
            conn.commit()
            
            session["user_id"] = c.lastrowid 
            conn.close() 
            
            return redirect("/training")
            
        except sqlite3.IntegrityError:
            conn.close()
            message = "Username already exists!"
            
    return render_template("register.html", message=message)

@app.route("/training")
def training_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("training.html")

#############################
@app.route("/save_keystrokes", methods=["POST"])
def save_keystrokes():
    if "user_id" not in session: 
        return jsonify({"status": "error", "message": "Not logged in"})
    
    # (strokes) بنستقبل مصفوفة 
    strokes = request.get_json() or []
    user_id = session["user_id"]
    
    conn = get_db()
    
    for k in strokes:
        conn.execute("""
            INSERT INTO keystrokes (user_id, key, press_time, release_time, dwell, flight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, k.get("key"), k.get("press"), k.get("release"),
              k.get("dwell"), k.get("flight")))
              
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok"})


@app.route("/train_model", methods=["GET", "POST"])
def trigger_training():
    # تأمين: لازم يكون مسجل دخول
    if "user_id" not in session:
        return redirect("/")
        
    user_id = session["user_id"]
    
    success = train_user_model(user_id)
    
    if success:
        session.pop("user_id", None)
        return """
            <div style='text-align:center; margin-top:50px; font-family:sans-serif;'>
                <h2 style='color:green;'>Model Trained Successfully!</h2>
                <p>The AI has learned your unique Keyboard pattern.</p>
                <a href='/' style='padding:10px 20px; background:blue; color:white; text-decoration:none; border-radius:5px;'>Go to Login Page</a>
            </div>
        """
    else:
        return "<h3>Error: Not enough data.</h3><a href='/training'>Go back to training</a>"
    

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    keystrokes_data_str = request.form.get("keystrokes_data", "[]")
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if not user or not check_password_hash(user[1], password):
        conn.close()
        return render_template("login.html", message="Invalid username or password")
        
    user_id = user[0]
    
    c.execute("""
        SELECT COUNT(*) FROM auth_log 
        WHERE user_id = ? AND result LIKE 'Blocked%' 
        AND timestamp >= datetime('now', '-1 minutes')
    """, (user_id,))
    
    failed_attempts = c.fetchone()[0]
    
    if failed_attempts >= 3:
        conn.close()
        lockout_msg = "Account Temporarily Locked: Too many anomalous typing attempts. Please try again in 1 minute."
        return render_template("login.html", message=lockout_msg)

    try:
        strokes = json.loads(keystrokes_data_str)
    except:
        strokes = []
        
    if not strokes:
        conn.close()
        return render_template("login.html", message="Keyboard data missing. Please type manually.")
        
    current_attempt = []
    for s in strokes:
        f_val = s.get("flight")
        if f_val is None:
            f_val = 0
        current_attempt.append([s.get("dwell"), f_val])
        
    X_test = np.array(current_attempt)
    
    scaler_path = f"models/scaler_{user_id}.pkl"
    svm_path = f"models/svm_{user_id}.pkl"
    iso_path = f"models/iso_{user_id}.pkl"
    
    if not (os.path.exists(scaler_path) and os.path.exists(svm_path) and os.path.exists(iso_path)):
        conn.close()
        session["user_id"] = user_id
        return redirect("/training")
        
    scaler = joblib.load(scaler_path)
    svm_model = joblib.load(svm_path)
    iso_model = joblib.load(iso_path)
    
    X_test_scaled = scaler.transform(X_test)
    
    svm_preds = svm_model.predict(X_test_scaled)
    iso_preds = iso_model.predict(X_test_scaled)
    
    svm_score = np.mean(svm_preds == 1) * 100
    iso_score = np.mean(iso_preds == 1) * 100
    
    if svm_score >= 60 and iso_score >= 60:
        result_status = "Success"
        message = "Login Successful: Keyboard Pattern Matched!"
    else:
        result_status = "Blocked: Anomaly Detected"
        message = f"Access Denied: Unusual authentication activity detected."
        
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
        
    c.execute("""
        INSERT INTO auth_log (user_id, result, svm_score, iso_score, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, result_status, svm_score, iso_score, ip_address, user_agent))
    
    conn.commit()
    conn.close()
    
    if result_status == "Success":
        return f"<h2 style='color:green; text-align:center; margin-top:50px;'>{message}</h2>"
    else:
        return render_template("login.html", message=message)
    
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT auth_log.id, users.username, auth_log.result, auth_log.svm_score, auth_log.iso_score, auth_log.timestamp, auth_log.ip_address, auth_log.user_agent
        FROM auth_log 
        JOIN users ON auth_log.user_id = users.id
        ORDER BY auth_log.timestamp DESC
    """)
    logs = c.fetchall()
    conn.close()
    return render_template("dashboard.html", logs=logs)


# Run Server 
if __name__ == "__main__": 
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    app.run(debug=debug_mode) 