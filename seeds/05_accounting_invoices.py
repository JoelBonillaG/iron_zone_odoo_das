"""
05_accounting_invoices.py
-------------------------
Creates exactly the demo subscriptions, each with a coherent billing history
(one paid invoice per recurrence period, back-dated month by month / year by year):

  - Cliente Portal 04 -> Suscripcion Anual   (2 yearly invoices)
  - Cliente Portal 07 -> Suscripcion Mensual (5 monthly invoices)

Confirming a sale order with a subscribable product creates the subscription
(see sale_order.action_confirm). We then issue back-dated paid invoices through
the subscription's own create_invoice() so the portal billing history reads
"hace un mes, hace dos meses..." instead of all on the same day.

Depends on: 01_customers.py, 02_subscription_config.py, 03_products.py
"""
import calendar
import xmlrpc.client
from datetime import date

from config import DB, PASSWORD, connect

IVA_RATE = 15.0

# The ONLY subscriptions seeded, with their billing cadence.
#   interval_months: 1 = monthly, 12 = yearly
#   periods: how many paid invoices of history to generate (last one = today)
SUBSCRIPTION_ASSIGNMENTS = [
    {"ref": "IZSUB-04", "email": "pruebasjos04@gmail.com", "product": "Suscripcion Anual",
     "interval_months": 12, "periods": 2},
    {"ref": "IZSUB-07", "email": "pruebasjos07@gmail.com", "product": "Suscripcion Mensual",
     "interval_months": 1, "periods": 5},
]


def execute(models, model, method, *args, **kwargs):
    return models.execute_kw(DB, UID, PASSWORD, model, method, list(args), kwargs)


def search_read(models, model, domain, fields, limit=None, order=None):
    kwargs = {"fields": fields}
    if limit:
        kwargs["limit"] = limit
    if order:
        kwargs["order"] = order
    return execute(models, model, "search_read", domain, **kwargs)


def read(models, model, ids, fields):
    if not ids:
        return []
    return execute(models, model, "read", ids, fields=fields)


def add_months(base, months):
    """Return base shifted by `months` (can be negative), clamping the day."""
    index = base.month - 1 + months
    year = base.year + index // 12
    month = index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def ensure_accounting_base(models):
    sale_journals = search_read(
        models, "account.journal", [["type", "=", "sale"]], ["id", "name", "code"], limit=1
    )
    payment_journals = search_read(
        models, "account.journal", [["type", "in", ["bank", "cash"]]],
        ["id", "name", "code", "type"], limit=1,
    )
    taxes = search_read(
        models, "account.tax",
        [["type_tax_use", "=", "sale"], ["amount", "=", IVA_RATE], ["active", "=", True]],
        ["id", "name", "amount"], limit=1,
    )

    if not sale_journals:
        raise RuntimeError("No sale journal found. Install/configure Accounting first.")
    if not payment_journals:
        raise RuntimeError("No bank or cash journal found. Configure a payment journal first.")
    if not taxes:
        raise RuntimeError(f"No active sales tax with {IVA_RATE:.0f}% found. Configure VAT/IVA first.")

    tax = taxes[0]
    products = execute(models, "product.template", "search", [["sale_ok", "=", True]])
    if products:
        execute(models, "product.template", "write", products, {"taxes_id": [(6, 0, [tax["id"]])]})

    print(f"Tax configured for sale products: {tax['name']} ({tax['amount']}%)")
    print(f"Sales journal: {sale_journals[0]['name']} [{sale_journals[0]['code']}]")
    print(f"Payment journal: {payment_journals[0]['name']} [{payment_journals[0]['code']}]")


def get_default_pricelist_id(models):
    pricelists = search_read(models, "product.pricelist", [], ["id"], limit=1)
    if pricelists:
        return pricelists[0]["id"]
    return execute(models, "product.pricelist", "create", {"name": "Tarifa Publica"})


def ensure_subscription_orders(models):
    """Create (idempotently) one sale order per assignment and return their ids."""
    pricelist_id = get_default_pricelist_id(models)
    order_ids = []
    for assignment in SUBSCRIPTION_ASSIGNMENTS:
        customers = search_read(
            models, "res.partner",
            [["email", "=", assignment["email"]], ["customer_rank", ">", 0]],
            ["id", "name"], limit=1,
        )
        products = search_read(
            models, "product.product",
            [["name", "=", assignment["product"]], ["sale_ok", "=", True]],
            ["id", "name"], limit=1,
        )
        if not customers or not products:
            print(f"  Skipping {assignment['ref']}: missing customer or product. "
                  f"Run 01_customers.py and 03_products.py first.")
            continue

        existing = search_read(
            models, "sale.order", [["client_order_ref", "=", assignment["ref"]]],
            ["id", "state"], limit=1,
        )
        if existing:
            order_id = existing[0]["id"]
            if existing[0]["state"] in ("draft", "sent"):
                execute(models, "sale.order", "write", [order_id], {"pricelist_id": pricelist_id})
        else:
            order_id = execute(models, "sale.order", "create", {
                "partner_id": customers[0]["id"],
                "client_order_ref": assignment["ref"],
                "pricelist_id": pricelist_id,
                "note": "Suscripcion Iron Zone (seed).",
            })
            execute(models, "sale.order.line", "create", {
                "order_id": order_id,
                "product_id": products[0]["id"],
                "product_uom_qty": 1,
            })
            print(f"  Created subscription order {assignment['ref']}: "
                  f"{customers[0]['name']} -> {assignment['product']}")
        order_ids.append(order_id)
    return order_ids


def confirm_orders(models, order_ids):
    if not order_ids:
        return
    orders = read(models, "sale.order", order_ids, ["id", "state"])
    to_confirm = [o["id"] for o in orders if o["state"] in ("draft", "sent")]
    if to_confirm:
        execute(models, "sale.order", "action_confirm", to_confirm)
        print(f"Confirmed sale orders: {len(to_confirm)} (subscriptions created in Borrador)")
    else:
        print("Sale orders already confirmed.")


def find_subscription_id(models, order_ref):
    orders = search_read(models, "sale.order", [["client_order_ref", "=", order_ref]], ["id"], limit=1)
    if not orders:
        return None
    subs = search_read(
        models, "sale.subscription", [["sale_order_id", "=", orders[0]["id"]]], ["id"], limit=1
    )
    return subs[0]["id"] if subs else None


def pay_invoice(models, invoice_id, payment_date):
    ctx = {"active_model": "account.move", "active_ids": [invoice_id], "active_id": invoice_id}
    wizard_id = execute(models, "account.payment.register", "create",
                        {"payment_date": payment_date}, context=ctx)
    execute(models, "account.payment.register", "action_create_payments", [wizard_id], context=ctx)


def generate_billing_history(models, sub_id, interval_months, periods):
    """Issue `periods` back-dated paid invoices, one per recurrence period."""
    existing = search_read(
        models, "account.move",
        [["subscription_id", "=", sub_id], ["move_type", "=", "out_invoice"]],
        ["id"],
    )
    if len(existing) >= periods:
        print(f"  Billing history already present for subscription {sub_id}.")
        return

    today = date.today()
    start = add_months(today, -interval_months * (periods - 1))
    invoice_dates = [add_months(start, interval_months * i) for i in range(periods)]

    for invoice_date in invoice_dates:
        iso = invoice_date.isoformat()
        # create_invoice() stamps the invoice with recurring_next_date as its date
        execute(models, "sale.subscription", "write", [sub_id], {"recurring_next_date": iso})
        try:
            execute(models, "sale.subscription", "create_invoice", [sub_id])
        except xmlrpc.client.Fault as fault:
            # create_invoice returns a recordset; XML-RPC can't marshal it, but the
            # invoice is created. Re-raise anything that is not that marshalling issue.
            if "marshal" not in fault.faultString:
                raise
        invoices = search_read(
            models, "account.move",
            [["subscription_id", "=", sub_id], ["invoice_date", "=", iso],
             ["move_type", "=", "out_invoice"]],
            ["id", "state"], order="id desc", limit=1,
        )
        if not invoices:
            continue
        invoice_id = invoices[0]["id"]
        if invoices[0]["state"] == "draft":
            execute(models, "account.move", "action_post", [invoice_id])
        pay_invoice(models, invoice_id, iso)

    # Finalise: active, started in the past, next billing in the future
    execute(models, "sale.subscription", "write", [sub_id], {"date_start": start.isoformat()})
    in_progress = search_read(
        models, "sale.subscription.stage", [["type", "=", "in_progress"]], ["id"], limit=1
    )
    if in_progress:
        execute(models, "sale.subscription", "write", [sub_id], {"stage_id": in_progress[0]["id"]})
    # Second write (no stage_id) so the model does not recompute it back to the past
    execute(models, "sale.subscription", "write", [sub_id],
            {"recurring_next_date": add_months(today, interval_months).isoformat()})
    print(f"  Generated {periods} paid invoices for subscription {sub_id}.")


def print_summary(models):
    subs = search_read(
        models, "sale.subscription",
        [["stage_type", "=", "in_progress"], ["active", "=", True]],
        ["name", "partner_id", "subscription_plan_id", "recurring_next_date"], order="id asc",
    )
    print("")
    print(f"Done: {len(subs)} active subscriptions:")
    for sub in subs:
        invoices = search_read(
            models, "account.move",
            [["subscription_id", "=", sub["id"]], ["move_type", "=", "out_invoice"],
             ["state", "=", "posted"]],
            ["invoice_date", "amount_total", "payment_state"], order="invoice_date asc",
        )
        partner = sub["partner_id"][1] if sub["partner_id"] else "-"
        print(f"  {sub['name']} | {partner} | next: {sub['recurring_next_date']} | "
              f"{len(invoices)} invoices")
        for inv in invoices:
            print(f"      {inv['invoice_date']} | {inv['amount_total']} | {inv['payment_state']}")


def run():
    global UID
    UID, models = connect()

    print(f"Running subscription seeding on {date.today().isoformat()}...")
    ensure_accounting_base(models)
    order_ids = ensure_subscription_orders(models)
    if not order_ids:
        print("No subscription orders could be created; aborting.")
        return
    confirm_orders(models, order_ids)

    for assignment in SUBSCRIPTION_ASSIGNMENTS:
        sub_id = find_subscription_id(models, assignment["ref"])
        if not sub_id:
            print(f"  Subscription for {assignment['ref']} not found; skipping history.")
            continue
        generate_billing_history(
            models, sub_id, assignment["interval_months"], assignment["periods"]
        )

    print_summary(models)


if __name__ == "__main__":
    UID = None
    run()
