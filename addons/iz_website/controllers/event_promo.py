from odoo import http
from odoo.http import request


class IzEventPromoController(http.Controller):
    """Handle special event promos (Women's Day, Men's Day)."""

    def _add_event_ticket_to_cart(self, event_slug):
        Event = request.env['event.event'].sudo()
        if not event_slug:
            return request.redirect('/shop')
            
        try:
            event_id = int(event_slug.split('-')[-1])
            event = Event.browse(event_id).exists()
        except (ValueError, AttributeError):
            event = Event.search([('name', '=ilike', event_slug)], limit=1)

        if not event:
            return request.redirect('/shop')

        ticket = request.env['event.event.ticket'].sudo().search([('event_id', '=', event.id)], limit=1)
        if not ticket or not ticket.product_id:
            return request.redirect('/shop')

        sale_order = request.website.sale_get_order(force_create=True)
        sale_order._cart_update(
            product_id=ticket.product_id.id,
            add_qty=1,
            ticket_id=ticket.id,
            event_id=event.id
        )
        return request.redirect('/shop/cart')

    @http.route("/promo/womens-day", type="http", auth="public", website=True, sitemap=False)
    def womens_day_promo(self, event_slug=None, **kwargs):
        user = request.env.user
        partner = user.partner_id

        # Verificar si es mujer
        if user._is_public() or partner.iz_gender != 'female':
            return request.redirect('/shop')

        return self._add_event_ticket_to_cart(event_slug)

    @http.route("/promo/mens-day", type="http", auth="public", website=True, sitemap=False)
    def mens_day_promo(self, event_slug=None, **kwargs):
        user = request.env.user
        partner = user.partner_id

        # Verificar si es hombre
        if user._is_public() or partner.iz_gender != 'male':
            return request.redirect('/shop')

        return self._add_event_ticket_to_cart(event_slug)
