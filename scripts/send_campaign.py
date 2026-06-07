#!/usr/bin/env python3
"""
send_campaign.py — Envia una campaña de correo de Iron Zone a un destinatario.

Las campañas son plantillas mail.template del modulo iz_website. Normalmente se
disparan por cron segun fecha/segmento; este script permite enviarlas a mano
para probar el contenido.

Uso (desde la raiz del proyecto, con Odoo corriendo):
    python scripts/send_campaign.py --list
    python scripts/send_campaign.py <campaña> <email>
    python scripts/send_campaign.py --all <email>

Ejemplos:
    python scripts/send_campaign.py womens_day josuegarcab2@hotmail.com
    python scripts/send_campaign.py --all josuegarcab2@hotmail.com
"""
import os
import sys
import xmlrpc.client

# Reusar la conexion XML-RPC de los seeds (lee .env, resuelve credenciales)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "seeds"))
from config import DB, PASSWORD, connect  # noqa: E402

# alias amigable -> xmlid de la plantilla (modulo iz_website)
CAMPAIGNS = {
    "welcome":            ("mail_template_welcome",            "Bienvenida nuevo miembro"),
    "birthday":           ("mail_template_birthday",           "Cumpleaños"),
    "womens_day":         ("mail_template_womens_day",         "Dia de la Mujer (8 mar)"),
    "mens_day":           ("mail_template_mens_day",           "Dia del Hombre (19 nov)"),
    "membership_expiry":  ("mail_template_membership_expiry",  "Membresia por vencer (7 dias)"),
    "goal_muscle":        ("mail_template_goal_muscle_gain",   "Objetivo: masa muscular"),
    "goal_weight_loss":   ("mail_template_goal_weight_loss",   "Objetivo: perdida de peso"),
    "goal_endurance":     ("mail_template_goal_endurance",     "Objetivo: resistencia"),
    "goal_fitness":       ("mail_template_goal_general_fitness", "Objetivo: fitness general"),
    "level_beginner":     ("mail_template_level_beginner",     "Nivel: principiante"),
    "level_intermediate": ("mail_template_level_intermediate", "Nivel: intermedio"),
    "level_advanced":     ("mail_template_level_advanced",     "Nivel: avanzado"),
    "seasonal":           ("mail_template_seasonal",           "Estacional (navidad/madre/padre)"),
}


def get_template_id(models, uid, xmlid):
    rows = models.execute_kw(
        DB, uid, PASSWORD, "ir.model.data", "search_read",
        [[("module", "=", "iz_website"), ("name", "=", xmlid)]],
        {"fields": ["res_id"], "limit": 1},
    )
    return rows[0]["res_id"] if rows else None


def get_or_create_partner(models, uid, email):
    rows = models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "search_read",
        [[("email", "=", email)]], {"fields": ["id", "name"], "limit": 1},
    )
    if rows:
        return rows[0]["id"]
    return models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "create",
        [{"name": email.split("@")[0], "email": email}],
    )


def send_one(models, uid, key, partner_id):
    xmlid, label = CAMPAIGNS[key]
    tmpl_id = get_template_id(models, uid, xmlid)
    if not tmpl_id:
        print(f"  [SKIP] plantilla no encontrada: {xmlid}")
        return False
    try:
        models.execute_kw(
            DB, uid, PASSWORD, "mail.template", "send_mail",
            [tmpl_id, partner_id], {"force_send": True},
        )
    except xmlrpc.client.Fault as fault:
        # send_mail puede no serializar el retorno; el correo igual se envia
        if "marshal" not in fault.faultString:
            print(f"  [FAIL] {key} ({label}): {fault.faultString.splitlines()[-1][:120]}")
            return False
    print(f"  [OK] {key} -> {label}")
    return True


def print_list():
    print("Campañas disponibles:")
    for key, (_xmlid, label) in CAMPAIGNS.items():
        print(f"  {key:<20} {label}")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("--list", "-l", "list"):
        print_list()
        return

    if args[0] == "--all":
        if len(args) < 2:
            print("Uso: python scripts/send_campaign.py --all <email>")
            return
        email = args[1]
        uid, models = connect()
        partner_id = get_or_create_partner(models, uid, email)
        print(f"Enviando TODAS las campañas a {email} ...")
        for key in CAMPAIGNS:
            send_one(models, uid, key, partner_id)
        print(f"\nListo. Revisa la bandeja (y SPAM) de {email}.")
        return

    if len(args) < 2:
        print("Uso: python scripts/send_campaign.py <campaña> <email>   (o --list)")
        return

    key, email = args[0], args[1]
    if key not in CAMPAIGNS:
        print(f"Campaña invalida: {key}")
        print_list()
        return
    uid, models = connect()
    partner_id = get_or_create_partner(models, uid, email)
    print(f"Enviando '{key}' a {email} ...")
    send_one(models, uid, key, partner_id)
    print(f"\nListo. Revisa la bandeja (y SPAM) de {email}.")


if __name__ == "__main__":
    main()
