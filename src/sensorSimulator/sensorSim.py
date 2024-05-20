import paho.mqtt.client as mqtt
import json
import time
import random

# Configuración del broker MQTT
broker_address = "localhost"
broker_port = 1883
topic = "sensor_data"

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
        data = generate_data()
        client.publish(topic, data)
        time.sleep(0.1)

# Conexión al broker MQTT
client = mqtt.Client()
client.connect(broker_address, broker_port)

# Inicio de la publicación de datos
publish_data(client)