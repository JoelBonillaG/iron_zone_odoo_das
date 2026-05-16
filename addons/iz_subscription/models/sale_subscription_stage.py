# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleSubscriptionStage(models.Model):
    _name = "sale.subscription.stage"
    _description = "Etapa de suscripcion"
    _order = "sequence, name, id"

    name = fields.Char(string="Nombre", required=True, translate=True)
    sequence = fields.Integer(string="Secuencia")
    in_progress = fields.Boolean(string="En progreso", default=False)
    fold = fields.Boolean(string="Plegada en kanban")
    description = fields.Text(string="Descripcion", translate=True)
    type = fields.Selection(
        [
            ("draft", "Borrador"),
            ("pre", "Lista para iniciar"),
            ("in_progress", "Activa"),
            ("post", "Cerrada"),
        ],
        string="Tipo",
        default="pre",
    )

    @api.constrains("type")
    def _check_lot_product(self):
        post_stages = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")]
        )
        if len(post_stages) > 1:
            raise ValidationError(
                self.env._("Ya existe una etapa de tipo Cerrada.")
            )
