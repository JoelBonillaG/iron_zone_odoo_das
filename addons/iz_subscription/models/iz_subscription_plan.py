from odoo import fields, models


class IzSubscriptionPlan(models.Model):
    _name = "iz.subscription.plan"
    _description = "Plan de suscripcion"
    _order = "priority desc, sequence, name"

    name = fields.Char(string="Nombre", required=True, translate=True)
    code = fields.Char(string="Codigo", required=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    priority = fields.Integer(
        string="Prioridad",
        default=10,
        help="Cuando un cliente tiene varias suscripciones activas, se usa el plan con mayor prioridad.",
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string="Descripcion", translate=True)
    product_template_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="subscription_plan_id",
        string="Productos que otorgan este plan",
    )
    benefit_ids = fields.One2many(
        comodel_name="iz.subscription.benefit",
        inverse_name="plan_id",
        string="Beneficios",
    )
