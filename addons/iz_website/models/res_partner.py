from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    iz_subscribed = fields.Boolean(string="Subscribed to Iron Zone mailing list")
    iz_birthdate = fields.Date(string="Fecha de nacimiento")
    iz_gender = fields.Selection(
        [
            ("male", "Masculino"),
            ("female", "Femenino"),
            ("prefer_not", "Prefiero no decirlo"),
        ],
        string="Género",
    )
    iz_fitness_goal = fields.Selection(
        [
            ("weight_loss", "Pérdida de peso"),
            ("muscle_gain", "Aumento de masa muscular"),
            ("endurance", "Resistencia física"),
            ("general_fitness", "Fitness general"),
        ],
        string="Objetivo de fitness",
    )
    iz_experience_level = fields.Selection(
        [
            ("beginner", "Principiante"),
            ("intermediate", "Intermedio"),
            ("advanced", "Avanzado"),
        ],
        string="Nivel de experiencia",
    )
    iz_age = fields.Integer(
        string="Edad (IZ)",
        compute="_compute_iz_age",
        store=False,
    )
    # Campo fantasma necesario para que Odoo valide vistas antiguas en la DB durante actualizaciones
    iz_last_birthday_year = fields.Integer(string="Último año de cumpleaños")
    iz_welcome_sent = fields.Boolean(string="Welcome Sent")
    
    iz_gender_last_update = fields.Datetime(
        string="Última modificación de género", 
        readonly=True
    )

    # ------------------------------------------------------------------
    # Computed
    # ------------------------------------------------------------------

    @api.depends("iz_birthdate")
    def _compute_iz_age(self):
        today = date.today()
        for partner in self:
            if partner.iz_birthdate:
                bd = partner.iz_birthdate
                partner.iz_age = (
                    today.year - bd.year
                    - ((today.month, today.day) < (bd.month, bd.day))
                )
            else:
                partner.iz_age = 0

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    @api.constrains("iz_birthdate")
    def _check_iz_minimum_age(self):
        today = date.today()
        for partner in self:
            if not partner.iz_birthdate:
                continue
            bd = partner.iz_birthdate
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 14:
                raise ValidationError(
                    "Debes tener al menos 14 años para registrarte en Iron Zone."
                )

    # ------------------------------------------------------------------
    # CRUD hooks
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        today = fields.Date.context_today(self)
        for partner in partners:
            try:
                if partner.iz_subscribed:
                    partner._iz_subscribe_to_mailing_list()
                partner._iz_assign_to_segment_lists()
                partner._iz_send_welcome_if_needed()
            except Exception:
                pass
            
            if partner.iz_birthdate and partner.iz_birthdate.month == today.month and partner.iz_birthdate.day == today.day:
                template = self.env.ref("iz_website.mail_template_birthday", raise_if_not_found=False)
                if template:
                    try:
                        template.send_mail(partner.id, force_send=True)
                    except Exception:
                        pass
        return partners

    def write(self, vals):
        # Actualizar timestamp si el género cambia
        if "iz_gender" in vals:
            vals["iz_gender_last_update"] = fields.Datetime.now()
            
        res = super().write(vals)
        today = fields.Date.context_today(self)
        try:
            for partner in self:
                if "iz_subscribed" in vals and vals.get("iz_subscribed"):
                    partner._iz_subscribe_to_mailing_list()
                partner._iz_assign_to_segment_lists()
                
                # Enviar cumpleanos inmediatamente si se edita para hoy
                if "iz_birthdate" in vals and partner.iz_birthdate and partner.iz_birthdate.month == today.month and partner.iz_birthdate.day == today.day:
                    template = self.env.ref("iz_website.mail_template_birthday", raise_if_not_found=False)
                    if template:
                        template.send_mail(partner.id, force_send=True)
        except Exception:
            pass
        return res

    # ------------------------------------------------------------------
    # Mailing helpers
    # ------------------------------------------------------------------

    def _iz_get_mailing_list(self, xmlid):
        """Return a mailing.list record by xmlid, or False."""
        MailingList = self.env.get("mailing.list")
        if not MailingList:
            return False
        return self.env.ref(f"iz_website.{xmlid}", raise_if_not_found=False)

    def _iz_add_to_list(self, mailing_list):
        """Add self (single partner) to a mailing.list if they have email."""
        self.ensure_one()
        if not mailing_list or not self.email:
            return
        MailingContact = self.env.get("mailing.contact")
        if not MailingContact:
            return
        contact = MailingContact.search(
            [("email", "=ilike", self.email)], limit=1
        )
        if not contact:
            contact = MailingContact.create(
                {"name": self.name or "-", "email": self.email}
            )
        try:
            mailing_list.write({"contact_ids": [(4, contact.id)]})
        except Exception:
            try:
                contact.write({"list_ids": [(4, mailing_list.id)]})
            except Exception:
                pass

    def _iz_subscribe_to_mailing_list(self):
        """Subscribe to the general Iron Zone customer list."""
        self.ensure_one()
        if not self.iz_subscribed or not self.email:
            return
        mailing_list = self._iz_get_mailing_list("mailing_list_customers")
        if mailing_list:
            self._iz_add_to_list(mailing_list)

    def _iz_assign_to_segment_lists(self):
        """Assign partner to segmented lists based on iz_* profile fields."""
        self.ensure_one()
        if not self.email:
            return

        # ── Género ──
        gender_map = {
            "female": "mailing_list_women",
            "male": "mailing_list_men",
        }
        if self.iz_gender in gender_map:
            lst = self._iz_get_mailing_list(gender_map[self.iz_gender])
            if lst:
                self._iz_add_to_list(lst)

        # ── Objetivo fitness ──
        goal_map = {
            "muscle_gain": "mailing_list_goal_muscle",
            "weight_loss": "mailing_list_goal_weight_loss",
            "endurance": "mailing_list_goal_endurance",
            "general_fitness": "mailing_list_goal_fitness",
        }
        if self.iz_fitness_goal in goal_map:
            lst = self._iz_get_mailing_list(goal_map[self.iz_fitness_goal])
            if lst:
                self._iz_add_to_list(lst)

        # ── Nivel de experiencia ──
        level_map = {
            "beginner": "mailing_list_beginners",
            "advanced": "mailing_list_advanced",
        }
        if self.iz_experience_level in level_map:
            lst = self._iz_get_mailing_list(level_map[self.iz_experience_level])
            if lst:
                self._iz_add_to_list(lst)

    def _iz_send_welcome_if_needed(self):
        self.ensure_one()
        if not self.iz_subscribed or not self.email:
            return
        template = self.env.ref(
            "iz_website.mail_template_welcome", raise_if_not_found=False
        )
        if not template:
            template = self.env["mail.template"].search(
                [("name", "=", "IZ Bienvenida")], limit=1
            )
        if not template:
            return
        try:
            template.send_mail(self.id, force_send=True)
        except Exception:
            pass
