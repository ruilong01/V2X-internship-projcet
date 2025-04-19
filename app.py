
from flask import Flask, render_template, jsonify
import threading
import socket
import json

app = Flask(__name__)

# Shared GPS data
gps_data = {"lat": 1.3521, "long": 103.8198, "speed": 0, "heading": 0}

def socket_listener():
    host = '0.0.0.0'
    port = 50007

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Socket listener active on port {port}...")

        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    data = conn.recv(1024)
                    if data:
                        decoded = json.loads(data.decode())
                        gps_data.update(decoded)
                        print(f"Updated GPS: {gps_data}")
                except Exception as e:
                    print(f"Error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update_marker", methods=["GET"])
def update_marker():
    return jsonify(gps_data)

if __name__ == "__main__":
    listener_thread = threading.Thread(target=socket_listener, daemon=True)
    listener_thread.start()
    app.run(host="0.0.0.0", port=8100, debug=True)
