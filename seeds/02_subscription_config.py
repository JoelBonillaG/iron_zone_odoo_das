"""
02_subscription_config.py
--------------------------
Seeds subscription templates, plans, stages, tags, close reasons, and benefits.
Must run before 03_products.py so products can reference templates and plans.
"""
from config import DB, PASSWORD, connect, create


def search_read(uid, models, model, domain, fields, **kwargs):
    options = {"fields": fields}
    options.update(kwargs)
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], options)


def search_one(uid, models, model, domain, fields=None):
    rows = search_read(uid, models, model, domain, fields or ["id"], limit=1)
    return rows[0] if rows else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def get_model_fields(uid, models, model):
    return models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})


def model_exists(uid, models, model):
    try:
        get_model_fields(uid, models, model)
        return True
    except Exception:
        return False


# ─── Subscription Templates ────────────────────────────────────────────────────

def ensure_subscription_templates(uid, models):
    if not model_exists(uid, models, "sale.subscription.template"):
        print("  sale.subscription.template not found — skipping.")
        return {}

    templates = [
        {
            "name": "Mensual",
            "code": "IZ_B01",
            "recurring_interval": 1,
            "recurring_rule_type": "months",
            "recurring_rule_boundary": "unlimited",
            "recurring_rule_count": 1,
            "invoicing_mode": "draft",
            "description": "Facturacion recurrente mensual para suscripciones Iron Zone.",
        },
        {
            "name": "Trimestral",
            "code": "IZ_P01",
            "recurring_interval": 3,
            "recurring_rule_type": "months",
            "recurring_rule_boundary": "unlimited",
            "recurring_rule_count": 3,
            "invoicing_mode": "draft",
            "description": "Facturacion recurrente cada tres meses para suscripciones Iron Zone.",
        },
        {
            "name": "Anual",
            "code": "IZ_PR01",
            "recurring_interval": 1,
            "recurring_rule_type": "years",
            "recurring_rule_boundary": "unlimited",
            "recurring_rule_count": 12,
            "invoicing_mode": "draft",
            "description": "Facturacion recurrente anual para suscripciones Iron Zone.",
        },
    ]

    template_ids = {}
    print("Syncing subscription templates...")
    for tmpl in templates:
        tmpl_id, created = create_or_update(
            uid, models, "sale.subscription.template",
            [("name", "=", tmpl["name"])], tmpl, fields=["id", "name"],
        )
        template_ids[tmpl["name"]] = tmpl_id
        action = "Created" if created else "Updated"
        print(f"  {action} subscription template: {tmpl['name']}")
    return template_ids


# ─── Subscription Stages ───────────────────────────────────────────────────────

def ensure_stages(uid, models):
    stages = [
        {"type": "draft",       "name": "Borrador",          "sequence": 0, "description": "Suscripcion en preparacion o pendiente de completar."},
        {"type": "pre",         "name": "Lista para iniciar","sequence": 1, "description": "Suscripcion creada y lista para activarse segun fecha o pago."},
        {"type": "in_progress", "name": "Activa",            "sequence": 2, "description": "Suscripcion vigente. La facturacion recurrente puede generar nuevas facturas."},
        {"type": "post",        "name": "Cerrada",           "sequence": 3, "description": "Suscripcion finalizada, cancelada o sin renovacion."},
    ]
    print("Syncing subscription stages...")
    for stage in stages:
        stage_id, created = create_or_update(
            uid, models, "sale.subscription.stage",
            [("type", "=", stage["type"])], stage, fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} stage: {stage['name']} ({stage_id})")


# ─── Subscription Plans ────────────────────────────────────────────────────────

def ensure_subscription_plans(uid, models):
    if not model_exists(uid, models, "iz.subscription.plan"):
        print("  iz.subscription.plan not found — skipping plans and benefits.")
        return {}

    plans = [
        {"name": "IronZone Basico",   "code": "IZ_B01",  "sequence": 10, "priority": 10, "description": "Plan base para clientes que empiezan con acceso y beneficios iniciales."},
        {"name": "IronZone Pro",      "code": "IZ_P01",  "sequence": 20, "priority": 20, "description": "Plan intermedio para clientes con mayor permanencia y beneficios superiores."},
        {"name": "IronZone Premium",  "code": "IZ_PR01", "sequence": 30, "priority": 30, "description": "Plan alto para clientes anuales con beneficios completos en clases."},
        {"name": "IronZone Integral", "code": "IZ_I01",  "sequence": 40, "priority": 40, "description": "Plan integral para clientes con entrenamiento y acompanamiento nutricional."},
    ]

    plan_ids = {}
    print("Syncing subscription plans...")
    for plan in plans:
        plan_id, created = create_or_update(
            uid, models, "iz.subscription.plan",
            [("code", "=", plan["code"])], plan, fields=["id", "name"],
        )
        plan_ids[plan["code"]] = plan_id
        action = "Created" if created else "Updated"
        print(f"  {action} subscription plan: {plan['name']}")
    return plan_ids


# ─── Subscription Benefits ─────────────────────────────────────────────────────

def ensure_subscription_benefits(uid, models, plan_ids):
    if not plan_ids or not model_exists(uid, models, "iz.subscription.benefit"):
        return

    benefits = [
        {"name": "10% en clases grupales",    "plan_code": "IZ_B01",  "sequence": 10, "benefit_scope": "events", "benefit_type": "discount", "discount_percent": 10.0,  "description": "Descuento base para clases y eventos del gimnasio."},
        {"name": "20% en clases grupales",    "plan_code": "IZ_P01",  "sequence": 10, "benefit_scope": "events", "benefit_type": "discount", "discount_percent": 20.0,  "description": "Descuento para clientes con plan trimestral."},
        {"name": "Clases grupales incluidas", "plan_code": "IZ_PR01", "sequence": 10, "benefit_scope": "events", "benefit_type": "free",     "discount_percent": 100.0, "description": "Acceso sin costo a clases y eventos base."},
        {"name": "Clases y nutricion incluidas", "plan_code": "IZ_I01", "sequence": 10, "benefit_scope": "events", "benefit_type": "free", "discount_percent": 100.0, "description": "Acceso incluido a clases base como parte del plan integral."},
    ]

    print("Syncing subscription benefits...")
    for benefit in benefits:
        plan_id = plan_ids.get(benefit.pop("plan_code"))
        if not plan_id:
            continue
        benefit["plan_id"] = plan_id
        _, created = create_or_update(
            uid, models, "iz.subscription.benefit",
            [("plan_id", "=", plan_id), ("name", "=", benefit["name"])],
            benefit, fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} benefit: {benefit['name']}")


# ─── Tags ──────────────────────────────────────────────────────────────────────

def ensure_tags(uid, models):
    tag_names = [
        "Mensual", "Trimestral", "Anual", "Nutricion", "Premium",
        "Familiar", "Corporativa", "Promocion", "Pendiente de pago",
        "Pago confirmado", "Renovacion manual", "Renovacion automatica",
    ]
    print("Syncing subscription tags...")
    tag_ids = {}
    for name in tag_names:
        tag_id, created = create_or_update(
            uid, models, "sale.subscription.tag",
            [("name", "=", name)], {"name": name}, fields=["id", "name"],
        )
        tag_ids[name] = tag_id
        action = "Created" if created else "Updated"
        print(f"  {action} tag: {name}")
    return tag_ids


# ─── Close Reasons ─────────────────────────────────────────────────────────────

def ensure_close_reasons(uid, models):
    old_to_new = {
        "The subscription is too expensive": "Precio elevado",
        "Subscription does not meet my requirements": "No cumple necesidades del cliente",
        "The subscription ended": "Periodo finalizado",
        "I don't really use it": "Bajo uso del servicio",
        "Other": "Otro",
    }
    reasons = [
        "Precio elevado", "No cumple necesidades del cliente", "Periodo finalizado",
        "Bajo uso del servicio", "Cambio de plan", "Falta de pago",
        "Cancelacion solicitada", "Otro",
    ]
    print("Syncing close reasons...")
    for old_name, new_name in old_to_new.items():
        record = search_one(uid, models, "sale.subscription.close.reason", [("name", "=", old_name)], fields=["id"])
        if record:
            models.execute_kw(DB, uid, PASSWORD, "sale.subscription.close.reason", "write", [[record["id"]], {"name": new_name}])
    for reason in reasons:
        _, created = create_or_update(
            uid, models, "sale.subscription.close.reason",
            [("name", "=", reason)], {"name": reason}, fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} close reason: {reason}")


# ─── Main ──────────────────────────────────────────────────────────────────────

def run():
    uid, models = connect()
    ensure_stages(uid, models)
    ensure_subscription_templates(uid, models)
    plan_ids = ensure_subscription_plans(uid, models)
    ensure_subscription_benefits(uid, models, plan_ids)
    ensure_tags(uid, models)
    ensure_close_reasons(uid, models)
    print("Done: subscription base config synced.")


if __name__ == "__main__":
    run()
