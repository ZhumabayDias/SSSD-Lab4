# app.py — vulnerable demo (Flask)
from flask import Flask, request, jsonify
import yaml
import os

app = Flask(__name__)

# Load config (we will intentionally commit config.yaml with "secrets")
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# Hardcoded secret (intentional, for demonstration)
API_TOKEN = "SUPER_SECRET_TOKEN_123"

@app.route("/")
def index():
    return "Lab4 vulnerable server"

# Endpoint that demonstrates internal information exposure from errors
@app.route("/cause-error")
def cause_error():
    # artificial error that includes a secret from config in the message
    raise RuntimeError("DB connection failed: " + CONFIG["database"]["password"])

# Endpoint with insecure deserialization (demonstration)
@app.route("/deserialize", methods=["POST"])
def insecure_deserialize():
    # expects JSON: { "pyobj": "<python literal>" }
    data = request.get_json()
    pyobj = data.get("pyobj", "")
    # Unsafe: eval will execute arbitrary code — used here only for demonstration
    result = eval(pyobj)
    return jsonify({"result": str(result), "token": API_TOKEN})

if __name__ == "__main__":
    # debug=True to show stack traces on errors (for demonstration)
    app.run(host="0.0.0.0", port=5000, debug=True)
