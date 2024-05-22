import paho.mqtt.client as mqtt
import json
import time
import random
import os
import logging

logging.basicConfig(filename='testing.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

# Configuración del broker MQTT
broker_address = os.environ.get('BROKER_ADD')
broker_port = int(os.environ.get('BROKER_PORT'))
topic = os.environ.get('MQTT_TOPIC')
logging.info(f"HOST = {broker_address}  class: {broker_address.__class__}")
logging.info(f"Port = {broker_port}  class: {broker_port.__class__}")
logging.info(f"Topic = {topic}  class: {topic.__class__}")

# Función para generar los datos aleatorios
def generate_data():
    sensor_id = "sensor_" + str(random.randint(1, 10))
    sensor_type = "type_" + str(random.randint(1, 3))
    value = random.uniform(0, 100)
    data = {"sensor_id": sensor_id, "sensor_type": sensor_type, "value": value}
    return json.dumps(data)

# Función para publicar los datos en el broker MQTT
def publish_data(client):
    while True:
        try:
            data = generate_data()
            client.publish(topic, data)
        except Exception as e:
            logging.error(f"Error publishing: {e}")
        finally:
            time.sleep(0.1)

try:
    # Conexión al broker MQTT
    client = mqtt.Client()
    client.connect(broker_address, broker_port)
except Exception as e:
    logging.error(f"Could not connect to broker: {e}")
else:
    # Inicio de la publicación de datos
    logging.info("Connected. Starting publish")
    publish_data(client)