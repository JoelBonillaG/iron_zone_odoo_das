# Iron Zone - Odoo 18

Sistema academico para la gestion de un gimnasio y centro deportivo desarrollado sobre Odoo 18 y PostgreSQL 15 con Docker.

## Tabla de contenidos

- Descripcion general
- Funcionalidades principales
- Requisitos
- Instalacion rapida
- Configuracion inicial
- Instalacion de modulos
- Carga de datos de prueba
- Credenciales de prueba
- Como usar la aplicacion
- Rutas principales
- Estructura del repositorio
- Modulos personalizados
- Configuracion de pagos y correo
- Documentacion del proyecto
- Comandos utiles
- Problemas comunes

## Descripcion general

Iron Zone integra procesos administrativos y operativos de un gimnasio:

- Sitio web publico.
- Tienda online.
- Suscripciones y planes.
- Eventos o clases.
- Guias de ejercicios.
- Inventario.
- Ventas.
- Facturacion.
- Email marketing y correos transaccionales.
- Localizacion ecuatoriana para facturacion y validaciones.

El proyecto usa modulos nativos de Odoo y varios addons personalizados ubicados en `addons/`.

## Funcionalidades principales

### Sitio web

- Pagina de inicio.
- Pagina Nosotros.
- Pagina Contacto.
- Menu web personalizado.
- Diseno visual oscuro para Iron Zone.

### Tienda y suscripciones

- Publicacion de planes y productos.
- Suscripciones mensuales, trimestrales y anuales.
- Integracion con ventas y pagos.
- Beneficios asociados a planes.

### Eventos y clases

- Publicacion de clases o eventos deportivos.
- Relacion con instructores o entrenadores.
- Registro de usuarios cuando aplica.

### Guias de ejercicios

- Guias publicadas en el portal web.
- Filtros por tipo, dificultad, grupo muscular y maquina.
- Relacion con maquinas del gimnasio.
- Imagen y video de referencia.
- Permisos por rol: visitante, portal, entrenador y administrador.

### Backend administrativo

- Gestion de ventas.
- Gestion de inventario.
- Facturacion.
- Usuarios y permisos.
- Configuracion tecnica de modulos.

## Requisitos

- Docker Desktop instalado y corriendo.
- Git.
- Python 3.
- Bash disponible para ejecutar scripts.
- Node.js opcional, solo si se desean automatizar capturas o tareas de documentacion.

## Instalacion rapida

```bash
git clone <repo-url>
cd iron_zone_odoo_das
cp .env.example .env
docker compose up -d
```

Abrir:

```text
http://localhost:8069
```

Esperar aproximadamente 30 segundos despues de levantar Docker.

## Configuracion inicial

Crear la base de datos desde el wizard de Odoo en `localhost:8069`.

| Campo | Valor |
| --- | --- |
| Master Password | `admin123` |
| Database Name | `iron_zone` |
| Email | `admin@ironzone.com` |
| Password | `admin123` |
| Phone | `032000000` |
| Language | Spanish |
| Country | Ecuador |
| Demo Data | Desactivado |

## Instalacion de modulos

Despues de crear la base de datos, ejecutar:

```bash
bash scripts/install_apps.sh
```

El script instala y actualiza modulos base y personalizados en la base `iron_zone`.

Modulos principales instalados:

- `website`
- `website_sale`
- `website_sale_stock`
- `account`
- `account_payment`
- `sale_management`
- `stock`
- `purchase`
- `event`
- `website_event`
- `hr`
- `mass_mailing`
- `appointment`
- `iz_website`
- `iz_inventory`
- `iz_backend_theme`
- `iz_subscription`
- `ironzone_exercise_guide`
- `training_plans`
- `l10n_ec_base`
- `l10n_ec_edi`
- `l10n_ec_sri`
- `l10n_ec_withholding`
- `l10n_ec_reports`

## Carga de datos de prueba

Ejecutar todos los seeds:

```bash
bash seeds/run_seeds.sh
```

Ejecutar un seed especifico:

```bash
bash seeds/run_seeds.sh 10_exercise_guides
```

Orden general de seeds:

1. Configuracion de empresa.
2. Configuracion SMTP.
3. Clientes.
4. Planes y suscripciones.
5. Productos.
6. Ventas.
7. Facturacion.
8. Empleados y entrenadores.
9. Eventos.
10. Email marketing.
11. Guias de ejercicios.

Los seeds usan XML-RPC para comunicarse con Odoo.

## Credenciales de prueba

| Rol | Usuario | Contrasena |
| --- | --- | --- |
| Administrador | `admin` | `admin` |
| Administrador alterno | `admin@ironzone.com` | `admin123` |
| Entrenador | `carlos.mendez@ironzone.ec` | `admin123` |
| Entrenador | `sofia.garcia@ironzone.ec` | `admin123` |
| Cliente portal | `pruebasjos04@gmail.com` | `admin123` |
| Cliente portal | `pruebasjos07@gmail.com` | `admin123` |
| Cliente portal | `pruebasjos08@gmail.com` | `admin123` |
| PostgreSQL | `odoo` | `odoo` |

## Como usar la aplicacion

### Usuario visitante

1. Entrar a `http://localhost:8069`.
2. Navegar por `Inicio`, `Tienda`, `Eventos`, `Nosotros`, `Guia de ejercicios` y `Contacto`.
3. Consultar productos, planes, eventos y guias publicas.
4. Usar el formulario de contacto si se requiere informacion adicional.

### Cliente portal

1. Ir a `Iniciar sesion`.
2. Ingresar con un usuario portal, por ejemplo `pruebasjos04@gmail.com`.
3. Entrar a `Mi cuenta`.
4. Revisar pedidos, facturas, suscripciones y accesos disponibles.
5. Consultar la tienda y las guias con sesion iniciada.

### Entrenador

1. Iniciar sesion con un usuario entrenador.
2. Acceder al backend de Odoo.
3. Gestionar sus propias guias de ejercicios.
4. Consultar el portal web para visualizar las guias como usuario final.

### Administrador

1. Iniciar sesion con `admin / admin`.
2. Acceder al backend.
3. Administrar aplicaciones, ventas, inventario, facturacion, eventos, suscripciones y guias.
4. Ejecutar scripts de instalacion o seeds cuando se requiera actualizar la base.

## Rutas principales

| Ruta | Descripcion |
| --- | --- |
| `/` | Inicio del sitio web |
| `/shop` | Tienda online |
| `/event` | Eventos y clases |
| `/aboutus` | Pagina Nosotros |
| `/contactus` | Contacto |
| `/exercise-guides` | Catalogo de guias de ejercicios |
| `/exercise-guides/<id>` | Detalle de una guia |
| `/web/login` | Inicio de sesion |
| `/my` | Portal de cliente |
| `/odoo` | Backend de Odoo |
| `/odoo/apps` | Aplicaciones instaladas |

## Estructura del repositorio

```text
iron_zone_odoo_das/
  addons/
    ironzone_exercise_guide/
    iz_backend_theme/
    iz_inventory/
    iz_subscription/
    iz_website/
    l10n_ec_base/
    l10n_ec_edi/
    l10n_ec_reports/
    l10n_ec_sri/
    l10n_ec_withholding/
    training_plans/
  config/
    odoo.conf
  docs/
  docs_notion/
  scripts/
    install_apps.sh
    reset_local_db.ps1
  seeds/
    run_seeds.sh
    config.py
  docker-compose.yml
  .env.example
  README.md
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  CHANGELOG.md
```

## Modulos personalizados

| Modulo | Proposito |
| --- | --- |
| `iz_website` | Personalizacion del sitio web, plantillas, footer, paginas, correo y experiencia visual. |
| `iz_backend_theme` | Ajustes visuales y grupos internos para el backend de Iron Zone. |
| `iz_subscription` | Gestion de planes, beneficios y suscripciones. |
| `iz_inventory` | Ajustes relacionados con inventario. |
| `ironzone_exercise_guide` | Guias de ejercicios, maquinas, categorias, portal y permisos. |
| `training_plans` | Planes de entrenamiento, si esta instalado y actualizado en la base. |
| `l10n_ec_*` | Localizacion ecuatoriana, facturacion electronica, retenciones y reportes. |

## Configuracion de pagos y correo

### Stripe Sandbox

Configurar variables en `.env` si se desea probar pagos:

```text
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

Para ver el secreto de webhook generado por Stripe CLI:

```bash
docker logs iron_zone_stripe
```

Luego ejecutar:

```bash
bash seeds/run_seeds.sh 00_payment_providers
```

Si no existen credenciales de Stripe, el sistema mantiene ese proveedor deshabilitado o en modo seguro.

### SMTP

Configurar variables en `.env`:

```text
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_ENCRYPTION=
```

Ejecutar:

```bash
bash seeds/run_seeds.sh 00_smtp_config
```

Verificacion en Odoo:

```text
Ajustes -> Tecnico -> Correo electronico -> Correo saliente
```

## Documentacion del proyecto

Documentacion principal para Notion:

```text
docs_notion/
```

Resumen de entrega:

```text
docs/DOCUMENTACION_ENTREGA.md
```

Archivos complementarios del repositorio:

- `README.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`

## Comandos utiles

Levantar contenedores:

```bash
docker compose up -d
```

Detener contenedores:

```bash
docker compose down
```

Reiniciar Odoo:

```bash
docker restart iron_zone_odoo
```

Ver logs:

```bash
docker compose logs -f odoo
```

Entrar a PostgreSQL:

```bash
docker exec -it iron_zone_db psql -U odoo -d iron_zone
```

Comandos utiles dentro de PostgreSQL:

```sql
\dt
SELECT name FROM res_partner LIMIT 10;
SELECT name FROM product_template LIMIT 10;
\q
```

## Problemas comunes

### Error de actualizacion concurrente

Mensaje:

```text
could not serialize access due to concurrent update
```

Causa probable:

- Dos procesos intentaron actualizar modulos al mismo tiempo.
- Odoo estaba arrancando mientras se ejecutaba `install_apps.sh`.
- Quedo un proceso previo de instalacion activo.

Solucion:

1. Evitar abrir otra actualizacion de modulos.
2. Reiniciar Odoo.
3. Esperar unos segundos.
4. Ejecutar nuevamente `bash scripts/install_apps.sh`.

### Menus duplicados en website

Causa probable:

- Dos modulos crearon el mismo `website.menu`.

Solucion:

- Mantener la configuracion del menu centralizada en `iz_website`.
- Actualizar modulos con `bash scripts/install_apps.sh`.

### Errores de cedula o RUC

La localizacion ecuatoriana puede validar documentos. Para pruebas usar una cedula ecuatoriana valida, por ejemplo:

```text
1804888764
```

Para RUC, agregar `001` al final de una cedula valida.

### Productos en Odoo 18

En Odoo 18, los seeds siguen esta convencion:

- Almacenable: `type="consu"` + `is_storable=True`.
- Consumible: `type="consu"` + `is_storable=False`.
- Servicio: `type="service"`.

## Notas finales

- `.env` no se versiona.
- Usar `.env.example` como plantilla.
- No subir credenciales reales.
- Ejecutar seeds solo despues de instalar los modulos.
- Mantener la documentacion actualizada cuando cambie el sistema.
