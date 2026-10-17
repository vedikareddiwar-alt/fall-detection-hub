import os
import threading
import time

import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "broker.hivemq.com")
TOPIC = "fallhub/teamone/test"
WAIT_SECONDS = 10

subscribed = threading.Event()
received = threading.Event()


def on_connect(client, userdata, flags, rc):
    print("Connected to", BROKER, "result code", rc, "(0 means OK)")
    client.subscribe(TOPIC)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to", TOPIC)
    subscribed.set()


def on_message(client, userdata, msg):
    print("RECEIVED:", msg.payload.decode())
    received.set()


client = mqtt.Client()
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

print("Connecting to", BROKER, "...")
client.connect(BROKER, 1883, 60)
client.loop_start()

if not subscribed.wait(WAIT_SECONDS):
    print("FAIL: could not subscribe. Try a phone hotspot.")
else:
    client.publish(TOPIC, "hello from my laptop")
    if received.wait(WAIT_SECONDS):
        print("PASS: broker round trip works.")
    else:
        print("FAIL: published but nothing came back in", WAIT_SECONDS, "seconds.")

client.loop_stop()
client.disconnect()
