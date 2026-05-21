from odoo import fields, models


class IzSubscriptionBenefit(models.Model):
    _inherit = "iz.subscription.benefit"

    benefit_scope = fields.Selection(
        selection_add=[("guides", "Guias de ejercicios")],
        ondelete={"guides": "set default"},
    )
