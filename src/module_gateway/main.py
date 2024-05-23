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
from datetime import datetime, timezone
import os
import sys

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
BROKER = os.environ.get('BROKER_ADD')
PORT = int(os.environ.get('BROKER_PORT', 1883))
TOPIC = os.environ.get('MQTT_TOPIC')
CLIENT_ID = os.environ.get('CLIENT_ID')
SQLITE_DB_PATH= os.environ.get('SQLITE_DB_PATH', 'sensor_events.db')
BATCH_SIZE= int(os.environ.get('BATCH_SIZE', 100))
TIMEOUT_SEC= int(os.environ.get('TIMEOUT_SEC', 60))


# Configure root logger to write to both file and STDOUT
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

# Create file handler
file_handler = logging.FileHandler(f'{CLIENT_ID}.log', encoding='utf-8')
file_handler.setLevel(LOGLEVEL)

# Create console handler (STDOUT)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOGLEVEL)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info(f"HOST = {BROKER}  class: {BROKER.__class__}")
logger.info(f"Port = {PORT}  class: {PORT.__class__}")
logger.info(f"Topic = {TOPIC}  class: {TOPIC.__class__}")
logger.info(f"ClientID = {CLIENT_ID}  class: {CLIENT_ID.__class__}")
logger.info(f"DB PATH = {SQLITE_DB_PATH}  class: {SQLITE_DB_PATH.__class__}")
logger.info(f"Batch size = {BATCH_SIZE}  class: {BATCH_SIZE.__class__}")
logger.info(f"Timeout secs = {TIMEOUT_SEC}  class: {TIMEOUT_SEC.__class__}")
# MQTT Settings


# Global variables
event_batches = {}
batch_size = BATCH_SIZE
batch_timeout = TIMEOUT_SEC  # seconds

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
        logger.error(f"Error calculating outliers: {e}")
        return []

# SQLite setup
def init_db():
    call("./setup.sh") # this is done in docker now

# Function to process batch
async def process_batch(events):
    logger.debug(f"4_1- entered process_batch with events len = {len(events)}")
    values = [event[4] for event in events]
    outlier_indices = filter_outliers(values)
    filtered_events = [event for index, event in enumerate(events) if index not in outlier_indices]

    del values
    del outlier_indices
    if filtered_events:
        logger.debug(f"4_2- Len after filter: {len(filtered_events)}")
        conn = sqlite3.connect(SQLITE_DB_PATH)
        logger.debug(f"4_3 DB connected")
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT INTO sensorEvents (receptionTs, receptionDt, idSensor, sensorType, sensorValue)
        VALUES (?, ?, ?, ?, ?)
        ''', filtered_events)
        conn.commit()
        conn.close()
        logger.debug(f"4_4 Events saved to DB")
    del filtered_events

# Timer callback function
def on_batch_timeout(sensor_id):
    with lock:
        logger.debug(f"4_- Timeout for {sensor_id} detected")
        if sensor_id in event_batches and event_batches[sensor_id][0]:
            asyncio.run(process_batch(event_batches[sensor_id][0]))
            event_batches[sensor_id] = ([], None)

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        logger.debug(f"1- received msg: {data}")

        sensor_id = data['sensor_id']
        sensor_type = data['sensor_type']
        value = float(data['value'])
        dt_now = datetime.now(tz=timezone.utc)
        timestamp = round(dt_now.timestamp() * 1000)
        datetime_str = dt_now.isoformat()
        del dt_now
        with lock:
            if sensor_id not in event_batches:
                event_batches[sensor_id] = ([], None)

            event_batches[sensor_id][0].append((timestamp, datetime_str, sensor_id, sensor_type, value))
            del timestamp
            del datetime_str
            logger.debug(f"2- sensor {sensor_id} batch size = {len(event_batches[sensor_id][0])}")

            if len(event_batches[sensor_id][0]) >= batch_size:
                logger.debug(f"3- Going to process batch for sensor {sensor_id}")
                if event_batches[sensor_id][1] is not None:
                    event_batches[sensor_id][1].cancel()
                asyncio.run(process_batch(event_batches[sensor_id][0]))
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
        logger.error(f"Error processing message: {e}")

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
    logger.debug("Signal received, stopping all timers...")
    with lock:
        for sensor_id, (events, timer) in event_batches.items():
            if timer is not None:
                timer.cancel()
        logger.debug("All timers stopped, processing remaining batches...")
        for sensor_id, (events, _) in event_batches.items():
            if events:
                asyncio.run(process_batch(events))
    logger.debug("All batches processed, exiting...")
    exit(0)

# Main
if __name__ == '__main__':
    # init_db() # Commented because this is done in docker now

    # Register signal handlers (CTRL + Z can be used to stop without forcing the signals)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        run_mqtt_client()
    except KeyboardInterrupt:
        logger.debug("Exiting...")
