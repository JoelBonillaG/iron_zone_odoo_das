from config import DB, PASSWORD, connect, create
from datetime import datetime, timedelta


PORTAL_PASSWORD = "admin123"

CLASSES = [
    {"name": "CrossFit AM", "instructor": "Carlos Mendez", "capacity": 20, "time": "06:00", "stage": "Nuevo"},
    {"name": "Yoga Principiantes", "instructor": "Sofia Garcia", "capacity": 15, "time": "07:00", "stage": "Nuevo"},
    {"name": "Spinning 18:00", "instructor": "Carlos Mendez", "capacity": 25, "time": "18:00", "stage": "Nuevo"},
    {"name": "Zumba Cardio", "instructor": "Sofia Garcia", "capacity": 30, "time": "19:00", "stage": "Nuevo"},
    {"name": "Pilates Avanzado", "instructor": "Sofia Garcia", "capacity": 12, "time": "09:00", "stage": "Nuevo"},
    {"name": "HIIT Entrenamiento", "instructor": "Carlos Mendez", "capacity": 20, "time": "17:30", "stage": "Nuevo"},
    {"name": "Boxeo Tecnica", "instructor": "Carlos Mendez", "capacity": 10, "time": "18:30", "stage": "Nuevo"},
    {"name": "Yoga Avanzado", "instructor": "Sofia Garcia", "capacity": 15, "time": "08:00", "stage": "Reservado"},
    {"name": "Natacion Adultos", "instructor": "Sofia Garcia", "capacity": 16, "time": "10:00", "stage": "Nuevo"},
    {"name": "Entrenamiento en Grupo", "instructor": "Carlos Mendez", "capacity": 22, "time": "16:00", "stage": "Nuevo"},
    {"name": "Tae Kwon Do Ninos", "instructor": "Carlos Mendez", "capacity": 18, "time": "15:00", "stage": "Reservado"},
    {"name": "Danza Contemporanea", "instructor": "Sofia Garcia", "capacity": 20, "time": "11:00", "stage": "Reservado"},
    {"name": "Musculacion Personalizada", "instructor": "Carlos Mendez", "capacity": 8, "time": "12:00", "stage": "Anunciado"},
    {"name": "Acuagym", "instructor": "Sofia Garcia", "capacity": 25, "time": "14:00", "stage": "Anunciado"},
    {"name": "Funcional Boot Camp", "instructor": "Carlos Mendez", "capacity": 15, "time": "06:30", "stage": "Anunciado"},
    {"name": "Meditacion Mindfulness", "instructor": "Sofia Garcia", "capacity": 12, "time": "19:30", "stage": "Anunciado"},
]

STAGE_SEQUENCE = {
    "Nuevo": 10,
    "Reservado": 20,
    "Anunciado": 30,
}

CLASS_NAMES = [class_info["name"] for class_info in CLASSES]


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


def xmlid_to_res_id(uid, models, xmlid):
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid,
        models,
        "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    if not record:
        raise RuntimeError(f"External ID not found: {xmlid}")
    return record["res_id"]


def ensure_instructor_portal_user(uid, models, user_id):
    instructor_group_id = xmlid_to_res_id(uid, models, "training_plans.group_training_instructor_portal")
    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.users",
        "write",
        [[user_id], {"groups_id": [(6, 0, [instructor_group_id])], "password": PORTAL_PASSWORD}],
    )


def ensure_event_admin_rule(uid, models):
    event_model_id = xmlid_to_res_id(uid, models, "event.model_event_event")
    admin_group_id = xmlid_to_res_id(uid, models, "base.group_system")
    create_or_update(
        uid,
        models,
        "ir.rule",
        [("name", "=", "Administrador ve todos los eventos"), ("model_id", "=", event_model_id)],
        {
            "name": "Administrador ve todos los eventos",
            "model_id": event_model_id,
            "groups": [(4, admin_group_id)],
            "domain_force": "[(1, '=', 1)]",
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        },
        fields=["id"],
    )


def ensure_event_stages(uid, models):
    stage_ids = {}
    for stage_name, sequence in STAGE_SEQUENCE.items():
        stage_id, _ = create_or_update(
            uid,
            models,
            "event.stage",
            [("name", "=", stage_name)],
            {"name": stage_name, "sequence": sequence},
            fields=["id", "name"],
        )
        stage_ids[stage_name] = stage_id
    return stage_ids


def archive_old_demo_events(uid, models):
    old_event_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "event.event",
        "search",
        [[("name", "not in", CLASS_NAMES), ("active", "=", True)]],
    )
    if old_event_ids:
        models.execute_kw(DB, uid, PASSWORD, "event.event", "write", [old_event_ids, {"active": False}])
        print(f"Archived {len(old_event_ids)} old demo event(s).")


def ensure_user_for_employee(uid, models, employee):
    if employee.get("user_id"):
        user_id = employee["user_id"][0]
        ensure_instructor_portal_user(uid, models, user_id)
        return user_id

    login = employee.get("work_email") or f"{employee['name'].lower().replace(' ', '.')}@ironzone.com"
    partner_id, _ = create_or_update(
        uid,
        models,
        "res.partner",
        [("email", "=", login)],
        {"name": employee["name"], "email": login, "active": True},
        fields=["id"],
    )
    user_id, _ = create_or_update(
        uid,
        models,
        "res.users",
        [("login", "=", login)],
        {
            "name": employee["name"],
            "login": login,
            "email": login,
            "partner_id": partner_id,
            "active": True,
        },
        fields=["id", "name"],
    )
    ensure_instructor_portal_user(uid, models, user_id)
    models.execute_kw(DB, uid, PASSWORD, "hr.employee", "write", [[employee["id"]], {"user_id": user_id}])
    return user_id


def run():
    uid, models = connect()
    ensure_event_admin_rule(uid, models)
    archive_old_demo_events(uid, models)

    instructor_user_ids = {}
    print("Mapping instructors from employees...")
    for class_info in CLASSES:
        instructor_name = class_info["instructor"]
        if instructor_name in instructor_user_ids:
            continue

        instructor = search_one(
            uid,
            models,
            "hr.employee",
            [("name", "=", instructor_name), ("active", "=", True)],
            fields=["id", "name", "work_email", "user_id"],
        )
        if instructor:
            user_id = ensure_user_for_employee(uid, models, instructor)
            instructor_user_ids[instructor_name] = user_id
            print(f"  Found instructor: {instructor_name} (Employee ID: {instructor['id']}, User ID: {user_id})")
        else:
            print(f"  Warning: Instructor not found: {instructor_name}")

    print("Fetching all members/customers...")
    all_members = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [[("customer_rank", ">", 0), ("active", "=", True)]],
        {"fields": ["id", "name", "email"], "limit": 100},
    )
    member_ids = {member["name"]: member["id"] for member in all_members}
    print(f"  Found {len(member_ids)} members")

    stage_ids = ensure_event_stages(uid, models)

    created_count = 0
    updated_count = 0
    event_ids = {}
    print("Syncing group classes...")
    base_date = datetime.now() + timedelta(days=1)

    for idx, class_info in enumerate(CLASSES):
        event_date = base_date + timedelta(days=idx % 7)
        hour, minute = [int(part) for part in class_info["time"].split(":")]
        event_datetime = event_date.replace(hour=hour, minute=minute)
        instructor_user_id = instructor_user_ids.get(class_info["instructor"])

        values = {
            "name": class_info["name"],
            "seats_available": class_info["capacity"],
            "seats_max": class_info["capacity"],
            "date_begin": odoo_datetime(event_datetime),
            "date_end": odoo_datetime(event_datetime + timedelta(hours=1)),
            "user_id": instructor_user_id or False,
            "stage_id": stage_ids.get(class_info.get("stage", "Nuevo")),
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

    print("Registering members to classes...")
    registrations_created = 0
    for idx, (member_name, member_id) in enumerate(member_ids.items()):
        num_classes = 3 + (idx % 2)
        for class_offset in range(num_classes):
            class_idx = (idx + class_offset) % len(CLASSES)
            class_info = CLASSES[class_idx]
            event_id = event_ids.get(class_info["name"])
            if not event_id:
                continue

            values = {
                "event_id": event_id,
                "partner_id": member_id,
                "name": member_name,
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
