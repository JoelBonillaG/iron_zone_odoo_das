from odoo import fields, http
from odoo.http import request


class SubscriptionPortalController(http.Controller):
    """Portal controller to display subscriptions and benefits to the portal user."""

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

        # Determine the best active plan (highest priority among subscriptions
        # that are in_progress, within date, and have a paid invoice).
        # This is the plan whose benefits the partner currently receives.
        best_plan = None
        best_plan_priority = -1
        active_benefits = request.env["iz.subscription.benefit"]

        for sub in subscriptions:
            if sub.subscription_benefits_active and sub.subscription_plan_id:
                plan = sub.subscription_plan_id
                if plan.priority > best_plan_priority:
                    best_plan_priority = plan.priority
                    best_plan = plan

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
            "best_plan": best_plan,
            "active_benefits": active_benefits,
            "scope_labels": scope_labels,
            "scope_icons": scope_icons,
            "benefit_type_labels": benefit_type_labels,
            "page_name": "subscriptions",
        }
        return request.render("iz_subscription.portal_my_subscriptions", values)
