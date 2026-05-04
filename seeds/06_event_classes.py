from config import DB, PASSWORD, connect, create
from datetime import datetime, timedelta


CLASSES = [
    {"name": "CrossFit AM", "instructor": "Mateo Rivas", "capacity": 20, "time": "06:00"},
    {"name": "Yoga Principiantes", "instructor": "Mateo Rivas", "capacity": 15, "time": "07:00"},
    {"name": "Spinning 18:00", "instructor": "Mateo Rivas", "capacity": 25, "time": "18:00"},
    {"name": "Zumba Cardio", "instructor": "Mateo Rivas", "capacity": 30, "time": "19:00"},
    {"name": "Pilates Avanzado", "instructor": "Mateo Rivas", "capacity": 12, "time": "09:00"},
    {"name": "HIIT Entrenamiento", "instructor": "Mateo Rivas", "capacity": 20, "time": "17:30"},
    {"name": "Boxeo Técnica", "instructor": "Mateo Rivas", "capacity": 10, "time": "18:30"},
    {"name": "Yoga Avanzado", "instructor": "Mateo Rivas", "capacity": 15, "time": "08:00"},
    {"name": "Natación Adultos", "instructor": "Mateo Rivas", "capacity": 16, "time": "10:00"},
    {"name": "Entrenamiento en Grupo", "instructor": "Mateo Rivas", "capacity": 22, "time": "16:00"},
]


def odoo_datetime(value):
    return value.replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "search_read",
        [domain],
        {"fields": fields or ["id"], "limit": 1, "context": {"active_test": False}},
    )
    return records[0] if records else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def ensure_user_for_employee(uid, models, employee):
    if employee.get("user_id"):
        return employee["user_id"][0]

    login = employee.get("work_email") or f"{employee['name'].lower().replace(' ', '.')}@ironzone.com"
    user_id, _ = create_or_update(
        uid,
        models,
        "res.users",
        [("login", "=", login)],
        {
            "name": employee["name"],
            "login": login,
            "email": login,
            "active": True,
        },
        fields=["id", "name"],
    )
    models.execute_kw(DB, uid, PASSWORD, "hr.employee", "write", [[employee["id"]], {"user_id": user_id}])
    return user_id


def run():
    uid, models = connect()

    # Buscar entrenadores de 05_employees.py y usar su usuario vinculado para el evento.
    instructor_user_ids = {}
    print("Mapping instructors from employees...")
    for class_info in CLASSES:
        instructor_name = class_info["instructor"]
        if instructor_name not in instructor_user_ids:
            instructor = search_one(
                uid,
                models,
                "hr.employee",
                [("name", "=", instructor_name)],
                fields=["id", "name", "work_email", "user_id"],
            )
            if instructor:
                user_id = ensure_user_for_employee(uid, models, instructor)
                instructor_user_ids[instructor_name] = user_id
                print(f"  Found instructor: {instructor_name} (Employee ID: {instructor['id']}, User ID: {user_id})")
            else:
                print(f"  Warning: Instructor not found: {instructor_name}")

    # Buscar todos los clientes (alumnos/socios) existentes
    print("Fetching all members/customers...")
    all_members = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [[("customer_rank", ">", 0)]],
        {"fields": ["id", "name"], "limit": 100},
    )
    
    member_ids = {member["name"]: member["id"] for member in all_members}
    print(f"  Found {len(member_ids)} members")

    # Crear eventos (clases)
    created_count = 0
    updated_count = 0
    event_ids = {}
    
    print("Syncing group classes...")
    base_date = datetime.now() + timedelta(days=1)
    
    for idx, class_info in enumerate(CLASSES):
        # Calcular fecha y hora del evento
        event_date = base_date + timedelta(days=idx % 7)
        time_parts = class_info["time"].split(":")
        event_datetime = event_date.replace(hour=int(time_parts[0]), minute=int(time_parts[1]))
        
        instructor_user_id = instructor_user_ids.get(class_info["instructor"])
        
        values = {
            "name": class_info["name"],
            "seats_available": class_info["capacity"],
            "seats_max": class_info["capacity"],
            "date_begin": odoo_datetime(event_datetime),
            "date_end": odoo_datetime(event_datetime + timedelta(hours=1)),
            "user_id": instructor_user_id if instructor_user_id else False,
        }
        
        event_id, created = create_or_update(
            uid,
            models,
            "event.event",
            [("name", "=", class_info["name"])],
            values,
            fields=["id", "name"],
        )
        event_ids[class_info["name"]] = event_id
        
        if created:
            created_count += 1
        else:
            updated_count += 1
        
        action = "Created" if created else "Updated"
        print(f"  {action} class: {class_info['name']} - Instructor: {class_info['instructor']}")

    # Registrar miembros a las clases
    print("Registering members to classes...")
    registrations_created = 0
    
    for idx, (member_name, member_id) in enumerate(member_ids.items()):
        # Asignar cada miembro a 3-4 clases diferentes
        num_classes = 3 + (idx % 2)
        for class_idx in range(num_classes):
            class_idx = (idx + class_idx) % len(CLASSES)
            class_info = CLASSES[class_idx]
            event_id = event_ids.get(class_info["name"])
            
            if not event_id:
                continue
            
            values = {
                "event_id": event_id,
                "partner_id": member_id,
                "name": member_name,
                "email": f"{member_name.lower().replace(' ', '.')}@ironzone.com",
            }
            
            _, created = create_or_update(
                uid,
                models,
                "event.registration",
                [("event_id", "=", event_id), ("partner_id", "=", member_id)],
                values,
                fields=["id"],
            )
            
            if created:
                registrations_created += 1

    print(f"Done: {created_count} classes created, {updated_count} updated.")
    print(f"Registered: {registrations_created} member registrations created.")


if __name__ == "__main__":
    run()
