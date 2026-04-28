from config import connect, create

PRODUCTS = [
    {"name": "Membresía Mensual",          "list_price": 35.00,  "type": "service", "description_sale": "Acceso ilimitado al gimnasio por 1 mes"},
    {"name": "Membresía Trimestral",       "list_price": 90.00,  "type": "service", "description_sale": "Acceso ilimitado al gimnasio por 3 meses"},
    {"name": "Membresía Anual",            "list_price": 300.00, "type": "service", "description_sale": "Acceso ilimitado al gimnasio por 12 meses"},
    {"name": "Clase de Spinning",          "list_price": 8.00,   "type": "service", "description_sale": "Clase grupal de spinning 60 minutos"},
    {"name": "Clase de CrossFit",          "list_price": 10.00,  "type": "service", "description_sale": "Clase grupal de CrossFit 60 minutos"},
    {"name": "Entrenamiento Personal",     "list_price": 25.00,  "type": "service", "description_sale": "Sesión personalizada con entrenador certificado"},
    {"name": "Guantes de Boxeo",           "list_price": 45.00,  "type": "consu",   "description_sale": "Guantes profesionales para boxeo y MMA"},
    {"name": "Botella Proteína Whey 1kg",  "list_price": 38.00,  "type": "consu",   "description_sale": "Proteína whey sabor chocolate, 30 porciones"},
    {"name": "Cuerda para Saltar",         "list_price": 12.00,  "type": "consu",   "description_sale": "Cuerda de velocidad ajustable"},
    {"name": "Plan Nutrición + Gym",       "list_price": 75.00,  "type": "service", "description_sale": "Membresía mensual + plan nutricional personalizado"},
]

def run():
    uid, models = connect()
    count = 0
    for p in PRODUCTS:
        p["sale_ok"]     = True
        p["purchase_ok"] = False
        create(uid, models, "product.template", p)
        count += 1
        print(f"  Created product: {p['name']}")
    print(f"Done: {count} products created.")

if __name__ == "__main__":
    run()
