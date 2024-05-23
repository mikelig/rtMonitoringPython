### Instrucciones para poner en funcionamiento los simuladores de sensores que publican al broker MQTT local
> Nota:
> En caso de querer utilizar un broker distinto a *localhost*, cambiar la variable de entorno '`BROKER_ADD`' del fichero *.env*

# Prerequisitos
Para poder ejecutar este módulo se necesitan tener instalados:
- docker
- docker-compose

# Puesta en marcha
## Opción A: Creación de imagen en runtime
Se ha creado un fichero bash llamado *run_sensors.sh* que crea e inicializa N contenedores de simulador, donde N es un número especificado en el archivo *docker-compose.yml* con la opción de `scale`. Este script crea una imagen a partir del *Dockerfile* especificado e inicializa los contenedores, por lo que en caso de utilizar esta opción solo se debe ejecutar el script.
1. Descargar el código fuente del [repositorio de Github](https://github.com/mikelig/rtMonitoringPython)
2. Hacer el script ejecutable:
   `chmod +x run_sensors.sh`
3. Ejecutar script especificando el archivo *Dockerfile* y el archivo *docker-compose.yml* a usar
   `./run_sensors.sh Dockerfile docker-compose.yml`
4. Comprobar estado contenedores (debería de haber tantos contenedores como el número de `scale` dentro del fichero docker-compose)
   `docker ps`
5. Para parar el script, presionar *CTRL + C*. El script está configurado para parar y eliminar los contenedores.



## Opción B: Puesta en marcha con código fuente local
1. Descargar el código fuente del [repositorio de Github](https://github.com/mikelig/rtMonitoringPython)
2. Crear la imagen docker con nombre de imagen *sensorsimulator*:
   `docker build -t sensorsimulator .`
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

## Opción C: Puesta en marcha con imagen de docker hub
He creado una imagen docker y lo he subido al Docker Hub, por lo que se puede utilizar esta imagen en vez de crear una nueva.
En caso de usar esta opción, se debe de crear un fichero *.env* y un fichero *docker-compose.yml* ya que la imagen usa variables de entorno. Se puede encontrar los ficheros originales en el [repositorio de Github](https://github.com/mikelig/rtMonitoringPython)
1. Descargar imagen docker:
   `docker pull mikelig/sensorsimulator:latest`
2. Crear fichero *.env*
3. Crear fichero *docker-compose.yml*
4. Seguir los mismos pasos de la seccion ***Opción B: Puesta en marcha con código fuente local*** a partir del paso 4.