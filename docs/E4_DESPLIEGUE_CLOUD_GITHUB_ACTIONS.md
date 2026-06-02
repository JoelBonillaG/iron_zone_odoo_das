# E4 - Despliegue en la nube, infraestructura y validacion con GitHub Actions

## Alcance del entregable

El entregable E4 documenta la puesta en produccion del sistema Iron Zone Odoo sobre una infraestructura en la nube, junto con el mecanismo de validacion automatizada incorporado al repositorio mediante GitHub Actions. Esta documentacion se concentra en dos aspectos evaluables del cierre del proyecto: la ejecucion de pruebas automaticas sobre las ramas `develop` y `main`, y la arquitectura de despliegue utilizada para operar el aplicativo en un VPS con Docker.

La solucion se plantea como un flujo de trabajo controlado entre desarrollo y produccion. La rama `develop` funciona como el espacio donde se integran cambios funcionales antes de su promocion, mientras que la rama `main` representa la version estable que debe coincidir con el aplicativo desplegado. Bajo este criterio, GitHub Actions se utiliza como una capa de verificacion previa que reduce el riesgo de publicar cambios con errores sintacticos, manifests invalidos o archivos XML mal formados.

## Validacion automatizada en `develop` y `main`

El repositorio incorpora un workflow de integracion continua ubicado en `.github/workflows/ci.yml`. Este workflow se ejecuta cuando se publica un cambio en las ramas `develop` o `main`, y tambien cuando se abre o actualiza un pull request dirigido a cualquiera de esas ramas. La intencion de esta configuracion es validar tanto el trabajo en progreso como los cambios que se preparan para produccion, sin ejecutar despliegues automaticos en ramas que todavia no representan una version final.

La validacion automatizada se apoya en un script interno ubicado en `.github/scripts/validate_repo.py`. Dicho script revisa la sintaxis de los archivos Python presentes en los directorios principales del proyecto, valida que los manifests de los modulos Odoo puedan interpretarse correctamente y comprueba que los archivos XML relevantes sean documentos bien formados. Esta verificacion es importante porque Odoo depende de archivos declarativos para cargar vistas, datos, permisos y configuraciones; un error en estos elementos puede impedir la actualizacion de modulos o afectar el arranque del sistema.

El workflow tambien prepara un entorno Node.js para verificar la consistencia de las dependencias declaradas en los archivos `package-lock.json`. En la raiz del proyecto se valida el paquete general asociado a herramientas de automatizacion, mientras que en `Pruebas/Modulo 2` se valida el conjunto de dependencias utilizado por los flujos de prueba end-to-end. Adicionalmente, los archivos JavaScript de estos flujos se someten a una comprobacion de sintaxis mediante Node.js, de modo que el repositorio detecte errores basicos antes de que los scripts sean utilizados manualmente o dentro de una futura etapa de pruebas funcionales mas completa.

Las pruebas configuradas para `develop` y `main` no modifican la base de datos de produccion ni ejecutan acciones destructivas sobre el servidor. Su objetivo es actuar como control de calidad previo, asegurando que los artefactos del repositorio mantengan una estructura valida. Esta decision permite que la validacion sea rapida, repetible y segura para ramas de integracion, sin depender de credenciales productivas ni de la disponibilidad del ambiente desplegado.

## Relacion entre Git, staging y produccion

El flujo propuesto establece que los cambios funcionales se integran primero en `develop`. Cuando el equipo considera que una version esta lista para publicarse, los cambios se promueven hacia `main` mediante pull request o merge controlado. Esta separacion permite sostener un flujo de staging logico aun cuando el proyecto no mantenga dos servidores separados: `develop` representa la validacion previa en repositorio y `main` representa el estado que debe ser desplegado.

El uso de GitHub Actions fortalece este flujo porque las validaciones se ejecutan en ambos puntos criticos. En `develop`, las pruebas ayudan a detectar problemas durante la integracion del equipo. En `main`, las mismas pruebas actuan como una ultima verificacion antes de que el workflow de despliegue pueda actualizar el servidor. De esta manera, la trazabilidad de Git queda conectada con la operacion del aplicativo en la nube.

## Despliegue en VPS

El sistema se encuentra desplegado en un servidor VPS accesible mediante dominio publico. La infraestructura utiliza Docker Compose para levantar los servicios principales del aplicativo: un contenedor de Odoo 18, un contenedor PostgreSQL 15 para la base de datos y un contenedor auxiliar de Stripe CLI para la recepcion de eventos de pago en ambiente de integracion. Esta composicion permite aislar responsabilidades, simplificar reinicios y mantener persistencia de datos mediante volumenes Docker.

El codigo fuente del proyecto se mantiene en el servidor dentro de `/home/iron_zone_odoo_das`. El directorio fue preparado para que el usuario operativo `adminops` pueda ejecutar tareas de despliegue sin usar la cuenta `root` como usuario de trabajo cotidiano. Esta decision responde a una practica de administracion segura: `root` se reserva para emergencias, mientras que `adminops` opera con permisos acotados y pertenencia al grupo `docker`.

El archivo `docker-compose.yml` define los servicios requeridos por la aplicacion. El servicio de Odoo expone el puerto `8069`, monta el directorio `addons` como ruta de modulos personalizados y utiliza `config/odoo.conf` como archivo de configuracion. El servicio de base de datos usa PostgreSQL 15 y conserva la informacion mediante un volumen persistente. El servicio asociado a Stripe se mantiene separado para evitar mezclar el proceso principal de Odoo con tareas externas de integracion de pagos.

La configuracion productiva conserva `proxy_mode = True` en `config/odoo.conf`, debido a que el aplicativo se sirve a traves de un dominio y un proxy inverso. Esta opcion permite que Odoo interprete correctamente cabeceras reenviadas por el proxy, incluyendo esquema, host y direccion de origen. La configuracion resulta necesaria para que las URL generadas por Odoo y los redireccionamientos funcionen correctamente en el dominio publico.

## Automatizacion del despliegue

El despliegue automatizado se define en `.github/workflows/deploy.yml`. Este workflow se ejecuta cuando existe un push sobre `main` o cuando el equipo lo dispara manualmente desde GitHub Actions. Antes de conectarse al servidor, el workflow ejecuta una validacion basica del repositorio para confirmar que los manifests, XML y archivos Python se mantienen en condiciones correctas.

La conexion hacia el VPS se realiza mediante SSH y utiliza una llave privada almacenada como secret de GitHub Actions. La llave publica correspondiente se instala en el archivo `authorized_keys` del usuario `adminops` en el servidor. Con ello, GitHub Actions puede autenticarse sin contrasenas y sin exponer credenciales personales del equipo. Los valores de host, puerto, usuario SSH, ruta de despliegue y base de datos se separan en secrets o variables del repositorio para que la configuracion pueda modificarse sin editar el workflow.

Durante el despliegue, el workflow entra al directorio del proyecto en el servidor, obtiene los cambios mas recientes desde GitHub, actualiza la rama `main` mediante `git pull --ff-only origin main` y ejecuta `scripts/install_apps.sh` con la base de datos configurada. Este script detiene temporalmente el contenedor de Odoo para liberar bloqueos, ejecuta Odoo en modo de inicializacion y actualizacion de modulos, y finalmente vuelve a levantar el servicio principal.

Al finalizar, el workflow verifica el estado de los servicios con Docker Compose y realiza una comprobacion HTTP contra la ruta `/web/login` de Odoo en `localhost`. Esta verificacion confirma que el proceso principal responde despues de la actualizacion. La prueba no reemplaza una validacion funcional completa de negocio, pero si entrega una evidencia automatica de que el despliegue termino, los contenedores estan activos y la interfaz web basica se encuentra disponible.

## Infraestructura involucrada

La infraestructura de produccion esta compuesta por el repositorio GitHub, GitHub Actions como mecanismo de automatizacion, un VPS como servidor de aplicacion, Docker Compose como orquestador local, Odoo 18 como plataforma ERP, PostgreSQL 15 como motor de base de datos y un dominio publico asociado al servicio web. Estos elementos trabajan en conjunto para sostener un flujo en el que el codigo validado en Git se convierte en una actualizacion operativa sobre el ambiente productivo.

El repositorio actua como fuente de verdad del codigo y de los archivos de configuracion versionados. GitHub Actions proporciona la trazabilidad de ejecuciones, resultados de validacion y despliegues. El VPS contiene el runtime real del sistema y mantiene los volumenes persistentes de datos. Docker Compose permite recrear o reiniciar servicios de forma declarativa, mientras que Odoo y PostgreSQL ejecutan la logica de negocio y almacenamiento de informacion del gimnasio.

## Consideraciones operativas

La automatizacion implementada mantiene separadas las credenciales sensibles del codigo fuente. La llave privada SSH, el host del servidor y los datos operativos del despliegue deben permanecer en GitHub Secrets o GitHub Variables, segun corresponda. Esta separacion evita que informacion critica quede expuesta dentro del repositorio y permite rotar accesos sin modificar el codigo.

El flujo tambien conserva una responsabilidad manual importante: el equipo debe revisar los cambios antes de fusionarlos a `main`. GitHub Actions valida estructura y sintaxis, pero no sustituye la revision funcional ni la demo completa del sistema. En el contexto del entregable E4, esta combinacion evidencia una arquitectura desplegada en VPS, una operacion basada en Docker, una promocion controlada desde Git y una capacidad tecnica para explicar el funcionamiento del sistema desde el repositorio hasta produccion.
