# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="sale_order_id",
        string="Suscripciones",
    )
    subscriptions_count = fields.Integer(compute="_compute_subscriptions_count")
    order_subscription_id = fields.Many2one(
        comodel_name="sale.subscription", string="Suscripcion"
    )

    @api.depends("subscription_ids")
    def _compute_subscriptions_count(self):
        data = self.env["sale.subscription"].read_group(
            domain=[("sale_order_id", "in", self.ids)],
            fields=["sale_order_id"],
            groupby=["sale_order_id"],
        )
        count_dict = {
            item["sale_order_id"][0]: item["sale_order_id_count"] for item in data
        }
        for record in self:
            record.subscriptions_count = count_dict.get(record.id, 0)

    def action_view_subscriptions(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "name": self.name,
            "view_mode": "list,form",
        }

    def get_next_interval(self, type_interval, interval):
        date_start = date.today()
        date_start += relativedelta(**{type_interval: interval})
        return date_start

    def create_subscription(self, lines, subscription_tmpl):
        self.ensure_one()
        if subscription_tmpl:
            subscription_lines = [
                Command.create(line.get_subscription_line_values()) for line in lines
            ]
            subscription_plan = self._get_subscription_plan_from_lines(lines)
            date_start = self._get_subscription_start_date(subscription_plan)
            pricelist_id = self.pricelist_id.id or self.partner_id.property_product_pricelist.id
            if not pricelist_id:
                company_id = self.company_id.id or self.env.company.id
                pricelist = self.env["product.pricelist"].search(
                    [("company_id", "in", [company_id, False])], limit=1
                )
                if not pricelist:
                    pricelist = self.env["product.pricelist"].search([], limit=1)
                pricelist_id = pricelist.id
            rec = self.env["sale.subscription"].create(
                {
                    "partner_id": self.partner_id.id,
                    "user_id": self.env.context.get("uid", self.env.uid),
                    "template_id": subscription_tmpl.id,
                    "subscription_plan_id": subscription_plan.id,
                    "pricelist_id": pricelist_id,
                    "date_start": date_start,
                    "sale_order_id": self.id,
                    "sale_subscription_line_ids": subscription_lines,
                }
            )
            # Assign draft stage so the subscription starts in "Borrador".
            # The admin activates it manually once payment is confirmed.
            # (Calling action_start_subscription() would skip straight to
            # in_progress and trigger billing immediately.)
            draft_stage = self.env["sale.subscription.stage"].search(
                [("type", "=", "draft")], limit=1
            )
            if draft_stage:
                rec.stage_id = draft_stage
            rec.recurring_next_date = self.get_next_interval(
                subscription_tmpl.recurring_rule_type,
                subscription_tmpl.recurring_interval,
            )

    def _get_subscription_start_date(self, target_plan):
        self.ensure_one()
        current_plan, current_subscription = self.partner_id._get_current_subscription_plan()
        if (
            current_plan
            and target_plan
            and target_plan.priority < current_plan.priority
            and current_subscription
        ):
            return (
                current_subscription.date
                or current_subscription.recurring_next_date
                or fields.Date.context_today(self)
            )
        return fields.Date.context_today(self)

    def _get_subscription_plan_from_lines(self, lines):
        subscription_plans = lines.mapped(
            "product_id.product_tmpl_id.subscription_plan_id"
        ).filtered(lambda plan: plan.active)
        return subscription_plans.sorted(
            key=lambda plan: (-plan.priority, plan.sequence, plan.id)
        )[:1]

    def _iz_to_int(self, value, default=0):
        try:
            return int(float(value or 0))
        except (TypeError, ValueError):
            return default

    def _iz_cart_warning_result(self, line=False, warning=""):
        option_ids = []
        if line:
            option_ids = list(
                set(
                    line.linked_line_ids.filtered(
                        lambda sol: sol.order_id == line.order_id
                    ).ids
                )
            )
        return {
            "line_id": line.id if line else 0,
            "quantity": line.product_uom_qty if line else 0,
            "option_ids": option_ids,
            "warning": warning,
        }

    def _iz_is_public_partner(self, partner):
        self.ensure_one()
        return bool(
            self.website_id
            and partner
            and partner == self.website_id.user_id.partner_id
        )

    def _iz_subscription_lines(self):
        return self.order_line.filtered(
            lambda line: line.product_id.product_tmpl_id.subscribable
        )

    def _iz_partner_has_existing_subscription(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner or self._iz_is_public_partner(partner):
            return False
        return bool(
            self.env["sale.subscription"].sudo().search_count(
                [
                    ("partner_id", "=", partner.id),
                    ("active", "=", True),
                    ("stage_type", "in", ["draft", "pre", "in_progress"]),
                ]
            )
        )

    def _iz_get_event_ticket(self, product, order_line=False, event_ticket_id=False):
        if event_ticket_id:
            ticket = self.env["event.event.ticket"].sudo().browse(
                self._iz_to_int(event_ticket_id)
            ).exists()
            if ticket:
                return ticket
        if order_line and "event_ticket_id" in order_line._fields and order_line.event_ticket_id:
            return order_line.event_ticket_id
        return self.env["event.event.ticket"].sudo().search(
            [("product_id", "=", product.id)], limit=1
        )

    def _iz_event_lines(self, event):
        return self.order_line.filtered(
            lambda line: "event_ticket_id" in line._fields
            and line.event_ticket_id
            and line.event_ticket_id.event_id == event
        )

    def _iz_partner_has_event_registration(self, event):
        self.ensure_one()
        partner = self.partner_id
        if not partner or self._iz_is_public_partner(partner):
            return False
        return bool(
            self.env["event.registration"].sudo().search_count(
                [
                    ("event_id", "=", event.id),
                    ("partner_id", "=", partner.id),
                    ("state", "!=", "cancel"),
                    # Exclude this order's own (draft) registrations, otherwise the
                    # post-payment confirmation would see the cart's own ticket and
                    # wrongly abort, leaving a paid-but-unconfirmed order.
                    ("sale_order_line_id.order_id", "!=", self.id),
                ]
            )
        )

    def _iz_current_cart_line(self, product_id, line_id, **kwargs):
        if line_id is not False:
            return self._cart_find_product_line(product_id, line_id, **kwargs)[:1]
        return self._cart_find_product_line(product_id, False, **kwargs)[:1]

    def _iz_adjust_subscription_cart_update(self, product, line_id, add_qty, set_qty, **kwargs):
        current_line = self._iz_current_cart_line(product.id, line_id, **kwargs)
        requested_qty = (
            self._iz_to_int(set_qty)
            if set_qty
            else (current_line.product_uom_qty if current_line else 0)
            + self._iz_to_int(add_qty)
        )
        if requested_qty <= 0:
            return add_qty, set_qty, ""

        warning = _(
            "Solo puedes comprar una suscripción a la vez. "
            "Finaliza o elimina la suscripción existente antes de elegir otra."
        )

        if self._iz_partner_has_existing_subscription():
            self._iz_subscription_lines().unlink()
            return None, None, self._iz_cart_warning_result(False, warning)

        subscription_lines = self._iz_subscription_lines()
        other_subscription_lines = subscription_lines - current_line
        if other_subscription_lines:
            return None, None, self._iz_cart_warning_result(
                other_subscription_lines[:1], warning
            )

        if set_qty and self._iz_to_int(set_qty) > 1:
            return add_qty, 1, warning
        if add_qty is not None:
            current_qty = current_line.product_uom_qty if current_line else 0
            allowed_add_qty = max(1 - current_qty, 0)
            if self._iz_to_int(add_qty) > allowed_add_qty:
                return allowed_add_qty, set_qty, warning
        return add_qty, set_qty, ""

    def _iz_adjust_event_cart_update(self, product, line_id, add_qty, set_qty, **kwargs):
        current_line = self._iz_current_cart_line(product.id, line_id, **kwargs)
        ticket = self._iz_get_event_ticket(
            product, current_line, kwargs.get("event_ticket_id")
        )
        if not ticket:
            return add_qty, set_qty, ""

        requested_qty = (
            self._iz_to_int(set_qty)
            if set_qty
            else (current_line.product_uom_qty if current_line else 0)
            + self._iz_to_int(add_qty)
        )
        if requested_qty <= 0:
            return add_qty, set_qty, ""

        warning = _(
            "Solo puedes comprar un boleto por evento. "
            "Ya tienes un boleto para este evento o está en tu carrito."
        )

        if self._iz_partner_has_event_registration(ticket.event_id):
            return None, None, self._iz_cart_warning_result(False, warning)

        same_event_lines = self._iz_event_lines(ticket.event_id)
        other_event_lines = same_event_lines - current_line
        if other_event_lines:
            return None, None, self._iz_cart_warning_result(other_event_lines[:1], warning)

        if set_qty and self._iz_to_int(set_qty) > 1:
            return add_qty, 1, warning
        if add_qty is not None:
            current_qty = current_line.product_uom_qty if current_line else 0
            allowed_add_qty = max(1 - current_qty, 0)
            if self._iz_to_int(add_qty) > allowed_add_qty:
                return allowed_add_qty, set_qty, warning
        return add_qty, set_qty, ""

    def group_subscription_lines(self):
        """
        Group sale order lines by their product's recurring template.
        Returns a dict {template_recordset: order_line_recordset}.
        """
        grouped = {}
        SaleOrderLine = self.env["sale.order.line"]
        for order_line in self.order_line.filtered(
            lambda line: line.product_id.subscribable
        ):
            tmpl = order_line.product_id.product_tmpl_id.subscription_template_id
            if tmpl not in grouped:
                grouped[tmpl] = SaleOrderLine
            grouped[tmpl] |= order_line
        return grouped

    def action_confirm(self):
        """
        Create a subscription per template from the Order's products
        """
        for record in self:
            if not record.website_id:
                continue
            subscription_lines = record._iz_subscription_lines()
            if subscription_lines:
                if len(subscription_lines) > 1 or sum(subscription_lines.mapped("product_uom_qty")) > 1:
                    raise UserError(_("Solo puedes comprar una suscripción por pedido."))
                if record._iz_partner_has_existing_subscription():
                    raise UserError(_("Ya tienes una suscripción activa o pendiente."))

            event_lines = record.order_line.filtered(
                lambda line: "event_ticket_id" in line._fields and line.event_ticket_id
            )
            for event in event_lines.mapped("event_ticket_id.event_id"):
                lines = record._iz_event_lines(event)
                if sum(lines.mapped("product_uom_qty")) > 1:
                    raise UserError(_("Solo puedes comprar un boleto por evento."))
                if record._iz_partner_has_event_registration(event):
                    raise UserError(_("Ya tienes un boleto para este evento."))

        res = super().action_confirm()
        for record in self:
            grouped = record.group_subscription_lines()
            for tmpl, lines in grouped.items():
                record.create_subscription(lines, tmpl)
        return res

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        self.ensure_one()
        product = self.env["product.product"].browse(self._iz_to_int(product_id)).exists()
        warning = ""
        if product and product.product_tmpl_id.subscribable:
            add_qty, set_qty, result_or_warning = self._iz_adjust_subscription_cart_update(
                product, line_id, add_qty, set_qty, **kwargs
            )
            if isinstance(result_or_warning, dict):
                return result_or_warning
            warning = result_or_warning or warning

        if product:
            add_qty, set_qty, result_or_warning = self._iz_adjust_event_cart_update(
                product, line_id, add_qty, set_qty, **kwargs
            )
            if isinstance(result_or_warning, dict):
                return result_or_warning
            warning = result_or_warning or warning

        result = super()._cart_update(
            product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs
        )
        if warning and not result.get("warning"):
            result["warning"] = warning
        return result

    def _cart_update_order_line(self, product_id, quantity, order_line, **kwargs):
        order_line = super()._cart_update_order_line(
            product_id, quantity, order_line, **kwargs
        )
        event_lines = self.order_line.filtered(
            lambda line: "event_ticket_id" in line._fields and line.event_ticket_id
        )
        if event_lines:
            event_lines._apply_subscription_event_benefit()
        product_lines = self.order_line.filtered(
            lambda line: line._is_subscription_product_line()
        )
        if product_lines:
            product_lines._apply_subscription_product_benefit()
        return order_line
