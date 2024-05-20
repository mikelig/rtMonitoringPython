import asyncio
import json
import sqlite3
import threading
import time
from paho.mqtt import client as mqtt_client
import numpy as np
from subprocess import call

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
batch_size = 100

# Establecer un token para modificar el diccionario 'event_batches', ya que como
# es llamado por process_batch() y esta funcion usa el modulo AsyncIO, puede haber conflictos.
lock = threading.Lock() 

# Filter outliers function
def filter_outliers(datos):
    '''
    Importante: 
    He modificado el codigo de filter_outliers para que en vez de generar una lista intermedia
    con los valores aceptables, me genere una lista con los indices de los valores que se posicionan fuera del 
    filtro. 
    He hecho esta modificación porque por una parte uso menos la memoria (ya que solo guardo los indices en vez de los valores float)
    y por otra, puedo más tarde usar estos indices para eliminar los valores fuera del filtro de una manera
    mucho más rápida y optimizada.
    '''
    mean = sum(datos) / len(datos)
    varianza = sum((x - mean) ** 2 for x in datos) / (len(datos) - 1)
    std = varianza ** 0.5
    
    low, high = mean - 3 * std, mean + 3 * std
    # low, high = mean - std, mean + std # for testing filter only
    
    # Get indices of outliers
    outlier_indices = [i for i, v in enumerate(datos) if v < low or v > high]
    return outlier_indices

# SQLite setup
def init_db():
    call("./setup.sh")

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
                event_batches[sensor_id] = []
            event_batches[sensor_id].append((timestamp, sensor_id, sensor_type, value))
            logging.debug(f"2- sensor {sensor_id} batch size = {len(event_batches[sensor_id])}")

            if len(event_batches[sensor_id]) >= batch_size:
                logging.debug(f"3- Going to process batch for sensor {sensor_id}")
                asyncio.run(process_batch(event_batches[sensor_id]))
                event_batches[sensor_id] = []
    except Exception as e:
        logging.error(f"Error processing message: {e}")

async def process_batch(events):
    logging.debug(f"4_1- entered process_batch with events len = {len(events)}")
    
    values = [event[3] for event in events]
    
    # Get indices of outliers
    outlier_indices = filter_outliers(values)
    
    # Filter events to exclude outliers
    filtered_events = [event for index, event in enumerate(events) if index not in outlier_indices]
    
    del values
    del outlier_indices
    if filtered_events:
        logging.debug(f"4_2- Len after filter: {len(filtered_events)}")

        # Insert filtered events to SQLite DB
        conn = sqlite3.connect('sensor_events.db')
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT INTO sensorEvents (receptionTs, idSensor, sensorType, sensorValue)
        VALUES (?, ?, ?, ?)
        ''', filtered_events)
        
        # # Insert backup -- Not implemented yet
        # backup_ts = int(time.time())
        # cursor.execute('''
        # INSERT INTO periodicBackups (idSensor, backupTs, mean, variance, stddev)
        # VALUES (?, ?, ?, ?, ?)
        # ''', (sensor_id, backup_ts, mean_val, variance_val, stddev_val))

        conn.commit()
        conn.close()
        
    del filtered_events

# MQTT Client Setup
def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    client.on_connect = lambda client, userdata, flags, rc: client.subscribe(TOPIC)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    return client

def run_mqtt_client():
    client = connect_mqtt()
    logging.debug(f"MQTT client connected == {client.is_connected()}")
    client.loop_forever()

# Main
if __name__ == '__main__':
    init_db()
    
    try:
        run_mqtt_client()
    except KeyboardInterrupt:
        logging.debug("Exiting...")
