import os
import platform
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

HOSTNAME = os.uname().nodename if hasattr(os, "uname") else platform.node()
START_TIME = datetime.now()


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Web Server using Docker",
            "status": "running",
            "host": HOSTNAME,
            "version": "1.0.0",
        }
    )


@app.route("/health")
def health():
    uptime = (datetime.now() - START_TIME).total_seconds()
    return jsonify(
        {
            "status": "healthy",
            "uptime_seconds": uptime,
            "host": HOSTNAME,
        }
    )


@app.route("/info")
def info():
    return jsonify(
        {
            "hostname": HOSTNAME,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "container": os.environ.get("CONTAINER", "unknown"),
        }
    )


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"received": data, "host": HOSTNAME})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
