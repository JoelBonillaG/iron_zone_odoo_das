# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Subscription"
    )

    def action_open_subscription(self):
        self.ensure_one()
        return self.subscription_id.get_formview_action()

    def _get_related_subscriptions_for_benefits(self):
        subscriptions = self.mapped("subscription_id")
        origin_orders = self.env["sale.order"].search([("invoice_ids", "in", self.ids)])
        subscriptions |= origin_orders.mapped("subscription_ids")
        subscriptions |= origin_orders.mapped("order_subscription_id")
        return subscriptions

    def _activate_paid_subscriptions(self):
        subscriptions = self._get_related_subscriptions_for_benefits()
        subscriptions = subscriptions.filtered(
            lambda subscription: subscription.active
            and subscription.stage_type not in ("in_progress", "post")
            and subscription._has_paid_invoice()
        )
        if subscriptions:
            subscriptions.action_start_subscription()

    def write(self, values):
        res = super().write(values)
        if "payment_state" in values or "state" in values:
            self._activate_paid_subscriptions()
        return res

    def action_post(self):
        res = super().action_post()
        self._activate_paid_subscriptions()
        return res


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def _activate_paid_subscriptions(self):
        moves = self.mapped("debit_move_id.move_id") | self.mapped(
            "credit_move_id.move_id"
        )
        moves.filtered(
            lambda move: move.move_type == "out_invoice"
        )._activate_paid_subscriptions()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._activate_paid_subscriptions()
        return records
