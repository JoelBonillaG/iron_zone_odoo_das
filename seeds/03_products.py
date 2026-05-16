import base64
import os

from config import DB, PASSWORD, connect, create


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB, uid, PASSWORD, model, "search_read", [domain],
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
    return models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})


def model_exists(uid, models, model):
    try:
        get_model_fields(uid, models, model)
        return True
    except Exception:
        return False


def xmlid_to_res_id(uid, models, xmlid):
    if "." not in xmlid:
        return False
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid, models, "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    return record["res_id"] if record else False


def find_tax(uid, models, type_tax_use, amount, name_fragments):
    taxes = search_read(
        uid, models, "account.tax",
        [("type_tax_use", "=", type_tax_use), ("amount", "=", amount), ("active", "=", True)],
        ["id", "name"],
    )
    for fragment in name_fragments:
        fragment = fragment.lower()
        for tax in taxes:
            if fragment in str(tax["name"]).lower():
                return tax["id"]
    return taxes[0]["id"] if taxes else False


def ensure_vendor(uid, models):
    country_ec = xmlid_to_res_id(uid, models, "base.ec")
    id_type_ruc = xmlid_to_res_id(uid, models, "l10n_ec.ec_ruc")
    contributor_type = xmlid_to_res_id(uid, models, "l10n_ec_base.contrib_sociedad")

    values = {
        "name": "Proveedor Iron Zone",
        "company_type": "company",
        "is_company": True,
        "supplier_rank": 1,
        "street": "Av. Los Shyris N37-25",
        "city": "Quito",
        "phone": "022345678",
        "email": "proveedor@ironzone.example",
        "vat": "1790016919001",
        "l10n_ec_taxpayer_type": "general",
    }
    if country_ec:
        values["country_id"] = country_ec
    if id_type_ruc:
        values["l10n_latam_identification_type_id"] = id_type_ruc
    if contributor_type:
        values["l10n_ec_contributor_type_id"] = contributor_type

    vendor_id, _ = create_or_update(
        uid, models, "res.partner",
        [("name", "=", values["name"])], values, fields=["id"],
    )
    return vendor_id


def sync_supplierinfo(uid, models, product_tmpl_id, vendor_id, price, currency_id=False):
    if not vendor_id or price <= 0:
        return
    values = {
        "partner_id": vendor_id,
        "product_tmpl_id": product_tmpl_id,
        "min_qty": 1.0,
        "price": price,
        "delay": 2,
    }
    if currency_id:
        values["currency_id"] = currency_id
    create_or_update(
        uid, models, "product.supplierinfo",
        [("partner_id", "=", vendor_id), ("product_tmpl_id", "=", product_tmpl_id), ("min_qty", "=", 1.0)],
        values, fields=["id"],
    )


def configure_delivery_products(uid, models, sale_services_tax, product_fields):
    if not sale_services_tax:
        return
    delivery_templates = models.execute_kw(
        DB, uid, PASSWORD, "product.template", "search_read",
        [["|", "|",
          ("default_code", "ilike", "Delivery"),
          ("name", "ilike", "delivery"),
          ("name", "ilike", "envío")]],
        {"fields": ["id", "name", "default_code"], "limit": 50},
    )
    values = {
        "name": "Envío estándar",
        "default_code": "SHIP-STD",
        "type": "service",
        "sale_ok": False,
        "purchase_ok": False,
        "description_sale": "Servicio de envío estándar.",
        "taxes_id": [(6, 0, [sale_services_tax])],
    }
    if "invoice_policy" in product_fields:
        values["invoice_policy"] = "order"
    for template in delivery_templates:
        models.execute_kw(DB, uid, PASSWORD, "product.template", "write", [[template["id"]], values])
        print(f"  Configured delivery product: {template.get('default_code') or ''} {template['name']} -> SHIP-STD")


def unpublish_duplicate_templates(uid, models, product_names, product_fields):
    publish_field = "website_published" if "website_published" in product_fields else "is_published"
    for name in product_names:
        templates = search_read(
            uid, models, "product.template",
            [("name", "=", name)], ["id", "name", publish_field], order="id asc",
        )
        if len(templates) <= 1:
            continue
        canonical = templates[0]
        duplicate_ids = [r["id"] for r in templates[1:]]
        models.execute_kw(DB, uid, PASSWORD, "product.template", "write", [duplicate_ids, {publish_field: False}])
        print(f"  Unpublished {len(duplicate_ids)} duplicate(s) for '{name}'. Canonical kept: {canonical['id']}")


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
        products = search_read(uid, models, "product.template", [("name", "=", old_name)], ["id", "name"])
        if products:
            models.execute_kw(
                DB, uid, PASSWORD, "product.template", "write",
                [[p["id"] for p in products], {"name": new_name}],
            )

    category_name_map = {
        "Membresias": "Suscripciones",
        "Membresías": "Suscripciones",
        "MembresÃ­as": "Suscripciones",
    }
    for model_name in ("product.category", "product.public.category"):
        for old_name, new_name in category_name_map.items():
            categories = search_read(uid, models, model_name, [("name", "=", old_name)], ["id", "name"])
            if categories:
                models.execute_kw(
                    DB, uid, PASSWORD, model_name, "write",
                    [[c["id"] for c in categories], {"name": new_name}],
                )


def ensure_internal_categories(uid, models):
    root_id, _ = create_or_update(uid, models, "product.category", [("name", "=", "Iron Zone")], {"name": "Iron Zone"}, fields=["id"])
    services_id, _ = create_or_update(uid, models, "product.category", [("name", "=", "Servicios"), ("parent_id", "=", root_id)], {"name": "Servicios", "parent_id": root_id}, fields=["id"])
    subscriptions_id, _ = create_or_update(uid, models, "product.category", [("name", "=", "Suscripciones"), ("parent_id", "=", services_id)], {"name": "Suscripciones", "parent_id": services_id}, fields=["id"])
    nutrition_id, _ = create_or_update(uid, models, "product.category", [("name", "=", "Planes integrales"), ("parent_id", "=", subscriptions_id)], {"name": "Planes integrales", "parent_id": subscriptions_id}, fields=["id"])
    print("Synced internal product categories: Iron Zone / Servicios / Suscripciones")
    return {"subscriptions": subscriptions_id, "nutrition": nutrition_id}


def get_subscription_template_ids(uid, models):
    """Return {name: id} map from already-seeded subscription templates (seeded by 03_subscription_config.py)."""
    if not model_exists(uid, models, "sale.subscription.template"):
        return {}
    templates = search_read(uid, models, "sale.subscription.template", [], ["id", "name"])
    return {t["name"]: t["id"] for t in templates}


def get_subscription_plan_ids(uid, models):
    """Return {code: id} map from already-seeded subscription plans."""
    if not model_exists(uid, models, "iz.subscription.plan"):
        return {}
    plans = search_read(uid, models, "iz.subscription.plan", [], ["id", "code"])
    return {p["code"]: p["id"] for p in plans}


def run():
    uid, models = connect()
    product_fields = get_model_fields(uid, models, "product.template")

    vendor_id = ensure_vendor(uid, models)
    usd = search_one(uid, models, "res.currency", [("name", "=", "USD")], fields=["id"])
    currency_id = usd["id"] if usd else False

    sale_goods_tax = find_tax(uid, models, "sale", 15, ["VAT 15% G", "411, B"])
    sale_services_tax = find_tax(uid, models, "sale", 15, ["VAT 15% S", "411, S"])
    purchase_inventory_tax = find_tax(uid, models, "purchase", 15, ["510 06 I", "Inv Créd", "Inv. Cred"])
    purchase_default_tax = find_tax(uid, models, "purchase", 15, ["510 01", "Créd"])

    rename_legacy_subscription_records(uid, models)
    internal_categories = ensure_internal_categories(uid, models)

    # Fetch subscription templates and plans seeded by 03_subscription_config.py
    subscription_template_ids = get_subscription_template_ids(uid, models)
    subscription_plan_ids = get_subscription_plan_ids(uid, models)

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
        uid, models, "product.public.category",
        [("name", "=", "Suscripciones")], {"name": "Suscripciones"},
    )

    PRODUCTS = [
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
        },
    ]

    created_count = 0
    updated_count = 0
    product_names = [p["name"] for p in PRODUCTS]

    for product in PRODUCTS:
        p = dict(product)
        img_file = p.pop("_img", None)
        subscription_template_name = p.pop("_subscription_template", None)
        subscription_plan_code = p.pop("_subscription_plan", None)

        p["sale_ok"] = True
        p["purchase_ok"] = False
        p["is_published"] = True
        if "invoice_policy" in product_fields:
            p["invoice_policy"] = "order"
        if "taxes_id" in product_fields and sale_services_tax:
            p["taxes_id"] = [(6, 0, [sale_services_tax])]
        if "website_published" in product_fields:
            p["website_published"] = True
        if "subscribable" in product_fields:
            p["subscribable"] = bool(subscription_template_name and subscription_template_ids)
        if "subscription_template_id" in product_fields:
            p["subscription_template_id"] = subscription_template_ids.get(subscription_template_name, False)
        if "subscription_plan_id" in product_fields:
            p["subscription_plan_id"] = subscription_plan_ids.get(subscription_plan_code, False)
        if img_file:
            p["image_1920"] = get_image(img_file)

        template_id, created = create_or_update(
            uid, models, "product.template",
            [("name", "=", p["name"])], p, fields=["id", "name"],
        )
        sync_supplierinfo(uid, models, template_id, vendor_id, product.get("standard_price", 0.0), currency_id)

        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        print(f"  {action} subscription product: {product['name']} (Template ID: {template_id})")

    unpublish_duplicate_templates(uid, models, product_names, product_fields)
    print(f"Done: {created_count} created, {updated_count} updated.")


if __name__ == "__main__":
    run()
