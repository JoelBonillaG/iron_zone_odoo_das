from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventRegistration(models.Model):
    _inherit = "event.registration"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription",
        string="Suscripcion aplicada",
        readonly=True,
        copy=False,
    )
    subscription_plan_id = fields.Many2one(
        comodel_name="iz.subscription.plan",
        string="Plan",
        readonly=True,
        copy=False,
    )
    subscription_benefit_id = fields.Many2one(
        comodel_name="iz.subscription.benefit",
        string="Beneficio aplicado",
        readonly=True,
        copy=False,
    )
    subscription_discount_percent = fields.Float(
        string="Descuento de suscripcion (%)",
        readonly=True,
        copy=False,
    )
    subscription_original_price = fields.Float(
        string="Precio original",
        readonly=True,
        copy=False,
    )
    subscription_final_price = fields.Float(
        string="Precio con suscripcion",
        readonly=True,
        copy=False,
    )

    def _get_subscription_ticket_price(self):
        self.ensure_one()
        ticket = self.event_ticket_id if "event_ticket_id" in self._fields else False
        if ticket:
            return ticket.price
        return 0.0

    def _prepare_subscription_benefit_values(self):
        self.ensure_one()
        price = self._get_subscription_ticket_price()
        values = {
            "subscription_id": False,
            "subscription_plan_id": False,
            "subscription_benefit_id": False,
            "subscription_discount_percent": 0.0,
            "subscription_original_price": price,
            "subscription_final_price": price,
        }
        if not self.partner_id:
            return values

        # --- Beneficio especial: Día de la Mujer ---
        ticket = self.event_ticket_id if "event_ticket_id" in self._fields else False
        event = ticket.event_id if ticket else False
        if event and self.partner_id.iz_gender == 'female':
            promo_keywords = ["yoga avanzado", "pilates avanzado"]
            if any(kw in (event.name or "").lower() for kw in promo_keywords):
                already_used = self.env['event.registration'].sudo().search_count([
                    ('partner_id', '=', self.partner_id.id),
                    ('id', '!=', self.id),
                    ('sale_order_id', '!=', self.sale_order_id.id if self.sale_order_id else False),
                    ('state', '!=', 'cancel'),
                    '|',
                    ('event_id.name', 'ilike', 'Yoga Avanzado'),
                    ('event_id.name', 'ilike', 'Pilates Avanzado')
                ])
                if already_used == 0:
                    values.update({
                        "subscription_discount_percent": 100.0,
                        "subscription_final_price": 0.0,
                    })
                    return values

        plan, subscription = self.partner_id._get_current_subscription_plan()
        if not plan:
            return values

        # Get event from the ticket (if any) to check allowed plans
        ticket = self.event_ticket_id if "event_ticket_id" in self._fields else False
        event = ticket.event_id if ticket else (self.event_id if "event_id" in self._fields else False)

        all_benefits = self.partner_id._get_current_subscription_benefits("events")
        if event and event.subscription_plan_ids:
            all_benefits = all_benefits.filtered(lambda b: b.plan_id in event.subscription_plan_ids)
        # (no else: if no plan restriction, benefit applies to all events)

        benefit = all_benefits[:1]
        if not benefit:
            return values

        values.update(
            {
                "subscription_id": subscription.id,
                "subscription_plan_id": plan.id,
                "subscription_benefit_id": benefit.id,
                "subscription_discount_percent": (
                    100.0
                    if benefit.benefit_type == "free"
                    else benefit.discount_percent
                ),
                "subscription_final_price": benefit.apply_to_amount(price),
            }
        )
        return values

    def _apply_subscription_benefit(self):
        for registration in self:
            registration.write(registration._prepare_subscription_benefit_values())

    def _check_single_registration_per_event(self, vals_list):
        seen_keys = set()
        for vals in vals_list:
            event_id = vals.get("event_id")
            if not event_id:
                continue

            partner_id = vals.get("partner_id")
            email = (vals.get("email") or "").strip().lower()
            if partner_id:
                key = (event_id, "partner", partner_id)
                domain = [
                    ("event_id", "=", event_id),
                    ("partner_id", "=", partner_id),
                    ("state", "!=", "cancel"),
                ]
            elif email:
                key = (event_id, "email", email)
                domain = [
                    ("event_id", "=", event_id),
                    ("email", "=ilike", email),
                    ("state", "!=", "cancel"),
                ]
            else:
                continue

            if key in seen_keys or self.sudo().search_count(domain):
                raise ValidationError(
                    _("Solo puedes tener un boleto por evento.")
                )
            seen_keys.add(key)

    @api.model_create_multi
    def create(self, vals_list):
        self._check_single_registration_per_event(vals_list)
        records = super().create(vals_list)
        records._apply_subscription_benefit()
        return records

    def write(self, values):
        res = super().write(values)
        watched_fields = {"partner_id", "event_ticket_id", "event_id"}
        readonly_fields = {
            "subscription_id",
            "subscription_plan_id",
            "subscription_benefit_id",
            "subscription_discount_percent",
            "subscription_original_price",
            "subscription_final_price",
        }
        if watched_fields.intersection(values) and not readonly_fields.intersection(values):
            self._apply_subscription_benefit()
        return res
