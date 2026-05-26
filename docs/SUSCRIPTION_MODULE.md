# Modulo de suscripciones

## Objetivo

El modulo `iz_subscription` gestiona planes, productos recurrentes, suscripciones del cliente y beneficios asociados. Su responsabilidad principal es responder:

- que plan activo y pagado tiene un cliente;
- que beneficios otorga ese plan;
- si una compra de suscripcion puede confirmarse;
- cuando una suscripcion debe activar beneficios.

La aplicacion de beneficios en otros modulos se hace con adaptadores pequenos por modulo.

## Modelos principales

| Modelo                    | Uso                                                                                                            |
| ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `iz.subscription.plan`    | Define el plan comercial, prioridad/rango, codigo, producto relacionado y beneficios.                          |
| `iz.subscription.benefit` | Define beneficios por plan: alcance (`events`, `products`, `general`), tipo (`discount`, `free`) y porcentaje. |
| `sale.subscription`       | Instancia vigente o pendiente de una suscripcion de un cliente.                                                |
| `sale.order`              | Compra inicial desde portal o backend; crea la suscripcion al confirmar.                                       |
| `sale.order.line`         | Lineas de venta. En eventos guarda beneficio aplicado, plan y descuento.                                       |
| `account.move`            | Facturas. Al quedar pagadas activan beneficios de suscripcion.                                                 |
| `res.partner`             | Motor de consulta del plan vigente y beneficios disponibles para el cliente.                                   |

## Flujo de compra y activacion

1. El cliente compra una suscripcion desde la tienda o un administrador crea/confirmar una orden.
2. `sale.order.action_confirm()` valida que el cliente no baje de rango si ya tiene un plan activo superior.
3. La orden confirmada crea una `sale.subscription` ligada a la orden.
4. La suscripcion queda pendiente/borrador hasta que exista factura pagada.
5. Cuando una factura relacionada queda pagada, `account.move` busca suscripciones vinculadas y activa la suscripcion.
6. Desde ese momento el cliente puede recibir beneficios.

## Regla de rangos

El rango se controla con `iz.subscription.plan.priority`.

- Mayor `priority` significa plan superior.
- Si el cliente tiene un plan activo y pagado, no puede comprar uno con prioridad menor.
- La validacion esta en `sale.order._check_subscription_downgrade()`.

Ejemplo actual:

| Plan             |    Codigo | Prioridad |
| ---------------- | --------: | --------: |
| IronZone Mensual |  `IZ_B01` |        10 |
| IronZone Anual   | `IZ_PR01` |        20 |

## Motor generico de beneficios

El motor generico esta en `res.partner`:

```python
partner._get_current_subscription_plan()
partner._get_current_subscription_benefits("events")
```

La primera funcion busca suscripciones activas, vigentes y con factura pagada. Si hay varias, escoge el plan de mayor prioridad.

La segunda funcion devuelve los beneficios activos del plan vigente, opcionalmente filtrados por alcance.

Alcances actuales:

| Scope      | Uso esperado                         |
| ---------- | ------------------------------------ |
| `events`   | Eventos y clases.                    |
| `products` | Productos de tienda.                 |
| `general`  | Beneficios generales o informativos. |

Tipos actuales:

| Tipo       | Uso                                                             |
| ---------- | --------------------------------------------------------------- |
| `discount` | Descuento porcentual usando `discount_percent`.                 |
| `free`     | Acceso gratis. Equivale a 100% en el adaptador correspondiente. |

## Adaptadores por modulo

El motor solo responde si el cliente tiene beneficios. Cada modulo decide como aplicarlos.

### Eventos y clases

Adaptadores actuales:

- `sale.order._cart_update_order_line()`: detecta boletos de evento (`event_ticket_id`) agregados al carrito.
- `sale.order.line._apply_subscription_event_benefit()`: pide beneficios `events` y aplica descuento en la linea.
- `event.registration._apply_subscription_benefit()`: registra en la inscripcion el plan, beneficio y precio final.
- `website_event_subscription_views.xml`: muestra el bloque "Beneficio por suscripcion" en modal, carrito y checkout.

Resultado:

- Mensual aplica 5% en clases/eventos.
- Anual aplica 100% porque su beneficio es `free`.

### Tienda / productos

El scope `products` existe como parte del motor, pero actualmente no hay adaptador activo para descuento automatico en productos fisicos. Si se necesita, debe implementarse sobre `sale.order.line` o sobre el flujo de `website_sale` revisando productos elegibles.

### General

El scope `general` se usa para beneficios informativos o futuros que no descuentan directamente una linea de venta.

## Como agregar beneficios a un modulo nuevo

1. Definir si el modulo usara un scope existente o uno nuevo.
2. Crear beneficios en `iz.subscription.benefit` para los planes aplicables.
3. En el modulo nuevo, consultar el motor:

```python
benefit = partner._get_current_subscription_benefits("events")[:1]
```

4. Aplicar la regla propia del modulo.

Ejemplo para un modulo de productos:

```python
benefit = partner._get_current_subscription_benefits("products")[:1]
if benefit:
    line.discount = 100.0 if benefit.benefit_type == "free" else benefit.discount_percent
```

Ejemplo para un modulo de reservas:

```python
benefit = partner._get_current_subscription_benefits("general")[:1]
if benefit and benefit.benefit_type == "free":
    booking.is_included_by_subscription = True
```

## Relaciones con otros modulos

| Modulo                    | Relacion                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| `website_sale`            | Publica productos de suscripcion y permite compra en portal.                                            |
| `website_event_sale`      | Vende boletos de eventos/clases; usa el adaptador de beneficios `events`.                               |
| `event`                   | Registra inscripciones y conserva trazabilidad del beneficio aplicado.                                  |
| `account`                 | Las facturas pagadas activan beneficios.                                                                |
| `sale_management`         | Ordenes de venta crean suscripciones y validan rangos.                                                  |
| `portal`                  | Muestra "Mis suscripciones" y beneficios activos al cliente.                                            |
| `iz_website`              | Presentacion visual de tienda, carrito, checkout y portal.                                              |
| `ironzone_exercise_guide` | Puede consultar suscripciones para controlar acceso a guias, pero no agrega scopes extra de beneficios. |

## Archivos clave

| Archivo                                                             | Responsabilidad                                                        |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `addons/iz_subscription/models/res_partner.py`                      | Motor de plan vigente y beneficios.                                    |
| `addons/iz_subscription/models/sale_order.py`                       | Creacion de suscripciones, validacion de downgrade y hook del carrito. |
| `addons/iz_subscription/models/sale_order_line.py`                  | Aplicacion del beneficio en lineas de evento.                          |
| `addons/iz_subscription/models/account_move.py`                     | Activacion de suscripciones al pagar facturas.                         |
| `addons/iz_subscription/models/event_registration.py`               | Trazabilidad del beneficio aplicado al registro de evento.             |
| `addons/iz_subscription/models/iz_subscription_benefit.py`          | Definicion y calculo basico de beneficios.                             |
| `addons/iz_subscription/views/website_event_subscription_views.xml` | UI del beneficio en evento/carrito/checkout.                           |
| `addons/iz_subscription/views/portal_subscription_views.xml`        | Centro de suscripciones del portal.                                    |
| `seeds/02_subscription_config.py`                                   | Planes, plantillas y beneficios base.                                  |
| `seeds/03_products.py`                                              | Productos de suscripcion y catalogo de tienda.                         |

## Estado actual del catalogo

Suscripciones publicadas:

| Producto            | Precio | Beneficio                         |
| ------------------- | -----: | --------------------------------- |
| Suscripcion Mensual |  35.00 | 5% de descuento en clases         |
| Suscripcion Anual   | 300.00 | Todas las clases incluidas gratis |

La tienda esta configurada con `shop_ppg = 10`; si hay mas de 10 productos publicados, Odoo debe paginar.
