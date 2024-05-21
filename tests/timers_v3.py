import asyncio
import json
import sqlite3
import threading
import time
import signal
from paho.mqtt import client as mqtt_client
import numpy as np
from subprocess import call
from threading import Timer
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='testing.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

# MQTT Settings
BROKER = 'localhost'
PORT = 1883
TOPIC = 'sensor_data'
CLIENT_ID = 'test_gw'

# Global variables
event_batches = {}
batch_size = 30
batch_timeout = 60  # seconds

# Lock for thread safety
lock = threading.Lock()

# Filter outliers function
def filter_outliers(datos):
    try:
        if len(datos) <= 1:
            return []
        mean = sum(datos) / len(datos)
        varianza = sum((x - mean) ** 2 for x in datos) / (len(datos) - 1)
        std = varianza ** 0.5
        low, high = mean - 3 * std, mean + 3 * std
        outlier_indices = [i for i, v in enumerate(datos) if v < low or v > high]
        return outlier_indices
    except Exception as e:
        logging.error(f"Error calculating outliers: {e}")
        return []

# SQLite setup
def init_db():
    call("./setup.sh")

# Function to process batch
async def process_batch(sensor_id, events):
    logging.debug(f"4_1- entered process_batch with events len = {len(events)}")
    values = [event[3] for event in events]
    outlier_indices = filter_outliers(values)
    filtered_events = [event for index, event in enumerate(events) if index not in outlier_indices]

    del values
    del outlier_indices
    if filtered_events:
        logging.debug(f"4_2- Len after filter: {len(filtered_events)}")
        conn = sqlite3.connect('sensor_events.db')
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT INTO sensorEvents (receptionTs, idSensor, sensorType, sensorValue)
        VALUES (?, ?, ?, ?)
        ''', filtered_events)
        conn.commit()
        conn.close()
    del filtered_events

# Timer callback function
def on_batch_timeout(sensor_id):
    with lock:
        logging.debug(f"4_- Timeout for {sensor_id} detected")
        if sensor_id in event_batches and event_batches[sensor_id][0]:
            asyncio.run(process_batch(sensor_id, event_batches[sensor_id][0]), debug=True)
            event_batches[sensor_id] = ([], None)

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        logging.debug(f"1- received msg: {data}")

        sensor_id = data['sensor_id']
        sensor_type = data['sensor_type']
        value = float(data['value'])
        timestamp = int(time.time())

        with lock:
            if sensor_id not in event_batches:
                event_batches[sensor_id] = ([], None)

            event_batches[sensor_id][0].append((timestamp, sensor_id, sensor_type, value))
            logging.debug(f"2- sensor {sensor_id} batch size = {len(event_batches[sensor_id][0])}")

            if len(event_batches[sensor_id][0]) >= batch_size:
                logging.debug(f"3- Going to process batch for sensor {sensor_id}")
                if event_batches[sensor_id][1] is not None:
                    event_batches[sensor_id][1].cancel()
                asyncio.run(process_batch(sensor_id, event_batches[sensor_id][0]), debug=True)
                event_batches[sensor_id] = ([], None)
            else:
                if event_batches[sensor_id][1] is not None:
                    event_batches[sensor_id][1].cancel()
                event_batches[sensor_id] = (
                    event_batches[sensor_id][0],
                    Timer(batch_timeout, on_batch_timeout, args=[sensor_id])
                )
                event_batches[sensor_id][1].start()

    except Exception as e:
        logging.error(f"Error processing message: {e}")

# MQTT Client Setup
def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    client.on_connect = lambda client, userdata, flags, rc: client.subscribe(TOPIC)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    return client

def run_mqtt_client():
    client = connect_mqtt()
    client.loop_forever()

# Signal handler for clean shutdown
def signal_handler(sig, frame):
    logging.debug("Signal received, stopping all timers...")
    with lock:
        for sensor_id, (events, timer) in event_batches.items():
            if timer is not None:
                timer.cancel()
        logging.debug("All timers stopped, processing remaining batches...")
        for sensor_id, (events, _) in event_batches.items():
            if events:
                asyncio.run(process_batch(sensor_id, events), debug=True)
    logging.debug("All batches processed, exiting...")
    exit(0)

# Main
if __name__ == '__main__':
    init_db()

    # Register signal handlers (CTRL + Z can be used to stop without forcing the signals)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        run_mqtt_client()
    except KeyboardInterrupt:
        logging.debug("Exiting...")
