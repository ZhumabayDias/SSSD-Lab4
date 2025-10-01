from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Try to load config if exists (but do not commit config.yaml to repo)
CONFIG = {}
try:
    import yaml as _yaml
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as f:
            CONFIG = _yaml.safe_load(f) or {}
except Exception:
    CONFIG = {}

# Read sensitive values from environment variables
API_TOKEN = os.environ.get("API_TOKEN")  # should be set in environment for deploy/test

# Configure logging to file (detailed errors go to log file)
logging.basicConfig(filename="app.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

@app.route("/")
def index():
    return "Lab4 server (secured demo)"

@app.route("/cause-error")
def cause_error():
    # Do not include secrets in exceptions returned to client
    logging.info("cause-error endpoint invoked")
    raise RuntimeError("Internal server error")

@app.errorhandler(Exception)
def handle_exception(e):
    # Log full details server-side, return generic message to client
    logging.exception("Unhandled exception: %s", e)
    return jsonify({"error": "Internal server error"}), 500

@app.route("/deserialize", methods=["POST"])
def insecure_deserialize():
    """
    Secure alternative to eval-based flow.
    Accept a small whitelist of operations, e.g.:
      {"operation": "add", "a": 2, "b": 3}
    """
    data = request.get_json(silent=True) or {}
    op = data.get("operation")
    if op == "add":
        try:
            a = int(data.get("a", 0))
            b = int(data.get("b", 0))
            return jsonify({"result": a + b})
        except Exception:
            logging.exception("Invalid input for add operation")
            return jsonify({"error": "Invalid input"}), 400
    return jsonify({"error": "Unsupported operation"}), 400

if __name__ == "__main__":
    # debug must be False in committed code
    app.run(host="0.0.0.0", port=5000, debug=False)
