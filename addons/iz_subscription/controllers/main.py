from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.http import request
from odoo import http

class IzWebsiteEventSaleController(WebsiteEventSaleController):

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        user = request.env.user
        if user and not user._is_public():
            partner = user.partner_id
            benefit = partner._get_current_subscription_benefits("events")[:1]
            if benefit and benefit.benefit_type == "free":
                # User has a free events benefit. Bypass the cart creation!
                return WebsiteEventController.registration_confirm(self, event, **post)
        
        return super().registration_confirm(event, **post)
