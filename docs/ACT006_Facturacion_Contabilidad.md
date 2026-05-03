# Informe ACT006: Suscripciones y Pagos Recurrentes
**Rol:** Analista Financiero
**Proyecto:** Iron Zone Gym - Odoo 18 Implementation

## 1. Automatizacion Financiera
Se implemento el seed `seeds/04_accounting_invoices.py` para reproducir el flujo financiero sobre cualquier despliegue local de la base `iron_zone`.

El script crea 10 pedidos de membresia identificados con la referencia `ACT006-MEMBERSHIP-01` a `ACT006-MEMBERSHIP-10`, asociando socios existentes con los productos de membresia del catalogo. Luego confirma los pedidos, genera las facturas, las publica y registra el cobro de 5 facturas para evidenciar el estado "Pagado".

Como Odoo Community no incluye un modulo de suscripciones recurrentes completo por defecto, el flujo se modela mediante pedidos de venta de membresias con referencia de contrato ACT006, lo cual cumple la alternativa indicada en la consigna: "pedidos de venta o contratos de suscripcion".

## 2. Flujo Ejecutado
- Verificacion del impuesto de ventas IVA 15%.
- Verificacion del diario de ventas y del diario de banco/caja.
- Creacion o reutilizacion de 10 pedidos de membresia ACT006.
- Confirmacion de los 10 pedidos de membresia.
- Generacion de facturas desde los pedidos de membresia.
- Publicacion de facturas contables.
- Registro de pagos para 5 de 10 facturas.

## 3. Comando de Ejecucion
Desde la raiz del proyecto:

```bash
python seeds/04_accounting_invoices.py
```

Tambien se puede ejecutar como parte del flujo completo:

```bash
bash seeds/run_seeds.sh
```

## 4. Evidencias (Capturas requeridas)
> Instrucciones para el informe final: Agregar las siguientes imagenes:
1. **[Captura de Pedidos ACT006]** - Titulo: 10 pedidos de membresia con referencia `ACT006-MEMBERSHIP`.
2. **[Captura de Pedido Confirmado]** - Titulo: Pedido de membresia confirmado y asociado a un socio.
3. **[Captura de Facturas]** - Titulo: Facturas generadas desde pedidos de membresia.
4. **[Captura de Estado Pagado]** - Titulo: 5 facturas con estado de pago "Pagado".
