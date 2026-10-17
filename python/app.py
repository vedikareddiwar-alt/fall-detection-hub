import csv
import json
import os
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template

BROKER = os.environ.get("MQTT_BROKER", "broker.hivemq.com")
PORT = 1883
TOPIC = "fallhub/teamone/event"
VIB_THRESHOLD = 3000
CSV_FILE = "events.csv"
# The device samples every 100 ms but publishes every 200 ms, so it reaches
# FALL_DETECTED before Python has seen 3 high readings. A fall row waits up
# to this long for the Python check before it is written.
CONFIRM_WINDOW = 1.5

lock = threading.Lock()
latest = {}
events = []
last_device_state = "NORMAL"
py_consecutive = 0
py_first_time = 0.0
py_last_fall = None
last_device_time = None
pending = None

app = Flask(__name__)


def python_check(vib, now):
    global py_consecutive, py_first_time
    if vib >= VIB_THRESHOLD:
        if py_consecutive == 0:
            py_first_time = now
        py_consecutive += 1
        if py_consecutive >= 3 and (now - py_first_time) <= 1.0:
            py_consecutive = 0
            return True
    else:
        py_consecutive = 0
    return False


def log_event(row):
    new_file = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker, result code", rc)
    client.subscribe(TOPIC)
    print("Subscribed to", TOPIC)


def reset_python_state():
    global py_consecutive, py_first_time, py_last_fall, pending
    py_consecutive = 0
    py_first_time = 0.0
    py_last_fall = None
    pending = None


def finalize_event(row, py_confirmed):
    row["python_check"] = "FALL" if py_confirmed else "no"
    events.insert(0, row)
    del events[20:]
    log_event(row)
    print("FALL EVENT:", row)


def on_message(client, userdata, msg):
    global last_device_state, py_last_fall, last_device_time, pending
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        print("Bad message:", msg.payload)
        return

    # Time the rule on the device's own clock (the "ms" field), so it works
    # even when the Wokwi simulator runs slower than real time.
    try:
        now = float(data["ms"]) / 1000.0
    except (KeyError, TypeError, ValueError):
        now = time.time()
    if last_device_time is not None and now < last_device_time:
        reset_python_state()  # simulator was restarted, its clock went back to 0
    last_device_time = now

    vib = int(data.get("vib", 0))
    device_state = data.get("state", "NORMAL")
    py_fall = python_check(vib, now)
    if py_fall:
        py_last_fall = now

    with lock:
        latest.clear()
        latest.update(data)
        latest["received"] = datetime.now().strftime("%H:%M:%S")
        latest["python_check"] = "FALL" if py_fall else "NORMAL"

        if device_state == "FALL_DETECTED" and last_device_state != "FALL_DETECTED":
            pending = {
                "since": now,
                "row": {
                    "received_at": datetime.now().isoformat(timespec="seconds"),
                    "device_state": device_state,
                    "python_check": "",
                    "vib": vib,
                    "pir": data.get("pir"),
                    "ldr": data.get("ldr"),
                },
            }
        last_device_state = device_state

        if pending is not None:
            confirmed = py_last_fall is not None and abs(now - py_last_fall) <= CONFIRM_WINDOW
            if confirmed or now - pending["since"] >= CONFIRM_WINDOW:
                finalize_event(pending["row"], confirmed)
                pending = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():
    with lock:
        return jsonify({"latest": dict(latest), "events": list(events)})


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    print("Dashboard at http://127.0.0.1:5000")
    app.run(port=5000, debug=False)
