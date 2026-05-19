# Iron Zone — Odoo 18

Gimnasio Iron Zone · Odoo 18 + PostgreSQL 15 en Docker.

## Requisitos

- Docker Desktop instalado y corriendo
- Git
- Python 3 instalado

## Levantar el entorno

```bash
git clone <repo-url>
cd iron_zone_odoo_das
cp .env.example .env
docker compose up -d
```

Esperar ~30 segundos y abrir: http://localhost:8069

## Configuración inicial (una sola vez)

**Paso 1 — Crear la base de datos** en el wizard de `localhost:8069`:

| Campo           | Valor                             |
|-----------------|-----------------------------------|
| Master Password | `admin123`                        |
| Database Name   | `iron_zone`                       |
| Email           | `admin@ironzone.com`              |
| Password        | `admin123`                        |
| Phone           | `032000000` (opcional)            |
| Language        | Spanish (Latin America)           |
| Country         | Ecuador                           |
| Demo Data       | desactivado                       |

---
## Módulo implementado: Automatización

Se agregó una automatización para preparar Odoo más rápido:

- `scripts/install_apps.sh`: instala los módulos base en la base `iron_zone`.
- `seeds/00_company_config.py`: configura la compañía (logo `seeds/IronZone.png` y moneda USD) antes de cargar datos.
- `seeds/00_smtp_config.py`: configura el servidor SMTP saliente (Correo) en Odoo usando variables del `.env`.

Orden de seeds recomendado:
1. Company config (empresa)
2. SMTP config (correo)
3. Seeds (datos)
---

**Paso 2 — Instalar aplicaciones base:**

Este proyecto incluye un instalador por consola que ejecuta Odoo dentro del contenedor para **instalar los módulos base** en la BD (equivale a instalarlos manualmente desde Apps, pero automatizado).

Desde la raíz del repo:

```bash
bash scripts/install_apps.sh
```

Qué hace:
- Instala un conjunto de módulos base (ventas, inventario, facturación, website, etc.) en la base `iron_zone`.
- Reinicia el contenedor de Odoo al finalizar.

Aplicaciones que deben quedar instaladas (Apps):
- Ventas
- Inventario
- Facturación / Contabilidad
- Sitio web
- eCommerce (Website Sale)
- Empleados (HR)
- Email Marketing (Mass Mailing)
- Citas (Appointments)

Módulos técnicos que instala el script (Odoo modules):
`website, website_sale, account, hr, mass_mailing, appointment, sale_management, stock`

> Si prefieres hacerlo manualmente, puedes instalar apps desde `localhost:8069/odoo/apps`, pero para que los seeds funcionen correctamente se recomienda usar el script.

---

**Paso 3 — Cargar datos de prueba:**

Primero instala apps (Paso 2). Luego ejecuta los seeds:

```bash
bash seeds/run_seeds.sh
```

Los seeds se ejecutan en este orden:

1) `00_company_config.py` (configura compañía)

2) `00_smtp_config.py` (configura SMTP saliente desde el `.env`)

3) Seeds de datos (clientes, productos, ventas, ...)

Si quieres probar solo el SMTP (recomendado para validar primero), ejecuta:

```bash
# 1) Empresa
bash seeds/run_seeds.sh 00_company_config

# 2) SMTP (carga .env automáticamente dentro del runner)
bash seeds/run_seeds.sh 00_smtp_config
```

### Verificar SMTP en Odoo

1) Entra a Odoo y activa **Modo desarrollador**

2) Ve a:
`Ajustes → Técnico → Correo electrónico → Correo → Correo saliente`

3) Debe aparecer el servidor: **Iron Zone SMTP**

4) Abre el registro y usa el botón **Probar conexión** para validar credenciales/conectividad.

---

## Credenciales

| Servicio     | Campo           | Valor                              |
|--------------|-----------------|------------------------------------|
| Odoo wizard  | Master Password | `admin123`                         |
| Odoo         | Email           | `admin@ironzone.com`               |
| Odoo         | Password        | `admin123`                         |
| PostgreSQL   | Usuario         | `odoo`                             |
| PostgreSQL   | Password        | `odoo`                             |
| PostgreSQL   | Base de datos   | `iron_zone`                        |

## Configuración de Pagos (Stripe Sandbox)

El proyecto incluye la automatización completa para integrar Stripe como pasarela de pago en modo de pruebas.

1. Asegúrate de colocar tus credenciales de Stripe (Sandbox) en el archivo `.env`:
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_SECRET_KEY`

2. Para recibir notificaciones de pago (Webhooks), el archivo `docker-compose.yml` incluye un contenedor del **Stripe CLI** que se conecta automáticamente a tu cuenta y redirige los eventos a Odoo. 

   Para obtener tu secreto de webhook:
   ```bash
   # 1. Levanta los servicios (incluyendo Stripe CLI)
   docker compose up -d
   
   # 2. Revisa los logs del contenedor para obtener el secreto (empieza con whsec_)
   docker logs iron_zone_stripe
   ```
   Copia el valor obtenido y pégalo en la variable `STRIPE_WEBHOOK_SECRET` de tu archivo `.env`.

3. Ejecuta el seed de proveedores de pago para que Odoo recoja las credenciales:
   ```bash
   bash seeds/run_seeds.sh 00_payment_providers
   ```

## Archivos de configuración

El proyecto tiene dos archivos de configuración con propósitos distintos — no confundirlos:

### `config/odoo.conf` — configuración del servidor Docker
Controla cómo arranca Odoo dentro del contenedor. **No tocar.**
```ini
admin_passwd = admin123   # Master Password del wizard (paso 1)
db_host = db              # nombre interno del contenedor PostgreSQL
db_user = odoo            # usuario de PostgreSQL (definido en .env)
```

### `seeds/config.py` — configuración de los scripts de datos
Contiene las credenciales que los scripts usan para conectarse a Odoo vía XML-RPC.
**Deben coincidir exactamente con lo que pusiste en el wizard (paso 1).**
```python
USERNAME = "admin@ironzone.com"  # email del wizard
PASSWORD = "admin123"            # password del wizard
```
> Si usaste credenciales diferentes en el wizard, edita `seeds/config.py` antes de correr los seeds.

## Estructura

```
iron_zone_odoo_das/
├── docker-compose.yml      # Servicios Odoo 18 + PostgreSQL 15
├── .env.example            # Variables de entorno de ejemplo
├── scripts/
│   └── install_apps.sh      # Instala módulos base en Odoo (Docker)
├── config/
│   └── odoo.conf           # Configuración de Odoo
├── addons/                 # Módulos personalizados
└── seeds/
    ├── 00_company_config.py # Configura compañía + logo
    ├── 00_smtp_config.py    # Configura SMTP saliente (ir.mail_server)
    ├── config.py           # Conexión XML-RPC compartida
    ├── 01_customers.py     # 10 clientes
    ├── 02_products.py      # 10 productos con imágenes y stock
    ├── 03_sale_orders.py   # 10 pedidos de venta
    ├── IronZone.png         # Logo y fallback de imágenes
    ├── images/
    │   └── products/       # Imágenes personalizadas de productos
    └── run_seeds.sh        # Runner automatizado
    ```

    ### Tareas Completadas

    - **ACT003 (Desarrollador Frontend):** Diseño CMS profesional en modo oscuro. Documentación en `docs/ACT003_Diseno_Web.md`.
    
    - **ACT004 (Especialista de Producto):** Catálogo con iconos SVG y gestión de stock. Documentación en `docs/ACT004_Inventario_Ecommerce.md`.
    
    ## Arquitectura Técnica: Roles, REST y Auditoría

    Para cumplir con los requerimientos de ingeniería de software de 7mo semestre:

    1.  **Gestión de Roles (RBAC):** Odoo utiliza Grupos de Seguridad (`res.groups`). Los permisos se definen por modelo (`ir.model.access`) y registros (`ir.rule`).
    2.  **Interfaz RESTful / XML-RPC:** El sistema expone todos los recursos mediante el protocolo XML-RPC (o JSON-RPC), permitiendo operaciones CRUD completas que respetan la lógica de negocio y los permisos del usuario.
    3.  **Auditoría y Trazabilidad:** Cada cambio en los recursos críticos (Productos, Pedidos) es auditado automáticamente por el "Chatter" de Odoo (`mail.message`), registrando quién, cuándo y qué se modificó.

    ---
    ## Guía de Navegación UI


Con Odoo corriendo y la BD creada:

Orden recomendado:

```bash
# 1) Instalar apps base
bash scripts/install_apps.sh

# 2) Cargar seeds (empresa → smtp → datos)
bash seeds/run_seeds.sh
```

```bash
# Todos los seeds en orden
bash seeds/run_seeds.sh

# Solo uno específico
bash seeds/run_seeds.sh 00_smtp_config
bash seeds/run_seeds.sh 01_customers
bash seeds/run_seeds.sh 02_products
bash seeds/run_seeds.sh 03_sale_orders
```

> Los seeds usan XML-RPC — no requieren dependencias extra, solo Python 3.
---

## Guía de Navegación UI

Para validar los datos cargados y cumplir con las entregas, utiliza las siguientes rutas en Odoo:

### 1. Inventario y Catálogo (ACT004)
*   **Catálogo Backend:** `Ventas` → `Productos` → `Productos`
    *   *Ruta:* `/odoo/action-sale.product_template_action`
*   **Tienda Online (Vista Cliente):** Menú principal → `Sitio Web` → `Tienda`
    *   *Ruta:* `/shop`
*   **Stock:** `Inventario` → `Productos` → `Productos` (Ver columna "A mano")

### 2. Diseño Web y CMS (ACT003)
*   **Inicio:** `/`
*   **Nosotros:** `/aboutus`
*   **Contacto:** `/contactus`
*   **Editor de Páginas:** En cualquier página del sitio, botón **"Editar"** (arriba a la derecha).

### 3. Ventas y Clientes
*   **Clientes:** `Contactos` o `Ventas` → `Pedidos` → `Clientes`
*   **Pedidos:** `Ventas` → `Pedidos` → `Pedidos`

### Nota Técnica: Validaciones de Cédula y RUC (Ecuador)

Debido a que el proyecto cuenta con la localización Ecuatoriana instalada (`l10n_ec`), **el sistema valida matemáticamente la autenticidad del documento de identidad**. Si intentas realizar una compra de prueba en la tienda online o registrar un nuevo cliente con una cédula inventada, el sistema arrojará un error y no te permitirá continuar (en la web se puede presentar como `400 Bad Request` en consola). 

> Para tus pruebas, asegúrate de utilizar una cédula ecuatoriana matemáticamente válida (por ejemplo: `1804888764`). Para RUC, agrega `001` al final de una cédula válida.

---
### Nota Técnica: Tipos de Productos (Odoo 18)

En Odoo 18, el manejo de tipos de productos cambió ligeramente. Los seeds siguen esta convención:
- **Almacenables (Storable):** `type="consu"` + `is_storable=True`.
- **Consumibles:** `type="consu"` + `is_storable=False`.
- **Servicios:** `type="service"`.

---


## Acceder al contenedor de PostgreSQL

```bash
docker exec -it iron_zone_db psql -U odoo -d iron_zone

# Comandos útiles dentro de psql
\dt                                         -- listar tablas
SELECT name FROM res_partner LIMIT 10;     -- ver clientes
SELECT name FROM product_template LIMIT 10; -- ver productos
\q                                          -- salir
```

## Comandos útiles

```bash
# Detener
docker compose down

# Ver logs de Odoo
docker compose logs -f odoo

# Reiniciar Odoo
docker restart iron_zone_odoo
```

## Notas

- `.env` no se versiona. Copiar `.env.example` a `.env` antes de levantar.
- Database Name en el wizard: `iron_zone`
