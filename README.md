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

El primer seed (`00_company_config.py`) corre antes que los demás y configura la compañía (incluye logo).

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
    ├── config.py           # Conexión XML-RPC compartida
    ├── 01_customers.py     # 10 clientes
    ├── 02_products.py      # 10 productos con imágenes y stock
    ├── 03_sale_orders.py   # 10 pedidos de venta
    ├── 04_website_pages.py # Diseño CMS (Inicio, Nosotros)
    ├── IronZone.png         # Logo y fallback de imágenes
    ├── images/
    │   └── products/       # Imágenes personalizadas de productos
    └── run_seeds.sh        # Runner automatizado
    ```

    ## Automatización y Portabilidad

    Este proyecto ha sido diseñado bajo estándares de **portabilidad absoluta**. Toda la configuración, desde el logo de la empresa hasta el diseño premium del sitio web, se realiza mediante **Data Seeders (XML-RPC)**.

    ### Tareas Académicas Completadas

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

# 2) Cargar datos
bash seeds/run_seeds.sh
```

```bash
# Todos los seeds en orden
bash seeds/run_seeds.sh

# Solo uno específico
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
