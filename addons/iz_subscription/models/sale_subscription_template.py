# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleSubscriptionTemplate(models.Model):
    _name = "sale.subscription.template"
    _description = "Plantillas de recurrencia"

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Terminos y condiciones")
    recurring_interval = fields.Integer(string="Repetir cada", default=1)
    recurring_rule_type = fields.Selection(
        [
            ("days", "Dia(s)"),
            ("weeks", "Semana(s)"),
            ("months", "Mes(es)"),
            ("years", "Ano(s)"),
        ],
        string="Recurrencia",
        default="months",
    )
    recurring_rule_boundary = fields.Selection(
        [("unlimited", "Indefinida"), ("limited", "Fija")],
        string="Duracion",
        default="unlimited",
    )
    invoicing_mode = fields.Selection(
        default="draft",
        string="Modo de facturacion",
        selection=[
            ("draft", "Factura en borrador"),
            ("invoice", "Validar factura"),
            ("invoice_send", "Validar y enviar factura"),
            ("sale_and_invoice", "Pedido de venta y factura"),
        ],
    )
    code = fields.Char(string="Codigo")
    recurring_rule_count = fields.Integer(default=1, string="Duracion")
    invoice_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Correo de factura",
        domain="[('model', '=', 'account.move')]",
    )
    product_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="subscription_template_id",
        string="Productos",
    )
    product_ids_count = fields.Integer(
        compute="_compute_product_ids_count", string="Productos"
    )
    subscription_ids = fields.One2many(
        comodel_name="sale.subscription",
        inverse_name="template_id",
        string="Suscripciones",
    )
    subscription_count = fields.Integer(
        compute="_compute_subscription_count", string="Suscripciones"
    )

    def _compute_subscription_count(self):
        data = self.env["sale.subscription"].read_group(
            domain=[("template_id", "in", self.ids)],
            fields=["template_id"],
            groupby=["template_id"],
        )
        count_dict = {
            item["template_id"][0]: item["template_id_count"] for item in data
        }
        for record in self:
            record.subscription_count = count_dict.get(record.id, 0)

    def action_view_subscription_ids(self):
        return {
            "name": self.name,
            "view_mode": "list,form",
            "res_model": "sale.subscription",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.subscription_ids.ids)],
        }

    def _get_date(self, date_start):
        self.ensure_one()
        return relativedelta(months=+self.recurring_rule_count) + date_start

    @api.depends("product_ids")
    def _compute_product_ids_count(self):
        for record in self:
            record.product_ids_count = len(record.product_ids)

    def action_view_product_ids(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "list,form",
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.product_ids.ids)],
        }
