# Informe ACT008: Email Marketing, Automatización y Portal del Socio
**Rol:** Analista de Sistemas / Desarrollador Back-End
**Proyecto:** Iron Zone Gym - Odoo 18 Implementation

## 1. Propósito de las funcionalidades
La implementación en el módulo `iz_website` tiene como finalidad optimizar y automatizar los flujos de comunicación transaccional y fidelización (Email Marketing) en conjunto con una experiencia integrada en el Portal de Usuario de Iron Zone. 

Su desarrollo busca capturar de forma ordenada las características de perfil de los socios (género, fecha de nacimiento, objetivo fitness y nivel de experiencia) desde el momento del registro y permitir su actualización dinámica desde su cuenta personal, automatizando al mismo tiempo la segmentación en listas de mercadeo y la asignación de etiquetas internas dentro del módulo de Odoo Contactos.

---

## 2. Alcance funcional
Las mejoras y automatizaciones implementadas cubren las siguientes áreas clave:

* **Formulario de Registro Público (`/web/signup`):** Integración de campos de perfil esenciales quitando opciones ambiguas (como "Otro" en género) para mantener una base de datos de socios estructurada y limpia.
* **Portal del Socio (`/my/account`):** Redistribución visualmente balanceada y estética de los campos personalizados (`iz_*`) colocados estratégicamente a lo ancho de la vista de detalles. El campo **Fecha de Nacimiento** se configuró en modo de solo lectura (sombreado en gris y bloqueado contra modificaciones) para asegurar la consistencia legal y de auditoría de los datos sensibles una vez registrados.
* **Limpieza de Segmentos de Correo (Mass Mailing):** Automatización a nivel de base de datos que detecta cuando un socio edita sus datos en el portal y elimina físicamente (`unlink`) sus suscripciones a listas previas (evitando duplicidades de envío).
* **Sincronización de Etiquetas de Odoo (`res.partner.category`):** Creación e invalidación automática de etiquetas del contacto en Odoo (con formatos claros tipo `Género: Masculino`, `Objetivo: Masa muscular`, `Nivel: Avanzado`) para facilitar filtros de administración rápidos en Odoo Contactos.
* **Diseño e Integración Premium de Plantillas Transaccionales (14 correos):** Rediseño estético completo de las plantillas transaccionales de email en Odoo, implementando textos altamente motivadores inspirados en superación física y deportiva.
* **Unificación de Bloque de Cumpleaños:** Fusión de los dos cuadros condicionales separados (el banner superior de alerta y el cuadro de beneficio en el cuerpo) en un único, espectacular y consistente bloque de felicitación de bienvenida que se activa dinámicamente si el registro coincide con el día de cumpleaños local del socio.
* **Solución Permanente de Visibilidad del Logo (CDN Público):** Reemplazo de todas las rutas locales e inyecciones dinámicas de imágenes por un CDN público permanente y de alta velocidad (`https://files.catbox.moe/agiuc9.png`) para el logotipo de Iron Zone. Esto resuelve el bloqueo de los servidores proxy de Gmail al intentar cargar recursos de `localhost`, permitiendo que el logo se renderice de forma impecable en cualquier bandeja de correo real.
* **Bypass Seguro SMTP de Gmail:** Unificación del remitente en las plantillas hacia el dominio corporativo seguro de Odoo (`contacto@ironzone.ec`) mediante parámetros dinámicos, garantizando entregas SMTP sin bloqueos de red o errores de SPF/DKIM al enviar correos masivos.
* **Enlaces Web Verídicos e Interactivos:** Cada botón de acción en los correos está enlazado directamente a rutas reales y eventos activos que existen en la base de datos de Iron Zone (ej. HIIT Entrenamiento, Musculación Personalizada, Pilates Avanzado, Yoga Principiantes, etc.), de modo que el socio puede agendar su beneficio con un solo clic.

---

## 3. Estructura técnica y Archivos del Módulo
La solución se integra en la estructura técnica del módulo `iz_website` de la siguiente manera:

* [res_partner.py](../addons/iz_website/models/res_partner.py): Aloja la lógica de negocio, triggers y métodos de sincronización de datos:
  * `create()` y `write()`: Detectan cambios de perfil en tiempo real.
  * `_iz_assign_to_segment_lists()`: Suscribe al socio a las listas correctas y remueve de forma física las suscripciones inactivas previas.
  * `_iz_sync_partner_tags()`: Sincroniza dinámicamente las etiquetas de Odoo Contactos y depura las etiquetas antiguas en tiempo real.
  * `_iz_send_welcome_if_needed()`: Gestiona el envío inmediato del correo de bienvenida y el trigger de cumpleaños si la fecha coincide con el día de hoy.
* [portal_templates.xml](../addons/iz_website/views/portal_templates.xml): Hereda la vista `portal.portal_my_details_fields` para reubicar de forma elegante los campos personalizados e implementar el bloqueo visual de la fecha de nacimiento.
* [website_signup_views.xml](../addons/iz_website/views/website_signup_views.xml): Remueve las opciones no requeridas del género y asegura la captura de la información durante el autoregistro.
* [email_templates.xml](../addons/iz_website/data/email_templates.xml): Contiene las 14 plantillas transaccionales reestructuradas (Bienvenida, Portal, Cumpleaños, Día de la Mujer, Día del Hombre, Objetivos, Niveles, Vencimiento, etc.), con variables Jinja que resuelven dinámicamente el remitente, el logo de CDN público, los datos del usuario y los botones con enlaces absolutos a los eventos reales.
* [mass_mailing.xml](../addons/iz_website/data/mass_mailing.xml): Registra las campañas demo interactivas para que el administrador visualice, edite y envíe correos promocionales con un diseño premium adaptado (como el Reto Iron Burn) desde el módulo de envíos masivos.

---

## 4. Guía de Uso y Configuración para el Administrador

### 4.1. Visualización y Gestión de Plantillas de Email
Para revisar o modificar manualmente las plantillas transaccionales predefinidas de Iron Zone:
1. Inicie sesión en Odoo como Administrador.
2. Vaya a **Ajustes** y active el **Modo de Desarrollador** en la parte inferior.
3. Navegue a **Ajustes -> Técnico -> Correo electrónico -> Plantillas** (o busque "Plantillas de email").
4. Busque por el término `IZ` en la barra de búsqueda. Verá el listado completo de plantillas configuradas (ej. *IZ Bienvenida*, *IZ Cumpleaños*, *IZ Día de la Mujer*, *IZ Campaña – Masa muscular*, etc.).
5. Al abrir cualquiera de ellas, podrá visualizar de forma limpia el diseño premium neón con los llamados a la acción y verificar que los remitentes utilicen el formato dinámico corporativo seguro.

### 4.2. Administración de Listas de Correo y Segmentos
El sistema automatiza por completo la segmentación sin que el administrador tenga que intervenir de forma manual:
1. Acceda a la aplicación de **Email Marketing**.
2. Vaya al menú **Listas de Correo -> Listas de Correo**.
3. Verá las listas preconfiguradas: *Iron Zone – Clientes*, *Iron Zone – Hombres*, *Iron Zone – Mujeres*, y las correspondientes a cada objetivo fitness y nivel.
4. Al hacer clic en cualquiera de ellas y revisar los **Contactos**, comprobará que cuando un socio cambia de perfil (por ejemplo, actualiza su nivel de Principiante a Avanzado), Odoo lo remueve automáticamente de la lista anterior y lo suscribe a la nueva.

### 4.3. Sincronización e Identificación en Odoo Contactos
Para identificar rápidamente a los socios de acuerdo a sus perfiles:
1. Navegue a la aplicación de **Contactos**.
2. Abra la ficha de cualquier socio registrado.
3. En el campo **Etiquetas**, observará las clasificaciones automáticas asignadas en tiempo real (ej. `Género: Femenino`, `Nivel: Avanzado`, `Objetivo: Masa muscular`).
4. Si realiza búsquedas o aplica filtros agrupados por etiqueta, podrá organizar campañas físicas o llamadas comerciales de forma inmediata.

### 4.4. Guía Interactiva para Pruebas de Campañas y Correos Transaccionales (Bajo Demanda)
Para facilitar la verificación unitaria de cada una de las 14 plantillas de correos transaccionales y de marketing de Iron Zone sin realizar envíos masivos, se ha desarrollado un script interactivo en la carpeta de herramientas:
* **Archivo de Pruebas**: [test_marketing_emails.py](../scripts/test_marketing_emails.py)

#### Flujo de Ejecución de Pruebas:
1. Configura la dirección de correo de destino real en tu archivo `.env` local editando la variable `TEST_EMAIL` (por defecto configurada a `ejemplo@ironzone.com`). Esto evita tener direcciones fijas en el código y permite a cada desarrollador del equipo usar su propio correo.
2. Abre el archivo `scripts/test_marketing_emails.py` en tu editor de código y edita la variable `TEMPLATE_TO_TEST` en la línea 19 con el identificador de la campaña que desees validar (por ejemplo, coloca `'womens_day'` para el Día de la Mujer, o `'welcome_birthday'` para probar el nuevo bloque de cumpleaños unificado).
3. Guarda el archivo y ejecuta la herramienta de ejecución rápida de PowerShell desde la raíz de tu proyecto para despachar el correo automáticamente:
   ```powershell
   .\scripts\run_test.ps1
   ```

El script se encargará automáticamente de:
1. Buscar o crear tu socio de prueba en la base de datos de Odoo.
2. Actualizar el perfil del socio (por ejemplo, cambiar su género a `female` si elegiste `'womens_day'`, o cambiar su fecha de cumpleaños a la fecha de hoy si elegiste `'welcome_birthday'`).
3. Recuperar la plantilla de correo específica de Odoo.
4. Generar el correo renderizado con el logotipo cargado desde el CDN público y despacharlo en tiempo real a tu bandeja de correo de Gmail mediante el motor SMTP de Odoo.

---

## 5. Criterios de Calidad y Robustez Aplicados
* **Integridad del Negocio:** Los campos sensibles como la fecha de nacimiento quedan protegidos para evitar fraude de edad o alteración de registros.
* **Optimización de Recursos (Base de Datos):** La remoción física de suscripciones antiguas evita la acumulación de registros huérfanos o redundantes en la tabla `mailing.subscription`.
* **Seguridad de Repositorio:** Se eliminaron todas las referencias a correos electrónicos privados o credenciales quemadas, dejando únicamente expresiones dinámicas.

---

## 6. Evidencias de Funcionamiento Requeridas
> **Instrucción para el informe de entrega:** anexar las siguientes capturas demostrativas del funcionamiento correcto del flujo:
> 
> 1. **[Captura del Perfil del Socio con Bloqueo de Nacimiento]** - Título: *Vista de Mi Cuenta en el Portal con campos personalizados distribuidos y Fecha de Nacimiento en gris y bloqueada.*
> 2. **[Captura del Listado de Plantillas en Ajustes Técnico]** - Título: *Administrador de Odoo visualizando el listado de plantillas transaccionales de Iron Zone.*
> 3. **[Captura de la Ficha de un Contacto con Etiquetas Dinámicas]** - Título: *Ficha de socio en Odoo Contactos mostrando etiquetas sincronizadas automáticamente de género, nivel y objetivo.*
> 4. **[Captura del Correo de Campaña del Reto Iron Burn]** - Título: *Visualización del correo promocional Reto Iron Burn con su botón interactivo directo enlazado al evento de HIIT.*
