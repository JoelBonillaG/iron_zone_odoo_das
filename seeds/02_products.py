import base64
import os

from config import DB, PASSWORD, connect, create


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "search_read",
        [domain],
        {"fields": fields or ["id"], "limit": 1},
    )
    return records[0] if records else None


def search_read(uid, models, model, domain, fields, **kwargs):
    options = {"fields": fields}
    options.update(kwargs)
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], options)


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


def ensure_subscription_templates(uid, models):
    if not model_exists(uid, models, "sale.subscription.template"):
        print("Subscriptions addon is not installed yet. Products will be synced without recurring templates.")
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
    for template in templates:
        template_id, created = create_or_update(
            uid,
            models,
            "sale.subscription.template",
            [("name", "=", template["name"])],
            template,
            fields=["id", "name"],
        )
        template_ids[template["name"]] = template_id
        action = "Created" if created else "Updated"
        print(f"  {action} subscription template: {template['name']}")

    return template_ids


def ensure_subscription_plans(uid, models):
    if not model_exists(uid, models, "iz.subscription.plan"):
        print("Subscription benefit models are not installed yet. Products will be synced without plans.")
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


def unpublish_duplicate_templates(uid, models, product_names, product_fields):
    publish_field = "website_published" if "website_published" in product_fields else "is_published"

    for name in product_names:
        templates = search_read(
            uid,
            models,
            "product.template",
            [("name", "=", name)],
            ["id", "name", publish_field],
            order="id asc",
        )
        if len(templates) <= 1:
            continue

        canonical = templates[0]
        duplicate_ids = [record["id"] for record in templates[1:]]
        models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.template",
            "write",
            [duplicate_ids, {publish_field: False}],
        )
        print(
            f"  Unpublished {len(duplicate_ids)} duplicate(s) for '{name}'. "
            f"Canonical template kept: {canonical['id']}"
        )


def archive_legacy_products(uid, models, product_fields):
    legacy_names = [
        "Clase de Spinning",
        "Clase de CrossFit",
        "Entrenamiento Personal",
        "Guantes de Boxeo",
        "Botella Proteina Whey 1kg",
        "Botella Proteína Whey 1kg",
        "Creatina Monohidratada 300g",
        "Cuerda para Saltar",
        "Agua Mineral",
    ]
    products = search_read(
        uid,
        models,
        "product.template",
        [("name", "in", legacy_names)],
        ["id", "name"],
    )
    if not products:
        return

    values = {}
    for field, value in {
        "active": False,
        "sale_ok": False,
        "purchase_ok": False,
        "is_published": False,
        "website_published": False,
        "subscribable": False,
        "subscription_template_id": False,
    }.items():
        if field in product_fields:
            values[field] = value

    product_ids = [product["id"] for product in products]
    models.execute_kw(DB, uid, PASSWORD, "product.template", "write", [product_ids, values])
    print("Archived non-subscription products:", ", ".join(product["name"] for product in products))


def archive_non_subscription_subscribable_products(uid, models, product_fields, allowed_names):
    if "subscribable" not in product_fields:
        return

    products = search_read(
        uid,
        models,
        "product.template",
        [("subscribable", "=", True), ("name", "not in", allowed_names)],
        ["id", "name"],
    )
    if not products:
        return

    values = {"subscribable": False, "subscription_template_id": False}
    for field, value in {
        "subscription_plan_id": False,
        "sale_ok": False,
        "purchase_ok": False,
        "is_published": False,
        "website_published": False,
        "active": False,
    }.items():
        if field in product_fields:
            values[field] = value

    product_ids = [product["id"] for product in products]
    models.execute_kw(DB, uid, PASSWORD, "product.template", "write", [product_ids, values])
    print(
        "Archived non-subscription recurring products:",
        ", ".join(product["name"] for product in products),
    )


def rename_legacy_subscription_records(uid, models):
    product_name_map = {
        "Membresía Mensual": "Suscripcion Mensual",
        "MembresÃ­a Mensual": "Suscripcion Mensual",
        "Membresía Trimestral": "Suscripcion Trimestral",
        "MembresÃ­a Trimestral": "Suscripcion Trimestral",
        "Membresía Anual": "Suscripcion Anual",
        "MembresÃ­a Anual": "Suscripcion Anual",
    }
    for old_name, new_name in product_name_map.items():
        products = search_read(
            uid,
            models,
            "product.template",
            [("name", "=", old_name)],
            ["id", "name"],
        )
        if products:
            models.execute_kw(
                DB,
                uid,
                PASSWORD,
                "product.template",
                "write",
                [[product["id"] for product in products], {"name": new_name}],
            )

    category_name_map = {
        "Membresias": "Suscripciones",
        "Membresías": "Suscripciones",
        "MembresÃ­as": "Suscripciones",
    }
    for model in ("product.category", "product.public.category"):
        for old_name, new_name in category_name_map.items():
            categories = search_read(
                uid,
                models,
                model,
                [("name", "=", old_name)],
                ["id", "name"],
            )
            if categories:
                models.execute_kw(
                    DB,
                    uid,
                    PASSWORD,
                    model,
                    "write",
                    [[category["id"] for category in categories], {"name": new_name}],
                )


def ensure_internal_categories(uid, models):
    root_id, _ = create_or_update(
        uid,
        models,
        "product.category",
        [("name", "=", "Iron Zone")],
        {"name": "Iron Zone"},
        fields=["id", "name"],
    )
    services_id, _ = create_or_update(
        uid,
        models,
        "product.category",
        [("name", "=", "Servicios"), ("parent_id", "=", root_id)],
        {"name": "Servicios", "parent_id": root_id},
        fields=["id", "name"],
    )
    subscriptions_id, _ = create_or_update(
        uid,
        models,
        "product.category",
        [("name", "=", "Suscripciones"), ("parent_id", "=", services_id)],
        {"name": "Suscripciones", "parent_id": services_id},
        fields=["id", "name"],
    )
    nutrition_id, _ = create_or_update(
        uid,
        models,
        "product.category",
        [("name", "=", "Planes integrales"), ("parent_id", "=", subscriptions_id)],
        {"name": "Planes integrales", "parent_id": subscriptions_id},
        fields=["id", "name"],
    )

    print("Synced internal product categories: Iron Zone / Servicios / Suscripciones")
    return {
        "subscriptions": subscriptions_id,
        "nutrition": nutrition_id,
    }


def run():
    uid, models = connect()
    product_fields = get_model_fields(uid, models, "product.template")
    subscription_template_ids = ensure_subscription_templates(uid, models)
    subscription_plan_ids = ensure_subscription_plans(uid, models)
    rename_legacy_subscription_records(uid, models)
    internal_categories = ensure_internal_categories(uid, models)

    image_path = os.path.join(os.path.dirname(__file__), "images", "products")
    logo_path = os.path.join(os.path.dirname(__file__), "IronZone.png")

    def get_image(filename):
        path = os.path.join(image_path, filename)
        if not os.path.exists(path):
            svg_filename = filename.rsplit(".", 1)[0] + ".svg"
            path = os.path.join(image_path, svg_filename)
        if not os.path.exists(path):
            path = logo_path
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    print("Syncing eCommerce categories...")
    categ_subscriptions, _ = create_or_update(
        uid,
        models,
        "product.public.category",
        [("name", "=", "Suscripciones")],
        {"name": "Suscripciones"},
    )

    products = [
        {
            "name": "Suscripcion Mensual",
            "list_price": 35.00,
            "standard_price": 0.0,
            "type": "service",
            "description_sale": "Acceso ilimitado por 1 mes a zona de fuerza, cardio y clases base.",
            "categ_id": internal_categories["subscriptions"],
            "public_categ_ids": [(6, 0, [categ_subscriptions])],
            "_subscription_template": "Mensual",
            "_subscription_plan": "IZ_B01",
            "_img": "membership_basic.png",
            "description_ecommerce": """
                <p>Ideal para clientes que quieren comenzar con flexibilidad y acceso completo al club.</p>
                <ul>
                    <li>Ingreso libre durante el horario habitual.</li>
                    <li>Acceso a musculacion, cardio y zonas funcionales.</li>
                    <li>Facturacion recurrente mensual.</li>
                </ul>
            """,
        },
        {
            "name": "Suscripcion Trimestral",
            "list_price": 90.00,
            "standard_price": 0.0,
            "type": "service",
            "description_sale": "Acceso ilimitado por 3 meses con mejor relacion costo / permanencia.",
            "categ_id": internal_categories["subscriptions"],
            "public_categ_ids": [(6, 0, [categ_subscriptions])],
            "_subscription_template": "Trimestral",
            "_subscription_plan": "IZ_P01",
            "_img": "membership_trim.png",
            "description_ecommerce": """
                <p>Recomendada para clientes que ya decidieron comprometerse con una etapa real de progreso fisico.</p>
                <ul>
                    <li>Mejor costo promedio mensual.</li>
                    <li>Facturacion recurrente cada tres meses.</li>
                    <li>Buena base para beneficios de permanencia.</li>
                </ul>
            """,
        },
        {
            "name": "Suscripcion Anual",
            "list_price": 300.00,
            "standard_price": 0.0,
            "type": "service",
            "description_sale": "Acceso ilimitado por 12 meses para clientes que priorizan continuidad.",
            "categ_id": internal_categories["subscriptions"],
            "public_categ_ids": [(6, 0, [categ_subscriptions])],
            "_subscription_template": "Anual",
            "_subscription_plan": "IZ_PR01",
            "_img": "membership_gold.png",
            "description_ecommerce": """
                <p>El plan mas conveniente para quienes entrenan con vision de largo plazo.</p>
                <ul>
                    <li>Doce meses de acceso al ecosistema del gimnasio.</li>
                    <li>Facturacion recurrente anual.</li>
                    <li>Base ideal para clientes recurrentes y comunidad fiel.</li>
                </ul>
            """,
        },
        {
            "name": "Plan Nutrición + Gym",
            "list_price": 75.00,
            "standard_price": 10.0,
            "type": "service",
            "description_sale": "Paquete mensual de asesoria nutricional y acceso al gimnasio.",
            "categ_id": internal_categories["nutrition"],
            "public_categ_ids": [(6, 0, [categ_subscriptions])],
            "_subscription_template": "Mensual",
            "_subscription_plan": "IZ_I01",
            "_img": "combo_plan.png",
            "description_ecommerce": """
                <p>Propuesta integral para clientes que quieren acompanar entrenamiento con guia alimentaria basica.</p>
                <ul>
                    <li>Combina suscripcion con componente de nutricion.</li>
                    <li>Facturacion recurrente mensual.</li>
                    <li>Ideal para campanas y ofertas de captacion.</li>
                </ul>
            """,
        },
    ]

    archive_legacy_products(uid, models, product_fields)
    archive_non_subscription_subscribable_products(
        uid,
        models,
        product_fields,
        [product["name"] for product in products],
    )

    created_count = 0
    updated_count = 0
    for product in products:
        img_file = product.pop("_img", None)
        subscription_template_name = product.pop("_subscription_template", None)
        subscription_plan_code = product.pop("_subscription_plan", None)

        product["sale_ok"] = True
        product["purchase_ok"] = False
        product["is_published"] = True
        if "website_published" in product_fields:
            product["website_published"] = True
        if "subscribable" in product_fields:
            product["subscribable"] = bool(subscription_template_name and subscription_template_ids)
        if "subscription_template_id" in product_fields:
            product["subscription_template_id"] = subscription_template_ids.get(subscription_template_name, False)
        if "subscription_plan_id" in product_fields:
            product["subscription_plan_id"] = subscription_plan_ids.get(subscription_plan_code, False)
        if img_file:
            product["image_1920"] = get_image(img_file)

        template_id, created = create_or_update(
            uid,
            models,
            "product.template",
            [("name", "=", product["name"])],
            product,
            fields=["id", "name"],
        )

        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        print(f"  {action} subscription product: {product['name']} (Template ID: {template_id})")

    unpublish_duplicate_templates(uid, models, [product["name"] for product in products], product_fields)
    print(f"Done: {created_count} created, {updated_count} updated.")


if __name__ == "__main__":
    run()
