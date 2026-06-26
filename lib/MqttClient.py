import json
import sys
import os
import paho.mqtt.client as mqtt
import time
import ssl
from collections import defaultdict

# Ensure lib/ is on sys.path so config.py is importable regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ENDPOINT, CERT_FILE, KEY_FILE, CA_FILE

class MqttClient:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def connect_to_broker(self, port=8883, client_id="PC-demo"):
        self._received = defaultdict(list)
        self._connected = False

        # Initialize MQTT client with a unique client ID
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv311
        )

        # Configure TLS/SSL using paths from config.py
        self._client.tls_set(
            ca_certs=CA_FILE,
            certfile=CERT_FILE,
            keyfile=KEY_FILE,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )

        # Set callbacks
        self._client.on_message = self._on_message
        self._client.on_connect = self._on_connect

        # Connect to AWS IoT broker
        self._client.connect(ENDPOINT, int(port), keepalive=60)

        # Start the network loop
        self._client.loop_start()

        # Wait for connection
        end_time = time.time() + 10
        while not self._connected and time.time() < end_time:
            time.sleep(0.1)
        if not self._connected:
            raise ConnectionError(f"Could not connect to broker at {ENDPOINT}:{port}")

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._connected = True
            print("Connected to AWS IoT!")
        else:
            print(f"Connection failed with reason code: {reason_code}")
            self._connected = False

    def _on_message(self, client, userdata, message):
        self._received[message.topic].append(message.payload.decode())

    def subscribe(self, topic):
        self._client.subscribe(topic)
        time.sleep(0.5)

    def publish_message(self, topic, message, qos=1):
        self._client.publish(topic, message, qos=int(qos))

    def publish_json_message(self, topic, payload_dict, qos=1):
        self._client.publish(topic, json.dumps(payload_dict), qos=int(qos))

    def wait_for_json_message(self, topic, required_key, timeout=30):
        end_time = time.time() + float(timeout)
        while time.time() < end_time:
            for msg in list(self._received[topic]):
                data = json.loads(msg)
                if required_key in data:
                    self._received[topic].remove(msg)
                    return data
            time.sleep(0.1)
        raise TimeoutError(f"No message with key '{required_key}' on '{topic}' within {timeout}s")

    def disconnect_from_broker(self):
        self._client.loop_stop()
        self._client.disconnect()