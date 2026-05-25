# Roles y permisos

Este documento describe los roles configurados en Iron Zone, los permisos principales y los usuarios existentes en la base de demostracion.

Fuente principal:

- `addons/iz_backend_theme/data/security_groups.xml`
- `addons/iz_backend_theme/data/menu_access.xml`
- `seeds/06_employees.py`
- `seeds/01_customers.py`

## Grupos funcionales Iron Zone

| Grupo | Permisos base heredados | Uso funcional |
|---|---|---|
| Iron Zone / Administracion y Gerencia | Usuario interno, Ajustes | Administracion global, configuracion, menus tecnicos y seguridad. |
| Iron Zone / RRHH | Usuario interno, Contactos, RRHH usuario | Gestion de empleados, departamentos y datos de RRHH. |
| Iron Zone / Entrenadores | Usuario interno, Mesa de registro de eventos | Gestion operativa de eventos/clases asignadas e inscripciones relacionadas. |
| Iron Zone / Recepcion Suscripciones | Usuario interno, Contactos, Ventas todos los documentos | Atencion de clientes, ventas, ordenes y suscripciones. |
| Iron Zone / Ventas | Usuario interno, Contactos, Ventas propias | Gestion comercial y seguimiento de clientes/ordenes propias. |
| Iron Zone / Facturacion y Contabilidad | Usuario interno, Contactos, Facturacion, Contabilidad completa, Ventas todos los documentos | Facturas, pagos, confirmacion de cobros, retenciones, configuracion contable y soporte a suscripciones. |
| Iron Zone / Inventario y Operaciones | Usuario interno, Inventario usuario | Stock, productos fisicos, operaciones y ajustes de inventario. |
| Iron Zone / Marketing | Usuario interno, Contactos, Email marketing | Campanas, listas, segmentos y comunicaciones. |
| Iron Zone / Sitio web y eCommerce | Usuario interno, Contactos, Editor web, Ventas todos los documentos | Paginas web, tienda, catalogo publicado y experiencia eCommerce. |
| Iron Zone / Eventos Admin | Usuario interno, Contactos, Eventos usuario | Configuracion y administracion de eventos/clases. |

## Acceso a menus principales

| Menu | Roles con acceso |
|---|---|
| Conversaciones, Calendario, Mantenimiento, Tableros, Administracion tecnica | Administracion y Gerencia |
| Contactos | Administracion, RRHH, Recepcion Suscripciones, Ventas, Facturacion, Marketing, Sitio web, Eventos Admin |
| Ventas | Administracion, Recepcion Suscripciones, Ventas, Facturacion, Sitio web |
| Suscripciones | Administracion, Recepcion Suscripciones, Facturacion |
| Facturacion | Administracion, Facturacion |
| Sitio web / configuracion web | Administracion, Sitio web y eCommerce |
| Email marketing | Administracion, Marketing |
| Eventos | Administracion, Entrenadores, Eventos Admin |
| Inventario | Administracion, Inventario y Operaciones |
| RRHH | Administracion, RRHH |

## Reglas especiales

### Entrenadores

Los entrenadores tienen reglas especificas:

- Pueden leer y editar eventos donde `event.user_id == user.id`.
- Pueden leer, crear y editar inscripciones de sus eventos.
- No tienen permiso de eliminacion sobre eventos o inscripciones desde las reglas del modulo.

Esto se configura en `seeds/06_employees.py` mediante:

- `Iron Zone Entrenadores - Eventos`
- `Iron Zone Entrenadores - Inscripciones`
- `Iron Zone Entrenador ve solo sus eventos`
- `Iron Zone Entrenador ve solo inscritos de sus eventos`

### Portal

Los clientes portal usan `base.group_portal`.

Permisos relevantes:

- Ver su portal `/my`.
- Ver sus ordenes, facturas y suscripciones propias.
- Ver tienda y eventos publicos.
- Comprar en el portal.
- Recibir beneficios si tienen suscripcion activa, vigente y pagada.

No tienen acceso al backend administrativo.

## Usuarios internos activos

| Usuario | Login | Activo | Puesto | Modulo / grupo del sistema |
|---|---|---|---|---|
| Administrator | admin@ironzone.com | Si | Interno | Iron Zone / Administracion y Gerencia |
| Ana Torres | ana.torres@ironzone.ec | Si | Recepcionista de Suscripciones | Iron Zone / Recepcion Suscripciones |
| Andres Vega | andres.vega@ironzone.ec | Si | Tecnico de Mantenimiento | Iron Zone / Inventario y Operaciones |
| Camila Ortiz | camila.ortiz@ironzone.ec | Si | Especialista en Email Marketing | Iron Zone / Marketing |
| Carlos Mendez | carlos.mendez@ironzone.ec | Si | Instructor de CrossFit | Iron Zone / Entrenadores |
| Diego Molina | diego.molina@ironzone.ec | Si | Contador | Iron Zone / Facturacion y Contabilidad |
| Elena Castro | elena.castro@ironzone.ec | Si | Analista de Recursos Humanos | Iron Zone / RRHH |
| Gabriela Salazar | gabriela.salazar@ironzone.ec | Si | Analista de Facturacion | Iron Zone / Facturacion y Contabilidad |
| Isabel Romero | isabel.romero@ironzone.ec | Si | Editor de Sitio web y eCommerce | Iron Zone / Sitio web y eCommerce |
| Luis Herrera | luis.herrera@ironzone.ec | Si | Administrador de Suscripciones | Iron Zone / Recepcion Suscripciones |
| Mateo Ruiz | mateo.ruiz@ironzone.ec | Si | Asesor Comercial | Iron Zone / Ventas |
| Nicolas Benitez | nicolas.benitez@ironzone.ec | Si | Coordinador de Campanas | Iron Zone / Marketing |
| Paula Naranjo | paula.naranjo@ironzone.ec | Si | Coordinador de Operaciones | Iron Zone / Inventario y Operaciones |
| Ricardo Ponce | ricardo.ponce@ironzone.ec | Si | Coordinador de Eventos | Iron Zone / Eventos Admin |
| Roberto Lima | roberto.lima@ironzone.ec | Si | Coordinador de Recursos Humanos | Iron Zone / RRHH |
| Sofia Garcia | sofia.garcia@ironzone.ec | Si | Instructor de Yoga | Iron Zone / Entrenadores |
| Valentina Paredes | valentina.paredes@ironzone.ec | Si | Ejecutivo de Ventas | Iron Zone / Ventas |

## Usuarios portal activos

| Usuario | Login | Activo | Modulo / grupo del sistema |
|---|---|---|---|
| Cliente Portal 04 | pruebasjos04@gmail.com | Si | Portal |
| Cliente Portal 07 | pruebasjos07@gmail.com | Si | Portal |
| Cliente Portal 08 | pruebasjos08@gmail.com | Si | Portal |

## Usuarios inactivos o tecnicos

| Usuario | Login | Activo | Rol |
|---|---|---|---|
| OdooBot | `__system__` | No | Usuario tecnico interno |
| Portal User Template | `portaltemplate` | No | Plantilla de usuario portal |

## Matriz resumida de responsabilidades

| Rol | Clientes | Ventas | Suscripciones | Facturacion | Eventos | Inventario | Web/eCommerce | Marketing | RRHH | Ajustes |
|---|---|---|---|---|---|---|---|---|---|---|
| Administracion y Gerencia | Total | Total | Total | Total | Total | Total | Total | Total | Total | Total |
| RRHH | Lectura/gestion contactos | No principal | No | No | No | No | No | No | Total RRHH | No |
| Entrenadores | Limitado | No principal | No | No | Eventos asignados | No | No | No | No | No |
| Recepcion Suscripciones | Clientes | Total | Gestion | No principal | No | No | No | No | No | No |
| Ventas | Clientes | Ventas propias | No principal | No | No | No | No | No | No | No |
| Facturacion y Contabilidad | Clientes | Total | Gestion operativa | Total facturacion y contabilidad | No | No | No | No | No | Configuracion contable |
| Inventario y Operaciones | No principal | No | No | No | No | Stock | No | No | No | No |
| Marketing | Contactos | No principal | No | No | No | No | No principal | Total marketing | No | No |
| Sitio web y eCommerce | Contactos | Total | No principal | No | No | No | Total web/catalogo | No | No | No |
| Eventos Admin | Contactos | No principal | No | No | Total eventos | No | No | No | No | No |
| Portal | Solo datos propios | Compra propia | Suscripciones propias | Facturas propias | Eventos publicos/inscripciones propias | No | Tienda publica | No | No | No |

## Mantenimiento

Cuando se agregue un usuario:

1. Crear o actualizar el usuario en `seeds/06_employees.py` si es interno.
2. Crear o actualizar el cliente en `seeds/01_customers.py` si es portal.
3. Asignar un solo rol funcional principal salvo que exista una razon operativa clara.
4. Actualizar este documento con usuario, login, puesto y rol.

Cuando se agregue un rol:

1. Crear el grupo en `addons/iz_backend_theme/data/security_groups.xml`.
2. Definir menus en `addons/iz_backend_theme/data/menu_access.xml`.
3. Definir accesos/modelos/reglas en seeds o security XML/CSV.
4. Documentar permisos y usuarios afectados aqui.
