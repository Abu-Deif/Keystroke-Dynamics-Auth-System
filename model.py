import sqlite3
import numpy as np
import joblib       # الفريزر أو مكتبة الحفظ
import os
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def get_user_data(user_id):
    conn = sqlite3.connect("project.db")
    c = conn.cursor()
    
    c.execute("""
        SELECT dwell, flight 
        FROM keystrokes 
        WHERE user_id = ? 
        ORDER BY id ASC
    """, (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return []
        
    return [list(row) for row in rows]

def train_user_model(user_id):
    data = get_user_data(user_id)
    
    if len(data) < 10:
        return False
        
    X = []
    for row in data:
        X.append([row[0], row[1]])

    X = np.array(X, dtype=float)
    X = np.nan_to_num(X, nan=0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    svm_model = OneClassSVM(kernel='rbf', gamma='scale', nu=0.1)
    svm_model.fit(X_scaled)
    
    iso_model = IsolationForest(contamination=0.1, random_state=42)
    iso_model.fit(X_scaled)
    
    if not os.path.exists("models"):
        os.makedirs("models")
        
    joblib.dump(scaler, f"models/scaler_{user_id}.pkl")
    joblib.dump(svm_model, f"models/svm_{user_id}.pkl")
    joblib.dump(iso_model, f"models/iso_{user_id}.pkl")
    
    return True
