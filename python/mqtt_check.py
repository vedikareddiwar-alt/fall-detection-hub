import os
import time
import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "broker.hivemq.com")
TOPIC = "fallhub/teamone/test"


def on_message(client, userdata, msg):
    print("RECEIVED:", msg.payload.decode())


client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_start()
time.sleep(1)
client.publish(TOPIC, "hello from my laptop")
time.sleep(2)
client.loop_stop()
client.disconnect()
