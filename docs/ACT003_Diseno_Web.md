# Informe ACT003: Diseño del Sitio Web
**Rol:** Desarrollador Frontend
**Proyecto:** Iron Zone Gym - Odoo 18 Implementation

## 1. Arquitectura de UI Modular
A diferencia de un diseño estático, este proyecto implementa un **Motor de UI personalizado** a través del módulo `iz_website`. Esta arquitectura separa la lógica de negocio del diseño visual, permitiendo actualizaciones en caliente sin afectar la base de datos.

### Componentes Clave:
- **Iron Engine (CSS/JS):** Inyección de estilos dinámicos para **Dark Mode Global**.
- **UX Pro:** Implementación de **pulsación larga** en selectores de cantidad para mejorar la fluidez de compra.
- **Header/Footer Dinámico:** Integración total con los datos de la empresa en Odoo, eliminando información redundante.

## 2. Páginas Diseñadas
- **Inicio (/):** Foco en conversión con diseño de alto impacto.
- **Nosotros (/aboutus):** Presentación del equipo técnico de 7 ingenieros con avatares circulares y skills específicas.
- **Catálogo (/shop):** Rediseño total de tarjetas de producto y filtros en modo oscuro.

## 3. Navegación
Estructura optimizada: Logo (Home) -> Tienda -> Nosotros -> Contacto.

## 4. Evidencias (Capturas requeridas)
> *Instrucciones para el informe final:* Agregar las siguientes imágenes:
1. **[Captura de la Página de Inicio]** - Título: Vista de Usuario - Landing Page
2. **[Captura de la Página Nosotros]** - Título: Presentación del Equipo de Ingeniería
3. **[Captura del Carrito de Compras]** - Título: UX Rediseñada en Modo Oscuro
