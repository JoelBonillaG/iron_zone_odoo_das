from odoo import api, fields, models


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

        plan, subscription = self.partner_id._get_current_subscription_plan()
        if not plan:
            return values

        benefit = self.partner_id._get_current_subscription_benefits("events")[:1]
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

    @api.model_create_multi
    def create(self, vals_list):
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
