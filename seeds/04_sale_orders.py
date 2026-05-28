"""
04_sale_orders.py
-----------------
Seeds 20 sale orders (mix of draft and confirmed) for portal customers.
Confirmed orders automatically trigger subscription creation in draft stage.
Depends on: 01_customers.py, 02_subscription_config.py, 03_products.py
"""
from config import DB, PASSWORD, connect, create, search_read

ORDER_REF_PREFIX = "SEED04-SALE"

CUSTOMER_EMAILS = [
    "pruebasjos04@gmail.com",
    "pruebasjos07@gmail.com",
    "pruebasjos08@gmail.com",
]

IRON_ZONE_PRODUCTS = [
    "Suscripcion Mensual",
    "Suscripcion Anual",
    "Proteina Whey 2 lb",
    "Barras de proteina",
    "Camiseta IronZone",
    "Shaker IronZone",
    "Toalla deportiva",
    "Guantes de entrenamiento",
    "Bandas de resistencia",
    "Straps de levantamiento",
]

# (customer_index, product_index, confirm)
# confirm=True  → order will be confirmed → subscription created in Borrador
# confirm=False → stays as draft Presupuesto
ORDERS = [
    (0, 0, False),   # 01 Portal04 -> Mensual -> Presupuesto
    (1, 1, True),    # 02 Portal07 -> Anual -> Confirmado
    (2, 2, False),   # 03 Portal08 -> Proteina -> Presupuesto
    (0, 3, True),    # 04 Portal04 -> Barras -> Confirmado
    (1, 4, False),   # 05 Portal07 -> Camiseta -> Presupuesto
    (2, 5, True),    # 06 Portal08 -> Shaker -> Confirmado
    (0, 6, False),   # 07 Portal04 -> Toalla -> Presupuesto
    (1, 7, True),    # 08 Portal07 -> Guantes -> Confirmado
    (2, 8, False),   # 09 Portal08 -> Bandas -> Presupuesto
    (0, 9, True),    # 10 Portal04 -> Straps -> Confirmado
    (1, 0, False),   # 11 Portal07 -> Mensual -> Presupuesto
    (2, 1, True),    # 12 Portal08 -> Anual -> Confirmado
    (0, 2, False),   # 13 Portal04 -> Proteina -> Presupuesto
    (1, 3, True),    # 14 Portal07 -> Barras -> Confirmado
    (2, 4, False),   # 15 Portal08 -> Camiseta -> Presupuesto
    (0, 5, True),    # 16 Portal04 -> Shaker -> Confirmado
    (1, 6, False),   # 17 Portal07 -> Toalla -> Presupuesto
    (2, 7, True),    # 18 Portal08 -> Guantes -> Confirmado
    (0, 8, False),   # 19 Portal04 -> Bandas -> Presupuesto
    (1, 9, True),    # 20 Portal07 -> Straps -> Confirmado
]


def run():
    uid, models = connect()

    customers = search_read(
        uid, models, "res.partner",
        [["email", "in", CUSTOMER_EMAILS], ["customer_rank", ">", 0], ["active", "=", True]],
        ["id", "name", "email"],
    )
    customers_by_email = {c["email"]: c for c in customers}
    missing_customers = [e for e in CUSTOMER_EMAILS if e not in customers_by_email]
    customers = [customers_by_email[e] for e in CUSTOMER_EMAILS if e in customers_by_email]

    products = search_read(
        uid, models, "product.product",
        [["name", "in", IRON_ZONE_PRODUCTS], ["sale_ok", "=", True]],
        ["id", "name"],
    )
    products_by_name = {p["name"]: p for p in products}
    missing_products = [n for n in IRON_ZONE_PRODUCTS if n not in products_by_name]
    products = [products_by_name[n] for n in IRON_ZONE_PRODUCTS if n in products_by_name]

    if len(customers) < len(set(ci for ci, _, _ in ORDERS)) or missing_products:
        print("ERROR: Run 01_customers.py, 02_subscription_config.py and 03_products.py first.")
        if missing_customers:
            print("Missing portal customers:", ", ".join(missing_customers))
        if missing_products:
            print("Missing products:", ", ".join(missing_products))
        return

    pricelists = search_read(uid, models, "product.pricelist", [], ["id"])
    if not pricelists:
        default_pricelist_id = create(uid, models, "product.pricelist", {"name": "Tarifa Publica"})
        print("  Created default pricelist: Tarifa Publica")
    else:
        default_pricelist_id = pricelists[0]["id"]

    created_count = 0
    updated_count = 0

    for index, (ci, pi, confirm) in enumerate(ORDERS, start=1):
        customer = customers[ci]
        product = products[pi]
        ref = f"{ORDER_REF_PREFIX}-{index:02d}"

        existing = search_read(
            uid, models, "sale.order",
            [["client_order_ref", "=", ref]],
            ["id", "name", "state"],
        )
        order = existing[0] if existing else None

        if not order:
            order_vals = {
                "partner_id": customer["id"],
                "client_order_ref": ref,
                "pricelist_id": default_pricelist_id,
            }
            order_id = create(uid, models, "sale.order", order_vals)
            create(uid, models, "sale.order.line", {
                "order_id": order_id,
                "product_id": product["id"],
                "product_uom_qty": 1,
            })
            order = search_read(uid, models, "sale.order", [["id", "=", order_id]], ["id", "name", "state"])[0]
            created_count += 1
        else:
            # Ensure pricelist on existing draft orders
            if order["state"] in ("draft", "sent"):
                models.execute_kw(DB, uid, PASSWORD, "sale.order", "write",
                                  [[order["id"]], {"pricelist_id": default_pricelist_id}])
            updated_count += 1

        if confirm and order["state"] in ("draft", "sent"):
            models.execute_kw(DB, uid, PASSWORD, "sale.order", "action_confirm", [[order["id"]]])
            state = "Confirmado (suscripcion en borrador)"
        elif confirm:
            state = "Ya confirmado"
        else:
            state = "Presupuesto"

        print(f"  [{index:02d}] {customer['name']} -> {product['name']} | {ref} | {state}")

    print(f"Done: {created_count} sale orders created, {updated_count} updated.")


if __name__ == "__main__":
    run()
