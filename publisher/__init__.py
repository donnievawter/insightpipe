import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import json  # Recommended over str() for payload formatting


load_dotenv()  # Load values from .env

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "insightpipe")  # Default topic if not set in .env

def publish(path, description, model, prompt):
    folder, filename = os.path.split(path)

    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT)

    payload = {
        "folder": folder,
        "filename": filename,
        "description": description,
        "model": model,
        "prompt": prompt
    }

    client.publish(MQTT_TOPIC, json.dumps(payload))
    client.disconnect()
