from config import DB, PASSWORD, connect


BANK_NAME = "Banco Pichincha"
BANK_ACCOUNT_NUMBER = "2200123456"
BANK_ACCOUNT_TYPE = "Cuenta corriente"
BANK_HOLDER = "Iron Zone"
BANK_CONTACT_EMAIL = "contacto@ironzone.ec"

PAYMENT_PROVIDERS = {
    "demo": {
        "name": "Pago directo",
        "state": "test",
        "is_published": True,
        "sequence": 1,
        "allow_tokenization": False,
        "allow_express_checkout": False,
        "pre_msg": "<p>Metodo de prueba para simular pagos en el portal.</p>",
        "done_msg": "<p>Pago demo procesado correctamente.</p>",
    },
    "custom": {
        "name": "Transferencia bancaria Iron Zone",
        "state": "enabled",
        "is_published": True,
        "sequence": 2,
        "custom_mode": "wire_transfer",
        "pre_msg": "<p>Realiza la transferencia con los datos bancarios de Iron Zone.</p>",
    },
}

PAYMENT_METHODS = {
    "demo": {"active": True, "sequence": 1, "sri_payment_code": "19"},
    "wire_transfer": {"active": True, "sequence": 2, "sri_payment_code": "20"},
}


def execute(models, uid, model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kwargs)


def search(models, uid, model, domain, limit=None, active_test=True):
    kwargs = {}
    if limit:
        kwargs["limit"] = limit
    if not active_test:
        kwargs["context"] = {"active_test": False}
    return execute(models, uid, model, "search", domain, **kwargs)


def read(models, uid, model, ids, fields):
    if not ids:
        return []
    return execute(models, uid, model, "read", ids, fields=fields)


def get_company(models, uid):
    companies = execute(
        models,
        uid,
        "res.company",
        "search_read",
        [],
        fields=["id", "name", "partner_id", "currency_id"],
        limit=1,
    )
    if not companies:
        raise RuntimeError("No company found.")
    return companies[0]


def get_website(models, uid):
    websites = execute(
        models,
        uid,
        "website",
        "search_read",
        [],
        fields=["id", "name"],
        limit=1,
    )
    return websites[0] if websites else None


def ensure_modules_installed(models, uid):
    modules = ["payment_demo", "payment_custom", "account_payment", "website_payment"]
    records = execute(
        models,
        uid,
        "ir.module.module",
        "search_read",
        [["name", "in", modules]],
        fields=["name", "state"],
    )
    states = {record["name"]: record["state"] for record in records}
    missing = [name for name in modules if states.get(name) != "installed"]
    if missing:
        raise RuntimeError(
            "Payment modules are not installed: "
            + ", ".join(missing)
            + ". Run scripts/install_apps.sh first."
        )


def transfer_pending_message():
    return f"""
        <div>
            <h5>Datos para transferencia bancaria</h5>
            <ul>
                <li><strong>Banco:</strong> {BANK_NAME}</li>
                <li><strong>Titular:</strong> {BANK_HOLDER}</li>
                <li><strong>Tipo de cuenta:</strong> {BANK_ACCOUNT_TYPE}</li>
                <li><strong>Numero de cuenta:</strong> {BANK_ACCOUNT_NUMBER}</li>
            </ul>
            <p>Usa el numero de factura como referencia del pago.</p>
            <p>Despues de transferir, envia el comprobante a {BANK_CONTACT_EMAIL}. El pago quedara pendiente hasta validacion administrativa.</p>
        </div>
    """


def ensure_bank_journal(models, uid):
    company = get_company(models, uid)
    partner_id = company["partner_id"][0]
    currency_id = company["currency_id"][0]

    bank_account_ids = search(
        models,
        uid,
        "res.partner.bank",
        [["acc_number", "=", BANK_ACCOUNT_NUMBER], ["partner_id", "=", partner_id]],
        limit=1,
        active_test=False,
    )
    bank_values = {
        "acc_number": BANK_ACCOUNT_NUMBER,
        "acc_holder_name": BANK_HOLDER,
        "partner_id": partner_id,
        "company_id": company["id"],
        "currency_id": currency_id,
    }
    if bank_account_ids:
        bank_account_id = bank_account_ids[0]
        execute(models, uid, "res.partner.bank", "write", [bank_account_id], bank_values)
    else:
        bank_account_id = execute(models, uid, "res.partner.bank", "create", bank_values)

    journal_ids = search(models, uid, "account.journal", [["type", "=", "bank"]], limit=1)
    if not journal_ids:
        raise RuntimeError("No bank journal found. Install Accounting first.")

    execute(
        models,
        uid,
        "account.journal",
        "write",
        journal_ids,
        {
            "name": "Banco Iron Zone",
            "bank_account_id": bank_account_id,
            "bank_acc_number": BANK_ACCOUNT_NUMBER,
        },
    )
    print(f"Bank journal configured: {BANK_NAME} - {BANK_ACCOUNT_NUMBER}")


def clear_restrictions(models, uid, provider_id):
    execute(
        models,
        uid,
        "payment.provider",
        "write",
        [provider_id],
        {
            "available_country_ids": [(5, 0, 0)],
            "available_currency_ids": [(5, 0, 0)],
            "maximum_amount": 0.0,
        },
    )


def configure_payment_methods(models, uid):
    method_fields = execute(models, uid, "payment.method", "fields_get", [])
    for code, values in PAYMENT_METHODS.items():
        method_ids = search(
            models,
            uid,
            "payment.method",
            [["code", "=", code]],
            limit=1,
            active_test=False,
        )
        if not method_ids:
            print(f"Payment method not found: {code}")
            continue
        write_values = {
            key: value for key, value in values.items() if key != "sri_payment_code"
        }
        sri_payment_code = values.get("sri_payment_code")
        if sri_payment_code and "l10n_ec_sri_payment_id" in method_fields:
            sri_payment_ids = search(
                models,
                uid,
                "l10n_ec.sri.payment",
                [["code", "=", sri_payment_code]],
                limit=1,
                active_test=False,
            )
            if sri_payment_ids:
                write_values["l10n_ec_sri_payment_id"] = sri_payment_ids[0]
            else:
                print(f"SRI payment method not found: {sri_payment_code}")
        execute(models, uid, "payment.method", "write", method_ids, write_values)
        print(f"Payment method enabled: {code}")


def configure_payment_providers(models, uid):
    website = get_website(models, uid)
    journal_ids = search(models, uid, "account.journal", [["type", "in", ["bank", "cash"]]], limit=1)
    for code, values in PAYMENT_PROVIDERS.items():
        if code == "custom":
            values = {**values, "pending_msg": transfer_pending_message()}
        provider_ids = search(models, uid, "payment.provider", [["code", "=", code]], limit=1)
        if not provider_ids:
            print(f"Payment provider not found: {code}")
            continue

        provider_id = provider_ids[0]
        clear_restrictions(models, uid, provider_id)
        if website:
            values["website_id"] = website["id"]
        if journal_ids:
            values["journal_id"] = journal_ids[0]
        execute(models, uid, "payment.provider", "write", [provider_id], values)

        provider = read(
            models,
            uid,
            "payment.provider",
            [provider_id],
            ["name", "code", "state", "is_published"],
        )[0]
        print(
            f"Payment provider configured: {provider['name']} "
            f"({provider['code']}, state={provider['state']}, published={provider['is_published']})"
        )


def print_summary(models, uid):
    providers = execute(
        models,
        uid,
        "payment.provider",
        "search_read",
        [["code", "in", list(PAYMENT_PROVIDERS)]],
        fields=["name", "code", "state", "is_published", "payment_method_ids"],
        order="sequence asc",
    )
    print("")
    print("Payment providers available for portal:")
    for provider in providers:
        print(
            f"  {provider['name']} | code={provider['code']} | "
            f"state={provider['state']} | published={provider['is_published']}"
        )


def run():
    uid, models = connect()
    ensure_modules_installed(models, uid)
    ensure_bank_journal(models, uid)
    configure_payment_providers(models, uid)
    configure_payment_methods(models, uid)
    print_summary(models, uid)


if __name__ == "__main__":
    run()
