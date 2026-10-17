# Fall-Detection Hub

A simulated fall-detection hub. An ESP32 running in Wokwi reads sensors and publishes events over MQTT. A Python app receives them, applies the fall rule a second time, logs falls to `events.csv`, and serves a live dashboard.

```
Wokwi (ESP32) --> MQTT broker (broker.hivemq.com) --> Python app --> dashboard + events.csv
```

## What it does

- Reads vibration (potentiometer), motion (PIR) and light (LDR) every 100 ms and publishes a JSON message every 200 ms.
- Fall rule: 3 consecutive high vibration readings within 1 second. The device and the Python app both apply it.
- On a fall: buzzer sounds, LCD shows `FALL_DETECTED`, alert holds for 5 seconds.
- Lamp turns on when motion is detected or the room is dark.
- Dashboard shows live state, a vibration chart, sensor values and a table of recent falls.

## Repository layout

| Path | Owner | Purpose |
|---|---|---|
| `wokwi/sketch.ino` | Person A | ESP32 firmware |
| `python/app.py`, `python/requirements.txt` | Person B | MQTT subscriber, rule check, logging, Flask server |
| `python/templates/index.html` | Person C | Live dashboard |
| `tests/results.md` | Person C | Test cases and results |
| `report/slides-notes.md` | Everyone | Notes for the presentation |

## MQTT

- Broker: `broker.hivemq.com`, port 1883
- Topic: `fallhub/teamone/event`
- Message, sent every 200 ms:

```json
{"ms":1234,"device":"hub1","vib":512,"pir":0,"ldr":430,"lamp":0,"state":"NORMAL"}
```

The topic must be identical in `sketch.ino` and `app.py`.

## Run it

1. Open the shared Wokwi project and press Play. Wait for `Connecting to MQTT... connected`.
2. In a terminal:

```bash
cd python
python -m venv venv
venv\Scripts\activate          # Mac: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

3. Open http://127.0.0.1:5000 for the dashboard and http://127.0.0.1:5000/data for raw JSON.
4. In Wokwi, drag the potentiometer to its maximum and hold for about 1 second. The buzzer sounds, the dashboard turns red, and a row is added to `events.csv`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Wokwi stuck on MQTT retrying | Press Stop, then Play. Check the broker is reachable. |
| `mqtt_check.py` times out | College Wi-Fi may block port 1883. Use a phone hotspot. |
| Dashboard says "Device offline" | Wokwi is stopped or paused. Press Play. |
| Dashboard says "Server unreachable" | `app.py` is not running, or you are on the wrong port. |
| Port 5000 busy on Mac | Change `port=5000` to `5001` in `app.py` and open that port. |
| Import error for paho-mqtt | Run `pip install "paho-mqtt<2.0"`. The code uses the 1.x API. |
| Nothing arrives | Check the team name in the topic matches in both files. |

## Team

- Person A: Wokwi circuit and device code
- Person B: Python subscriber, rule check and logging
- Person C: Dashboard, tests and repository

Note: the course template names ESP8266. We use ESP32 as a simulator-only substitution.
