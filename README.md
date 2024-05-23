# Estructura del repositorio
El repositorio incluye 2 modulos:
## module_gateway
Incluye el código y los archivos necesarios para iniciar el módulo del gateway.
Las instrucciones para ello se encuentran [dentro del módulo de module_gateway](/src/module_gateway/setup_gateway.md)

## sensorsimulator
Incluye el código y los archivos necesarios para iniciar los simuladores del sensor.
Las instrucciones para ello se encuentran [dentro del módulo de sensorSImulator](/src/sensorSimulator/setup_simulator.md)


# Implementación
## Target HW
El código se ha pensado para la implementación de un Hardware con las siguientes características:
- 512 MiB RAM
- 1 CPU, 2 cores
- 800MHz clock
  
## module_gateway
La imagen Docker tiene un entrypoint, por lo que al iniciar un contenedor con esta imagen se ejecutara primero el script [entrypoint.sh](/src/module_gateway/entrypoint.sh), el cual:
1. ejecuta el script [init_db.sh](/src/module_gateway/init_db.sh) usado para la inicialización de la base de datos
   - El SQLite es inicializado con las siguientes configuraciones:
     - WAL: Mejor rendimiento de escritura que el default ‘DELETE’
     - Sincronización NORMAL: Garantiza que cada transacción se escriba en el disco, pero se permite cierto grado de asincronía
     - Mapeo memoria: 256MB (RAM / 2)
     - Tamaño caché: 2MB (se puede disminuir optimizando la memoria pero aumentando tiempo inserción)
     
2. Ejecuta el script python [main.py](/src/module_gateway/main.py)

## Script main.py
### Función filter_outliers
He modificado el codigo de filter_outliers para que en vez de generar una lista intermedia
con los valores aceptables, me genere una lista con los indices de los valores que se posicionan fuera del 
filtro. 
He hecho esta modificación porque por una parte uso menos la memoria (ya que solo guardo los indices en vez de los valores float)
y por otra, puedo más tarde usar estos indices para eliminar los valores fuera del filtro de una manera
mucho más rápida y optimizada.

### Uso de la librería AsyncIO
Aunque para tareas que requieren un uso del CPU se suele utilizar `multiprocessing`, he optado por utilizar `AsyncIO` ya que la funcion `filter_outliers` no requiere de un uso excesivo de recursos. AsyncIO es mejor para tareas con I/O, pero también maneja eficientemente múltiples conexiones simultáneas con menor consumo de memoria y sin la sobrecarga de crear múltiples procesos, haciendolo una opción válida para este caso de uso.


