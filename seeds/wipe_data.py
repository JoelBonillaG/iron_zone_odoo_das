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
        "Carlos Mendez", "Sofia Garcia", "Ana Torres", "Luis Herrera",
        "Mateo Ruiz", "Valentina Paredes", "Gabriela Salazar", "Diego Molina",
        "Elena Castro", "Roberto Lima", "Paula Naranjo", "Andres Vega",
        "Camila Ortiz", "Nicolas Benitez", "Isabel Romero", "Ricardo Ponce"
    ]
    employees = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search', [[('name', 'in', employee_names)]])
    for e in employees:
        try: models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'write', [[e], {'active': False}])
        except: pass

    employee_logins = [
        "carlos.mendez@ironzone.ec", "sofia.garcia@ironzone.ec",
        "ana.torres@ironzone.ec", "luis.herrera@ironzone.ec",
        "mateo.ruiz@ironzone.ec", "valentina.paredes@ironzone.ec",
        "gabriela.salazar@ironzone.ec", "diego.molina@ironzone.ec",
        "elena.castro@ironzone.ec", "roberto.lima@ironzone.ec",
        "paula.naranjo@ironzone.ec", "andres.vega@ironzone.ec",
        "camila.ortiz@ironzone.ec", "nicolas.benitez@ironzone.ec",
        "isabel.romero@ironzone.ec", "ricardo.ponce@ironzone.ec"
    ]
    users = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'search', [[('login', 'in', employee_logins)]])
    for user in users:
        try: models.execute_kw(DB, uid, PASSWORD, 'res.users', 'write', [[user], {'active': False}])
        except: pass

    # 5. Archive Job Positions
    job_names = [
        "Instructor de CrossFit", "Instructor de Yoga", "Recepcionista de Membresias",
        "Administrador de Membresias", "Asesor Comercial", "Ejecutivo de Ventas",
        "Analista de Facturacion", "Contador", "Analista de Recursos Humanos",
        "Coordinador de Recursos Humanos", "Coordinador de Operaciones",
        "Tecnico de Mantenimiento", "Especialista en Email Marketing",
        "Coordinador de Campanas", "Editor de Sitio web y eCommerce",
        "Coordinador de Eventos"
    ]
    jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search', [[('name', 'in', job_names)]])
    for j in jobs:
        try: models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'unlink', [[j]])
        except: pass
    
    # 6. Archive Departments
    dept_names = [
        "Administracion", "Entrenamiento", "Atencion al Cliente", "Ventas",
        "Finanzas", "Recursos Humanos", "Operaciones", "Mantenimiento",
        "Marketing", "Seguridad"
    ]
    departments = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search', [[('name', 'in', dept_names)]])
    for d in departments:
        try: models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'unlink', [[d]])
        except: pass
    
    # 7. Try unlink categories
    categ_names = ["Membresías", "Clases", "Equipamiento", "Suplementos"]
    categories = models.execute_kw(DB, uid, PASSWORD, 'product.public.category', 'search', [[('name', 'in', categ_names)]])
    for c in categories:
        try: models.execute_kw(DB, uid, PASSWORD, 'product.public.category', 'unlink', [[c]])
        except: pass
    
    # 8. Archive event registrations and events (clases grupales)
    event_registrations = models.execute_kw(DB, uid, PASSWORD, 'event.registration', 'search', [[]])
    if event_registrations:
        for reg_id in event_registrations:
            try: models.execute_kw(DB, uid, PASSWORD, 'event.registration', 'unlink', [[reg_id]])
            except: pass
    
    # Nombres de clases a borrar (Nueva, Reservado, Anunciado)
    class_names = [
        "CrossFit AM", "Yoga Principiantes", "Spinning 18:00", "Zumba Cardio",
        "Pilates Avanzado", "HIIT Entrenamiento", "Boxeo Tecnica", "Yoga Avanzado",
        "Natacion Adultos", "Entrenamiento en Grupo", "Tae Kwon Do Ninos",
        "Danza Contemporanea", "Musculacion Personalizada", "Acuagym",
        "Funcional Boot Camp", "Meditacion Mindfulness"
    ]
    events = models.execute_kw(DB, uid, PASSWORD, 'event.event', 'search', [[('name', 'in', class_names)]])
    if events:
        for event_id in events:
            try: models.execute_kw(DB, uid, PASSWORD, 'event.event', 'unlink', [[event_id]])
            except: pass
        
    print("Limpieza completada.\n")

if __name__ == "__main__":
    run()
