# Test Results

Tester: ____________  Date: ____________  Wokwi link: ____________

Setup for all tests: Wokwi running, `python app.py` running, dashboard open at http://127.0.0.1:5000. Threshold is 3000 (ADC range 0 to 4095).

| ID | Test | Steps | Expected | Actual | Pass/Fail |
|---|---|---|---|---|---|
| T1 | Broker connection | Run `mqtt_check.py` | Prints `RECEIVED: hello from my laptop` | | |
| T2 | Device boots | Press Play in Wokwi | Serial shows Wi-Fi connected, then MQTT connected | | |
| T3 | Message format | Watch Serial Monitor | JSON line every ~200 ms with keys ms, device, vib, pir, ldr, lamp, state | | |
| T4 | Normal state | Leave pot low | LCD `NORMAL`, buzzer silent, dashboard green `Normal` | | |
| T5 | Python receives data | Open `/data` | `latest` shows current reading with `received` and `python_check` | | |
| T6 | Below threshold | Set pot to about 2500 for 5 s | No fall, no CSV row | | |
| T7 | Single spike | Push pot above 3000, release within 0.2 s | No fall | | |
| T8 | Two high readings | Hold above 3000 for about 0.15 s | No fall (needs 3 consecutive) | | |
| T9 | Valid fall | Hold pot at max for about 1 s | Buzzer on, LCD `FALL_DETECTED`, dashboard red | | |
| T10 | Fall logged | After T9 | New row in `events.csv` and in dashboard table | | |
| T11 | Terminal message | After T9 | `FALL EVENT:` printed by `app.py` | | |
| T12 | Python agrees with device | After T9 | Event row `python_check` is `FALL`; dashboard shows Agrees | | |
| T13 | Fall holds then clears | Release pot after T9 and wait | Alert clears about 5 s after the fall start, state returns to `NORMAL` | | |
| T14 | No duplicate rows | Hold pot high for 10 s | One row per fall, not one per message | | |
| T15 | Two falls in sequence | Repeat T9 after T13 | Two separate rows | | |
| T16 | PIR turns lamp on | Trigger PIR in Wokwi | `pir` is 1, lamp LED on, dashboard Lamp ON | | |
| T17 | Dark turns lamp on | Lower LDR light (ldr below 1500) | `lamp` is 1, LED on | | |
| T18 | Bright and still | PIR idle, LDR bright | Lamp OFF | | |
| T19 | Dashboard live chart | Move pot slowly | Chart line follows the pot | | |
| T20 | Offline detection | Stop Wokwi, wait 4 s | Dashboard shows `Device offline` | | |
| T21 | Recovery | Press Play again | Dashboard returns to live state | | |
| T22 | Server down | Stop `app.py` | Dashboard shows `Server unreachable` | | |
| T23 | Restart keeps log | Restart `app.py`, trigger fall | CSV appends, header not repeated | | |
| T24 | Bad message | Publish `not json` to topic | `Bad message:` printed, app keeps running | | |
| T25 | Hotspot fallback | Run on phone hotspot | Everything works the same | | |

## Issues found

| ID | Description | Owner | Status |
|---|---|---|---|
| | | | |

## Summary

Passed: ___ / 25   Failed: ___   Retested: ___
