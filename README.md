# Iron Zone — Gestión integral de gimnasio sobre Odoo 18

Iron Zone es una solución empresarial para la gestión de un **gimnasio y centro deportivo**, construida sobre **Odoo 18** y **PostgreSQL 15** con **Docker**. Integra el sitio web público, la tienda online, las suscripciones y planes, las clases/eventos, las guías de ejercicios, el inventario, las ventas, la facturación y la localización ecuatoriana (SRI) en un único producto desplegable.

> Reúne módulos nativos de Odoo y varios addons personalizados ubicados en `addons/`.

---

## Tabla de contenidos

- [Propósito y problema que resuelve](#propósito-y-problema-que-resuelve)
- [Módulos principales](#módulos-principales)
- [Flujo funcional principal](#flujo-funcional-principal)
- [Roles / actores](#roles--actores)
- [Entidades principales del dominio](#entidades-principales-del-dominio)
- [Tecnologías usadas](#tecnologías-usadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración inicial en Odoo](#configuración-inicial-en-odoo)
- [Instalación de módulos](#instalación-de-módulos)
- [Carga de datos de prueba (seeds)](#carga-de-datos-de-prueba-seeds)
- [Credenciales de prueba](#credenciales-de-prueba)
- [Rutas principales](#rutas-principales)
- [Pagos y correo](#pagos-y-correo)
- [Pruebas](#pruebas)
- [Validación y comandos útiles](#validación-y-comandos-útiles)
- [Estado del proyecto](#estado-del-proyecto)
- [Notas para despliegue o demostración](#notas-para-despliegue-o-demostración)

---

## Propósito y problema que resuelve

Un gimnasio gestiona, normalmente con herramientas dispersas: membresías y cobros recurrentes, catálogo de productos y suplementos, reserva de clases, contenido de entrenamiento, facturación y obligaciones tributarias locales. Iron Zone **centraliza esos procesos** en una sola plataforma Odoo:

- Vende y publica **planes/membresías** y **productos** desde una tienda online.
- Gestiona **suscripciones** y facturación periódica.
- Publica **clases/eventos** y permite el registro de asistentes.
- Ofrece un catálogo de **guías de ejercicios** con permisos por rol.
- Administra **inventario, ventas y facturación** desde el backend.
- Cumple con la **facturación electrónica de Ecuador (SRI)**: comprobantes, firma, retenciones y reportes.

## Módulos principales

Addons personalizados incluidos en `addons/`:

| Módulo | Nombre en Odoo | Propósito |
| --- | --- | --- |
| `iz_website` | IZ Website | Personalización del sitio web, plantillas, footer, pasarela visual, correo y experiencia de usuario. |
| `iz_backend_theme` | IZ Backend Theme | Tema moderno y ajustes internos para el backend de Iron Zone. |
| `iz_subscription` | Iron Zone - Suscripciones | Suscripciones, productos recurrentes y facturación periódica. |
| `iz_inventory` | IZ Inventory | Convenciones de inventario y stock para la tienda eCommerce. |
| `iz_tasks` | Gestión de Tareas Iron Zone | Gestión y asignación de tareas con dashboard. |
| `ironzone_exercise_guide` | Iron Zone - Guías de Ejercicios | Guías de ejercicios, máquinas, categorías, portal y permisos por rol. |
| `l10n_ec_base` | Ecuador - Base Localization (NEC 2026) | Plan de cuentas, plantillas de impuestos y validación de identidad (SRI). |
| `l10n_ec_edi` | Ecuador - Electronic Invoicing (SRI 2026) | Facturación electrónica, firma XAdES-BES y transmisión al SRI. |
| `l10n_ec_sri` | Ecuador SRI Electronic Invoicing | Cumplimiento completo de facturación electrónica SRI (2025-2026). |
| `l10n_ec_withholding` | Ecuador - Withholding (Retenciones) | Retenciones en facturas de proveedor, autorización SRI, regla de 5 días. |
| `l10n_ec_reports` | Ecuador - Reports (ATS, Form 104) | Generación del XML del ATS (Anexo Transaccional Simplificado). |

Además, el proyecto se apoya en módulos nativos de Odoo: `website`, `website_sale`, `website_sale_stock`, `account`, `account_payment`, `sale_management`, `stock`, `purchase`, `event`, `website_event`, `hr`, `mass_mailing`, `appointment`, `calendar`, `payment_stripe`, `l10n_ec`, entre otros (ver `scripts/install_apps.sh`).

## Flujo funcional principal

1. Un **visitante** entra al sitio web público y navega por inicio, tienda, eventos y guías de ejercicios.
2. Consulta **planes/membresías** y **productos**, y puede comprarlos o suscribirse desde la tienda (`/shop`).
3. La compra/suscripción genera una **orden de venta** y, según configuración, su **facturación periódica**.
4. El sistema emite la **factura** y, con la localización ecuatoriana, el **comprobante electrónico (SRI)**.
5. El **cliente portal** consulta sus pedidos, facturas, suscripciones y accesos en `/my`.
6. **Entrenadores** y **administradores** gestionan desde el backend las guías, clases/eventos, inventario y facturación.
7. Los procesos de **email marketing** y correos transaccionales acompañan el ciclo de vida del cliente.

## Roles / actores

| Rol | Descripción |
| --- | --- |
| Visitante | Navega contenido público: tienda, eventos y guías publicadas. |
| Cliente portal | Usuario registrado; consulta pedidos, facturas, suscripciones y accesos. |
| Entrenador | Gestiona sus guías de ejercicios y consulta el portal como usuario final. |
| Administrador | Administra aplicaciones, ventas, inventario, facturación, eventos, suscripciones y guías. |

## Entidades principales del dominio

- **Producto / Plan / Membresía** — catálogo de la tienda y suscripciones.
- **Suscripción** — relación recurrente con facturación periódica.
- **Evento / Clase** — actividades deportivas con registro de asistentes e instructores.
- **Guía de ejercicio** — contenido con tipo, dificultad, grupo muscular y máquina asociada.
- **Máquina / Categoría** — recursos del gimnasio relacionados con las guías.
- **Cliente (res.partner)** — contactos y clientes del portal.
- **Empleado / Entrenador (hr.employee)** — equipo del gimnasio.
- **Orden de venta / Factura** — flujo comercial y contable.
- **Comprobante electrónico / Retención (SRI)** — documentos de la localización ecuatoriana.

## Tecnologías usadas

- **Odoo 18** (Python, framework ORM, QWeb, controladores web).
- **PostgreSQL 15** como base de datos.
- **Docker / Docker Compose** para el despliegue local.
- **XML-RPC** para los seeds de datos de prueba.
- **Stripe CLI** (opcional) para probar pagos en sandbox.
- **Node.js + Playwright/Stagehand** para pruebas E2E (carpeta `pruebas_e2e`).
- **GitHub Actions** para validación de manifests, XML y sintaxis (CI).

## Estructura del proyecto

```text
iron_zone_odoo_das/
  addons/                      # Módulos personalizados de Iron Zone y localización EC
    ironzone_exercise_guide/
    iz_backend_theme/
    iz_inventory/
    iz_subscription/
    iz_tasks/
    iz_website/
    l10n_ec_base/
    l10n_ec_edi/
    l10n_ec_reports/
    l10n_ec_sri/
    l10n_ec_withholding/
  config/
    odoo.conf                  # Configuración de Odoo
  scripts/                     # Instalación, reset de BD y utilidades de correo
  seeds/                       # Datos de prueba (XML-RPC) e imágenes asociadas
    images/
    run_seeds.sh
  pruebas_e2e/                 # Pruebas E2E locales (Node.js + Playwright/Stagehand)
  .github/                     # Workflows de CI/CD y validador del repo
  docker-compose.yml
  .env.example
  README.md
```

## Requisitos previos

- **Docker Desktop** instalado y en ejecución.
- **Git**.
- **Python 3** (para ejecutar los seeds).
- **Bash** disponible para los scripts.
- **Node.js 20+** (opcional, solo para las pruebas E2E de `pruebas_e2e`).

## Instalación

```bash
git clone <repo-url>
cd iron_zone_odoo_das
cp .env.example .env
docker compose up -d
```

Abrir `http://localhost:8069` y esperar ~30 segundos tras levantar los contenedores.

## Configuración inicial en Odoo

Crear la base de datos desde el wizard de Odoo en `localhost:8069`:

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

> Estos valores son los esperados por los scripts (`DB_NAME=iron_zone`). Si cambias el nombre de la base, ajusta las variables al ejecutar los scripts.

## Instalación de módulos

Tras crear la base de datos:

```bash
bash scripts/install_apps.sh
```

El script instala y actualiza los módulos base y personalizados en la base `iron_zone` (lista completa en `scripts/install_apps.sh`).

## Carga de datos de prueba (seeds)

Los seeds usan **XML-RPC** para poblar la instancia. Ejecutar todos:

```bash
bash seeds/run_seeds.sh
```

Ejecutar uno específico:

```bash
bash seeds/run_seeds.sh 10_exercise_guides
```

Orden general: configuración de empresa y SMTP → plantillas de correo → clientes → suscripciones → productos → ventas → facturación → empleados/entrenadores → eventos → email marketing → guías de ejercicios.

> Ejecuta los seeds **solo después** de instalar los módulos.

## Credenciales de prueba

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Administrador | `admin` | `admin` |
| Administrador alterno | `admin@ironzone.com` | `admin123` |
| Entrenador | `carlos.mendez@ironzone.ec` | `admin123` |
| Entrenador | `sofia.garcia@ironzone.ec` | `admin123` |
| Cliente portal | `pruebasjos04@gmail.com` | `admin123` |
| PostgreSQL | `odoo` | `odoo` |

> Credenciales de demostración local. No usar en producción.

## Rutas principales

| Ruta | Descripción |
| --- | --- |
| `/` | Inicio del sitio web |
| `/shop` | Tienda online |
| `/event` | Eventos y clases |
| `/aboutus` | Página Nosotros |
| `/contactus` | Contacto |
| `/exercise-guides` | Catálogo de guías de ejercicios |
| `/exercise-guides/<id>` | Detalle de una guía |
| `/web/login` | Inicio de sesión |
| `/my` | Portal de cliente |
| `/odoo` | Backend de Odoo |

## Pagos y correo

### Stripe (sandbox)

Configurar en `.env` si se desean probar pagos:

```text
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

El secreto de webhook generado por Stripe CLI puede verse con `docker logs iron_zone_stripe`. Luego ejecutar `bash seeds/run_seeds.sh 00_payment_providers`. Sin credenciales, el proveedor permanece deshabilitado.

### SMTP

Configurar en `.env` (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_ENCRYPTION`) y ejecutar `bash seeds/run_seeds.sh 00_smtp_config`. Verificar en *Ajustes → Técnico → Correo electrónico → Correo saliente*.

## Pruebas

El repositorio incluye varios niveles de validación:

- **Validación estática (CI)** — `.github/scripts/validate_repo.py` compila el Python de `addons/`, `scripts/` y `seeds/`, valida los `__manifest__.py` y parsea todos los XML. Se ejecuta automáticamente en GitHub Actions y también localmente:
  ```bash
  python .github/scripts/validate_repo.py
  ```
- **Tests de Odoo** — pruebas unitarias/funcionales dentro de los addons (`iz_subscription/tests`, `l10n_ec_base/tests`, `l10n_ec_sri/tests`). Para ejecutarlas con la instancia levantada:
  ```bash
  docker compose run --rm odoo odoo -d iron_zone -u <modulo> --test-enable --stop-after-init
  ```
- **Pruebas E2E locales (UI)** — escenarios que validan la app local (`localhost:8069`) con Node.js + Playwright/Stagehand en `pruebas_e2e/`:
  ```bash
  cd pruebas_e2e
  npm ci
  npm run test:clases          # registro en clases grupales
  npm run test:guias           # navegación de guías de ejercicios
  npm run test:suscripciones   # compra/suscripción en la tienda
  ```
  > La ruta `pruebas_e2e` está fijada en el workflow de CI; no la renombres sin actualizar `.github/workflows/ci.yml`.
- **Pruebas de correo** — `scripts/run_test.ps1` (PowerShell) ejecuta `scripts/test_marketing_emails.py` dentro del contenedor de Odoo.

## Validación y comandos útiles

```bash
# Estado del repositorio
git status

# Buscar residuales antes de subir cambios
find . -type d -name "__pycache__" -not -path '*/.git/*'
find . -name "*.pyc" -not -path '*/.git/*'

# Validar sintaxis de Python (todo el repo)
python -m compileall addons scripts seeds

# Validación completa del repo (manifests + XML + Python)
python .github/scripts/validate_repo.py

# Levantar / detener / logs
docker compose up -d
docker compose down
docker compose logs -f odoo
docker restart iron_zone_odoo

# Acceso a PostgreSQL
docker exec -it iron_zone_db psql -U odoo -d iron_zone
```

## Estado del proyecto

- **Funcional / demostrable en local.** Pensado para despliegue y demostración.
- CI activo (validación de manifests, XML y sintaxis JS/Python).
- La localización ecuatoriana (SRI/EDI) cuenta con documentación extensa en `addons/l10n_ec_sri/docs/` — **requiere verificación** contra el estado real de transmisión al SRI antes de uso productivo.

## Notas para despliegue o demostración

- `.env` **no** se versiona; usa `.env.example` como plantilla y no subas credenciales reales.
- Ejecuta los seeds solo después de instalar los módulos.
- Para pruebas con la localización ecuatoriana, usa una cédula válida (ej. `1804888764`); para RUC, añade `001` al final de una cédula válida.
- Convención de productos en Odoo 18: almacenable `type="consu"` + `is_storable=True`; consumible `type="consu"` + `is_storable=False`; servicio `type="service"`.
- Si aparece `could not serialize access due to concurrent update`, evita actualizaciones simultáneas, reinicia Odoo y vuelve a ejecutar `bash scripts/install_apps.sh`.
