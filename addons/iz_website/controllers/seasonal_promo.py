from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class IzSeasonalPromoController(Website):
    """Handle seasonal campaign promo links."""

    def _get_annual_product(self):
        ProductTemplate = request.env["product.template"].sudo()
        IrConfig = request.env["ir.config_parameter"].sudo()

        product_id = IrConfig.get_param("iz_website.seasonal_promo_product_id")
        if product_id:
            try:
                product = ProductTemplate.browse(int(product_id)).exists()
            except (TypeError, ValueError):
                product = ProductTemplate
            if product and product.sale_ok:
                return product

        if "subscription_plan_id" in ProductTemplate._fields:
            product = ProductTemplate.search(
                [
                    ("sale_ok", "=", True),
                    ("subscription_plan_id.code", "=", "IZ_PR01"),
                ],
                limit=1,
            )
            if product:
                return product

        product = ProductTemplate.search(
            [("sale_ok", "=", True), ("name", "ilike", "anual")],
            limit=1,
        )
        if product:
            return product

        if "subscription_plan_id" in ProductTemplate._fields:
            return ProductTemplate.search(
                [("sale_ok", "=", True), ("subscription_plan_id", "!=", False)],
                limit=1,
            )
        return ProductTemplate

    def _add_annual_product(self, sale_order):
        product_tmpl = self._get_annual_product()
        if not product_tmpl or not product_tmpl.sale_ok:
            return False

        product = product_tmpl.product_variant_id
        if not product:
            return False

        existing = sale_order.order_line.filtered(lambda line: line.product_id == product)
        if not existing:
            sale_order._cart_update(product_id=product.id, add_qty=1)
        return True

    @http.route("/promo/seasonal", type="http", auth="public", website=True, sitemap=False)
    def seasonal_promo(self, promo_code=None, **kwargs):
        expected_code = request.env["ir.config_parameter"].sudo().get_param(
            "iz_website.seasonal_promo_code", "IRONZONE25"
        )
        if promo_code != expected_code:
            return request.redirect("/shop")

        sale_order = request.website.sale_get_order(force_create=True)
        if not sale_order:
            return request.redirect("/shop")

        partner = request.env.user.partner_id
        user_email = (
            request.params.get("email")
            or kwargs.get("email")
            or (partner.email if partner else "")
            or ""
        ).strip().lower()

        if user_email and sale_order._iz_seasonal_email_already_used(user_email):
            sale_order._iz_remove_seasonal_discount()
            return request.redirect("/shop/cart?promo_already_used=1")

        if not self._add_annual_product(sale_order):
            return request.redirect("/shop")

        if user_email:
            sale_order.sudo().write({"iz_seasonal_promo_email": user_email})
        sale_order._iz_apply_seasonal_discount(email=user_email)
        return request.redirect("/shop/cart")


class IzSeasonalPromoWebsiteSale(WebsiteSale):
    """Keep the seasonal discount alive through checkout/payment recalculations."""

    def _reapply_seasonal_promo(self, order):
        if order and order.iz_seasonal_promo_email:
            order.sudo()._iz_apply_seasonal_discount(
                email=order.iz_seasonal_promo_email
            )

    def _get_shop_payment_values(self, order, **kwargs):
        self._reapply_seasonal_promo(order)
        return super()._get_shop_payment_values(order, **kwargs)

    @http.route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        order = request.website.sale_get_order()
        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(int(sale_order_id)).exists()
        self._reapply_seasonal_promo(order)
        return super().shop_payment_validate(sale_order_id=sale_order_id, **post)
