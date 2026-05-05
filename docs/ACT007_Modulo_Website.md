# Informe ACT007: Módulo Website y Experiencia Digital
**Rol:** Analista de Sistemas / Desarrollador Web
**Proyecto:** Iron Zone Gym - Odoo 18 Implementation

## 1. Propósito del módulo
El módulo `iz_website` tiene como finalidad adaptar la experiencia pública del sitio web de Iron Zone a una identidad visual unificada, moderna y coherente con la marca. Su implementación se orienta a presentar información comercial, facilitar el contacto con la organización, mostrar el catálogo de servicios y productos, y mantener una navegación consistente entre las páginas principales del portal.

A diferencia de una web genérica, este módulo integra el diseño visual con datos reales de Odoo, de modo que el contenido corporativo se obtiene directamente desde la configuración de la empresa y de los módulos relacionados con ventas, comercio electrónico y pagos.

## 2. Alcance funcional
El módulo cubre las siguientes áreas funcionales:

- Rediseño visual completo del sitio público.
- Personalización del encabezado y del pie de página.
- Presentación de la página de inicio con enfoque comercial.
- Estructuración de la página "Nosotros".
- Adaptación de la página de contacto.
- Ajustes del catálogo eCommerce y ficha de producto.
- Incorporación de páginas legales y términos del servicio.
- Soporte visual para el portal de cliente, incluyendo páginas de seguridad y estados de documentos.
- Integración con el flujo de pagos de Odoo.

## 3. Estructura técnica
La solución se apoya en una arquitectura modular compuesta por tres capas principales:

### 3.1. Capa de presentación
Se implementa mediante archivos XML de vistas y una hoja de estilos centralizada.

- `website_layout.xml`: modifica la estructura base del layout.
- `website_footer.xml`: reemplaza el pie de página con información de marca y contacto.
- `website_branding_views.xml`: refuerza la identidad visual del sitio.
- `website_pages.xml`: define la página de inicio y la página "Nosotros".
- `website_sale_views.xml`: personaliza la tienda y la ficha de producto.
- `website_contact_views.xml`: estructura el formulario de contacto.
- `website_terms_views.xml`: incorpora las páginas de términos y condiciones.
- `iron_zone.css`: concentra la personalización visual, incluyendo colores, tipografía, espaciado y estilos del portal.

### 3.2. Capa de comportamiento
Se utiliza JavaScript para ajustar interacciones específicas del sitio.

- `iron_zone.js`: mejora la interacción en componentes del catálogo.
- `payment_demo_fix.js`: corrige el flujo de pago de demostración para el entorno de prueba.

### 3.3. Capa de integración
El módulo depende de funcionalidades nativas de Odoo para funcionar correctamente.

- `website` para el sitio público.
- `website_sale` para la tienda en línea.
- `account` y `payment` para la integración financiera.
- `payment_demo`, `payment_custom`, `account_payment` y `website_payment` para los flujos de cobro.

## 4. Flujo de navegación del sitio
El flujo de navegación del sitio se diseña para acompañar al visitante desde la primera impresión hasta la finalización de una acción objetivo (p. ej., compra, suscripción o contacto), privilegiando la claridad informativa y la reducción de fricción.

1. Página principal (landing). La entrada principal funciona como punto de impacto: contiene un hero con mensaje comercial y un llamado a la acción (CTA) prominente orientado a la conversión. Desde aquí el visitante puede identificar rápidamente la propuesta de valor y acceder a las secciones clave (tienda, programas, contacto).

2. Exploración del catálogo. La sección tienda presenta el catálogo de planes, servicios y productos mediante tarjetas visuales y filtros de búsqueda. El diseño facilita la comparación rápida de alternativas (precio, características, disponibilidad) y expone señales de recomendación o promociones para guiar la decisión.

3. Ficha de producto. Cada producto o plan dispone de una página de detalle que agrupa información esencial: imágenes, descripción, atributos relevantes, precio y elementos de confianza. Las llamadas a la acción (añadir al carrito, reservar, suscribirse) están visibles y enlazan con el flujo de compra o con formularios adicionales.

4. Carrito y proceso de compra. El flujo de compra permite revisar los artículos seleccionados, aplicar descuentos y elegir método de pago. El proceso integra la pasarela de pago y genera comprobantes/facturas según la configuración de Odoo; las pantallas muestran estados claros (pendiente, pagado, fallido) y opciones para soporte si es necesario.

5. Canales de contacto y soporte. Desde cualquier punto del recorrido el usuario puede acceder al formulario de contacto y a la información de la empresa (teléfono, email, ubicaciones). Estos canales están diseñados para consultas previas a la compra y para atención postventa, con formularios pre‑llenables cuando el usuario está autenticado.

6. Portal de usuario y gestión personal. Los usuarios autenticados pueden acceder al portal (historial de pedidos, facturas, métodos de pago y configuraciones de seguridad). El portal utiliza vistas optimizadas para lectura y gestión de datos sensibles, manteniendo separada la experiencia pública de la privada.

7. Referencias legales y navegación secundaria. Los enlaces a términos, políticas y la información en el footer permanecen accesibles en todas las páginas como respaldo normativo y punto de referencia para el usuario.

8. Consideraciones de usabilidad y accesibilidad. El recorrido prioriza CTAs claros, feedback visual en cada interacción, compatibilidad móvil y consistencia en la navegación (breadcrumbs, links permanentes y estructura de encabezados) para minimizar abandonos durante la conversión.

En conjunto, estas etapas configuran un flujo continuo donde cada pantalla aporta la información necesaria para avanzar o buscar ayuda, reduciendo la incertidumbre del usuario y facilitando la finalización de la acción objetivo.

## 5. Páginas principales implementadas

### 5.1. Página de inicio
La página principal funciona como la puerta de entrada al ecosistema digital. Su propósito es comunicar la propuesta de valor del gimnasio, mostrar bloques informativos, destacar programas de entrenamiento y guiar al usuario hacia la tienda o el contacto.

### 5.2. Página "Nosotros"
La sección institucional presenta la identidad del proyecto, su enfoque de servicio y su orientación hacia el entrenamiento, la comunidad y los productos complementarios.

### 5.3. Tienda eCommerce
La tienda fue adaptada para exhibir productos y membresías con una presentación más visual, incluyendo tarjetas de producto, jerarquía clara de información y una ficha de producto más coherente con el diseño general.

### 5.4. Formulario de contacto
El formulario de contacto permite que el visitante envíe consultas sobre membresías, clases, visitas o productos. Esta página enlaza la comunicación comercial con los datos oficiales de la empresa.

### 5.5. Páginas legales
Las páginas de términos y condiciones complementan la experiencia del usuario y aportan formalidad al sitio, lo cual resulta necesario para una implementación empresarial. En esta implementación la página dedicada se personaliza sobre la plantilla de términos de la aplicación de cuentas (`account.account_terms_conditions_page`) y está disponible desde varios puntos del sitio:

- En la ficha de producto, mediante el bloque de términos/compartir (`.iz-product_terms_share`), que enlaza a la página legal desde la vista del producto.
- En el proceso de compra (checkout), donde conviene colocar o mostrar un enlace a los términos antes de finalizar la transacción.
- En el footer del sitio, como enlace permanente de navegación secundaria (recomendado), de modo que el usuario pueda consultarlos desde cualquier página.

Estas ubicaciones garantizan que el usuario pueda acceder a la información legal en el momento de toma de decisión (ficha de producto), durante la compra (checkout) o como referencia permanente (footer). Para referencia técnica, la plantilla personalizada se define en `addons/iz_website/views/website_terms_views.xml`.

### 5.6. Portal de cliente
El portal presenta estilos adaptados para mejorar la lectura de información sensible, como estados de órdenes, datos de seguridad y formularios internos del usuario.

## 6. Criterios de diseño aplicados
El desarrollo visual se ejecuta bajo criterios de coherencia, contraste y legibilidad.

- Se utiliza una paleta oscura como base de la identidad visual.
- Se mantienen acentos naranjas para resaltar acciones importantes.
- Se prioriza la lectura en tarjetas, formularios y estados del portal.
- Se unifican bordes, sombras y radios para reforzar consistencia visual.
- Se mantienen espacios amplios para favorecer la comprensión del contenido.
- Se evita la dispersión visual entre páginas públicas y el portal interno.

## 7. Integración con el negocio
El módulo no se limita a una mejora estética. Su estructura apoya directamente los objetivos operativos del proyecto:

- Presenta los servicios y productos de manera comercialmente clara.
- Facilita el contacto con la empresa.
- Da soporte al proceso de venta digital.
- Refuerza la imagen corporativa de Iron Zone.
- Mejora la experiencia de usuario en páginas críticas del portal.

## 8. Relevancia para el proyecto
Esta implementación es relevante porque conecta la capa pública de la plataforma con el resto de módulos del sistema. El sitio web no actúa como un componente aislado, sino como la interfaz visible de una operación más amplia que incluye catálogo, pagos, contacto con clientes y administración del contenido institucional.

## 9. Evidencias gráficas requeridas
> **Instrucción para el informe final:** insertar las siguientes capturas con su respectivo título.

1. **[Captura de la Página de Inicio]** - Título: *Página principal del sitio Iron Zone con hero comercial y bloques de programas.*
2. **[Captura de la Sección Nosotros]** - Título: *Vista institucional del proyecto con presentación de identidad corporativa.*
3. **[Captura de la Tienda Online]** - Título: *Catálogo eCommerce con tarjetas de productos y membresías.*
4. **[Captura de la Ficha de Producto]** - Título: *Detalle de producto con descripción, acciones y estilo unificado.*
5. **[Captura del Formulario de Contacto]** - Título: *Formulario oficial de contacto con datos de empresa y envío de consultas.*
6. **[Captura del Footer Personalizado]** - Título: *Pie de página institucional con navegación y datos de contacto.*
7. **[Captura del Portal de Seguridad]** - Título: *Portal de cliente con interfaz mejorada para la administración de credenciales.*
8. **[Captura de la Vista de Términos]** - Título: *Página legal y condiciones del servicio dentro del sitio web.*

## 10. Conclusión
El módulo `iz_website` consolida la presencia digital de Iron Zone mediante una experiencia visual consistente, una navegación clara y una integración correcta con los módulos de negocio de Odoo. La solución permite presentar la información institucional y comercial de forma ordenada, mejorar la interacción del usuario y fortalecer la percepción profesional del sistema ante clientes y usuarios internos.
