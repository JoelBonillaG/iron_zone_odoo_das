import xmlrpc.client

from config import DB, PASSWORD, connect, create


PORTAL_PASSWORD = "admin123"
DEFAULT_CUSTOMER_LANGS = ("es_EC", "es_419", "es_ES", "en_US")

# ──────────────────────────────────────────────────────────────────────
# Clientes de demostración
# Incluyen campos iz_* para demostrar segmentación en email marketing
# ──────────────────────────────────────────────────────────────────────
CUSTOMERS = [
    {
        "name": "Cliente Portal 04",
        "email": "pruebasjos04@gmail.com",
        "phone": "0991234501",
        "street": "Av. Cevallos 123",
        "city": "Ambato",
        "vat": "1801234566001",
        "identification_type_xmlid": "l10n_ec.ec_ruc",
        "l10n_ec_identifier_type": "ruc",
        "contributor_type_xmlid": "l10n_ec_base.contrib_persona_natural",
        "l10n_ec_taxpayer_type": "general",
        "l10n_ec_related_party": False,
        # IZ profile fields
        "iz_gender": "female",
        "iz_birthdate": "1995-03-08",   # 31 años – campaña Día Mujer
        "iz_fitness_goal": "weight_loss",
        "iz_experience_level": "intermediate",
        "iz_subscribed": True,
    },
    {
        "name": "Cliente Portal 07",
        "email": "pruebasjos07@gmail.com",
        "phone": "0991234502",
        "street": "Calle Bolivar 456",
        "city": "Ambato",
        "vat": "1850191253",
        "identification_type_xmlid": "l10n_ec.ec_dni",
        "l10n_ec_identifier_type": "cedula",
        "contributor_type_xmlid": "l10n_ec_base.contrib_persona_natural_profesionales",
        "l10n_ec_taxpayer_type": "general",
        "l10n_ec_related_party": False,
        # IZ profile fields
        "iz_gender": "male",
        "iz_birthdate": "1990-11-19",   # 35 años – campaña Día Hombre
        "iz_fitness_goal": "muscle_gain",
        "iz_experience_level": "advanced",
        "iz_subscribed": True,
    },
    {
        "name": "Cliente Portal 08",
        "email": "pruebasjos08@gmail.com",
        "phone": "0991234503",
        "street": "Av. Miraflores 789",
        "city": "Ambato",
        "vat": "0912345675001",
        "identification_type_xmlid": "l10n_ec.ec_ruc",
        "l10n_ec_identifier_type": "ruc",
        "contributor_type_xmlid": "l10n_ec_base.contrib_rimpe_negocio",
        "l10n_ec_taxpayer_type": "rimpe_p",
        "l10n_ec_related_party": False,
        # IZ profile fields
        "iz_gender": "male",
        "iz_birthdate": "2005-07-14",   # 20 años – joven, principiante
        "iz_fitness_goal": "endurance",
        "iz_experience_level": "beginner",
        "iz_subscribed": True,
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


def resolve_customer_lang(uid, models):
    def installed_lang():
        lang_records = models.execute_kw(
            DB, uid, PASSWORD, "res.lang", "search_read",
            [[("code", "in", list(DEFAULT_CUSTOMER_LANGS))]],
            {"fields": ["id", "code", "active"], "context": {"active_test": False}},
        )
        records_by_code = {record["code"]: record for record in lang_records}
        for lang_code in DEFAULT_CUSTOMER_LANGS:
            record = records_by_code.get(lang_code)
            if not record:
                continue
            if not record["active"]:
                models.execute_kw(DB, uid, PASSWORD, "res.lang", "write", [[record["id"]], {"active": True}])
                print(f"Activated language: {lang_code}")
            return lang_code
        return False

    lang = installed_lang()
    if lang:
        return lang

    for lang_code in DEFAULT_CUSTOMER_LANGS:
        try:
            wizard_id = create(uid, models, "base.language.install", {"lang": lang_code, "overwrite": False})
            models.execute_kw(DB, uid, PASSWORD, "base.language.install", "lang_install", [[wizard_id]])
            print(f"Installed language: {lang_code}")
            return lang_code
        except xmlrpc.client.Fault:
            continue

    lang_records = models.execute_kw(
        DB, uid, PASSWORD, "res.lang", "search_read",
        [[("code", "in", list(DEFAULT_CUSTOMER_LANGS))]],
        {"fields": ["code"], "context": {"active_test": False}},
    )
    available_codes = {record["code"] for record in lang_records}
    for lang_code in DEFAULT_CUSTOMER_LANGS:
        if lang_code in available_codes:
            return lang_code
    return False


def ensure_portal_user(uid, models, partner_id, customer, default_lang):
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
    lang = customer.get("lang") or default_lang
    if lang:
        values["lang"] = lang
    user_id, created = create_or_update(
        uid, models, "res.users",
        [("login", "=", customer["email"])],
        values,
        fields=["id", "login"],
    )
    return user_id, created


def archive_old_demo_customers(uid, models):
    allowed_emails = [c["email"] for c in CUSTOMERS]
    old_ids = models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "search",
        [[("customer_rank", ">", 0), ("email", "not in", allowed_emails)]],
    )
    if old_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.partner", "write", [old_ids, {"active": False}])
        print(f"Archived {len(old_ids)} old demo customer(s).")

    allowed_contact_emails = ALLOWED_PORTAL_LOGINS + ["admin@ironzone.com", "deividjosue52@gmail.com"]
    old_contact_ids = models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "search",
        [[
            ("active", "=", True),
            ("email", "!=", False),
            ("email", "not in", allowed_contact_emails),
            ("user_ids", "=", False),
        ]],
    )
    if old_contact_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.partner", "write", [old_contact_ids, {"active": False}])
        print(f"Archived {len(old_contact_ids)} old contact(s) without portal login.")


def deactivate_old_portal_users(uid, models):
    old_user_ids = models.execute_kw(
        DB, uid, PASSWORD, "res.users", "search",
        [[("share", "=", True), ("login", "not in", ALLOWED_PORTAL_LOGINS)]],
    )
    if old_user_ids:
        models.execute_kw(DB, uid, PASSWORD, "res.users", "write", [old_user_ids, {"active": False}])
        print(f"Deactivated {len(old_user_ids)} old portal user(s).")


def run():
    uid, models = connect()
    default_lang = resolve_customer_lang(uid, models)
    country = search_one(uid, models, "res.country", [("code", "=", "EC")], fields=["id"])
    country_id = country["id"] if country else False

    archive_old_demo_customers(uid, models)
    deactivate_old_portal_users(uid, models)

    created_count = 0
    updated_count = 0
    for customer in CUSTOMERS:
        values = {
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "street": customer["street"],
            "city": customer["city"],
            "vat": customer["vat"],
            "l10n_ec_identifier_type": customer["l10n_ec_identifier_type"],
            "l10n_ec_taxpayer_type": customer["l10n_ec_taxpayer_type"],
            "l10n_ec_related_party": customer["l10n_ec_related_party"],
            "customer_rank": 1,
            "active": True,
            # ── IZ profile fields ──
            "iz_gender": customer.get("iz_gender", False),
            "iz_birthdate": customer.get("iz_birthdate", False),
            "iz_fitness_goal": customer.get("iz_fitness_goal", False),
            "iz_experience_level": customer.get("iz_experience_level", False),
            "iz_subscribed": customer.get("iz_subscribed", False),
        }
        lang = customer.get("lang") or default_lang
        if lang:
            values["lang"] = lang
        if country_id:
            values["country_id"] = country_id

        values["l10n_latam_identification_type_id"] = xmlid_to_res_id(
            uid, models, customer["identification_type_xmlid"]
        )
        values["l10n_ec_contributor_type_id"] = xmlid_to_res_id(
            uid, models, customer["contributor_type_xmlid"]
        )

        partner_id, created = create_or_update(
            uid, models, "res.partner",
            [("email", "=", customer["email"])],
            values,
            fields=["id", "name"],
        )
        user_id, user_created = ensure_portal_user(uid, models, partner_id, customer, default_lang)
        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        user_action = "created" if user_created else "updated"
        gender_lbl = customer.get("iz_gender", "-")
        goal_lbl = customer.get("iz_fitness_goal", "-")
        level_lbl = customer.get("iz_experience_level", "-")
        print(
            f"  {action} customer: {customer['name']} ({customer['email']}) | "
            f"gender={gender_lbl} goal={goal_lbl} level={level_lbl} | "
            f"portal user {user_action}: {user_id}"
        )

    print(f"Done: {created_count} customers created, {updated_count} updated.")


if __name__ == "__main__":
    run()
