from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
licenses = {}

@app.route("/generate", methods=["POST"])
def generate_key():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    key = str(uuid.uuid4()).replace("-", "")[:16]
    expiry = datetime.now() + timedelta(days=30)
    licenses[key] = {"email": email, "expires_at": expiry.strftime("%Y-%m-%d")}
    return jsonify({"key": key, "expires_at": licenses[key]["expires_at"]})

@app.route("/verify", methods=["GET"])
def verify_key():
    key = request.args.get("key")
    email = request.args.get("email")

    data = licenses.get(key)
    if not data or data["email"] != email:
        return jsonify({"valid": False}), 401

    expiry = datetime.strptime(data["expires_at"], "%Y-%m-%d")
    if datetime.now() > expiry:
        return jsonify({"valid": False, "message": "Expired"}), 403

    return jsonify({"valid": True, "expires_at": data["expires_at"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
