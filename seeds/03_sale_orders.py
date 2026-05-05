from config import DB, PASSWORD, connect, create, search_read

ORDERS = [
    (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
    (5, 5), (6, 6), (7, 7), (8, 8), (9, 9),
]

ORDER_REF_PREFIX = "SEED03-SALE"

CUSTOMER_NAMES = [
    "Carlos Andrade",
    "María Sánchez",
    "Luis Moreira",
    "Ana Villacís",
    "Diego Paredes",
    "Sofía Castillo",
    "Andrés Flores",
    "Gabriela Torres",
    "Sebastián Ruiz",
    "Valeria Guzmán",
]

IRON_ZONE_PRODUCTS = [
    "Agua Mineral",
    "Botella Proteína Whey 1kg",
    "Clase de CrossFit",
    "Clase de Spinning",
    "Cuerda para Saltar",
    "Entrenamiento Personal",
    "Guantes de Boxeo",
    "Membresía Anual",
    "Membresía Mensual",
    "Membresía Trimestral",
]

def run():
    uid, models = connect()

    customers = search_read(uid, models, "res.partner",
                            [["name", "in", CUSTOMER_NAMES], ["customer_rank", ">", 0]], ["id", "name"])
    customers_by_name = {customer["name"]: customer for customer in customers}
    missing_customers = [name for name in CUSTOMER_NAMES if name not in customers_by_name]
    customers = [customers_by_name[name] for name in CUSTOMER_NAMES if name in customers_by_name]

    products  = search_read(uid, models, "product.product",
                            [["name", "in", IRON_ZONE_PRODUCTS], ["sale_ok", "=", True]], ["id", "name"])
    products_by_name = {product["name"]: product for product in products}
    missing_products = [name for name in IRON_ZONE_PRODUCTS if name not in products_by_name]
    products = [products_by_name[name] for name in IRON_ZONE_PRODUCTS if name in products_by_name]

    if missing_customers or missing_products:
        print("ERROR: Run 01_customers.py and 02_products.py first.")
        if missing_customers:
            print("Missing Iron Zone customers:", ", ".join(missing_customers))
        if missing_products:
            print("Missing Iron Zone products:", ", ".join(missing_products))
        return

    created_count = 0
    updated_count = 0
    for index, (ci, pi) in enumerate(ORDERS, start=1):
        customer = customers[ci]
        product = products[pi]
        ref = f"{ORDER_REF_PREFIX}-{index:02d}"

        orders = search_read(
            uid,
            models,
            "sale.order",
            [["client_order_ref", "=", ref]],
            ["id", "name", "state"],
        )
        order = orders[0] if orders else None

        if not order:
            existing_lines = search_read(
                uid,
                models,
                "sale.order.line",
                [
                    ["order_id.partner_id", "=", customer["id"]],
                    ["order_id.client_order_ref", "in", [False, ""]],
                    ["product_id", "=", product["id"]],
                ],
                ["order_id"],
            )
            if existing_lines:
                order_id = existing_lines[0]["order_id"][0]
                models.execute_kw(
                    DB,
                    uid,
                    PASSWORD,
                    "sale.order",
                    "write",
                    [[order_id], {"client_order_ref": ref}],
                )
                order = search_read(
                    uid,
                    models,
                    "sale.order",
                    [["id", "=", order_id]],
                    ["id", "name", "state"],
                )[0]
                updated_count += 1
            else:
                order_id = create(uid, models, "sale.order", {
                    "partner_id": customer["id"],
                    "client_order_ref": ref,
                })
                create(uid, models, "sale.order.line", {
                    "order_id": order_id,
                    "product_id": product["id"],
                    "product_uom_qty": 1,
                })
                order = search_read(
                    uid,
                    models,
                    "sale.order",
                    [["id", "=", order_id]],
                    ["id", "name", "state"],
                )[0]
                created_count += 1
        else:
            updated_count += 1
        
        # Confirmar algunos pedidos para que el estado sea diferente ("sale")
        if index % 2 == 0:
            if order["state"] in ("draft", "sent"):
                models.execute_kw(DB, uid, PASSWORD, "sale.order", "action_confirm", [[order["id"]]])
            state = "Confirmado"
        else:
            state = "Borrador (Presupuesto)"
            
        print(f"  Synced order: {customer['name']} -> {product['name']} | Ref: {ref} | Status: {state}")

    print(f"Done: {created_count} sale orders created, {updated_count} already synced.")

if __name__ == "__main__":
    run()
