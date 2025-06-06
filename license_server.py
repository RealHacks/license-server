from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

# Simple in-memory "database" for keys (for demo)
licenses = {}

def generate_key(email):
    raw = f"{email}-{datetime.utcnow()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    key = generate_key(email)
    expires_at = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
    licenses[key] = {"email": email, "expires_at": expires_at}
    return jsonify({"key": key, "email": email, "expires_at": expires_at})

@app.route('/verify', methods=['GET'])
def verify():
    key = request.args.get('key')
    email = request.args.get('email')
    if not key or not email:
        return jsonify({"valid": False, "error": "Missing key or email"}), 400
    license = licenses.get(key)
    if license and license["email"] == email:
        expiry_date = datetime.strptime(license["expires_at"], "%Y-%m-%d")
        if datetime.utcnow() <= expiry_date:
            return jsonify({"valid": True, "expires_at": license["expires_at"]})
    return jsonify({"valid": False})

@app.route('/')
def home():
    return "License verification server is running."

if __name__ == "__main__":
    app.run()
