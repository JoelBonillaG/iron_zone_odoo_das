from config import DB, PASSWORD, connect, create, search_read

ORDERS = [
    (0, 0),
    (1, 1),
    (2, 2),
]

ORDER_REF_PREFIX = "SEED03-SALE"

CUSTOMER_EMAILS = [
    "pruebasjos04@gmail.com",
    "pruebasjos07@gmail.com",
    "pruebasjos08@gmail.com",
]

IRON_ZONE_PRODUCTS = [
    "Suscripcion Mensual",
    "Suscripcion Trimestral",
    "Suscripcion Anual",
    "Plan Nutrición + Gym",
]


def run():
    uid, models = connect()

    customers = search_read(
        uid,
        models,
        "res.partner",
        [["email", "in", CUSTOMER_EMAILS], ["customer_rank", ">", 0], ["active", "=", True]],
        ["id", "name", "email"],
    )
    customers_by_email = {customer["email"]: customer for customer in customers}
    missing_customers = [email for email in CUSTOMER_EMAILS if email not in customers_by_email]
    customers = [customers_by_email[email] for email in CUSTOMER_EMAILS if email in customers_by_email]

    products = search_read(
        uid,
        models,
        "product.product",
        [["name", "in", IRON_ZONE_PRODUCTS], ["sale_ok", "=", True]],
        ["id", "name"],
    )
    products_by_name = {product["name"]: product for product in products}
    missing_products = [name for name in IRON_ZONE_PRODUCTS if name not in products_by_name]
    products = [products_by_name[name] for name in IRON_ZONE_PRODUCTS if name in products_by_name]

    if len(customers) < len(ORDERS) or missing_products:
        print("ERROR: Run 01_customers.py and 02_products.py first.")
        if missing_customers:
            print("Missing portal customers:", ", ".join(missing_customers))
        if missing_products:
            print("Missing Iron Zone products:", ", ".join(missing_products))
        return

    pricelists = search_read(uid, models, "product.pricelist", [], ["id"])
    if not pricelists:
        default_pricelist_id = create(uid, models, "product.pricelist", {"name": "Tarifa Publica"})
    else:
        default_pricelist_id = pricelists[0]["id"]

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
            order_vals = {
                "partner_id": customer["id"],
                "client_order_ref": ref,
            }
            if default_pricelist_id:
                order_vals["pricelist_id"] = default_pricelist_id
            order_id = create(uid, models, "sale.order", order_vals)
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
            if order["state"] in ("draft", "sent") and default_pricelist_id:
                models.execute_kw(DB, uid, PASSWORD, "sale.order", "write", [[order["id"]], {"pricelist_id": default_pricelist_id}])
            updated_count += 1

        if index % 2 == 0 and order["state"] in ("draft", "sent"):
            models.execute_kw(DB, uid, PASSWORD, "sale.order", "action_confirm", [[order["id"]]])
            state = "Confirmado"
        elif index % 2 == 0:
            state = "Confirmado"
        else:
            state = "Borrador (Presupuesto)"

        print(f"  Synced order: {customer['name']} -> {product['name']} | Ref: {ref} | Status: {state}")

    print(f"Done: {created_count} sale orders created, {updated_count} already synced.")


if __name__ == "__main__":
    run()
