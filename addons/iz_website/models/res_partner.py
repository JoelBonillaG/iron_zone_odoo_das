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
    iz_onboarding_day1_sent = fields.Boolean(string="Onboarding Day 1 Sent")
    iz_onboarding_day23_sent = fields.Boolean(string="Onboarding Day 2-3 Sent")
    
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
        if self.env.context.get('iz_skip_automation'):
            return partners
            
        for partner in partners:
            try:
                # Synchronize partner category tags
                partner._iz_sync_partner_tags()
                
                if partner.iz_subscribed and partner.email:
                    partner._iz_subscribe_to_mailing_list()
                if partner.email:
                    partner._iz_assign_to_segment_lists()
            except Exception:
                pass
            
            # Enviar siempre la bienvenida en el alta; si hoy es su cumpleaños, pasar flag
            if partner.email:
                template = self.env.ref("iz_website.mail_template_welcome", raise_if_not_found=False)
                if template:
                    try:
                        is_bday = False
                        if partner.iz_birthdate and partner.iz_birthdate.month == today.month and partner.iz_birthdate.day == today.day:
                            is_bday = True
                        ctx = {"partner": partner, "is_birthday": is_bday, "is_birthday_today": is_bday}
                        template.with_context(**ctx).send_mail(partner.id)
                        try:
                            partner.sudo().write({"iz_welcome_sent": True})
                        except Exception:
                            pass
                    except Exception:
                        pass
        return partners

    def write(self, vals):
        if self.env.context.get('iz_skip_automation'):
            return super().write(vals)
        self = self.with_context(iz_skip_automation=True)
        # Actualizar timestamp si el género cambia
        if "iz_gender" in vals:
            vals["iz_gender_last_update"] = fields.Datetime.now()
            
        res = super().write(vals)
        today = fields.Date.context_today(self)

        try:
            for partner in self:
                # Synchronize partner category tags
                partner._iz_sync_partner_tags()
                
                # Trigger general and segment subscriptions if they have email and subscribed
                if partner.email:
                    if partner.iz_subscribed:
                        partner._iz_subscribe_to_mailing_list()
                    partner._iz_assign_to_segment_lists()
                
                # Enviar correo de campaña específico al actualizar objetivo fitness
                if "iz_fitness_goal" in vals and partner.iz_fitness_goal and partner.email:
                    template_xmlid = f"mail_template_goal_{partner.iz_fitness_goal}"
                    template = self.env.ref(f"iz_website.{template_xmlid}", raise_if_not_found=False)
                    if template:
                        try:
                            template.send_mail(partner.id)
                        except Exception:
                            pass
                
                # Enviar correo de campaña específico al actualizar nivel de experiencia
                if "iz_experience_level" in vals and partner.iz_experience_level and partner.email:
                    template_xmlid = f"mail_template_level_{partner.iz_experience_level}"
                    template = self.env.ref(f"iz_website.{template_xmlid}", raise_if_not_found=False)
                    if template:
                        try:
                            template.send_mail(partner.id)
                        except Exception:
                            pass
                
                # Enviar cumpleanos inmediatamente si se edita para hoy
                if partner.email and "iz_birthdate" in vals and partner.iz_birthdate and partner.iz_birthdate.month == today.month and partner.iz_birthdate.day == today.day:
                    template = self.env.ref("iz_website.mail_template_birthday", raise_if_not_found=False)
                    if template:
                        try:
                            template.with_context(partner=partner).send_mail(partner.id)
                        except Exception:
                            pass
        except Exception:
            pass
        return res

    # ------------------------------------------------------------------
    # Mailing helpers
    # ------------------------------------------------------------------

    def _iz_get_mailing_list(self, xmlid):
        """Return a mailing.list record by xmlid, or False."""
        if "mailing.list" not in self.env:
            return False
        res = self.env.ref(f"iz_website.{xmlid}", raise_if_not_found=False)
        return res

    def _iz_add_to_list(self, mailing_list):
        """Add self (single partner) to a mailing.list if they have email."""
        self.ensure_one()
        if not mailing_list or not self.email:
            return
        if "mailing.contact" not in self.env:
            return
        MailingContact = self.env["mailing.contact"]
        contact = MailingContact.search(
            [("email", "=ilike", self.email)], limit=1
        )
        if not contact:
            contact = MailingContact.create(
                {"name": self.name or "-", "email": self.email}
            )
        
        # Native Odoo 18 subscription creation
        if "mailing.subscription" not in self.env:
            return
        MailingSubscription = self.env["mailing.subscription"]
        sub = MailingSubscription.search([
            ("contact_id", "=", contact.id),
            ("list_id", "=", mailing_list.id),
        ], limit=1)
        if not sub:
            try:
                MailingSubscription.create({
                    "contact_id": contact.id,
                    "list_id": mailing_list.id,
                    "opt_out": False,
                })
            except Exception:
                pass
        else:
            if sub.opt_out:
                try:
                    sub.write({"opt_out": False})
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
        """Assign partner to segmented lists based on iz_* profile fields, and remove them from old ones."""
        self.ensure_one()
        if not self.email:
            return

        if "mailing.contact" not in self.env:
            return
        MailingContact = self.env["mailing.contact"]
        contact = MailingContact.search([("email", "=ilike", self.email)], limit=1)
        if not contact:
            contact = MailingContact.create({"name": self.name or "-", "email": self.email})

        if "mailing.subscription" not in self.env:
            return
        MailingSubscription = self.env["mailing.subscription"]

        # ── Categories and their mapping ──
        gender_map = {
            "female": "mailing_list_women",
            "male": "mailing_list_men",
        }
        all_gender_xmlids = ["mailing_list_women", "mailing_list_men"]

        goal_map = {
            "muscle_gain": "mailing_list_goal_muscle",
            "weight_loss": "mailing_list_goal_weight_loss",
            "endurance": "mailing_list_goal_endurance",
            "general_fitness": "mailing_list_goal_fitness",
        }
        all_goal_xmlids = [
            "mailing_list_goal_muscle",
            "mailing_list_goal_weight_loss",
            "mailing_list_goal_endurance",
            "mailing_list_goal_fitness",
        ]

        level_map = {
            "beginner": "mailing_list_beginners",
            "intermediate": "mailing_list_intermediates",
            "advanced": "mailing_list_advanced",
        }
        all_level_xmlids = [
            "mailing_list_beginners",
            "mailing_list_intermediates",
            "mailing_list_advanced",
        ]

        def process_category(current_value, value_map, all_xmlids):
            # Resolve the active mailing list record (if any)
            active_list = False
            if current_value in value_map:
                active_list = self._iz_get_mailing_list(value_map[current_value])

            # Resolve all mailing lists in this category
            all_lists = {}
            for xmlid in all_xmlids:
                lst = self._iz_get_mailing_list(xmlid)
                if lst:
                    all_lists[xmlid] = lst

            # Unsubscribe/delete subscriptions from other lists in this category
            other_list_ids = [
                lst.id for xmlid, lst in all_lists.items()
                if not active_list or lst.id != active_list.id
            ]
            if other_list_ids:
                old_subs = MailingSubscription.search([
                    ("contact_id", "=", contact.id),
                    ("list_id", "in", other_list_ids),
                ])
                if old_subs:
                    try:
                        old_subs.unlink()
                    except Exception:
                        pass

            # Subscribe to the active list
            if active_list:
                sub = MailingSubscription.search([
                    ("contact_id", "=", contact.id),
                    ("list_id", "=", active_list.id),
                ], limit=1)
                if not sub:
                    try:
                        MailingSubscription.create({
                            "contact_id": contact.id,
                            "list_id": active_list.id,
                            "opt_out": False,
                        })
                    except Exception:
                        pass
                elif sub.opt_out:
                    try:
                        sub.write({"opt_out": False})
                    except Exception:
                        pass

        # Process each category
        process_category(self.iz_gender, gender_map, all_gender_xmlids)
        process_category(self.iz_fitness_goal, goal_map, all_goal_xmlids)
        process_category(self.iz_experience_level, level_map, all_level_xmlids)

    def _iz_sync_partner_tags(self):
        """Synchronize partner tags (category_id) with their current gender, goal, and level."""
        self.ensure_one()
        if "res.partner.category" not in self.env:
            return
        PartnerCategory = self.env["res.partner.category"]
        
        # Helper to get or create tag
        def get_or_create_tag(name):
            tag = PartnerCategory.search([("name", "=", name)], limit=1)
            if not tag:
                try:
                    tag = PartnerCategory.create({"name": name})
                except Exception:
                    pass
            return tag

        # Define all possible tags we manage
        managed_tags = {
            "gender": {
                "male": "Género: Masculino",
                "female": "Género: Femenino",
            },
            "goal": {
                "muscle_gain": "Objetivo: Masa muscular",
                "weight_loss": "Objetivo: Pérdida de peso",
                "endurance": "Objetivo: Resistencia",
                "general_fitness": "Objetivo: Fitness general",
            },
            "level": {
                "beginner": "Nivel: Principiante",
                "intermediate": "Nivel: Intermedio",
                "advanced": "Nivel: Avanzado",
            }
        }

        # Gather all managed tag names
        all_managed_names = []
        for cat, val_map in managed_tags.items():
            all_managed_names.extend(val_map.values())

        # Resolve actual tag records for all managed ones
        managed_tag_records = PartnerCategory.search([("name", "in", all_managed_names)])
        
        # Find which tags the partner SHOULD have
        should_have_names = []
        if self.iz_gender in managed_tags["gender"]:
            should_have_names.append(managed_tags["gender"][self.iz_gender])
            
        if self.iz_fitness_goal in managed_tags["goal"]:
            should_have_names.append(managed_tags["goal"][self.iz_fitness_goal])
            
        if self.iz_experience_level in managed_tags["level"]:
            should_have_names.append(managed_tags["level"][self.iz_experience_level])

        # Get or create the tags the partner should have
        tags_to_add = PartnerCategory.browse([])
        for name in should_have_names:
            t = get_or_create_tag(name)
            if t:
                tags_to_add |= t

        # Get current categories excluding the other managed tags
        current_other_tags = self.category_id.filtered(lambda c: c.id not in managed_tag_records.ids)
        
        # Final set of tags
        try:
            self.sudo().write({
                "category_id": [(6, 0, (current_other_tags | tags_to_add).ids)]
            })
        except Exception:
            pass

    def _iz_send_welcome_if_needed(self):
        self.ensure_one()
        if not self.iz_subscribed or not self.email or self.iz_welcome_sent:
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
            is_bday = bool(self.iz_birthdate and self.iz_birthdate.month == today.month and self.iz_birthdate.day == today.day)
            template.with_context(partner=self, is_birthday=is_bday, is_birthday_today=is_bday).send_mail(self.id)
            self.sudo().write({"iz_welcome_sent": True})
        except Exception:
            pass
