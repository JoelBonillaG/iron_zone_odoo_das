from config import connect, create, search_read

ORDERS = [
    (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
    (5, 5), (6, 6), (7, 7), (8, 8), (9, 9),
]

def run():
    uid, models = connect()

    customers = search_read(uid, models, "res.partner",
                            [["customer_rank", ">", 0]], ["id", "name"])
    products  = search_read(uid, models, "product.product",
                            [["sale_ok", "=", True]], ["id", "name"])

    if len(customers) < 10 or len(products) < 10:
        print("ERROR: Run 01_customers.py and 02_products.py first.")
        return

    count = 0
    import config
    for ci, pi in ORDERS:
        order_id = create(uid, models, "sale.order", {
            "partner_id": customers[ci]["id"],
        })
        create(uid, models, "sale.order.line", {
            "order_id":   order_id,
            "product_id": products[pi]["id"],
            "product_uom_qty": 1,
        })
        count += 1
        
        # Confirmar algunos pedidos para que el estado sea diferente ("sale")
        if count % 2 == 0:
            models.execute_kw(config.DB, uid, config.PASSWORD, "sale.order", "action_confirm", [[order_id]])
            state = "Confirmado"
        else:
            state = "Borrador (Presupuesto)"
            
        print(f"  Created order: {customers[ci]['name']} → {products[pi]['name']} | Status: {state}")

    print(f"Done: {count} sale orders created.")

if __name__ == "__main__":
    run()
