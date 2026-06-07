from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    iz_seasonal_promo_email = fields.Char(
        string="Email de promo estacional",
        copy=False,
        readonly=True,
    )

    def _iz_seasonal_discount_percent(self):
        value = self.env["ir.config_parameter"].sudo().get_param(
            "iz_website.seasonal_promo_discount", "25"
        )
        try:
            return min(max(float(value or 0.0), 0.0), 100.0)
        except (TypeError, ValueError):
            return 25.0

    def _iz_get_seasonal_product_template(self):
        IrConfig = self.env["ir.config_parameter"].sudo()
        ProductTemplate = self.env["product.template"].sudo()

        product_id = IrConfig.get_param("iz_website.seasonal_promo_product_id")
        if product_id:
            try:
                product = ProductTemplate.browse(int(product_id)).exists()
            except (TypeError, ValueError):
                product = ProductTemplate
            if product and product.sale_ok:
                return product

        domain = [("sale_ok", "=", True)]
        if "subscription_plan_id" in ProductTemplate._fields:
            plan_domain = domain + [("subscription_plan_id.code", "=", "IZ_PR01")]
            product = ProductTemplate.search(plan_domain, limit=1)
            if product:
                return product

        product = ProductTemplate.search(domain + [("name", "ilike", "anual")], limit=1)
        if product:
            return product

        if "subscription_plan_id" in ProductTemplate._fields:
            return ProductTemplate.search(
                domain + [("subscription_plan_id", "!=", False)], limit=1
            )
        return ProductTemplate

    def _iz_seasonal_identity_email(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id or self.partner_id
        if self._iz_is_seasonal_public_partner(partner):
            return ""
        return (partner.email or self.partner_id.email or "").strip().lower()

    def _iz_seasonal_claim_email(self):
        self.ensure_one()
        return (self.iz_seasonal_promo_email or self._iz_seasonal_identity_email()).strip().lower()

    def _iz_is_seasonal_public_partner(self, partner):
        self.ensure_one()
        return bool(
            partner
            and self.website_id
            and self.website_id.user_id
            and partner == self.website_id.user_id.partner_id
        )

    def _iz_seasonal_email_already_used(self, email):
        if not email:
            return False
        return bool(
            self.env["res.partner"].sudo().search_count(
                [
                    ("email", "=ilike", email),
                    ("iz_seasonal_promo_used", "=", True),
                ]
            )
        )

    def _iz_can_apply_seasonal_promo(self, email=None):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id or self.partner_id
        if partner and not self._iz_is_seasonal_public_partner(partner) and partner.iz_seasonal_promo_used:
            return False
        return not self._iz_seasonal_email_already_used(
            email or self._iz_seasonal_claim_email()
        )

    def _iz_seasonal_order_lines(self):
        self.ensure_one()
        product_tmpl = self._iz_get_seasonal_product_template()
        if not product_tmpl:
            return self.env["sale.order.line"]
        return self.order_line.filtered(
            lambda line: line.product_id.product_tmpl_id == product_tmpl
        )

    def _iz_remove_seasonal_discount(self):
        discount = self._iz_seasonal_discount_percent()
        for order in self:
            for line in order._iz_seasonal_order_lines():
                if abs((line.discount or 0.0) - discount) < 0.0001:
                    line.sudo().write({"discount": 0.0})

    def _iz_apply_seasonal_discount(self, email=None):
        self.ensure_one()
        if not self._iz_can_apply_seasonal_promo(email=email):
            self._iz_remove_seasonal_discount()
            return False
        discount = self._iz_seasonal_discount_percent()
        lines = self._iz_seasonal_order_lines()
        if not lines:
            return False
        lines.sudo().write({"discount": discount})
        return True

    def _iz_mark_seasonal_promo_used(self):
        for order in self:
            if not order._iz_seasonal_order_lines().filtered(lambda line: line.discount):
                continue
            claim_email = order._iz_seasonal_claim_email()
            if claim_email:
                partners = self.env["res.partner"].sudo().search(
                    [("email", "=ilike", claim_email)]
                )
                if partners:
                    partners.write({"iz_seasonal_promo_used": True})
                    continue
            partner = order.partner_id.commercial_partner_id or order.partner_id
            if partner and not order._iz_is_seasonal_public_partner(partner):
                partner.sudo().write({"iz_seasonal_promo_used": True})

    def action_confirm(self):
        for order in self:
            seasonal_lines = order._iz_seasonal_order_lines().filtered(
                lambda line: line.discount
            )
            if seasonal_lines:
                claim_email = order._iz_seasonal_claim_email()
                customer_email = order._iz_seasonal_identity_email()
                if claim_email and customer_email and claim_email != customer_email:
                    raise UserError(
                        _(
                            "Este descuento estacional pertenece a otro cliente."
                        )
                    )
                if not order._iz_can_apply_seasonal_promo(email=claim_email):
                    raise UserError(
                        _(
                            "El descuento estacional del 25% ya fue reclamado para este cliente."
                        )
                    )
        result = super().action_confirm()
        self._iz_mark_seasonal_promo_used()
        return result
