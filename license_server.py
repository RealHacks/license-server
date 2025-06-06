from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import hashlib
import json

app = Flask(__name__)
LICENSES = {}

def generate_key(email, days_valid=30):
    expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d')
    raw_string = f"{email}-{expiry_date}"
    key = hashlib.sha256(raw_string.encode()).hexdigest()
    LICENSES[key] = {"email": email, "expiry": expiry_date}
    return key, expiry_date

@app.route("/generate", methods=["GET"])
def generate():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400
    key, expiry = generate_key(email)
    return jsonify({"key": key, "expiry": expiry})

@app.route("/verify", methods=["GET"])
def verify():
    key = request.args.get("key")
    email = request.args.get("email")
    license_info = LICENSES.get(key)
    if not license_info or license_info["email"] != email:
        return jsonify({"valid": False}), 400
    if datetime.strptime(license_info["expiry"], '%Y-%m-%d') < datetime.now():
        return jsonify({"valid": False, "reason": "Expired"}), 400
    return jsonify({"valid": True, "expiry": license_info["expiry"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)