from config import DB, PASSWORD, connect


SALE_ORDER_PREFIXES = ["SEED04-SALE", "ACT006-SUBSCRIPTION", "ACT006-MEMBERSHIP"]

PORTAL_CUSTOMER_EMAILS = [
    "pruebasjos04@gmail.com",
    "pruebasjos07@gmail.com",
    "pruebasjos08@gmail.com",
]

SUBSCRIPTION_PRODUCT_NAMES = [
    "Suscripcion Mensual",
    "Suscripcion Trimestral",
    "Suscripcion Anual",
    "Plan Nutricion + Gym",
    "Plan Nutrición + Gym",
    "Plan NutriciÃ³n + Gym",
    "Membresia Mensual",
    "Membresía Mensual",
    "MembresÃ­a Mensual",
    "Membresia Trimestral",
    "Membresía Trimestral",
    "MembresÃ­a Trimestral",
    "Membresia Anual",
    "Membresía Anual",
    "MembresÃ­a Anual",
]

LEGACY_PRODUCT_NAMES = [
    "Clase de Spinning",
    "Clase de CrossFit",
    "Entrenamiento Personal",
    "Guantes de Boxeo",
    "Botella Proteina Whey 1kg",
    "Botella Proteína Whey 1kg",
    "Botella ProteÃ­na Whey 1kg",
    "Creatina Monohidratada 300g",
    "Cuerda para Saltar",
    "Agua Mineral",
]

EMPLOYEE_LOGINS = [
    "carlos.mendez@ironzone.ec",
    "sofia.garcia@ironzone.ec",
    "ana.torres@ironzone.ec",
    "luis.herrera@ironzone.ec",
    "mateo.ruiz@ironzone.ec",
    "valentina.paredes@ironzone.ec",
    "gabriela.salazar@ironzone.ec",
    "diego.molina@ironzone.ec",
    "elena.castro@ironzone.ec",
    "roberto.lima@ironzone.ec",
    "paula.naranjo@ironzone.ec",
    "andres.vega@ironzone.ec",
    "camila.ortiz@ironzone.ec",
    "nicolas.benitez@ironzone.ec",
    "isabel.romero@ironzone.ec",
    "ricardo.ponce@ironzone.ec",
]

EMPLOYEE_NAMES = [
    "Carlos Mendez",
    "Sofia Garcia",
    "Ana Torres",
    "Luis Herrera",
    "Mateo Ruiz",
    "Valentina Paredes",
    "Gabriela Salazar",
    "Diego Molina",
    "Elena Castro",
    "Roberto Lima",
    "Paula Naranjo",
    "Andres Vega",
    "Camila Ortiz",
    "Nicolas Benitez",
    "Isabel Romero",
    "Ricardo Ponce",
]

JOB_NAMES = [
    "Instructor de CrossFit",
    "Instructor de Yoga",
    "Recepcionista de Suscripciones",
    "Administrador de Suscripciones",
    "Recepcionista de Membresias",
    "Administrador de Membresias",
    "Asesor Comercial",
    "Ejecutivo de Ventas",
    "Analista de Facturacion",
    "Contador",
    "Analista de Recursos Humanos",
    "Coordinador de Recursos Humanos",
    "Coordinador de Operaciones",
    "Tecnico de Mantenimiento",
    "Especialista en Email Marketing",
    "Coordinador de Campanas",
    "Editor de Sitio web y eCommerce",
    "Coordinador de Eventos",
]

DEPARTMENT_NAMES = [
    "Administracion",
    "Entrenamiento",
    "Atencion al Cliente",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
    "Mantenimiento",
    "Marketing",
    "Seguridad",
]

CLASS_NAMES = [
    "CrossFit AM",
    "Yoga Principiantes",
    "Spinning 18:00",
    "Zumba Cardio",
    "Pilates Avanzado",
    "HIIT Entrenamiento",
    "Boxeo Tecnica",
    "Yoga Avanzado",
    "Natacion Adultos",
    "Entrenamiento en Grupo",
    "Tae Kwon Do Ninos",
    "Danza Contemporanea",
    "Musculacion Personalizada",
    "Acuagym",
    "Funcional Boot Camp",
    "Meditacion Mindfulness",
]


def execute(models, model, method, *args, **kwargs):
    return models.execute_kw(DB, UID, PASSWORD, model, method, list(args), kwargs)


def search(models, model, domain):
    return execute(models, model, "search", domain, context={"active_test": False})


def search_read(models, model, domain, fields):
    return execute(
        models,
        model,
        "search_read",
        domain,
        fields=fields,
        context={"active_test": False},
    )


def model_has_field(models, model, field_name):
    fields = execute(models, model, "fields_get", [field_name])
    return field_name in fields


def try_call(label, func):
    try:
        return func()
    except Exception as error:
        print(f"  Skipped {label}: {error}")
        return None


def archive_records(models, model, ids, label, values=None):
    if not ids:
        return
    archived = 0
    archive_values = values or {"active": False}
    for record_id in ids:
        if try_call(
            f"archive {label} {record_id}",
            lambda rid=record_id: execute(models, model, "write", [rid], archive_values),
        ):
            archived += 1
    print(f"{label}: {archived} archived.")


def unlink_records(models, model, ids, label):
    if not ids:
        return
    deleted = 0
    for record_id in ids:
        if try_call(f"unlink {label} {record_id}", lambda rid=record_id: execute(models, model, "unlink", [rid])):
            deleted += 1
    print(f"{label}: {deleted} deleted.")


def hide_records(models, model, ids, label, values=None):
    if not ids:
        return
    if model_has_field(models, model, "active"):
        archive_records(models, model, ids, label, values=values)
        return
    print(f"{label}: {len(ids)} kept; model has no active field.")


def order_ref_domain():
    domain = []
    for prefix in SALE_ORDER_PREFIXES:
        if domain:
            domain.insert(0, "|")
        domain.append(("client_order_ref", "ilike", prefix))
    return domain


def invoice_origin_domain():
    domain = []
    for prefix in SALE_ORDER_PREFIXES:
        if domain:
            domain.insert(0, "|")
        domain.append(("invoice_origin", "ilike", prefix))
    return domain


def move_domain():
    return [
        ("move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"]),
    ]


def cancel_and_remove_account_moves(models):
    move_ids = search(models, "account.move", move_domain())

    payment_ids = search(models, "account.payment", [])
    for payment_id in payment_ids:
        try_call(f"cancel payment {payment_id}", lambda pid=payment_id: execute(models, "account.payment", "action_cancel", [pid]))

    for move_id in move_ids:
        try_call(f"reset invoice {move_id}", lambda mid=move_id: execute(models, "account.move", "button_draft", [mid]))
        try_call(f"cancel invoice {move_id}", lambda mid=move_id: execute(models, "account.move", "button_cancel", [mid]))
    print(f"Payments targeted: {len(payment_ids)}")
    print(f"Account moves targeted: {len(move_ids)}")


def cancel_and_remove_sale_orders(models):
    order_ids = search(models, "sale.order", [])
    for order_id in order_ids:
        try_call(
            f"cancel sale order {order_id}",
            lambda oid=order_id: execute(
                models,
                "sale.order",
                "action_cancel",
                [oid],
                context={"disable_cancel_warning": True},
            ),
        )
    print(f"Sale orders targeted: {len(order_ids)}")


def wipe_events(models):
    event_ids = search(models, "event.event", [("name", "in", CLASS_NAMES)])
    registration_ids = search(models, "event.registration", [("event_id", "in", event_ids)])
    ticket_ids = search(models, "event.event.ticket", [("event_id", "in", event_ids)])
    attachment_ids = search(
        models,
        "ir.attachment",
        [("res_model", "=", "event.event"), ("res_id", "in", event_ids), ("name", "=", "event_cover")],
    )
    hide_records(models, "event.registration", registration_ids, "Event registrations")
    hide_records(models, "event.event.ticket", ticket_ids, "Event tickets")
    unlink_records(models, "ir.attachment", attachment_ids, "Event covers")
    hide_records(models, "event.event", event_ids, "Events")


def wipe_subscriptions(models):
    subscription_ids = search(models, "sale.subscription", [])
    hide_records(models, "sale.subscription", subscription_ids, "Subscriptions")

    benefit_ids = search(models, "iz.subscription.benefit", [])
    hide_records(models, "iz.subscription.benefit", benefit_ids, "Subscription benefits")

    plan_ids = search(models, "iz.subscription.plan", [])
    hide_records(models, "iz.subscription.plan", plan_ids, "Subscription plans")


def wipe_products(models):
    product_names = SUBSCRIPTION_PRODUCT_NAMES + LEGACY_PRODUCT_NAMES
    product_ids = search(models, "product.template", [("name", "in", product_names)])
    for product_id in product_ids:
        try_call(
            f"archive product {product_id}",
            lambda pid=product_id: execute(
                models,
                "product.template",
                "write",
                [pid],
                {
                    "active": False,
                    "sale_ok": False,
                    "purchase_ok": False,
                    "is_published": False,
                    "website_published": False,
                },
            ),
        )
    print(f"Products archived: {len(product_ids)}")

    vendor_ids = search(models, "res.partner", [("name", "=", "Proveedor Iron Zone")])
    for vendor_id in vendor_ids:
        try_call(f"archive vendor {vendor_id}", lambda vid=vendor_id: execute(models, "res.partner", "write", [vid], {"active": False}))


def wipe_people(models):
    users = search(models, "res.users", [("login", "in", EMPLOYEE_LOGINS + PORTAL_CUSTOMER_EMAILS)])
    for user_id in users:
        try_call(
            f"archive user {user_id}",
            lambda current_user_id=user_id: execute(
                models,
                "res.users",
                "write",
                [current_user_id],
                {"active": False},
            ),
        )

    employees = search(models, "hr.employee", [("name", "in", EMPLOYEE_NAMES)])
    for employee_id in employees:
        try_call(
            f"archive employee {employee_id}",
            lambda eid=employee_id: execute(models, "hr.employee", "write", [eid], {"active": False}),
        )

    partners = search(models, "res.partner", ["|", ("email", "in", PORTAL_CUSTOMER_EMAILS), ("name", "in", EMPLOYEE_NAMES)])
    for partner_id in partners:
        try_call(
            f"archive partner {partner_id}",
            lambda pid=partner_id: execute(models, "res.partner", "write", [pid], {"active": False}),
        )


def wipe_hr_config(models):
    jobs = search(models, "hr.job", [("name", "in", JOB_NAMES)])
    hide_records(models, "hr.job", jobs, "Jobs")

    departments = search(models, "hr.department", [("name", "in", DEPARTMENT_NAMES)])
    hide_records(models, "hr.department", departments, "Departments")


def wipe_categories(models):
    public_categories = search(
        models,
        "product.public.category",
        [("name", "in", ["Suscripciones", "Membresias", "Membresías", "MembresÃ­as"])],
    )
    hide_records(models, "product.public.category", public_categories, "Public categories")

    categories = search(
        models,
        "product.category",
        [("name", "in", ["Iron Zone", "Servicios", "Suscripciones", "Planes integrales"])],
    )
    if categories:
        print(f"Product categories kept: {len(categories)}")


def run():
    global UID
    UID, models = connect()
    print("Cleaning generated Iron Zone seed data...")

    wipe_events(models)
    cancel_and_remove_account_moves(models)
    cancel_and_remove_sale_orders(models)
    wipe_subscriptions(models)
    wipe_products(models)
    wipe_people(models)
    wipe_hr_config(models)
    wipe_categories(models)

    print("Seed data cleanup completed.")


if __name__ == "__main__":
    UID = None
    run()
