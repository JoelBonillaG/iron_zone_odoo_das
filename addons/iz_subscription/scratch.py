import sys
import inspect
try:
    from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
    print(inspect.getsource(WebsiteEventSaleController.registration_confirm))
except Exception as e:
    print(e)
