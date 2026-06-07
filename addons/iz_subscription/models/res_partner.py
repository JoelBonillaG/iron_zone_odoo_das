# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="partner_id",
        string="Suscripciones",
    )
    subscription_count = fields.Integer(
        required=False,
        compute="_compute_subscription_count",
    )

    def _compute_subscription_count(self):
        data = self.env["sale.subscription"].read_group(
            domain=[("partner_id", "in", self.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )
        count_dict = {item["partner_id"][0]: item["partner_id_count"] for item in data}
        for record in self:
            record.subscription_count = count_dict.get(record.id, 0)

    def action_view_subscription_ids(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "list,form",
            "context": {
                "default_partner_id": self.id,
            },
        }

    def _get_paid_active_subscriptions(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        subscriptions = self.env["sale.subscription"].search(
            [
                ("partner_id", "=", self.id),
                ("stage_type", "=", "in_progress"),
                ("active", "=", True),
                "|",
                ("date", "=", False),
                ("date", ">=", today),
            ]
        )
        return subscriptions.filtered(lambda subscription: subscription._has_paid_invoice())

    def _get_current_subscription_plan(self):
        self.ensure_one()
        candidates = []
        for subscription in self._get_paid_active_subscriptions():
            plan = subscription._get_subscription_plan()
            if plan:
                candidates.append((plan.priority, plan.sequence, plan.id, plan, subscription))
        if not candidates:
            return self.env["iz.subscription.plan"], self.env["sale.subscription"]
        candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
        best = candidates[0]
        return best[3], best[4]

    def _get_current_subscription_benefits(self, benefit_scope=False):
        self.ensure_one()
        plan, subscription = self._get_current_subscription_plan()
        if not plan:
            return self.env["iz.subscription.benefit"]
        benefits = plan.benefit_ids.filtered(lambda benefit: benefit.active)
        if benefit_scope:
            benefits = benefits.filtered(
                lambda benefit: benefit.benefit_scope == benefit_scope
            )
        return benefits

    def _has_previous_event_registration(self, exclude_order_id=False):
        """Returns True if this partner has at least one non-cancelled event registration.
        Used to implement the 'first event free' business rule."""
        self.ensure_one()
        domain = [
            ("partner_id", "=", self.id),
            ("state", "!=", "cancel"),
        ]
        if exclude_order_id:
            # Evita contarse a sí mismo si ya existe una inscripción borrador en la orden actual
            domain.append(("sale_order_id", "!=", exclude_order_id))
        return bool(self.env["event.registration"].sudo().search_count(domain))
