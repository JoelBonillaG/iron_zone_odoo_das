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
    return models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "fields_get",
        [],
        {"attributes": ["type"]},
    )


def model_exists(uid, models, model):
    try:
        get_model_fields(uid, models, model)
        return True
    except Exception:
        return False


def ensure_stages(uid, models):
    stages = [
        {
            "type": "draft",
            "name": "Borrador",
            "sequence": 0,
            "description": "Suscripcion en preparacion o pendiente de completar.",
        },
        {
            "type": "pre",
            "name": "Lista para iniciar",
            "sequence": 1,
            "description": "Suscripcion creada y lista para activarse segun fecha o pago.",
        },
        {
            "type": "in_progress",
            "name": "Activa",
            "sequence": 2,
            "description": "Suscripcion vigente. La facturacion recurrente puede generar nuevas facturas.",
        },
        {
            "type": "post",
            "name": "Cerrada",
            "sequence": 3,
            "description": "Suscripcion finalizada, cancelada o sin renovacion.",
        },
    ]

    print("Syncing subscription stages...")
    for stage in stages:
        stage_id, created = create_or_update(
            uid,
            models,
            "sale.subscription.stage",
            [("type", "=", stage["type"])],
            stage,
            fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} stage: {stage['name']} ({stage_id})")


def ensure_tags(uid, models):
    tag_names = [
        "Mensual",
        "Trimestral",
        "Anual",
        "Nutricion",
        "Premium",
        "Familiar",
        "Corporativa",
        "Promocion",
        "Pendiente de pago",
        "Pago confirmado",
        "Renovacion manual",
        "Renovacion automatica",
    ]

    print("Syncing subscription tags...")
    tag_ids = {}
    for name in tag_names:
        tag_id, created = create_or_update(
            uid,
            models,
            "sale.subscription.tag",
            [("name", "=", name)],
            {"name": name},
            fields=["id", "name"],
        )
        tag_ids[name] = tag_id
        action = "Created" if created else "Updated"
        print(f"  {action} tag: {name}")

    return tag_ids


def ensure_close_reasons(uid, models):
    old_to_new = {
        "The subscription is too expensive": "Precio elevado",
        "Subscription does not meet my requirements": "No cumple necesidades del cliente",
        "The subscription ended": "Periodo finalizado",
        "I don't really use it": "Bajo uso del servicio",
        "Other": "Otro",
    }
    reasons = [
        "Precio elevado",
        "No cumple necesidades del cliente",
        "Periodo finalizado",
        "Bajo uso del servicio",
        "Cambio de plan",
        "Falta de pago",
        "Cancelacion solicitada",
        "Otro",
    ]

    print("Syncing close reasons...")
    for old_name, new_name in old_to_new.items():
        record = search_one(
            uid,
            models,
            "sale.subscription.close.reason",
            [("name", "=", old_name)],
            fields=["id", "name"],
        )
        if record:
            models.execute_kw(
                DB,
                uid,
                PASSWORD,
                "sale.subscription.close.reason",
                "write",
                [[record["id"]], {"name": new_name}],
            )

    for reason in reasons:
        _, created = create_or_update(
            uid,
            models,
            "sale.subscription.close.reason",
            [("name", "=", reason)],
            {"name": reason},
            fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} close reason: {reason}")


def ensure_subscription_plans(uid, models):
    if not model_exists(uid, models, "iz.subscription.plan"):
        print("Subscription benefit models are not installed yet. Skipping plans and benefits.")
        return {}

    plans = [
        {
            "name": "IronZone Basico",
            "code": "IZ_B01",
            "sequence": 10,
            "priority": 10,
            "description": "Plan base para clientes que empiezan con acceso y beneficios iniciales.",
        },
        {
            "name": "IronZone Pro",
            "code": "IZ_P01",
            "sequence": 20,
            "priority": 20,
            "description": "Plan intermedio para clientes con mayor permanencia y beneficios superiores.",
        },
        {
            "name": "IronZone Premium",
            "code": "IZ_PR01",
            "sequence": 30,
            "priority": 30,
            "description": "Plan alto para clientes anuales con beneficios completos en clases.",
        },
        {
            "name": "IronZone Integral",
            "code": "IZ_I01",
            "sequence": 40,
            "priority": 40,
            "description": "Plan integral para clientes con entrenamiento y acompanamiento nutricional.",
        },
    ]

    plan_ids = {}
    print("Syncing subscription plans...")
    for plan in plans:
        plan_id, created = create_or_update(
            uid,
            models,
            "iz.subscription.plan",
            [("code", "=", plan["code"])],
            plan,
            fields=["id", "name"],
        )
        plan_ids[plan["code"]] = plan_id
        action = "Created" if created else "Updated"
        print(f"  {action} subscription plan: {plan['name']}")

    return plan_ids


def ensure_subscription_benefits(uid, models, plan_ids):
    if not plan_ids or not model_exists(uid, models, "iz.subscription.benefit"):
        return

    benefits = [
        {
            "name": "10% en clases grupales",
            "plan_code": "IZ_B01",
            "sequence": 10,
            "benefit_scope": "events",
            "benefit_type": "discount",
            "discount_percent": 10.0,
            "description": "Descuento base para clases y eventos del gimnasio.",
        },
        {
            "name": "20% en clases grupales",
            "plan_code": "IZ_P01",
            "sequence": 10,
            "benefit_scope": "events",
            "benefit_type": "discount",
            "discount_percent": 20.0,
            "description": "Descuento para clientes con plan trimestral.",
        },
        {
            "name": "Clases grupales incluidas",
            "plan_code": "IZ_PR01",
            "sequence": 10,
            "benefit_scope": "events",
            "benefit_type": "free",
            "discount_percent": 100.0,
            "description": "Acceso sin costo a clases y eventos base.",
        },
        {
            "name": "Clases y nutricion incluidas",
            "plan_code": "IZ_I01",
            "sequence": 10,
            "benefit_scope": "events",
            "benefit_type": "free",
            "discount_percent": 100.0,
            "description": "Acceso incluido a clases base como parte del plan integral.",
        },
    ]

    print("Syncing subscription benefits...")
    for benefit in benefits:
        plan_id = plan_ids.get(benefit.pop("plan_code"))
        if not plan_id:
            continue
        benefit["plan_id"] = plan_id
        _, created = create_or_update(
            uid,
            models,
            "iz.subscription.benefit",
            [("plan_id", "=", plan_id), ("name", "=", benefit["name"])],
            benefit,
            fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} benefit: {benefit['name']}")


def tag_existing_subscriptions(uid, models, tag_ids):
    subscriptions = search_read(
        uid,
        models,
        "sale.subscription",
        [],
        ["id", "name", "template_id", "stage_id", "invoice_ids", "sale_subscription_line_ids"],
    )
    if not subscriptions:
        return

    print("Tagging existing subscriptions...")
    for subscription in subscriptions:
        names = set()
        template_name = subscription["template_id"][1] if subscription["template_id"] else ""
        if "Mensual" in template_name:
            names.add("Mensual")
        if "Trimestral" in template_name:
            names.add("Trimestral")
        if "Anual" in template_name:
            names.add("Anual")

        line_ids = subscription.get("sale_subscription_line_ids") or []
        if line_ids:
            lines = search_read(
                uid,
                models,
                "sale.subscription.line",
                [("id", "in", line_ids)],
                ["product_id"],
            )
            product_names = " ".join(line["product_id"][1] for line in lines if line["product_id"])
            if "Nutricion" in product_names or "Nutrición" in product_names:
                names.add("Nutricion")

        invoice_ids = subscription.get("invoice_ids") or []
        if invoice_ids:
            invoices = search_read(
                uid,
                models,
                "account.move",
                [("id", "in", invoice_ids)],
                ["payment_state"],
            )
            if any(invoice["payment_state"] == "paid" for invoice in invoices):
                names.add("Pago confirmado")
            else:
                names.add("Pendiente de pago")

        ids = [tag_ids[name] for name in sorted(names) if name in tag_ids]
        if ids:
            models.execute_kw(
                DB,
                uid,
                PASSWORD,
                "sale.subscription",
                "write",
                [[subscription["id"]], {"tag_ids": [(6, 0, ids)]}],
            )
            print(f"  Tagged {subscription['name']}: {', '.join(sorted(names))}")


def assign_subscription_levels(uid, models):
    if not model_exists(uid, models, "iz.subscription.plan"):
        return

    subscriptions = search_read(
        uid,
        models,
        "sale.subscription",
        [],
        ["id", "name", "subscription_plan_id", "sale_subscription_line_ids"],
    )
    if not subscriptions:
        return

    print("Assigning plans to existing subscriptions...")
    for subscription in subscriptions:
        if subscription.get("subscription_plan_id"):
            continue
        line_ids = subscription.get("sale_subscription_line_ids") or []
        if not line_ids:
            continue
        lines = search_read(
            uid,
            models,
            "sale.subscription.line",
            [("id", "in", line_ids)],
            ["product_id"],
        )
        product_ids = [line["product_id"][0] for line in lines if line.get("product_id")]
        if not product_ids:
            continue
        products = search_read(
            uid,
            models,
            "product.product",
            [("id", "in", product_ids)],
            ["product_tmpl_id"],
        )
        template_ids = [
            product["product_tmpl_id"][0]
            for product in products
            if product.get("product_tmpl_id")
        ]
        if not template_ids:
            continue
        templates = search_read(
            uid,
            models,
            "product.template",
            [("id", "in", template_ids)],
            ["subscription_plan_id"],
        )
        plan_ids = [
            template["subscription_plan_id"][0]
            for template in templates
            if template.get("subscription_plan_id")
        ]
        if not plan_ids:
            continue
        plans = search_read(
            uid,
            models,
            "iz.subscription.plan",
            [("id", "in", plan_ids)],
            ["priority", "sequence"],
            order="priority desc, sequence asc, id asc",
            limit=1,
        )
        if not plans:
            continue
        models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "sale.subscription",
            "write",
            [[subscription["id"]], {"subscription_plan_id": plans[0]["id"]}],
        )
        print(f"  Assigned plan to {subscription['name']}: {plans[0]['id']}")


def run():
    uid, models = connect()
    ensure_stages(uid, models)
    tag_ids = ensure_tags(uid, models)
    ensure_close_reasons(uid, models)
    plan_ids = ensure_subscription_plans(uid, models)
    ensure_subscription_benefits(uid, models, plan_ids)
    assign_subscription_levels(uid, models)
    tag_existing_subscriptions(uid, models, tag_ids)
    print("Done: subscription configuration synced.")


if __name__ == "__main__":
    run()
