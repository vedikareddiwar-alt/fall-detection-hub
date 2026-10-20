
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* TOPIC = "fallhub/teamone/event";

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

const char* MQTT_HOST = "broker.hivemq.com";
const int MQTT_PORT = 1883;

const int PIN_VIB = 34;
const int PIN_PIR = 27;
const int PIN_LDR = 35;
const int PIN_BUZZER = 25;
const int PIN_LAMP = 26;

const int VIB_THRESHOLD = 3000;
const int DARK_THRESHOLD = 1500;

const unsigned long SAMPLE_MS = 100;
const unsigned long PUBLISH_MS = 200;
const unsigned long FALL_HOLD_MS = 5000;

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
LiquidCrystal_I2C lcd(0x27, 16, 2);

int consecutiveHigh = 0;
unsigned long firstHighTime = 0;
bool fallActive = false;
unsigned long fallStart = 0;
unsigned long lastSample = 0;
unsigned long lastPublish = 0;
int lastVib = 0;

String lastLcdLine1 = "";
String lastLcdLine2 = "";

void connectMqtt() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT...");

    String id = "fallhub-" + String(random(0xffff), HEX);

    if (mqtt.connect(id.c_str())) {
      Serial.println(" connected");
    } else {
      Serial.print(" failed, state=");
      Serial.println(mqtt.state());
      delay(1000);
    }
  }
}

void showLcd(const String& line1, const String& line2) {
  if (line1 == lastLcdLine1 &&
      line2 == lastLcdLine2) {
    return;
  }

  lastLcdLine1 = line1;
  lastLcdLine2 = line2;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_PIR, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LAMP, OUTPUT);

  Wire.begin(21, 22);

  lcd.init();
  lcd.backlight();

  showLcd("Fall Hub", "Starting...");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Wi-Fi connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
  }

  Serial.println(" connected");

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(256);

  connectMqtt();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    delay(500);
    return;
  }

  if (!mqtt.connected()) {
    connectMqtt();
  }

  mqtt.loop();

  unsigned long now = millis();

  if (now - lastSample >= SAMPLE_MS) {
    lastSample = now;
    lastVib = analogRead(PIN_VIB);

    if (lastVib >= VIB_THRESHOLD) {
      if (consecutiveHigh == 0) {
        firstHighTime = now;
      }

      consecutiveHigh++;

      if (consecutiveHigh >= 3 &&
          now - firstHighTime <= 1000 &&
          !fallActive) {
        fallActive = true;
        fallStart = now;
        consecutiveHigh = 0;
        Serial.println("FALL DETECTED!");
      }
    } else {
      consecutiveHigh = 0;
    }
  }

  if (fallActive &&
      now - fallStart >= FALL_HOLD_MS) {
    fallActive = false;
  }

  int pir = digitalRead(PIN_PIR);
  int ldr = analogRead(PIN_LDR);

  bool lampOn = (pir == HIGH) ||
                (ldr < DARK_THRESHOLD);

  if (fallActive) {
  tone(PIN_BUZZER, 2000);  // 2 kHz audible tone
} else {
  noTone(PIN_BUZZER);      // Stop the sound
}

  digitalWrite(PIN_LAMP,
               lampOn ? HIGH : LOW);

  String state = fallActive
                   ? "FALL_DETECTED"
                   : "NORMAL";

  showLcd(state,
          lampOn ? "Lamp: ON" : "Lamp: OFF");

  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;

    char msg[220];

    snprintf(msg, sizeof(msg),
      "{\"ms\":%lu,\"device\":\"hub1\","
      "\"vib\":%d,\"pir\":%d,\"ldr\":%d,"
      "\"lamp\":%d,\"state\":\"%s\"}",
      now,
      lastVib,
      pir,
      ldr,
      lampOn ? 1 : 0,
      state.c_str()
    );

    bool published = mqtt.publish(TOPIC, msg);

    Serial.println(msg);

    if (!published) {
      Serial.println("MQTT publish failed");
    }
  }
}
