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

    # Setup SMTP mail server from environment variables if provided
    try:
        import os

        smtp_host = os.environ.get("SMTP_HOST")
        if smtp_host:
            smtp_port = os.environ.get("SMTP_PORT") or "25"
            smtp_user = os.environ.get("SMTP_USER")
            smtp_pass = os.environ.get("SMTP_PASSWORD")
            smtp_encryption = os.environ.get("SMTP_ENCRYPTION") or "none"
            smtp_from = os.environ.get("SMTP_FROM")

            MailServer = env["ir.mail_server"].sudo()
            existing = MailServer.search([("smtp_host", "=", smtp_host)], limit=1)
            vals = {
                "name": "Iron Zone SMTP",
                "smtp_host": smtp_host,
                "smtp_port": int(smtp_port) if str(smtp_port).isdigit() else 25,
                "smtp_user": smtp_user or False,
                "smtp_pass": smtp_pass or False,
                "smtp_encryption": smtp_encryption or "none",
            }
            if existing:
                try:
                    existing.write(vals)
                except Exception:
                    pass
            else:
                try:
                    MailServer.create(vals)
                except Exception:
                    pass

            # Set a sensible catchall / notification sender so templates without explicit from work
            try:
                # Prefer the authenticated SMTP user as sender (some providers require this)
                catchall = smtp_user or smtp_from
                if catchall:
                    env["ir.config_parameter"].sudo().set_param("mail.catchall", catchall)
            except Exception:
                pass
    except Exception:
        pass
