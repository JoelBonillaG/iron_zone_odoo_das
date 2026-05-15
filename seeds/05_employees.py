from config import DB, PASSWORD, connect, create


DEFAULT_PASSWORD = "admin123"

DEPARTMENTS = [
    {"name": "Administracion"},
    {"name": "Entrenamiento"},
    {"name": "Atencion al Cliente"},
    {"name": "Ventas"},
    {"name": "Finanzas"},
    {"name": "Recursos Humanos"},
    {"name": "Operaciones"},
    {"name": "Mantenimiento"},
    {"name": "Marketing"},
    {"name": "Seguridad"},
]

JOBS = [
    {"name": "Instructor de CrossFit", "department": "Entrenamiento"},
    {"name": "Instructor de Yoga", "department": "Entrenamiento"},
    {"name": "Recepcionista de Membresias", "department": "Atencion al Cliente"},
    {"name": "Administrador de Membresias", "department": "Administracion"},
    {"name": "Asesor Comercial", "department": "Ventas"},
    {"name": "Ejecutivo de Ventas", "department": "Ventas"},
    {"name": "Analista de Facturacion", "department": "Finanzas"},
    {"name": "Contador", "department": "Finanzas"},
    {"name": "Analista de Recursos Humanos", "department": "Recursos Humanos"},
    {"name": "Coordinador de Recursos Humanos", "department": "Recursos Humanos"},
    {"name": "Coordinador de Operaciones", "department": "Operaciones"},
    {"name": "Tecnico de Mantenimiento", "department": "Mantenimiento"},
    {"name": "Especialista en Email Marketing", "department": "Marketing"},
    {"name": "Coordinador de Campanas", "department": "Marketing"},
    {"name": "Editor de Sitio web y eCommerce", "department": "Marketing"},
    {"name": "Coordinador de Eventos", "department": "Entrenamiento"},
]

IRON_ZONE_GROUPS = {
    "admin": {
        "name": "Iron Zone / Administracion y Gerencia",
        "xmlid": "iz_backend_theme.group_ironzone_admin",
        "implied": [
            "base.group_user",
            "base.group_system",
        ],
    },
    "hr": {
        "name": "Iron Zone / RRHH",
        "xmlid": "iz_backend_theme.group_ironzone_hr",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "hr.group_hr_user",
        ],
    },
    "trainer": {
        "name": "Iron Zone / Entrenadores",
        "xmlid": "iz_backend_theme.group_ironzone_trainers",
        "implied": [
            "base.group_user",
            "event.group_event_registration_desk",
        ],
    },
    "membership": {
        "name": "Iron Zone / Recepcion Membresias",
        "xmlid": "iz_backend_theme.group_ironzone_membership",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "sales_team.group_sale_salesman_all_leads",
        ],
    },
    "sales": {
        "name": "Iron Zone / Ventas",
        "xmlid": "iz_backend_theme.group_ironzone_sales",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "sales_team.group_sale_salesman",
        ],
    },
    "billing": {
        "name": "Iron Zone / Facturacion y Contabilidad",
        "xmlid": "iz_backend_theme.group_ironzone_billing",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "account.group_account_invoice",
            "sales_team.group_sale_salesman_all_leads",
        ],
    },
    "operations": {
        "name": "Iron Zone / Inventario y Operaciones",
        "xmlid": "iz_backend_theme.group_ironzone_operations",
        "implied": [
            "base.group_user",
            "stock.group_stock_user",
        ],
    },
    "email_marketing": {
        "name": "Iron Zone / Marketing",
        "xmlid": "iz_backend_theme.group_ironzone_marketing",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "mass_mailing.group_mass_mailing_user",
            "mass_mailing.group_mass_mailing_campaign",
        ],
    },
    "website": {
        "name": "Iron Zone / Sitio web y eCommerce",
        "xmlid": "iz_backend_theme.group_ironzone_website",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "website.group_website_designer",
            "sales_team.group_sale_salesman_all_leads",
        ],
    },
    "events_admin": {
        "name": "Iron Zone / Eventos Admin",
        "xmlid": "iz_backend_theme.group_ironzone_events_admin",
        "implied": [
            "base.group_user",
            "base.group_partner_manager",
            "event.group_event_user",
        ],
    },
}

EMPLOYEES = [
    {
        "name": "Carlos Mendez",
        "login": "carlos.mendez@ironzone.ec",
        "work_email": "carlos.mendez@ironzone.ec",
        "job": "Instructor de CrossFit",
        "department": "Entrenamiento",
        "mobile_phone": "0991234525",
        "work_phone": "032400105",
        "role": "trainer",
    },
    {
        "name": "Sofia Garcia",
        "login": "sofia.garcia@ironzone.ec",
        "work_email": "sofia.garcia@ironzone.ec",
        "job": "Instructor de Yoga",
        "department": "Entrenamiento",
        "mobile_phone": "0991234526",
        "work_phone": "032400106",
        "role": "trainer",
    },
    {
        "name": "Ana Torres",
        "login": "ana.torres@ironzone.ec",
        "work_email": "ana.torres@ironzone.ec",
        "job": "Recepcionista de Membresias",
        "department": "Atencion al Cliente",
        "mobile_phone": "0991234527",
        "work_phone": "032400107",
        "role": "membership",
    },
    {
        "name": "Luis Herrera",
        "login": "luis.herrera@ironzone.ec",
        "work_email": "luis.herrera@ironzone.ec",
        "job": "Administrador de Membresias",
        "department": "Administracion",
        "mobile_phone": "0991234528",
        "work_phone": "032400108",
        "role": "membership",
    },
    {
        "name": "Mateo Ruiz",
        "login": "mateo.ruiz@ironzone.ec",
        "work_email": "mateo.ruiz@ironzone.ec",
        "job": "Asesor Comercial",
        "department": "Ventas",
        "mobile_phone": "0991234529",
        "work_phone": "032400109",
        "role": "sales",
    },
    {
        "name": "Valentina Paredes",
        "login": "valentina.paredes@ironzone.ec",
        "work_email": "valentina.paredes@ironzone.ec",
        "job": "Ejecutivo de Ventas",
        "department": "Ventas",
        "mobile_phone": "0991234530",
        "work_phone": "032400110",
        "role": "sales",
    },
    {
        "name": "Gabriela Salazar",
        "login": "gabriela.salazar@ironzone.ec",
        "work_email": "gabriela.salazar@ironzone.ec",
        "job": "Analista de Facturacion",
        "department": "Finanzas",
        "mobile_phone": "0991234531",
        "work_phone": "032400111",
        "role": "billing",
    },
    {
        "name": "Diego Molina",
        "login": "diego.molina@ironzone.ec",
        "work_email": "diego.molina@ironzone.ec",
        "job": "Contador",
        "department": "Finanzas",
        "mobile_phone": "0991234532",
        "work_phone": "032400112",
        "role": "billing",
    },
    {
        "name": "Elena Castro",
        "login": "elena.castro@ironzone.ec",
        "work_email": "elena.castro@ironzone.ec",
        "job": "Analista de Recursos Humanos",
        "department": "Recursos Humanos",
        "mobile_phone": "0991234533",
        "work_phone": "032400113",
        "role": "hr",
    },
    {
        "name": "Roberto Lima",
        "login": "roberto.lima@ironzone.ec",
        "work_email": "roberto.lima@ironzone.ec",
        "job": "Coordinador de Recursos Humanos",
        "department": "Recursos Humanos",
        "mobile_phone": "0991234534",
        "work_phone": "032400114",
        "role": "hr",
    },
    {
        "name": "Paula Naranjo",
        "login": "paula.naranjo@ironzone.ec",
        "work_email": "paula.naranjo@ironzone.ec",
        "job": "Coordinador de Operaciones",
        "department": "Operaciones",
        "mobile_phone": "0991234535",
        "work_phone": "032400115",
        "role": "operations",
    },
    {
        "name": "Andres Vega",
        "login": "andres.vega@ironzone.ec",
        "work_email": "andres.vega@ironzone.ec",
        "job": "Tecnico de Mantenimiento",
        "department": "Mantenimiento",
        "mobile_phone": "0991234536",
        "work_phone": "032400116",
        "role": "operations",
    },
    {
        "name": "Camila Ortiz",
        "login": "camila.ortiz@ironzone.ec",
        "work_email": "camila.ortiz@ironzone.ec",
        "job": "Especialista en Email Marketing",
        "department": "Marketing",
        "mobile_phone": "0991234537",
        "work_phone": "032400117",
        "role": "email_marketing",
    },
    {
        "name": "Nicolas Benitez",
        "login": "nicolas.benitez@ironzone.ec",
        "work_email": "nicolas.benitez@ironzone.ec",
        "job": "Coordinador de Campanas",
        "department": "Marketing",
        "mobile_phone": "0991234538",
        "work_phone": "032400118",
        "role": "email_marketing",
    },
    {
        "name": "Isabel Romero",
        "login": "isabel.romero@ironzone.ec",
        "work_email": "isabel.romero@ironzone.ec",
        "job": "Editor de Sitio web y eCommerce",
        "department": "Marketing",
        "mobile_phone": "0991234539",
        "work_phone": "032400119",
        "role": "website",
    },
    {
        "name": "Ricardo Ponce",
        "login": "ricardo.ponce@ironzone.ec",
        "work_email": "ricardo.ponce@ironzone.ec",
        "job": "Coordinador de Eventos",
        "department": "Entrenamiento",
        "mobile_phone": "0991234540",
        "work_phone": "032400120",
        "role": "events_admin",
    },
]


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


def xmlid_to_res_id(uid, models, xmlid, required=True):
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid,
        models,
        "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    if not record:
        if required:
            raise RuntimeError(f"External ID not found: {xmlid}")
        print(f"  Warning: group not found, skipped: {xmlid}")
        return None
    return record["res_id"]


def ensure_iron_zone_groups(uid, models):
    group_ids = {}
    for key, group in IRON_ZONE_GROUPS.items():
        implied_ids = [
            xmlid_to_res_id(uid, models, xmlid, required=False)
            for xmlid in group["implied"]
        ]
        implied_ids = [group_id for group_id in implied_ids if group_id]

        group_id = None
        if group.get("xmlid"):
            group_id = xmlid_to_res_id(uid, models, group["xmlid"], required=False)

        values = {
            "name": group["name"],
            "implied_ids": [(6, 0, implied_ids)],
        }
        if group_id:
            models.execute_kw(DB, uid, PASSWORD, "res.groups", "write", [[group_id], values])
            created = False
        else:
            group_id, created = create_or_update(
                uid,
                models,
                "res.groups",
                [("name", "=", group["name"])],
                values,
                fields=["id", "name"],
            )

        group_ids[key] = group_id
        action = "Created" if created else "Updated"
        print(f"  {action} group: {group['name']}")
    return group_ids


def assign_admin_group(uid, models, group_ids):
    admin_group_id = group_ids.get("admin")
    if not admin_group_id:
        return
    admin_user = search_one(
        uid,
        models,
        "res.users",
        [("login", "=", "admin@ironzone.com")],
        fields=["id", "name"],
    )
    if admin_user:
        models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "res.users",
            "write",
            [[admin_user["id"]], {"groups_id": [(4, admin_group_id)]}],
        )
        print("  Updated admin user with Iron Zone / Administracion y Gerencia")


def model_id(uid, models, model):
    record = search_one(uid, models, "ir.model", [("model", "=", model)], fields=["id"])
    if not record:
        raise RuntimeError(f"Model not found: {model}")
    return record["id"]


def ensure_model_access(uid, models, group_id, model_name, access_name, permissions):
    access_values = {
        "name": access_name,
        "model_id": model_id(uid, models, model_name),
        "group_id": group_id,
        "perm_read": permissions.get("read", False),
        "perm_write": permissions.get("write", False),
        "perm_create": permissions.get("create", False),
        "perm_unlink": permissions.get("unlink", False),
    }
    create_or_update(
        uid,
        models,
        "ir.model.access",
        [("name", "=", access_name), ("model_id.model", "=", model_name), ("group_id", "=", group_id)],
        access_values,
        fields=["id"],
    )


def ensure_record_rule(uid, models, group_id, model_name, rule_name, domain_force, permissions):
    rule_values = {
        "name": rule_name,
        "model_id": model_id(uid, models, model_name),
        "groups": [(6, 0, [group_id])],
        "domain_force": domain_force,
        "perm_read": permissions.get("read", False),
        "perm_write": permissions.get("write", False),
        "perm_create": permissions.get("create", False),
        "perm_unlink": permissions.get("unlink", False),
    }
    create_or_update(
        uid,
        models,
        "ir.rule",
        [("name", "=", rule_name), ("model_id.model", "=", model_name)],
        rule_values,
        fields=["id"],
    )


def ensure_role_security(uid, models, group_ids):
    trainer_group_id = group_ids["trainer"]
    ensure_model_access(
        uid,
        models,
        trainer_group_id,
        "event.event",
        "Iron Zone Entrenadores - Eventos",
        {"read": True, "write": True, "create": False, "unlink": False},
    )
    ensure_model_access(
        uid,
        models,
        trainer_group_id,
        "event.registration",
        "Iron Zone Entrenadores - Inscripciones",
        {"read": True, "write": True, "create": True, "unlink": False},
    )
    ensure_record_rule(
        uid,
        models,
        trainer_group_id,
        "event.event",
        "Iron Zone Entrenador ve solo sus eventos",
        "[('user_id', '=', user.id)]",
        {"read": True, "write": True, "create": False, "unlink": False},
    )
    ensure_record_rule(
        uid,
        models,
        trainer_group_id,
        "event.registration",
        "Iron Zone Entrenador ve solo inscritos de sus eventos",
        "[('event_id.user_id', '=', user.id)]",
        {"read": True, "write": True, "create": True, "unlink": False},
    )
    print("  Updated trainer access rights and record rules")


def resolve_groups(group_ids, role):
    group_id = group_ids.get(role)
    return [group_id] if group_id else []


def archive_old_demo_employees(uid, models):
    allowed_emails = [employee["work_email"] for employee in EMPLOYEES]
    old_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "hr.employee",
        "search",
        [[("work_email", "!=", False), ("work_email", "not in", allowed_emails)]],
    )
    if old_ids:
        models.execute_kw(DB, uid, PASSWORD, "hr.employee", "write", [old_ids, {"active": False}])
        print(f"Archived {len(old_ids)} old demo employee(s).")


def archive_old_demo_users(uid, models):
    allowed_logins = [employee["login"] for employee in EMPLOYEES]
    employee_names = [employee["name"] for employee in EMPLOYEES]
    old_user_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.users",
        "search",
        [[("name", "in", employee_names), ("login", "not in", allowed_logins), ("active", "=", True)]],
    )
    if old_user_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.users", "write", [old_user_ids, {"active": False}])
        print(f"Archived {len(old_user_ids)} old demo user(s).")


def ensure_user(uid, models, employee, group_ids):
    partner_id, _ = create_or_update(
        uid,
        models,
        "res.partner",
        [("email", "=", employee["work_email"])],
        {
            "name": employee["name"],
            "email": employee["work_email"],
            "phone": employee["work_phone"],
            "mobile": employee["mobile_phone"],
            "active": True,
        },
        fields=["id"],
    )

    user_group_ids = resolve_groups(group_ids, employee["role"])
    values = {
        "name": employee["name"],
        "login": employee["login"],
        "email": employee["work_email"],
        "partner_id": partner_id,
        "groups_id": [(6, 0, user_group_ids)],
        "password": DEFAULT_PASSWORD,
        "active": True,
    }
    user_id, created = create_or_update(
        uid,
        models,
        "res.users",
        [("login", "=", employee["login"])],
        values,
        fields=["id", "name"],
    )
    return user_id, created


def run():
    uid, models = connect()

    print("Syncing Iron Zone role groups...")
    group_ids = ensure_iron_zone_groups(uid, models)
    assign_admin_group(uid, models, group_ids)
    ensure_role_security(uid, models, group_ids)

    department_ids = {}
    print("Syncing employee departments...")
    for department in DEPARTMENTS:
        department_id, created = create_or_update(
            uid,
            models,
            "hr.department",
            [("name", "=", department["name"])],
            department,
            fields=["id", "name"],
        )
        department_ids[department["name"]] = department_id
        action = "Created" if created else "Updated"
        print(f"  {action} department: {department['name']}")

    job_ids = {}
    print("Syncing employee job positions...")
    for job in JOBS:
        values = {
            "name": job["name"],
            "department_id": department_ids[job["department"]],
        }
        job_id, created = create_or_update(
            uid,
            models,
            "hr.job",
            [("name", "=", job["name"])],
            values,
            fields=["id", "name"],
        )
        job_ids[job["name"]] = job_id
        action = "Created" if created else "Updated"
        print(f"  {action} job position: {job['name']}")

    created_count = 0
    updated_count = 0
    user_created_count = 0
    user_updated_count = 0
    archive_old_demo_employees(uid, models)
    archive_old_demo_users(uid, models)

    print("Syncing users and employees...")
    for employee in EMPLOYEES:
        user_id, user_created = ensure_user(uid, models, employee, group_ids)
        values = {
            "name": employee["name"],
            "job_title": employee["job"],
            "job_id": job_ids[employee["job"]],
            "department_id": department_ids[employee["department"]],
            "work_email": employee["work_email"],
            "mobile_phone": employee["mobile_phone"],
            "work_phone": employee["work_phone"],
            "user_id": user_id,
            "active": True,
        }
        _, created = create_or_update(
            uid,
            models,
            "hr.employee",
            [("work_email", "=", employee["work_email"])],
            values,
            fields=["id", "name"],
        )
        created_count += int(created)
        updated_count += int(not created)
        user_created_count += int(user_created)
        user_updated_count += int(not user_created)
        action = "Created" if created else "Updated"
        user_action = "created" if user_created else "updated"
        print(f"  {action} employee: {employee['name']} ({employee['job']}) - user {user_action}")

    print(
        "Done: "
        f"{created_count} employees created, {updated_count} updated; "
        f"{user_created_count} users created, {user_updated_count} updated."
    )


if __name__ == "__main__":
    run()
