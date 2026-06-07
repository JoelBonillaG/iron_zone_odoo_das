# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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

    @api.depends("product_id", "product_uom_qty", "order_id.partner_id", "order_id.partner_id.iz_gender", "event_ticket_id")
    def _compute_discount(self):
        super()._compute_discount()
        # Garantiza que el beneficio se aplique cada vez que Odoo recalcula el descuento
        self._apply_subscription_event_benefit()

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
            partner = line.order_id.partner_id
            if not ticket or not partner:
                continue

            # --- Priority 1: Women's Day Promo (Yoga Avanzado / Pilates Avanzado) ---
            # Solo aplica para mujeres y solo puede elegir una de las dos clases.
            promo_keywords_f = ["yoga avanzado", "pilates avanzado"]
            promo_keywords_m = ["crossfit am", "boxeo técnica"]
            
            event_name = (ticket.event_id.name or "").lower()
            
            is_promo_event_f = any(kw in event_name for kw in promo_keywords_f)
            if is_promo_event_f and partner.iz_gender == 'female':
                # Verificar si ya usó el beneficio (registros pasados en cualquiera de las dos)
                # Excluimos la orden actual para que el sistema no se bloquee al añadir el item
                already_used = self.env['event.registration'].sudo().search_count([
                    ('partner_id', '=', partner.id),
                    ('state', '!=', 'cancel'),
                    ('sale_order_id', '!=', line.order_id.id),
                    ('event_id.name', 'in', ['Yoga Avanzado', 'Pilates Avanzado'])
                ])
                # Verificar si ya tiene otra línea de la promo con 100% en este mismo carrito
                other_promo_lines = line.order_id.order_line.filtered(
                    lambda l: l != line and l.event_ticket_id and \
                              any(kw in (l.event_ticket_id.event_id.name or "").lower() for kw in promo_keywords_f) and \
                              l.discount == 100.0
                )
                if already_used == 0 and not other_promo_lines:
                    line.discount = 100.0
                    line.subscription_benefit_id = False
                    line.subscription_plan_id = False
                    line.subscription_discount_percent = 100.0
                    continue

            promo_keywords_m = ["crossfit am", "entrenamiento en grupo", "boxeo tecnica", "boxeo técnica"]
            is_promo_event_m = any(kw in event_name for kw in promo_keywords_m)
            if is_promo_event_m and partner.iz_gender == 'male':
                already_used = self.env['event.registration'].sudo().search_count([
                    ('partner_id', '=', partner.id),
                    ('state', '!=', 'cancel'),
                    ('sale_order_id', '!=', line.order_id.id),
                    ('event_id.name', 'in', ['CrossFit AM', 'Entrenamiento en Grupo', 'Boxeo Tecnica', 'Boxeo Técnica'])
                ])
                other_promo_lines = line.order_id.order_line.filtered(
                    lambda l: l != line and l.event_ticket_id and \
                              any(kw in (l.event_ticket_id.event_id.name or "").lower() for kw in promo_keywords_m) and \
                              l.discount == 100.0
                )
                if already_used == 0 and not other_promo_lines:
                    line.discount = 100.0
                    line.subscription_benefit_id = False
                    line.subscription_plan_id = False
                    line.subscription_discount_percent = 100.0
                    continue

            # --- Priority 2: First event free (General) ---
            # Evitar aplicar si ya tiene registros O si ya hay otra línea gratis en el carrito
            other_free_lines = line.order_id.order_line.filtered(
                lambda l: l != line and l.event_ticket_id and l.discount == 100.0
            )
            if not partner._has_previous_event_registration(exclude_order_id=line.order_id.id) and not other_free_lines:
                line.discount = 100.0
                line.subscription_benefit_id = False
                line.subscription_plan_id = False
                line.subscription_discount_percent = 100.0
                continue
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
