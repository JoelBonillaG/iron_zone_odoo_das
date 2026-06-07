from datetime import date

from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class IzSeasonalPromoController(Website):
    """Handle seasonal campaign promo links."""

    def _get_annual_product(self):
        """Find the annual subscription product by slug, name, or configurable ID."""
        annual_slug = request.env['ir.config_parameter'].sudo().get_param(
            'iz_website.seasonal_promo_product_slug', 'suscripcion-anual-4'
        )
        product_id = request.env['ir.config_parameter'].sudo().get_param(
            'iz_website.seasonal_promo_product_id', '4'
        )
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            product_id = 4

        ProductTemplate = request.env['product.template'].sudo()

        # Try by configured ID first
        product = ProductTemplate.browse(product_id)
        if product.exists() and product.sale_ok:
            return product

        # Fallback: match by name containing 'anual' or 'annual'
        product = ProductTemplate.search([
            ('sale_ok', '=', True),
            ('name', 'ilike', 'anual'),
        ], limit=1)
        if product:
            return product

        # Last fallback: first sale_ok product with a subscription plan
        product = ProductTemplate.search([
            ('sale_ok', '=', True),
            ('subscription_plan_id', '!=', False),
        ], limit=1)
        return product

    def _apply_annual_discount(self, sale_order):
        """Ensure annual subscription is in cart and apply seasonal discount."""
        discount_percent = float(
            request.env['ir.config_parameter'].sudo().get_param(
                'iz_website.seasonal_promo_discount', '25'
            )
        )
        product_tmpl = self._get_annual_product()
        if not product_tmpl or not product_tmpl.sale_ok:
            return False

        variant = product_tmpl.product_variant_id
        if not variant:
            return False

        # Check if already in cart
        existing = sale_order.order_line.filtered(
            lambda l: l.product_id.id == variant.id
        )
        if existing:
            existing.write({'price_unit': round(existing.price_unit * (1 - discount_percent / 100), 2)})
        else:
            # Add to cart with discounted price
            sale_order.write({
                'order_line': [
                    (0, 0, {
                        'product_id': variant.id,
                        'product_uom_qty': 1,
                        'price_unit': round(product_tmpl.list_price * (1 - discount_percent / 100), 2),
                    })
                ]
            })

        sale_order.message_post(
            body=(f"Descuento campaña estacional aplicado: {discount_percent}% "
                  f"sobre '{product_tmpl.name}'. Precio final: "
                  f"{round(product_tmpl.list_price * (1 - discount_percent / 100), 2)}")
        )
        return True

    @http.route('/promo/seasonal', type='http', auth='public', website=True, sitemap=False)
    def seasonal_promo(self, promo_code=None, **kwargs):
        expected_code = request.env['ir.config_parameter'].sudo().get_param(
            'iz_website.seasonal_promo_code', 'IRONZONE25'
        )
        if promo_code != expected_code:
            return request.redirect('/shop')

        sale_order = request.website.sale_get_order(force_create=True)
        if not sale_order:
            return request.redirect('/shop')

        partner = request.env.user.partner_id
        if partner and partner.iz_seasonal_promo_used:
            return request.redirect('/shop/cart?promo_already_used=1')

        self._apply_annual_discount(sale_order)

        if partner:
            partner.sudo().write({'iz_seasonal_promo_used': True})

        return request.redirect('/shop/cart')
