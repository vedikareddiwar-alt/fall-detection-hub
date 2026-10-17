# Slides Notes

Each person adds their own section. Do not edit other sections.

## Person A: Wokwi and device
- (add: circuit, parts, pin table, fall rule on device, screenshot of Serial Monitor)

## Person B: Python and MQTT
- (add: subscriber flow, second rule check, CSV logging, screenshot of terminal)

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
