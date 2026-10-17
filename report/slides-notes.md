# Slides Notes

Each person adds their own section. Do not edit other sections.

## Person A: Wokwi and device
- (add: circuit, parts, pin table, fall rule on device, screenshot of Serial Monitor)

## Person B: Python and MQTT
### Subscriber flow
- `app.py` connects to `broker.hivemq.com:1883` with paho-mqtt 1.x and subscribes to `fallhub/teamone/event`.
- The MQTT client runs in a background thread (`loop_start`), so Flask can serve the dashboard at the same time.
- Each message is parsed as JSON. Malformed messages are printed as `Bad message` and skipped, so the app never crashes on bad input.
- The latest reading is stored in memory behind a lock and served as JSON at `/data`, which the dashboard polls.

### Second rule check (Python)
- Python applies the same fall rule as the device independently: 3 consecutive vibration readings >= 3000 within 1 second.
- Result is shown as `python_check` (FALL / NORMAL), so we can show the device and the server agree.
- Why two checks: the device reacts instantly (buzzer, LCD) without the network; the server verifies the data it actually received.

### CSV logging
- A fall is logged once, on the transition from NORMAL to FALL_DETECTED, not on every message during the 5-second alert.
- Each row in `events.csv`: time received, device state, Python check, vibration, motion, light.
- The last 20 falls are also kept in memory for the dashboard table.

### Testing done
- `mqtt_check.py` publishes and receives a test message to confirm the broker is reachable (use a phone hotspot if college Wi-Fi blocks port 1883).
- Tested with a simulated device sending the exact message format every 200 ms: one fall produced exactly one `FALL EVENT` row, device and Python both reported FALL, and a malformed message was skipped.

### Screenshot to add
- Terminal showing `Connected to broker`, `Subscribed to fallhub/teamone/event`, and a `FALL EVENT:` line.

## Person C: Dashboard, tests and repo

### Dashboard
- Single page served by Flask at `/`, reads `/data` every 500 ms.
- Large state banner: green `Normal`, flashing red `FALL DETECTED`, grey when the device is silent.
- Live vibration chart with the 3000 threshold line.
- Sensor panel: motion, light, lamp, and whether Python agrees with the device.
- Table of the last 20 falls, also saved in `events.csv`.
- Handles three failure cases: no data yet, device offline (no reading for 3 s), server unreachable.

### Testing
- 25 test cases in `tests/results.md` covering connection, fall rule edge cases, sensors, logging, and failures.
- Edge cases for the rule: single spike, two readings, exactly three within 1 second.
- Result: ___ of 25 passed.

### Repository
- Public GitHub repo with file ownership per person to avoid merge conflicts.
- README with run steps and troubleshooting.

### Demo script (2 minutes)
1. Show the dashboard in Normal state.
2. Trigger PIR and show the lamp turn on.
3. Hold the potentiometer high for 1 second: buzzer, LCD and dashboard all react.
4. Show the new row in the table and in `events.csv`.
5. Stop Wokwi to show the offline state.

### Limits and next steps
- Simulated sensors only. A real build would use an accelerometer instead of a potentiometer.
- Public broker means anyone with the topic name can read or publish. A real build would use a private broker with authentication.
- AI add-on was dropped for this submission.
