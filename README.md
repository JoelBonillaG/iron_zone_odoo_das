# Iron Zone — Odoo 18

Gimnasio Iron Zone · Odoo 18 + PostgreSQL 15 en Docker.

## Requisitos

- Docker Desktop instalado y corriendo
- Git

## Levantar el entorno

```bash
git clone <repo-url>
cd iron_zone_odoo_das
cp .env.example .env
docker compose up -d
```

Esperar ~30 segundos y abrir: http://localhost:8069

**Primer acceso:** crear la base de datos desde el wizard con nombre `iron_zone`.

Master password (para el wizard): `admin123`

## Estructura

```
iron_zone_odoo_das/
├── docker-compose.yml      # Servicios Odoo 18 + PostgreSQL 15
├── config/
│   └── odoo.conf           # Configuración de Odoo
├── addons/                 # Módulos personalizados (vacío por ahora)
├── scripts/
│   ├── export_db.sh        # Exportar BD a backups/
│   └── import_db.sh        # Importar BD desde un .sql
└── backups/                # Archivos .sql (ignorados por git)
```

## Comandos útiles

```bash
# Detener
docker compose down

# Ver logs de Odoo
docker compose logs -f odoo

# Reiniciar solo Odoo
docker compose restart odoo

# Exportar base de datos
bash scripts/export_db.sh iron_zone

# Importar base de datos
bash scripts/import_db.sh backups/iron_zone_20250428_120000.sql iron_zone
```

## Estrategia de compartir BD con el equipo

Exportar `.sql` y compartir por Drive/WhatsApp:

1. Exportar: `bash scripts/export_db.sh iron_zone`
2. Subir el `.sql` de `backups/` al grupo (Drive, WhatsApp, etc.)
3. El compañero importa: `bash scripts/import_db.sh backups/archivo.sql iron_zone`

## Notas

- `.env` no se versiona. Cada integrante copia `.env.example` a `.env` (`cp .env.example .env`).
- Backups `.sql` no se versionan. Compartir por Drive/WhatsApp.
