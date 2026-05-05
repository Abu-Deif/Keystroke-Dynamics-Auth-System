# Keystroke Dynamics Authentication System & SOC Dashboard

## Project Overview
This is my graduation project for my Cybersecurity degree. It is an advanced authentication system that uses **Behavioral Biometrics** (Keystroke Dynamics) combined with **Machine Learning** to detect anomalies and unauthorized access attempts in real-time.

Instead of relying solely on passwords, the system analyzes *how* a user types, specifically measuring:
*   **Dwell Time:** The time a key is pressed down.
*   **Flight Time:** The time between releasing one key and pressing the next.

## Key Features
1.  **AI-Driven Anomaly Detection:** Uses Machine Learning models (like Support Vector Machine - SVM and Isolation Forest) to create a unique typing profile for each user.
2.  **Real-Time SOC Dashboard:** A custom-built security dashboard designed for SOC Analysts to monitor login attempts.
3.  **Live Filtering:** Instantly search and filter through authentication logs by IP, Username, or Status.
4.  **Behavioral Blocking:** Automatically blocks access if the AI detects a typing pattern that deviates from the user's established baseline.

## Tech Stack 🛠️
*   **Backend:** Python, Flask
*   **Database:** SQLite (Ignored in this repository for security purposes)
*   **Machine Learning:** Scikit-Learn (SVM, Isolation Forest)
*   **Frontend:** HTML, CSS, JavaScript (Vanilla JS for real-time DOM manipulation)

## Security Practices Implemented
*   Local database files (`.db`) and python cache (`__pycache__`) are excluded via `.gitignore` to prevent data leakage.
*   Single Page Application (SPA) logic applied to the dashboard search to prevent unnecessary server requests and page reloads.

## 👤 Author
**Mohamed Abu Deif Ahmed**
*Cybersecurity Student | SOC Analyst | Bug Bounty Hunter*
