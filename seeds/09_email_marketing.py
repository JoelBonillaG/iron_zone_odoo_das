"""
09_email_marketing.py
─────────────────────
1. Actualiza los campos iz_* de partners existentes que los tengan vacíos.
2. Asigna partners a listas de correo segmentadas según sus campos iz_*.
3. Crea 3 mailings de demostración en Odoo Mass Mailing.

Ejecución:
    cd seeds
    python 09_email_marketing.py
"""
from config import DB, PASSWORD, connect

# ── Datos de enriquecimiento para partners existentes sin iz_* ──────────
# Clave: email del partner
PARTNER_IZ_DATA = {
    "pruebasjos04@gmail.com": {
        "iz_gender": "female",
        "iz_birthdate": "1995-03-08",
        "iz_fitness_goal": "weight_loss",
        "iz_experience_level": "intermediate",
        "iz_subscribed": True,
    },
    "pruebasjos07@gmail.com": {
        "iz_gender": "male",
        "iz_birthdate": "1990-11-19",
        "iz_fitness_goal": "muscle_gain",
        "iz_experience_level": "advanced",
        "iz_subscribed": True,
    },
    "pruebasjos08@gmail.com": {
        "iz_gender": "male",
        "iz_birthdate": "2005-07-14",
        "iz_fitness_goal": "endurance",
        "iz_experience_level": "beginner",
        "iz_subscribed": True,
    },
    "josuegarcab2@gmail.com": {
        "iz_gender": "female",
        "iz_birthdate": "2000-05-15",
        "iz_fitness_goal": "general_fitness",
        "iz_experience_level": "beginner",
        "iz_subscribed": True,
    },
    "josuegarcab2@hotmail.com": {
        "iz_gender": "male",
        "iz_birthdate": "1985-12-25",
        "iz_fitness_goal": "muscle_gain",
        "iz_experience_level": "advanced",
        "iz_subscribed": True,
    },
}

# ── Listas segmentadas (xmlid → name) ───────────────────────────────────
SEGMENT_LISTS = {
    "mailing_list_customers":    "Iron Zone – Clientes",
    "mailing_list_women":        "Iron Zone – Mujeres",
    "mailing_list_men":          "Iron Zone – Hombres",
    "mailing_list_goal_muscle":  "Iron Zone – Objetivo: Masa muscular",
    "mailing_list_goal_weight_loss": "Iron Zone – Objetivo: Pérdida de peso",
    "mailing_list_goal_endurance": "Iron Zone – Objetivo: Resistencia",
    "mailing_list_goal_fitness": "Iron Zone – Objetivo: Fitness general",
    "mailing_list_beginners":    "Iron Zone – Principiantes",
    "mailing_list_intermediates": "Iron Zone – Intermedios",
    "mailing_list_advanced":     "Iron Zone – Avanzados",
}

# ── Demo mailings ────────────────────────────────────────────────────────
DEMO_MAILINGS = [
    {
        "name": "IZ Demo – Bienvenida nuevos miembros",
        "subject": "¡Bienvenido a Iron Zone! 🔥",
        "list_name": "Iron Zone – Clientes",
        "body": "<p>Bienvenido a Iron Zone. ¡Empieza a entrenar hoy!</p>",
    },
    {
        "name": "IZ Demo – Campaña Día de la Mujer",
        "subject": "💜 Feliz Día de la Mujer – Tu clase gratis te espera",
        "list_name": "Iron Zone – Mujeres",
        "body": "<p>Celebra el Día de la Mujer con una clase funcional gratuita.</p>",
    },
    {
        "name": "IZ Demo – Programa Iron Bulk (masa muscular)",
        "subject": "💪 Nuevo programa Iron Bulk – Empieza hoy",
        "list_name": "Iron Zone – Objetivo: Masa muscular",
        "body": "<p>Nuevo programa de hipertrofia disponible para ti.</p>",
    },
]


# ────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────

def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB, uid, PASSWORD, model, "search_read", [domain],
        {"fields": fields or ["id"], "limit": 1, "context": {"active_test": False}},
    )
    return records[0] if records else None


def xmlid_to_id(uid, models, module, name):
    rec = search_one(
        uid, models, "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    return rec["res_id"] if rec else None


def ensure_mailing_contact(uid, models, name, email):
    contact = search_one(uid, models, "mailing.contact", [("email", "=ilike", email)], fields=["id"])
    if contact:
        return contact["id"]
    return models.execute_kw(DB, uid, PASSWORD, "mailing.contact", "create",
                             [{"name": name, "email": email}])


def add_contact_to_list(uid, models, contact_id, list_id):
    try:
        models.execute_kw(DB, uid, PASSWORD, "mailing.list", "write",
                          [[list_id], {"contact_ids": [(4, contact_id)]}])
    except Exception:
        try:
            models.execute_kw(DB, uid, PASSWORD, "mailing.contact", "write",
                              [[contact_id], {"list_ids": [(4, list_id)]}])
        except Exception:
            pass


# ────────────────────────────────────────────────────────────────────────
# Mapping helpers
# ────────────────────────────────────────────────────────────────────────

GENDER_TO_LISTS = {
    "female": ["mailing_list_women"],
    "male": ["mailing_list_men"],
}

GOAL_TO_LISTS = {
    "muscle_gain": ["mailing_list_goal_muscle"],
    "weight_loss": ["mailing_list_goal_weight_loss"],
    "endurance": ["mailing_list_goal_endurance"],
    "general_fitness": ["mailing_list_goal_fitness"],
}

LEVEL_TO_LISTS = {
    "beginner": ["mailing_list_beginners"],
    "intermediate": ["mailing_list_intermediates"],
    "advanced": ["mailing_list_advanced"],
}


def get_list_ids_for_partner(uid, models, partner_data):
    """Return list of mailing.list IDs the partner should belong to."""
    list_xmlids = ["mailing_list_customers"]  # always general
    gender = partner_data.get("iz_gender", "")
    goal = partner_data.get("iz_fitness_goal", "")
    level = partner_data.get("iz_experience_level", "")
    list_xmlids += GENDER_TO_LISTS.get(gender, [])
    list_xmlids += GOAL_TO_LISTS.get(goal, [])
    list_xmlids += LEVEL_TO_LISTS.get(level, [])

    ids = []
    for xmlid in list_xmlids:
        lid = xmlid_to_id(uid, models, "iz_website", xmlid)
        if lid:
            ids.append(lid)
        else:
            # fallback: search by name
            lst = search_one(uid, models, "mailing.list",
                             [("name", "=", SEGMENT_LISTS.get(xmlid, ""))], fields=["id"])
            if lst:
                ids.append(lst["id"])
    return ids


# ────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────

def run():
    uid, models = connect()
    print("=" * 60)
    print("Iron Zone – Email Marketing Seed")
    print("=" * 60)

    # ── 1. Asegurar que las listas existen ──────────────────────────────
    print("\n[1] Verificando listas de correo segmentadas...")
    list_ids_by_name = {}
    for xmlid, list_name in SEGMENT_LISTS.items():
        lid = xmlid_to_id(uid, models, "iz_website", xmlid)
        if not lid:
            # Buscar por nombre
            lst = search_one(uid, models, "mailing.list", [("name", "=", list_name)], fields=["id"])
            if lst:
                lid = lst["id"]
            else:
                lid = models.execute_kw(DB, uid, PASSWORD, "mailing.list", "create",
                                        [{"name": list_name}])
                print(f"  [OK] Creada lista: {list_name}")
        list_ids_by_name[list_name] = lid
        print(f"  Lista '{list_name}' -> ID {lid}")

    # ── 2. Actualizar campos iz_* en partners existentes ────────────────
    print("\n[2] Actualizando campos iz_* en partners existentes...")
    for email, iz_data in PARTNER_IZ_DATA.items():
        partner = search_one(uid, models, "res.partner", [("email", "=", email)],
                             fields=["id", "name", "iz_gender"])
        if not partner:
            print(f"  [WARN] Partner no encontrado: {email}")
            continue
        models.execute_kw(DB, uid, PASSWORD, "res.partner", "write",
                          [[partner["id"]], iz_data])
        print(f"  [OK] Actualizado: {partner['name']} ({email})")

    # ── 3. Asignar partners a listas segmentadas ─────────────────────────
    print("\n[3] Asignando partners a listas de correo segmentadas...")
    all_partners = models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "search_read",
        [[("email", "!=", False), ("active", "=", True)]],
        {"fields": ["id", "name", "email", "iz_gender", "iz_fitness_goal",
                    "iz_experience_level", "iz_subscribed"]},
    )
    assigned = 0
    for partner in all_partners:
        if not partner.get("iz_gender") and not partner.get("iz_fitness_goal"):
            continue  # skip partners without iz fields
        contact_id = ensure_mailing_contact(uid, models, partner["name"], partner["email"])
        list_ids = get_list_ids_for_partner(uid, models, {
            "iz_gender": partner.get("iz_gender", ""),
            "iz_fitness_goal": partner.get("iz_fitness_goal", ""),
            "iz_experience_level": partner.get("iz_experience_level", ""),
        })
        for lid in list_ids:
            add_contact_to_list(uid, models, contact_id, lid)
        assigned += 1
        print(f"  [OK] {partner['name']} -> {len(list_ids)} lista(s)")

    print(f"\n  Total asignados: {assigned} partners")

    print("\n  [OK] Mailings de demostración creados automáticamente en mass_mailing.xml")

    print("\n" + "=" * 60)
    print("Email Marketing Seed completado.")
    print("Puedes enviar los mailings desde: Odoo -> Email Marketing -> Envios")
    print("=" * 60)


if __name__ == "__main__":
    run()
