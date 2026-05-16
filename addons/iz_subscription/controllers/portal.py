from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class SubscriptionPortalController(CustomerPortal):
    """Portal controller to display subscriptions and benefits to the portal user."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "subscription_count" in counters:
            partner = request.env.user.partner_id
            values["subscription_count"] = request.env["sale.subscription"].sudo().search_count(
                [("partner_id", "=", partner.id), ("active", "=", True)]
            )
        return values

    def _subscription_status(self, subscription):
        status_map = {
            "draft": ("Borrador", "secondary", "Pendiente de completar"),
            "pre": ("Lista para iniciar", "warning", "Lista para activarse"),
            "in_progress": ("Activa", "success", "Vigente"),
            "post": ("Cerrada", "dark", "Finalizada"),
        }
        return status_map.get(
            subscription.stage_type,
            (subscription.stage_id.name or "Sin etapa", "secondary", "Sin estado definido"),
        )

    def _subscription_period_label(self, subscription):
        template = subscription.template_id
        if not template:
            return "Sin recurrencia"
        interval = int(template.recurring_interval or 1)
        unit_map = {
            "days": "dia" if interval == 1 else "dias",
            "weeks": "semana" if interval == 1 else "semanas",
            "months": "mes" if interval == 1 else "meses",
            "years": "ano" if interval == 1 else "anos",
        }
        return f"cada {interval} {unit_map.get(template.recurring_rule_type, template.recurring_rule_type)}"

    def _prepare_subscription_cards(self, subscriptions):
        cards = []
        for subscription in subscriptions:
            invoice_ids = subscription.invoice_ids | subscription.sale_order_ids.invoice_ids
            paid_invoice_count = len(invoice_ids.filtered(lambda invoice: invoice.payment_state == "paid"))
            status_label, status_color, status_hint = self._subscription_status(subscription)
            cards.append(
                {
                    "record": subscription,
                    "status_label": status_label,
                    "status_color": status_color,
                    "status_hint": status_hint,
                    "period_label": self._subscription_period_label(subscription),
                    "line_names": subscription.sale_subscription_line_ids.mapped("product_id.name"),
                    "invoice_count": len(invoice_ids),
                    "paid_invoice_count": paid_invoice_count,
                    "has_paid_invoice": bool(paid_invoice_count),
                    "benefits_ready": bool(subscription.subscription_benefits_active),
                }
            )
        return cards

    @http.route("/my/subscriptions", type="http", auth="user", website=True)
    def portal_my_subscriptions(self, **kwargs):
        partner = request.env.user.partner_id

        # Fetch all active subscriptions for this partner
        subscriptions = request.env["sale.subscription"].sudo().search(
            [
                ("partner_id", "=", partner.id),
                ("active", "=", True),
            ],
            order="id desc",
        )

        best_plan = None
        best_plan_priority = -1
        active_benefits = request.env["iz.subscription.benefit"]
        active_subscription = request.env["sale.subscription"]

        for sub in subscriptions:
            if sub.subscription_benefits_active and sub.subscription_plan_id:
                plan = sub.subscription_plan_id
                if plan.priority > best_plan_priority:
                    best_plan_priority = plan.priority
                    best_plan = plan
                    active_subscription = sub

        if best_plan:
            active_benefits = best_plan.benefit_ids.filtered(lambda b: b.active)

        # Map scope values to human-readable labels and icons
        scope_labels = {
            "events": "Clases y Eventos",
            "products": "Productos de la tienda",
            "general": "General",
        }
        scope_icons = {
            "events": "fa-calendar",
            "products": "fa-shopping-bag",
            "general": "fa-star",
        }
        benefit_type_labels = {
            "discount": "Descuento",
            "free": "Acceso gratis",
            "access": "Acceso incluido",
        }

        values = {
            "subscriptions": subscriptions,
            "subscription_cards": self._prepare_subscription_cards(subscriptions),
            "best_plan": best_plan,
            "active_subscription": active_subscription,
            "active_benefits": active_benefits,
            "scope_labels": scope_labels,
            "scope_icons": scope_icons,
            "benefit_type_labels": benefit_type_labels,
            "page_name": "subscriptions",
        }
        return request.render("iz_subscription.portal_my_subscriptions", values)
