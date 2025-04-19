# V2X / IoT Mini‑Demo 🚗📡

A **self‑contained showcase** of the end‑to‑end data path I built for a vehicle‑to‑everything (V2X) prototype:

| Layer | File(s) | Tech | What it demonstrates |
|-------|---------|------|----------------------|
| **Edge / Driver HMI** | `24_1_2024.py`, `25_1_2024server.py` | Python + `tkin­ter` on Raspberry Pi | Multi‑threaded TCP parsing → safe GUI updates (Queue) → LED / buzzer feedback |
| **Backend / Dashboard** | `app.py`, `index.html` | Flask, WebSockets, Leaflet | Real‑time map & status panel (< 100 ms latency) |
| **Test feeder** | `mock_client.py` | Python sockets | Streams SAE‑J2735‑style JSON/GPS packets for local testing |
| **Walk‑through video** | `v2x_communication_team.mp4` | ‑ | 45 s demo of the full flow |

> **Note:** Embedded C++ sources for secure BSM encoding/decoding are under NDA, so this repo focuses on the public‑shareable Python components that illustrate the same design patterns.

---

## Quick Start (Local)

```bash
# 1 – Optional : create a virtual env
python -m venv venv
source venv/bin/activate   # Windows → venv\Scripts\activate

# 2 – Install minimal deps
pip install flask gevent eventlet

# 3 – Run the dashboard
python app.py
# -> http://127.0.0.1:8100

# 4 – In another terminal, stream mock data
python mock_client.py
```

---

## 🎥 Demo Videos

<details>
<summary><strong>▶ Real-time GPS Mapping Demo</strong></summary>

<video src="map.mp4" controls width="640"></video>  
</details>

<details>
<summary><strong>▶ Traffic Notification System</strong></summary>

<video src="traffic noti.mp4" controls width="640"></video>  
</details>


---

## Why this matters

* **Concurrency** – Uses Python threads & `queue.Queue` to avoid GUI freezes.
* **Low‑latency streaming** – Flask + WebSockets pushes data straight to the browser; no polling.
* **Edge ↔ Cloud separation** – Same pattern scales from Raspberry Pi to an industrial PLC + cloud dashboard.
* **Clean code** – < 500 LOC combined, heavily commented.

---

## Running on a Raspberry Pi

1. `sudo apt install python3-tk python3-pil python3-pil.imagetk`
2. Copy the repo to the Pi and run `25_1_2024server.py`.
3. Wire the LED / push‑button as shown in the schematic inside the script comments.
4. The Pi HMI reacts to messages from the dashboard (LED on/off & audio alert).

---

## License & Credits

MIT License for all Python/HTML in this repo.  
C++ snippets referenced in the README belong to **Unex Technology** and are not redistributed.

---  

**Maintainer – Ruilong Yin**  
*B.Eng. EEE, NTU • Python/C++ • Embedded Systems & Control Engineering*  
