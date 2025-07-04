import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()  # Load values from .env

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "wildlife/insightpipe")  # Default topic if not set in .env

def publish(path, description, model):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT)
    payload = {
        "path": path,
        "description": description,
        "model": model
    }
    client.publish(MQTT_TOPIC, str(payload))
    client.disconnect()

