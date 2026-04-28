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

**Paso 2 — Instalar aplicaciones** desde `localhost:8069/odoo/apps`:

- Ventas
- Inventario
- Facturación
- Sitio web

**Paso 3 — Cargar datos de prueba:**

```bash
bash seeds/run_seeds.sh
```

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
├── config/
│   └── odoo.conf           # Configuración de Odoo
├── addons/                 # Módulos personalizados
└── seeds/
    ├── config.py           # Conexión XML-RPC compartida
    ├── 01_customers.py     # 10 clientes
    ├── 02_products.py      # 10 productos y servicios
    ├── 03_sale_orders.py   # 10 pedidos de venta
    └── run_seeds.sh        # Runner
```

## Cargar datos de prueba (seeds)

Con Odoo corriendo y la BD creada:

```bash
# Todos los seeds en orden
bash seeds/run_seeds.sh

# Solo uno específico
bash seeds/run_seeds.sh 01_customers
bash seeds/run_seeds.sh 02_products
bash seeds/run_seeds.sh 03_sale_orders
```

> Los seeds usan XML-RPC — no requieren dependencias extra, solo Python 3.

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
