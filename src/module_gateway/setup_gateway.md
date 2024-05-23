### Instrucciones para poner en funcionamiento el módulo del gateway, el cual actua como un subscritor de MQTT que recibe los datos de los sensores, los procesa y los descarta o guarda en la base de datos.
> Nota:
> En caso de querer utilizar un broker distinto a *localhost*, cambiar la variable de entorno '`BROKER_ADD`' del fichero *.env*

# Prerequisitos
Para poder ejecutar este módulo se necesitan tener instalados:
- docker
- docker-compose

# Puesta en marcha
## Opción A: Puesta en marcha con código fuente local
1. Descargar el código fuente del [repositorio de Github](https://github.com/mikelig/rtMonitoringPython)
2. Crear la imagen docker con nombre de imagen *gatewaysubscriber*:
   `docker build -t gatewaysubscriber .`
3. En caso necesario, se pueden modificar las variables de entorno en el archibo *.env*
4. Iniciar contenedor con docker-compose:
  `docker-compose up -d` <br>
   > [!info]
   > A veces da el error "`KeyError: 'ContainerConfig'`". En esos casos, usar el comando:
   > `docker compose up -d`
1. Verificar que está corriendo:
   `docker ps`
2. Usar docker-compose para parar/arrancar/remover el contenedor:
   `docker-compose {down/stop/start}`

## Opción B: Puesta en marcha con imagen de docker hub
He creado una imagen docker y lo he subido al Docker Hub, por lo que se puede utilizar esta imagen en vez de crear una nueva.
En caso de usar esta opción, se debe de crear un fichero *.env* y un fichero *docker-compose.yml* ya que la imagen usa variables de entorno. Se puede encontrar los ficheros originales en el [repositorio de Github](https://github.com/mikelig/rtMonitoringPython)
1. Descargar imagen docker:
   `docker pull mikelig/gatewaysubscriber:latest`
2. Crear fichero *.env*
3. Crear fichero *docker-compose.yml*
4. Seguir los mismos pasos de la seccion ***Opción A: Puesta en marcha con código fuente local*** a partir del paso 4.