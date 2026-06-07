# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subscription_benefit_id = fields.Many2one(
        "iz.subscription.benefit",
        string="Beneficio de suscripcion",
        readonly=True,
        copy=False,
    )
    subscription_plan_id = fields.Many2one(
        "iz.subscription.plan",
        string="Plan de suscripcion",
        readonly=True,
        copy=False,
    )
    subscription_discount_percent = fields.Float(
        string="Descuento por suscripcion",
        readonly=True,
        copy=False,
    )

    def _get_subscription_event_benefit(self):
        self.ensure_one()
        ticket = self.event_ticket_id if "event_ticket_id" in self._fields else False
        if not ticket:
            return (
                self.env["iz.subscription.plan"],
                self.env["sale.subscription"],
                self.env["iz.subscription.benefit"],
            )
        partner = self.order_id.partner_id
        if not partner:
            return (
                self.env["iz.subscription.plan"],
                self.env["sale.subscription"],
                self.env["iz.subscription.benefit"],
            )
        plan, subscription = partner._get_current_subscription_plan()
        if not plan:
            return plan, subscription, self.env["iz.subscription.benefit"]
        benefits = partner._get_current_subscription_benefits("events")
        # If the event restricts to specific plans, filter — otherwise apply to all events
        if ticket.event_id and ticket.event_id.subscription_plan_ids:
            benefits = benefits.filtered(lambda b: b.plan_id in ticket.event_id.subscription_plan_ids)
        # (no else: if subscription_plan_ids is empty, all benefits apply)
        benefit = benefits[:1]
        return plan, subscription, benefit

    def _apply_subscription_event_benefit(self):
        for line in self:
            ticket = line.event_ticket_id if "event_ticket_id" in line._fields else False

            # --- Priority 1: First event free (highest priority) ---
            if ticket:
                partner = line.order_id.partner_id
                if partner and not partner._has_previous_event_registration():
                    line.discount = 100.0
                    line.subscription_benefit_id = False
                    line.subscription_plan_id = False
                    line.subscription_discount_percent = 100.0
                    continue

            # --- Priority 2: Subscription benefit discount ---
            plan, _subscription, benefit = line._get_subscription_event_benefit()
            if not benefit:
                if "event_ticket_id" in line._fields and line.event_ticket_id:
                    line.discount = 0.0
                    line.subscription_benefit_id = False
                    line.subscription_plan_id = False
                    line.subscription_discount_percent = 0.0
                continue
            discount = (
                100.0
                if benefit.benefit_type == "free"
                else benefit.discount_percent
            )
            discount = min(max(discount, 0.0), 100.0)
            line.discount = discount
            line.subscription_benefit_id = benefit
            line.subscription_plan_id = plan
            line.subscription_discount_percent = discount


    def _is_subscription_product_line(self):
        """True for plain shop products eligible for the 'products' benefit.
        Excludes the subscription plan itself and event tickets (those use the
        events benefit), so a line never gets two subscription discounts."""
        self.ensure_one()
        if not self.product_id:
            return False
        if self.product_id.product_tmpl_id.subscribable:
            return False
        if "event_ticket_id" in self._fields and self.event_ticket_id:
            return False
        return True

    def _apply_subscription_product_benefit(self):
        """Apply the active 'products' benefit (a discount) to plain product lines."""
        for line in self:
            if not line._is_subscription_product_line():
                continue
            partner = line.order_id.partner_id
            benefit = (
                partner._get_current_subscription_benefits("products")[:1]
                if partner
                else self.env["iz.subscription.benefit"]
            )
            # Only discounts apply to products (no "free" giveaway of the shop)
            if not benefit or benefit.benefit_type != "discount":
                # Reset only a discount we set ourselves from a products benefit
                if (
                    line.subscription_benefit_id
                    and line.subscription_benefit_id.benefit_scope == "products"
                ):
                    line.discount = 0.0
                    line.subscription_benefit_id = False
                    line.subscription_plan_id = False
                    line.subscription_discount_percent = 0.0
                continue
            plan, _subscription = partner._get_current_subscription_plan()
            discount = min(max(benefit.discount_percent, 0.0), 100.0)
            line.discount = discount
            line.subscription_benefit_id = benefit
            line.subscription_plan_id = plan
            line.subscription_discount_percent = discount

    def get_subscription_line_values(self):
        return {
            "product_id": self.product_id.id,
            "name": self.product_id.name,
            "product_uom_qty": self.product_uom_qty,
            "price_unit": self.price_unit,
            "discount": self.discount,
            "price_subtotal": self.price_subtotal,
            "analytic_distribution": self.analytic_distribution,
        }
