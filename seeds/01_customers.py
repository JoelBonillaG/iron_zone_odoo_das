from config import DB, PASSWORD, connect, create


PORTAL_PASSWORD = "admin123"

CUSTOMERS = [
    {
        "name": "Cliente Portal 04",
        "email": "pruebasjos04@gmail.com",
        "phone": "0991234501",
        "street": "Av. Cevallos 123",
        "city": "Ambato",
        "vat": "1801234567001",
    },
    {
        "name": "Cliente Portal 07",
        "email": "pruebasjos07@gmail.com",
        "phone": "0991234502",
        "street": "Calle Bolivar 456",
        "city": "Ambato",
        "vat": "1712345678",
    },
    {
        "name": "Cliente Portal 08",
        "email": "pruebasjos08@gmail.com",
        "phone": "0991234503",
        "street": "Av. Miraflores 789",
        "city": "Ambato",
        "vat": "0912345678001",
    },
]

ALLOWED_PORTAL_LOGINS = [
    "pruebasjos04@gmail.com",
    "pruebasjos07@gmail.com",
    "pruebasjos08@gmail.com",
    "josuegarcab2@gmail.com",
    "josuegarcab2@hotmail.com",
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


def xmlid_to_res_id(uid, models, xmlid):
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid,
        models,
        "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    if not record:
        raise RuntimeError(f"External ID not found: {xmlid}")
    return record["res_id"]


def ensure_portal_user(uid, models, partner_id, customer):
    portal_group_id = xmlid_to_res_id(uid, models, "base.group_portal")
    values = {
        "name": customer["name"],
        "login": customer["email"],
        "email": customer["email"],
        "partner_id": partner_id,
        "groups_id": [(6, 0, [portal_group_id])],
        "active": True,
        "password": PORTAL_PASSWORD,
    }
    user_id, created = create_or_update(
        uid,
        models,
        "res.users",
        [("login", "=", customer["email"])],
        values,
        fields=["id", "login"],
    )
    return user_id, created


def archive_old_demo_customers(uid, models):
    allowed_emails = [customer["email"] for customer in CUSTOMERS]
    old_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search",
        [[("customer_rank", ">", 0), ("email", "not in", allowed_emails)]],
    )
    if old_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.partner", "write", [old_ids, {"active": False}])
        print(f"Archived {len(old_ids)} old demo customer(s).")


def deactivate_old_portal_users(uid, models):
    old_user_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.users",
        "search",
        [[("share", "=", True), ("login", "not in", ALLOWED_PORTAL_LOGINS)]],
    )
    if old_user_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.users", "write", [old_user_ids, {"active": False}])
        print(f"Deactivated {len(old_user_ids)} old portal user(s).")


def run():
    uid, models = connect()
    country = search_one(uid, models, "res.country", [("code", "=", "EC")], fields=["id"])
    country_id = country["id"] if country else False

    archive_old_demo_customers(uid, models)
    deactivate_old_portal_users(uid, models)

    created_count = 0
    updated_count = 0
    for customer in CUSTOMERS:
        values = {
            **customer,
            "customer_rank": 1,
            "active": True,
        }
        if country_id:
            values["country_id"] = country_id

        partner_id, created = create_or_update(
            uid,
            models,
            "res.partner",
            [("email", "=", customer["email"])],
            values,
            fields=["id", "name"],
        )
        user_id, user_created = ensure_portal_user(uid, models, partner_id, customer)
        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        user_action = "created" if user_created else "updated"
        print(f"  {action} customer: {customer['name']} ({customer['email']}) - portal user {user_action}: {user_id}")

    print(f"Done: {created_count} customers created, {updated_count} updated.")


if __name__ == "__main__":
    run()
