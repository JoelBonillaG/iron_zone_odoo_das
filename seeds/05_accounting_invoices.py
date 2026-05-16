import math
import xmlrpc.client
from datetime import date

from config import DB, PASSWORD, connect

IVA_RATE = 15.0
PAYMENT_RATIO = 0.5
TARGET_ORDER_COUNT = 10
ACT006_REF_PREFIX = "ACT006-SUBSCRIPTION"
SUBSCRIPTION_PRODUCT_KEYWORDS = ["Suscripcion", "Plan Nutricion", "Plan Nutrición"]


def execute(models, model, method, *args, **kwargs):
    return models.execute_kw(DB, UID, PASSWORD, model, method, list(args), kwargs)


def search(models, model, domain, limit=None):
    kwargs = {}
    if limit:
        kwargs["limit"] = limit
    return execute(models, model, "search", domain, **kwargs)


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


def ensure_accounting_base(models):
    sale_journals = search_read(
        models,
        "account.journal",
        [["type", "=", "sale"]],
        ["id", "name", "code"],
        limit=1,
    )
    payment_journals = search_read(
        models,
        "account.journal",
        [["type", "in", ["bank", "cash"]]],
        ["id", "name", "code", "type"],
        limit=1,
    )
    taxes = search_read(
        models,
        "account.tax",
        [
            ["type_tax_use", "=", "sale"],
            ["amount", "=", IVA_RATE],
            ["active", "=", True],
        ],
        ["id", "name", "amount"],
        limit=1,
    )

    if not sale_journals:
        raise RuntimeError("No sale journal found. Install/configure Accounting first.")
    if not payment_journals:
        raise RuntimeError("No bank or cash journal found. Configure an accounting payment journal first.")
    if not taxes:
        raise RuntimeError(f"No active sales tax with {IVA_RATE:.0f}% found. Configure VAT/IVA first.")

    tax = taxes[0]
    products = search(models, "product.template", [["sale_ok", "=", True]])
    if products:
        execute(models, "product.template", "write", products, {"taxes_id": [(6, 0, [tax["id"]])]})

    print(f"Tax configured for sale products: {tax['name']} ({tax['amount']}%)")
    print(f"Sales journal: {sale_journals[0]['name']} [{sale_journals[0]['code']}]")
    print(f"Payment journal: {payment_journals[0]['name']} [{payment_journals[0]['code']}]")


def get_customers(models):
    customers = search_read(
        models,
        "res.partner",
        [["customer_rank", ">", 0]],
        ["id", "name"],
        limit=TARGET_ORDER_COUNT,
        order="id asc",
    )
    if len(customers) < TARGET_ORDER_COUNT:
        raise RuntimeError(f"Run 01_customers.py first. ACT006 requires {TARGET_ORDER_COUNT} customer/member records.")
    return customers


def get_subscription_products(models):
    domain = [
        "|",
        ["name", "ilike", SUBSCRIPTION_PRODUCT_KEYWORDS[0]],
        ["name", "ilike", SUBSCRIPTION_PRODUCT_KEYWORDS[1]],
    ]
    products = search_read(
        models,
        "product.product",
        domain,
        ["id", "name"],
        order="name asc",
    )
    if not products:
        raise RuntimeError("Run 02_products.py first. ACT006 requires subscription products.")
    return products


def get_act006_sale_orders(models):
    orders = search_read(
        models,
        "sale.order",
        [
            ["client_order_ref", "ilike", ACT006_REF_PREFIX],
            ["state", "in", ["draft", "sent", "sale"]],
        ],
        ["id", "name", "state", "invoice_status", "invoice_ids", "client_order_ref"],
        order="name asc",
    )
    return orders


def ensure_subscription_orders(models):
    existing_orders = get_act006_sale_orders(models)
    existing_refs = {order["client_order_ref"] for order in existing_orders}

    customers = get_customers(models)
    subscription_products = get_subscription_products(models)

    created = 0
    for index in range(TARGET_ORDER_COUNT):
        ref = f"{ACT006_REF_PREFIX}-{index + 1:02d}"
        if ref in existing_refs:
            continue

        customer = customers[index]
        product = subscription_products[index % len(subscription_products)]
        order_id = execute(
            models,
            "sale.order",
            "create",
            {
                "partner_id": customer["id"],
                "client_order_ref": ref,
                "note": "ACT006: contrato de suscripcion / pago recurrente simulado.",
            },
        )
        execute(
            models,
            "sale.order.line",
            "create",
            {
                "order_id": order_id,
                "product_id": product["id"],
                "product_uom_qty": 1,
            },
        )
        created += 1
        print(f"Created subscription order {ref}: {customer['name']} -> {product['name']}")

    if created:
        print(f"ACT006 subscription orders created: {created}")
    else:
        print("ACT006 subscription orders already exist.")

    orders = get_act006_sale_orders(models)
    if len(orders) < TARGET_ORDER_COUNT:
        raise RuntimeError(f"ACT006 requires {TARGET_ORDER_COUNT} subscription orders; found {len(orders)}.")
    return orders


def confirm_orders(models, orders):
    to_confirm = [order["id"] for order in orders if order["state"] in ("draft", "sent")]
    if to_confirm:
        execute(models, "sale.order", "action_confirm", to_confirm)
        print(f"Confirmed sale orders: {len(to_confirm)}")
    else:
        print("Sale orders already confirmed.")


def create_invoice_for_order(models, order_id):
    ctx = {"active_model": "sale.order", "active_ids": [order_id], "active_id": order_id}
    wizard_id = execute(
        models,
        "sale.advance.payment.inv",
        "create",
        {
            "advance_payment_method": "delivered",
            "sale_order_ids": [(6, 0, [order_id])],
        },
        context=ctx,
    )

    try:
        execute(models, "sale.advance.payment.inv", "create_invoices", [wizard_id], context=ctx)
    except xmlrpc.client.Fault as fault:
        # Odoo creates the invoice, then XML-RPC can fail while serializing the UI action.
        if "cannot marshal None" not in fault.faultString:
            raise


def ensure_invoices(models, orders):
    invoice_ids = []

    for order in orders:
        current_invoice_ids = order["invoice_ids"]
        if not current_invoice_ids:
            create_invoice_for_order(models, order["id"])
            refreshed = read(models, "sale.order", [order["id"]], ["invoice_ids", "name"])[0]
            current_invoice_ids = refreshed["invoice_ids"]
            if current_invoice_ids:
                print(f"Created invoice for {refreshed['name']}")
        else:
            print(f"Invoice already exists for {order['name']}")

        invoice_ids.extend(current_invoice_ids)

    return sorted(set(invoice_ids))


def post_invoices(models, invoice_ids):
    invoices = read(models, "account.move", invoice_ids, ["id", "name", "state", "payment_state"])
    draft_ids = [invoice["id"] for invoice in invoices if invoice["state"] == "draft"]
    if draft_ids:
        execute(models, "account.move", "action_post", draft_ids)
        print(f"Posted invoices: {len(draft_ids)}")
    else:
        print("Invoices already posted.")


def pay_invoice(models, invoice_id):
    ctx = {"active_model": "account.move", "active_ids": [invoice_id], "active_id": invoice_id}
    wizard_id = execute(models, "account.payment.register", "create", {}, context=ctx)
    execute(models, "account.payment.register", "action_create_payments", [wizard_id], context=ctx)


def register_payments(models, invoice_ids):
    invoices = read(
        models,
        "account.move",
        invoice_ids,
        ["id", "name", "state", "payment_state", "amount_residual", "invoice_origin"],
    )
    posted = [invoice for invoice in invoices if invoice["state"] == "posted"]
    paid = [invoice for invoice in posted if invoice["payment_state"] == "paid"]
    target_paid = math.ceil(len(posted) * PAYMENT_RATIO)
    pending = [invoice for invoice in posted if invoice["payment_state"] != "paid"]
    to_pay = pending[: max(0, target_paid - len(paid))]

    for invoice in to_pay:
        pay_invoice(models, invoice["id"])
        print(f"Registered payment: {invoice['name']} ({invoice['invoice_origin']})")

    if not to_pay:
        print(f"At least half of the invoices are already paid ({len(paid)}/{len(posted)}).")


def print_summary(models, invoice_ids):
    invoices = read(
        models,
        "account.move",
        invoice_ids,
        ["name", "invoice_origin", "state", "payment_state", "amount_total"],
    )
    paid_count = 0
    print("")
    print("ACT006 subscription invoice summary:")
    for invoice in sorted(invoices, key=lambda item: item["name"] or ""):
        if invoice["payment_state"] == "paid":
            paid_count += 1
        print(
            f"  {invoice['name']} | Order: {invoice['invoice_origin']} | "
            f"State: {invoice['state']} | Payment: {invoice['payment_state']} | "
            f"Total: {invoice['amount_total']}"
        )
    print(f"Done: {len(invoices)} subscription invoices generated, {paid_count} paid.")


def run():
    global UID
    UID, models = connect()

    print(f"Running ACT006 accounting automation on {date.today().isoformat()}...")
    ensure_accounting_base(models)
    orders = ensure_subscription_orders(models)
    confirm_orders(models, orders)

    refreshed_orders = get_act006_sale_orders(models)
    invoice_ids = ensure_invoices(models, refreshed_orders)
    if not invoice_ids:
        raise RuntimeError("No invoices were generated.")

    post_invoices(models, invoice_ids)
    register_payments(models, invoice_ids)
    print_summary(models, invoice_ids)


if __name__ == "__main__":
    UID = None
    run()
