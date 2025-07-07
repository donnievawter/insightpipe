#!/usr/bin/env python3

import os
import json
import sqlite3
from paho.mqtt.client import Client
from dotenv import load_dotenv
from datetime import datetime
TEST_RUN_TS = datetime.now().isoformat()

# 🔑 Load environment variables from .env
load_dotenv()

MQTT_USER     = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_HOST     = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT     = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC    = os.getenv("MQTT_TOPIC", "insightpipe")
DB_PATH       = os.getenv("RESULTS_DB", "results.db")

# 🗃️ Initialize SQLite connection
conn = sqlite3.connect(DB_PATH)
db = conn.cursor()

# 🧱 Ensure results table exists
db.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    folder TEXT,
    filename TEXT,
    description TEXT,
    model TEXT,
    prompt TEXT,
    test_run_timestamp DATETIME
)
""")
conn.commit()

# 📥 Message handler for incoming MQTT payloads
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)

        folder      = data.get("folder", "")
        filename    = data.get("filename", "")
        description = data.get("description", "")
        model       = data.get("model", "")
        prompt      = data.get("prompt", "")

        db.execute("""
            INSERT INTO results (test_run_timestamp, folder, filename, description, model, prompt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (TEST_RUN_TS,folder, filename, description, model, prompt))
        conn.commit()

        print(f"📸 Logged: {filename} from {model}")
    except Exception as e:
        print(f"⚠️ Error processing message: {e}")

# 🚦 Set up MQTT client
client = Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message

print(f"🔌 Connecting to MQTT @ {MQTT_HOST}:{MQTT_PORT}, subscribing to '{MQTT_TOPIC}'")

try:
    client.connect(MQTT_HOST, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
except Exception as e:
    print(f"❌ MQTT Connection Error: {e}")
    exit(1)
print("🧭 MQTT subscriber initialized, entering event loop...")
client.loop_forever()
print("⚠️ Loop exited unexpectedly")