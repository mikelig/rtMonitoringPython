# Instrucciones live demo
## Setup del demo
- Máquina virtual con broker MQTT Mosquitto
- Codigo fuente pre-descargado
- 2000 eventos/s: Escalado de simuladores puesto a "20"

## Pasos:
1. Crear imagen *gatewaysubscriber* (saltar si no es necesario):
    `docker build -t gatewaysubscriber .`
2. Empezar contenedor gatewaysubscriber en dettached mode:
  `docker-compose up -d`
  Si da error:
  `docker compose up -d`
3. Iniciar simuladores con bash script:
   `./run_sensors.sh Dockerfile docker-compose.yml`
5. Meterse al SQLite para mirar el primer dato:
   `select * from sensorEvent order by idEvent ASC LIMIT 3;`
6. Esperar 30 segundos, parar contenedor *gatewaysubscriber*
   `docker-compose stop`
7. Esperar 2 min
8. Arrancar contenedor *gatewaysubscriber*
9.  Meterse al SQLite para mirar el primer dato y mirar persistencia:
    `select * from sensorEvent order by idEvent ASC LIMIT 3;`
10. Meterse al SQLite para mirar el último dato:
    `select * from sensorEvent order by idEvent DESC LIMIT 3;`