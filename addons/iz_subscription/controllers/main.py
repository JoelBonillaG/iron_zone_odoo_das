from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class IzWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        user = request.env.user
        if user and not user._is_public():
            product = request.env['product.product'].sudo().browse(int(product_id))
            # We assume event tickets might have detailed_type == 'event' or we can just check benefits
            if getattr(product, 'detailed_type', '') == 'event' or getattr(product, 'event_ticket_ids', False):
                partner = user.partner_id
                benefits = partner._get_current_subscription_benefits("events")
                
                ticket = request.env['event.event.ticket'].sudo().search([('product_id', '=', int(product_id))], limit=1)
                if ticket and ticket.event_id and ticket.event_id.subscription_plan_ids:
                    benefits = benefits.filtered(lambda b: b.plan_id in ticket.event_id.subscription_plan_ids)
                else:
                    benefits = request.env['iz.subscription.benefit']
                
                if benefits and any(b.benefit_type == 'free' or b.discount_percent == 100 for b in benefits):
                    _add_qty = float(add_qty or 0)
                    _set_qty = float(set_qty or 0)
                    
                    order = request.website.sale_get_order()
                    current_qty = 0
                    if order:
                        line = order.order_line.filtered(lambda l: l.product_id.id == int(product_id))
                        if line:
                            current_qty = sum(line.mapped('product_uom_qty'))
                            
                    if _set_qty > 1:
                        set_qty = 1
                    elif _add_qty > 0 and current_qty + _add_qty > 1:
                        add_qty = 1 - current_qty
                        if add_qty < 0: add_qty = 0
                        
        return super().cart_update(product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        if order and order.amount_total == 0.0:
            has_sub_event = False
            for line in order.order_line:
                if getattr(line, 'event_id', False) and getattr(line, 'subscription_benefit_id', False):
                    if line.subscription_discount_percent == 100:
                        has_sub_event = True
                        break
            
            if has_sub_event:
                # It's a free event due to subscription benefit. Auto-confirm.
                order.action_confirm()
                
                # We need to make sure the event registration is processed.
                # action_confirm triggers the creation of event.registration.
                
                # Redirect directly to confirmation or success
                # But wait, Odoo's standard payment validation goes to /shop/payment/validate
                # Let's redirect to /shop/confirmation which is the standard order confirmation page
                return request.redirect('/shop/confirmation')
                
        return super().checkout(**post)
