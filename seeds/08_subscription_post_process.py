"""
08_subscription_post_process.py
--------------------------------
Post-processing for subscriptions: assigns plans and tags to subscriptions
that were created by 04_sale_orders.py and 05_accounting_invoices.py.
Runs AFTER subscriptions exist.
"""
from config import DB, PASSWORD, connect


def search_read(uid, models, model, domain, fields, **kwargs):
    options = {"fields": fields}
    options.update(kwargs)
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], options)


def search_one(uid, models, model, domain, fields=None):
    rows = search_read(uid, models, model, domain, fields or ["id"], limit=1)
    return rows[0] if rows else None


def model_exists(uid, models, model):
    try:
        models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})
        return True
    except Exception:
        return False


def assign_subscription_levels(uid, models):
    """Assign the highest-priority plan to subscriptions that don't have one yet."""
    if not model_exists(uid, models, "iz.subscription.plan"):
        return

    subscriptions = search_read(
        uid, models, "sale.subscription", [],
        ["id", "name", "subscription_plan_id", "sale_subscription_line_ids"],
    )
    if not subscriptions:
        return

    print("Assigning plans to existing subscriptions...")
    for sub in subscriptions:
        if sub.get("subscription_plan_id"):
            continue
        line_ids = sub.get("sale_subscription_line_ids") or []
        if not line_ids:
            continue
        lines = search_read(uid, models, "sale.subscription.line", [("id", "in", line_ids)], ["product_id"])
        product_ids = [l["product_id"][0] for l in lines if l.get("product_id")]
        if not product_ids:
            continue
        products = search_read(uid, models, "product.product", [("id", "in", product_ids)], ["product_tmpl_id"])
        tmpl_ids = [p["product_tmpl_id"][0] for p in products if p.get("product_tmpl_id")]
        if not tmpl_ids:
            continue
        templates = search_read(uid, models, "product.template", [("id", "in", tmpl_ids)], ["subscription_plan_id"])
        plan_ids = [t["subscription_plan_id"][0] for t in templates if t.get("subscription_plan_id")]
        if not plan_ids:
            continue
        plans = search_read(uid, models, "iz.subscription.plan", [("id", "in", plan_ids)],
                            ["priority", "sequence"], order="priority desc, sequence asc, id asc", limit=1)
        if not plans:
            continue
        models.execute_kw(DB, uid, PASSWORD, "sale.subscription", "write",
                          [[sub["id"]], {"subscription_plan_id": plans[0]["id"]}])
        print(f"  Assigned plan to {sub['name']}")


def tag_existing_subscriptions(uid, models):
    """Tag subscriptions by billing cycle and payment status."""
    tag_map_raw = search_read(uid, models, "sale.subscription.tag", [], ["id", "name"])
    tag_ids = {t["name"]: t["id"] for t in tag_map_raw}

    subscriptions = search_read(
        uid, models, "sale.subscription", [],
        ["id", "name", "template_id", "invoice_ids", "sale_subscription_line_ids"],
    )
    if not subscriptions:
        return

    print("Tagging existing subscriptions...")
    for sub in subscriptions:
        names = set()
        template_name = sub["template_id"][1] if sub["template_id"] else ""
        for period in ("Mensual", "Trimestral", "Anual"):
            if period in template_name:
                names.add(period)

        line_ids = sub.get("sale_subscription_line_ids") or []
        if line_ids:
            lines = search_read(uid, models, "sale.subscription.line", [("id", "in", line_ids)], ["product_id"])
            product_names = " ".join(l["product_id"][1] for l in lines if l.get("product_id"))
            if "Nutricion" in product_names or "Nutrición" in product_names:
                names.add("Nutricion")

        invoice_ids = sub.get("invoice_ids") or []
        if invoice_ids:
            invoices = search_read(uid, models, "account.move", [("id", "in", invoice_ids)], ["payment_state"])
            if any(inv["payment_state"] == "paid" for inv in invoices):
                names.add("Pago confirmado")
            else:
                names.add("Pendiente de pago")

        ids_to_set = [tag_ids[n] for n in sorted(names) if n in tag_ids]
        if ids_to_set:
            models.execute_kw(DB, uid, PASSWORD, "sale.subscription", "write",
                              [[sub["id"]], {"tag_ids": [(6, 0, ids_to_set)]}])
            print(f"  Tagged {sub['name']}: {', '.join(sorted(names))}")


def run():
    uid, models = connect()
    assign_subscription_levels(uid, models)
    tag_existing_subscriptions(uid, models)
    print("Done: subscription post-processing complete.")


if __name__ == "__main__":
    run()
