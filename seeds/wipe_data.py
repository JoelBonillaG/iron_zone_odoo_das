from config import connect, DB, PASSWORD

def run():
    uid, models = connect()
    print("Archivando/Limpiando datos generados...")
    
    # 1. Cancel / unlink Sale orders
    sale_orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search', [[]])
    if sale_orders:
        for so_id in sale_orders:
            try: models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'action_cancel', [[so_id]])
            except: pass
            try: models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'unlink', [[so_id]])
            except: pass
    
    # 2. Archive products
    product_names = [
        "Membresía Mensual", "Membresía Trimestral", "Membresía Anual",
        "Clase de Spinning", "Clase de CrossFit", "Entrenamiento Personal",
        "Guantes de Boxeo", "Botella Proteína Whey 1kg", "Cuerda para Saltar",
        "Agua Mineral", "Plan Nutrición + Gym"
    ]
    products = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'search', [[('name', 'in', product_names)]])
    for p in products:
        try: models.execute_kw(DB, uid, PASSWORD, 'product.template', 'write', [[p], {'active': False}])
        except: pass
        
    # 3. Archive Customers
    customer_names = [
        "Carlos Andrade", "María Sánchez", "Luis Moreira", "Ana Villacís",
        "Diego Paredes", "Sofía Castillo", "Andrés Flores", "Gabriela Torres",
        "Sebastián Ruiz", "Valeria Guzmán"
    ]
    customers = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search', [[('name', 'in', customer_names)]])
    for c in customers:
        try: models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'write', [[c], {'active': False}])
        except: pass

    # 4. Archive Employees
    employee_names = [
        "Daniela Morales", "Mateo Rivas", "Camila Torres", "Jorge Paredes"
    ]
    employees = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search', [[('name', 'in', employee_names)]])
    for e in employees:
        try: models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'write', [[e], {'active': False}])
        except: pass

    # 5. Try unlink categories
    categ_names = ["Membresías", "Clases", "Equipamiento", "Suplementos"]
    categories = models.execute_kw(DB, uid, PASSWORD, 'product.public.category', 'search', [[('name', 'in', categ_names)]])
    for c in categories:
        try: models.execute_kw(DB, uid, PASSWORD, 'product.public.category', 'unlink', [[c]])
        except: pass
    
    # 6. Archive event registrations and events (clases grupales)
    event_registrations = models.execute_kw(DB, uid, PASSWORD, 'event.registration', 'search', [[]])
    if event_registrations:
        for reg_id in event_registrations:
            try: models.execute_kw(DB, uid, PASSWORD, 'event.registration', 'unlink', [[reg_id]])
            except: pass
    
    events = models.execute_kw(DB, uid, PASSWORD, 'event.event', 'search', [[]])
    if events:
        for event_id in events:
            try: models.execute_kw(DB, uid, PASSWORD, 'event.event', 'unlink', [[event_id]])
            except: pass
        
    print("Limpieza completada.\n")

if __name__ == "__main__":
    run()
