from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class IzWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        user = request.env.user
        if user and not user._is_public():
            # Detect if the product is tied to an event ticket
            ticket = request.env['event.event.ticket'].sudo().search(
                [('product_id', '=', int(product_id))], limit=1
            )
            if ticket:
                partner = user.partner_id
                benefits = partner._get_current_subscription_benefits("events")
                # Filter benefits by what this specific event allows
                if ticket.event_id and ticket.event_id.subscription_plan_ids:
                    benefits = benefits.filtered(
                        lambda b: b.plan_id in ticket.event_id.subscription_plan_ids
                    )
                else:
                    benefits = request.env['iz.subscription.benefit']

                # Restrict qty to 1 if user has any active benefit for this event
                if benefits:
                    _add_qty = float(add_qty or 0)
                    _set_qty = float(set_qty or 0)

                    order = request.website.sale_get_order()
                    current_qty = 0
                    if order:
                        existing = order.order_line.filtered(
                            lambda l: l.product_id.id == int(product_id)
                        )
                        if existing:
                            current_qty = sum(existing.mapped('product_uom_qty'))

                    if _set_qty > 1:
                        set_qty = 1
                    elif _add_qty > 0 and current_qty + _add_qty > 1:
                        add_qty = max(1 - current_qty, 0)

        return super().cart_update(product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        if order and order.amount_total == 0.0:
            # Detect free event lines backed by a 100% subscription benefit
            has_free_sub_event = any(
                "event_ticket_id" in line._fields
                and line.event_ticket_id
                and line.subscription_discount_percent == 100
                for line in order.order_line
            )

            if has_free_sub_event:
                # Auto-confirm the order; Odoo creates event.registration on confirm
                order.sudo().action_confirm()
                return request.redirect('/shop/confirmation')

        return super().checkout(**post)
