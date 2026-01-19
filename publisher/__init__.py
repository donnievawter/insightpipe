import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import json  # Recommended over str() for payload formatting
import logging

logger = logging.getLogger("insightpipe")

load_dotenv(override=True)  # Load values from .env, overriding system environment variables

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def test_mqtt_connection(timeout=5):
    """
    Test MQTT connection and credentials.
    Returns (success: bool, error_message: str)
    """
    if not MQTT_HOST:
        return False, "MQTT_HOST environment variable not set"
    if not MQTT_USER:
        return False, "MQTT_USER environment variable not set"
    if not MQTT_PASSWORD:
        return False, "MQTT_PASSWORD environment variable not set"
    
    try:
        logger.info(f"Testing MQTT connection to {MQTT_HOST}:{MQTT_PORT}...")
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        
        # Set up connection callbacks
        connection_result = {"success": False, "error": None}
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                connection_result["success"] = True
                logger.info("✅ MQTT connection test successful")
            else:
                error_messages = {
                    1: "Connection refused - incorrect protocol version",
                    2: "Connection refused - invalid client identifier",
                    3: "Connection refused - server unavailable",
                    4: "Connection refused - bad username or password",
                    5: "Connection refused - not authorized"
                }
                connection_result["error"] = error_messages.get(rc, f"Unknown error code {rc}")
                logger.error(f"❌ MQTT connection failed: {connection_result['error']}")
        
        client.on_connect = on_connect
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=timeout)
        client.loop_start()
        
        # Wait for connection result
        import time
        for _ in range(timeout * 10):
            if connection_result["success"] or connection_result["error"]:
                break
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        if connection_result["success"]:
            return True, None
        elif connection_result["error"]:
            return False, connection_result["error"]
        else:
            return False, f"Connection timeout after {timeout} seconds"
            
    except Exception as e:
        error_msg = f"MQTT connection test failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg

def publish(path, description, model, prompt, mqtt_topic="insightpipe"):
    """
    Publish metadata to MQTT broker with proper error handling.
    """
    try:
        folder, filename = os.path.split(path)

        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        
        logger.debug(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

        payload = {
            "folder": folder,
            "filename": filename,
            "description": description,
            "model": model,
            "prompt": prompt
        }

        result = client.publish(mqtt_topic, json.dumps(payload))
        
        # Wait for publish to complete
        result.wait_for_publish(timeout=5)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"📤 Published to MQTT topic '{mqtt_topic}': {filename}")
        else:
            logger.warning(f"⚠️ MQTT publish may have failed with code {result.rc} for {filename}")
        
        client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Failed to publish to MQTT: {str(e)}")
        logger.error(f"   MQTT Host: {MQTT_HOST}:{MQTT_PORT}")
        logger.error(f"   Topic: {mqtt_topic}")
        logger.error(f"   File: {path}")
        # Don't raise - allow processing to continue even if MQTT fails
