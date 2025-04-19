
"""
mock_client.py
--------------
Tiny client that connects to app.py and streams random latitude/longitude
pairs over a TCP socket once per second.

Usage:
    python mock_client.py
"""

import json
import random
import socket
import time

HOST, PORT = "127.0.0.1", 50007   # must match HOST/PORT in app.py


def jitter(base: float, spread: float = 0.0003) -> float:
    """Return base ± random jitter (uniform)."""
    return base + random.uniform(-spread, spread)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"[Client] Connected to {HOST}:{PORT}")

        while True:
            payload = {
                "lat": jitter(1.311251),      # NTU coordinates ± jitter
                "long": jitter(103.779060)
            }
            s.sendall((json.dumps(payload) + "\n").encode())
            print(f"[Client] Sent → {payload}")
            time.sleep(1)
