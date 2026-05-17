def post_init_hook(cr, registry):
    """Post-install hook: configure website and subscribe existing partners."""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Configure the website (language, menus, pages)
    try:
        env["website"]._iz_configure_site()
    except Exception:
        pass

    # Back-fill: subscribe existing partners with email to the general list
    # and assign them to segmented lists if they have iz_* fields set.
    partners = env["res.partner"].search([("email", "!=", False), ("active", "=", True)])
    for partner in partners:
        try:
            if partner.iz_subscribed:
                partner._iz_subscribe_to_mailing_list()
            partner._iz_assign_to_segment_lists()
        except Exception:
            pass
