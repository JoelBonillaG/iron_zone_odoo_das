from datetime import date, timedelta

from odoo import api, fields, models


class IzMarketing(models.TransientModel):
    _name = "iz.marketing"
    _description = "Iron Zone Marketing – Campañas automáticas"

    # ------------------------------------------------------------------
    # Helper privado
    # ------------------------------------------------------------------

    def _get_template(self, xmlid):
        return self.env.ref(f"iz_website.{xmlid}", raise_if_not_found=False)

    def _send_to_partners(self, partners, template):
        """Envía template a cada partner; ignora errores individuales."""
        if not template:
            return 0
        sent = 0
        for partner in partners:
            try:
                template.with_context(partner=partner).send_mail(partner.id, force_send=True)
                sent += 1
            except Exception:
                pass
        return sent

    def _signup_age_days(self, partner):
        if not partner.create_date:
            return None
        create_date = fields.Datetime.to_datetime(partner.create_date)
        return (fields.Date.context_today(self) - create_date.date()).days

    def _send_onboarding_batch(self, partners, template, flag_field):
        sent = 0
        for partner in partners:
            try:
                template.with_context(partner=partner).send_mail(partner.id, force_send=True)
                partner.sudo().write({flag_field: True})
                sent += 1
            except Exception:
                pass
        return sent

    # ------------------------------------------------------------------
    # Cumpleaños
    # ------------------------------------------------------------------

    @api.model
    def send_birthday_emails(self):
        today = fields.Date.context_today(self)
        partners = self.env["res.partner"].search([
            ("iz_birthdate", "!=", False),
            ("email", "!=", False),
            ("active", "=", True),
        ])
        birthday_partners = partners.filtered(
            lambda p: p.iz_birthdate.month == today.month and p.iz_birthdate.day == today.day
        )
        template = self._get_template("mail_template_birthday")
        sent = self._send_to_partners(birthday_partners, template)
        if sent:
            self.env["ir.logging"].sudo().create({
                "name": "iz.marketing",
                "type": "server",
                "level": "info",
                "message": f"Cumpleaños: {sent} emails enviados.",
                "path": "iz.marketing",
                "func": "send_birthday_emails",
                "line": 0,
            })

    # ------------------------------------------------------------------
    # Día de la Mujer – 8 de marzo
    # ------------------------------------------------------------------

    @api.model
    def send_womens_day_campaign(self):
        today = fields.Date.context_today(self)
        if today.month != 3 or today.day != 8:
            return
        partners = self.env["res.partner"].search([
            ("iz_gender", "=", "female"),
            ("email", "!=", False),
            ("active", "=", True),
        ])
        template = self._get_template("mail_template_womens_day")
        self._send_to_partners(partners, template)

    # ------------------------------------------------------------------
    # Día del Hombre – 19 de noviembre
    # ------------------------------------------------------------------

    @api.model
    def send_mens_day_campaign(self):
        today = fields.Date.context_today(self)
        if today.month != 11 or today.day != 19:
            return
        partners = self.env["res.partner"].search([
            ("iz_gender", "=", "male"),
            ("email", "!=", False),
            ("active", "=", True),
        ])
        template = self._get_template("mail_template_mens_day")
        self._send_to_partners(partners, template)

    # ------------------------------------------------------------------
    # Membresía próxima a vencer (7 días)
    # ------------------------------------------------------------------

    @api.model
    def send_membership_expiry_campaign(self):
        target_date = fields.Date.context_today(self) + timedelta(days=7)
        subscriptions = self.env["sale.subscription"].search([
            ("date", "=", target_date),
            ("stage_type", "=", "in_progress"),
            ("active", "=", True),
        ])
        template = self._get_template("mail_template_membership_expiry")
        partners_notified = self.env["res.partner"]
        for sub in subscriptions:
            partner = sub.partner_id
            if partner and partner.email and partner not in partners_notified:
                if template:
                    try:
                        template.send_mail(partner.id, force_send=True)
                    except Exception:
                        pass
                partners_notified |= partner

    # ------------------------------------------------------------------
    # Campañas estacionales
    # ------------------------------------------------------------------

    @api.model
    def send_seasonal_campaigns(self):
        today = fields.Date.context_today(self)
        occasion = None

        # Navidad – 25 de diciembre
        if today.month == 12 and today.day == 25:
            occasion = "christmas"

        # Día de la Madre – segundo domingo de mayo
        if today.month == 5:
            sundays = [
                d for d in (date(today.year, 5, d) for d in range(1, 32)
                            if d <= 31)
                if d.weekday() == 6
            ]
            if len(sundays) >= 2 and today == sundays[1]:
                occasion = "mothers_day"

        # Día del Padre – tercer domingo de junio
        if today.month == 6:
            sundays = [
                d for d in (date(today.year, 6, d) for d in range(1, 31)
                            if d <= 30)
                if d.weekday() == 6
            ]
            if len(sundays) >= 3 and today == sundays[2]:
                occasion = "fathers_day"

        if not occasion:
            return

        partners = self.env["res.partner"].search([
            ("email", "!=", False),
            ("active", "=", True),
            ("iz_subscribed", "=", True),
        ])
        template = self._get_template("mail_template_seasonal")
        self._send_to_partners(partners, template)

    # ------------------------------------------------------------------
    # Campañas de marketing general (orquestador)
    # ------------------------------------------------------------------

    @api.model
    def send_marketing_campaigns(self):
        """Orquestador principal – llamado por el cron diario."""
        partners = self.env["res.partner"].search([
            ("email", "!=", False),
            ("active", "=", True),
            ("iz_subscribed", "=", True),
        ])

        day1_partners = partners.filtered(
            lambda partner: self._signup_age_days(partner) == 1 and not partner.iz_onboarding_day1_sent
        )
        day23_partners = partners.filtered(
            lambda partner: self._signup_age_days(partner) in (2, 3) and not partner.iz_onboarding_day23_sent
        )

        self._send_onboarding_batch(
            day1_partners,
            self._get_template("mail_template_level_beginner"),
            "iz_onboarding_day1_sent",
        )
        self._send_onboarding_batch(
            day23_partners,
            self._get_template("mail_template_goal_muscle_gain"),
            "iz_onboarding_day23_sent",
        )

        self.send_womens_day_campaign()
        self.send_mens_day_campaign()
        self.send_seasonal_campaigns()
        self.send_membership_expiry_campaign()
