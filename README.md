# Bot de ayuda de la asignatura Modelos de Optimización

Bot de telegram de la asignatura Modelos de Optimización para la ayuda a los
estudiantes en la resolución problemas o situaciones especificas. 

## Uso

- El estudiante accede al bot [Bot](https://t.me/ModelosOptimizacion_bot), el
  cual se iniciará con el comando `/start`. 
- Luego se puede acceder a los problemas disponibles usando el comando `/enum`.
- Se mostrará una lista con los problemas y un comando asociado a cada uno de
  ellos, al precionar este comando se obtendrá información acerca de este
  problema.
- Al abrir información de un problema, ademas de la explicación acerca de este,
  se muestran dos botones.
- El primero muestra como es el formato para mandar una solución al problema.
- El segundo muestra como es el formato para mandar una solución al problema,
  con parametros definidos por el usuario.
- Las soluciones deben tener formato `.json`, esta solución se puede enviar en 
  un archivo o en un mensaje de telegram.
- Una vez enviado la solución del problema se retornará un conjunto de mensajes
  los cuales tienen como objetivo hacer conocer al estudiante que tanto se
  acerca su solución a la optima de manera personalizada, y también si tuvo
  algún error al enviarla.

## Problemas

Los problemas que contiene el bot los da un proveedor, el proveedor por defecto
es uno local ya definido que contiene todos los problemas disponibles en el
directorio `/src/solvers/`.

La clase abstracta `BaseProvider` da la posibilidad de definir otros proveedores
de problemas que hereden de esta y establecerlos en el archivo `src/config.py`. 
Un ejemplo de esto es el proveedor GithubProvider (`src/github_provider.py`) 
que obtiene los problemas de un repositorio de github dado por el usuario.

## Añadir problemas por defecto

Añadir problemas al bot depende del proveedor de problemas, ya que este puede
incluso ser un servicio online, pero para el proveedor por defecto se debe
crear una clase que herede de la clase abstracta `BaseSolver` y rellenar con la
información asociada al problema y los metodos de resolución computarizada de
este.
