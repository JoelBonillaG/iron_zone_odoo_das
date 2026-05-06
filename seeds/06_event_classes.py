from config import DB, PASSWORD, connect, create
from datetime import datetime, timedelta


PORTAL_PASSWORD = "admin123"

COMPANY_ADDRESS = {
    "street": "Av. Cevallos y Montalvo 245",
    "city": "Ambato",
    "phone": "+593 3 282 4450",
    "email": "contacto@ironzone.ec",
}

CLASSES = [
    {
        "name": "CrossFit AM",
        "instructor": "Carlos Mendez",
        "capacity": 20,
        "time": "06:00",
        "stage": "Nuevo",
        "description": "Entrena con intensidad. CrossFit es un programa de acondicionamiento físico de alto nivel que combina levantamiento de pesas, gimnasia y cardio.",
    },
    {
        "name": "Yoga Principiantes",
        "instructor": "Sofia Garcia",
        "capacity": 15,
        "time": "07:00",
        "stage": "Nuevo",
        "description": "Iniciación al yoga. Perfecta para quienes inician su viaje en el yoga. Aprenderás posturas básicas, respiración y meditación.",
    },
    {
        "name": "Spinning 18:00",
        "instructor": "Carlos Mendez",
        "capacity": 25,
        "time": "18:00",
        "stage": "Nuevo",
        "description": "Clases de bicicleta estática de alta energía. Quema calorías mientras disfrutas de la música y la motivación del grupo.",
    },
    {
        "name": "Zumba Cardio",
        "instructor": "Sofia Garcia",
        "capacity": 30,
        "time": "19:00",
        "stage": "Nuevo",
        "description": "Baila al ritmo de la música latina. Mejora tu coordinación, quema calorías y diviértete con nuestros instructores certificados.",
    },
    {
        "name": "Pilates Avanzado",
        "instructor": "Sofia Garcia",
        "capacity": 12,
        "time": "09:00",
        "stage": "Nuevo",
        "description": "Fortalecimiento del core y flexibilidad. Requiere experiencia previa en pilates. Trabajaremos con mayor intensidad.",
    },
    {
        "name": "HIIT Entrenamiento",
        "instructor": "Carlos Mendez",
        "capacity": 20,
        "time": "17:30",
        "stage": "Nuevo",
        "description": "Entrenamiento de intervalos de alta intensidad. Máximo rendimiento en mínimo tiempo. Para atletas motivados.",
    },
    {
        "name": "Boxeo Tecnica",
        "instructor": "Carlos Mendez",
        "capacity": 10,
        "time": "18:30",
        "stage": "Nuevo",
        "description": "Aprende técnica de boxeo desde cero. Desarrollo de defensa personal, cardio y confianza.",
    },
    {
        "name": "Yoga Avanzado",
        "instructor": "Sofia Garcia",
        "capacity": 15,
        "time": "08:00",
        "stage": "Reservado",
        "description": "Posturas avanzadas y meditación profunda. Requiere práctica previa en yoga. Nivel intermedio-avanzado.",
    },
    {
        "name": "Natacion Adultos",
        "instructor": "Sofia Garcia",
        "capacity": 16,
        "time": "10:00",
        "stage": "Nuevo",
        "description": "Clases de natación para adultos. Aprende o mejora tu técnica con nuestros instructores certificados en piscina.",
    },
    {
        "name": "Entrenamiento en Grupo",
        "instructor": "Carlos Mendez",
        "capacity": 22,
        "time": "16:00",
        "stage": "Nuevo",
        "description": "Sesiones de acondicionamiento grupal. Motivación compartida, objetivos comunes. Apto para todos los niveles.",
    },
    {
        "name": "Tae Kwon Do Ninos",
        "instructor": "Carlos Mendez",
        "capacity": 18,
        "time": "15:00",
        "stage": "Reservado",
        "description": "Artes marciales para niños. Disciplina, defensa personal y diversión. Clases adaptadas por edad.",
    },
    {
        "name": "Danza Contemporanea",
        "instructor": "Sofia Garcia",
        "capacity": 20,
        "time": "11:00",
        "stage": "Reservado",
        "description": "Expresión artística a través del movimiento. Danza moderna contemporánea. Apto para todos los niveles.",
    },
    {
        "name": "Musculacion Personalizada",
        "instructor": "Carlos Mendez",
        "capacity": 8,
        "time": "12:00",
        "stage": "Anunciado",
        "description": "Entrenamiento de musculación con plan personalizado. Máximo 8 participantes para atención individual.",
    },
    {
        "name": "Acuagym",
        "instructor": "Sofia Garcia",
        "capacity": 25,
        "time": "14:00",
        "stage": "Anunciado",
        "description": "Gym acuático de bajo impacto. Ideal para recuperación, flexibilidad y cardio sin estrés articular.",
    },
    {
        "name": "Funcional Boot Camp",
        "instructor": "Carlos Mendez",
        "capacity": 15,
        "time": "06:30",
        "stage": "Anunciado",
        "description": "Join us for this 24 hours Event. Every year we invite our community, partners and end-users to come and meet us! It's the ideal event to get together and present new features, roadmap of future versions, achievements of the software, workshops, training sessions, etc. This event is also an opportunity to showcase our partners' case studies, methodology or developments. Be there and see directly from the source the features of the new version!",
    },
    {
        "name": "Meditacion Mindfulness",
        "instructor": "Sofia Garcia",
        "capacity": 12,
        "time": "19:30",
        "stage": "Anunciado",
        "description": "Meditación y mindfulness para reducir estrés. Técnicas de respiración, relajación y bienestar mental.",
    },
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

    old_stage_ids = models.execute_kw(
        DB, uid, PASSWORD, "event.stage", "search",
        [[("name", "not in", list(STAGE_SEQUENCE.keys()))]],
    )
    deletable = []
    for sid in old_stage_ids:
        count = models.execute_kw(DB, uid, PASSWORD, "event.event", "search_count", [[("stage_id", "=", sid)]])
        if count == 0:
            deletable.append(sid)
    if deletable:
        models.execute_kw(DB, uid, PASSWORD, "event.stage", "unlink", [deletable])
        print(f"Deleted {len(deletable)} old event stage(s).")

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

    # Get company info
    company_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.company",
        "search",
        [[]],
        {"limit": 1},
    )[0]
    
    company_data = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.company",
        "read",
        [[company_id], ["name", "phone", "email", "street", "city", "country_id"]],
    )[0]

    # Get or create location address
    location_partner_id, _ = create_or_update(
        uid,
        models,
        "res.partner",
        [("name", "=", "Iron Zone - Sede Ambato")],
        {
            "name": "Iron Zone - Sede Ambato",
            "type": "other",
            "street": COMPANY_ADDRESS.get("street", ""),
            "city": COMPANY_ADDRESS.get("city", ""),
            "email": COMPANY_ADDRESS.get("email", ""),
            "phone": COMPANY_ADDRESS.get("phone", ""),
            "country_id": company_data.get("country_id", (False,))[0],
        },
        fields=["id"],
    )

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
            "description": class_info.get("description", ""),
            "seats_available": class_info["capacity"],
            "seats_max": class_info["capacity"],
            "date_begin": odoo_datetime(event_datetime),
            "date_end": odoo_datetime(event_datetime + timedelta(hours=1)),
            "user_id": instructor_user_id or False,
            "stage_id": stage_ids.get(class_info.get("stage", "Nuevo")),
            "website_published": True,
            "address_id": location_partner_id,
            "contact_phone": COMPANY_ADDRESS.get("phone", ""),
            "contact_email": COMPANY_ADDRESS.get("email", ""),
            "event_type_id": False,  # Puede ser personalizado si existe
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
