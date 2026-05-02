from config import connect, create, search_read

def run():
    uid, models = connect()
    
    print("Creating eCommerce Categories...")
    categ_memberships = create(uid, models, "product.public.category", {"name": "Membresías"})
    categ_classes     = create(uid, models, "product.public.category", {"name": "Clases"})
    categ_equipment   = create(uid, models, "product.public.category", {"name": "Equipamiento"})
    categ_suppliments = create(uid, models, "product.public.category", {"name": "Suplementos"})

    # Odoo 17/18 convention:
    # - type="consu" + is_storable=True  => Storable Product (Stockable)
    # - type="consu" + is_storable=False => Consumable Product
    # - type="service"                   => Service
    PRODUCTS = [
        {"name": "Membresía Mensual",          "list_price": 35.00,  "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 1 mes", "public_categ_ids": [(6, 0, [categ_memberships])]},
        {"name": "Membresía Trimestral",       "list_price": 90.00,  "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 3 meses", "public_categ_ids": [(6, 0, [categ_memberships])]},
        {"name": "Membresía Anual",            "list_price": 300.00, "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 12 meses", "public_categ_ids": [(6, 0, [categ_memberships])]},
        {"name": "Clase de Spinning",          "list_price": 8.00,   "standard_price": 2.0,  "type": "service", "description_sale": "Clase grupal de spinning 60 mins", "public_categ_ids": [(6, 0, [categ_classes])]},
        {"name": "Clase de CrossFit",          "list_price": 10.00,  "standard_price": 3.0,  "type": "service", "description_sale": "Clase grupal de CrossFit 60 mins", "public_categ_ids": [(6, 0, [categ_classes])]},
        {"name": "Entrenamiento Personal",     "list_price": 25.00,  "standard_price": 15.0, "type": "service", "description_sale": "Sesión personalizada 1v1", "public_categ_ids": [(6, 0, [categ_classes])]},
        {"name": "Guantes de Boxeo",           "list_price": 45.00,  "standard_price": 20.0, "type": "consu", "is_storable": True, "description_sale": "Guantes profesionales", "public_categ_ids": [(6, 0, [categ_equipment])], "_stock": 15},
        {"name": "Botella Proteína Whey 1kg",  "list_price": 38.00,  "standard_price": 25.0, "type": "consu", "is_storable": True, "description_sale": "Proteína whey, 30 porciones", "public_categ_ids": [(6, 0, [categ_suppliments])], "_stock": 20},
        {"name": "Cuerda para Saltar",         "list_price": 12.00,  "standard_price": 4.0,  "type": "consu", "is_storable": True, "description_sale": "Cuerda de velocidad ajustable", "public_categ_ids": [(6, 0, [categ_equipment])], "_stock": 50},
        {"name": "Agua Mineral",               "list_price": 1.00,   "standard_price": 0.5,  "type": "consu", "is_storable": False, "description_sale": "Agua mineral sin gas", "public_categ_ids": [(6, 0, [categ_suppliments])]},
        {"name": "Plan Nutrición + Gym",       "list_price": 75.00,  "standard_price": 10.0, "type": "service", "description_sale": "Plan nutricional + Mensualidad", "public_categ_ids": [(6, 0, [categ_memberships])]},
    ]
    
    try:
        stock_locations = search_read(uid, models, "stock.location", [("usage", "=", "internal")], ["id"])
        stock_location_id = stock_locations[0]["id"] if stock_locations else False
    except Exception as e:
        print("Warning: stock.location error", e)
        stock_location_id = False

    count = 0
    for p in PRODUCTS:
        stock_to_add = p.pop("_stock", None)
        p["sale_ok"]     = True
        p["purchase_ok"] = True
        p["is_published"] = True
        
        template_id = create(uid, models, "product.template", p)
        
        if stock_to_add and stock_location_id and p.get("is_storable"):
            products = search_read(uid, models, "product.product", [("product_tmpl_id", "=", template_id)], ["id"])
            if products:
                product_id = products[0]["id"]
                create(uid, models, "stock.quant", {
                    "product_id": product_id,
                    "location_id": stock_location_id,
                    "inventory_quantity": stock_to_add,
                })
                quant_ids = search_read(uid, models, "stock.quant", [("product_id", "=", product_id), ("location_id", "=", stock_location_id)], ["id"])
                if quant_ids:
                    try:
                        # Odoo's action_apply_inventory returning None crashes XML-RPC unless allow_none=True
                        models.execute_kw('iron_zone', uid, 'admin123', 'stock.quant', 'action_apply_inventory', [[quant_ids[0]['id']]])
                    except Exception as e:
                        if "cannot marshal None" not in str(e):
                            raise

        count += 1
        print(f"  Created product/service: {p['name']} (Type: {p['type']}, Cost: {p['standard_price']})")
        
    print(f"Done: {count} products created.")

if __name__ == "__main__":
    run()
