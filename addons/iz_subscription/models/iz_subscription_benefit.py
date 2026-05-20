from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IzSubscriptionBenefit(models.Model):
    _name = "iz.subscription.benefit"
    _description = "Beneficio de suscripcion"
    _order = "plan_id, sequence, name"

    name = fields.Char(string="Nombre", required=True, translate=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    active = fields.Boolean(default=True)
    plan_id = fields.Many2one(
        comodel_name="iz.subscription.plan",
        string="Plan",
        required=True,
        ondelete="cascade",
    )
    benefit_scope = fields.Selection(
        selection=[
            ("events", "Eventos y clases"),
            ("products", "Productos"),
            ("general", "General"),
        ],
        string="Aplica a",
        required=True,
        default="events",
    )
    benefit_type = fields.Selection(
        selection=[
            ("discount", "Descuento"),
            ("free", "Acceso gratis"),
            ("access", "Acceso incluido"),
        ],
        string="Tipo de beneficio",
        required=True,
        default="discount",
    )
    discount_percent = fields.Float(string="Descuento (%)", default=0.0)
    description = fields.Text(string="Descripcion", translate=True)

    @api.constrains("benefit_type", "discount_percent")
    def _check_discount_percent(self):
        for record in self:
            if record.discount_percent < 0 or record.discount_percent > 100:
                raise ValidationError("El descuento debe estar entre 0 y 100.")
            if record.benefit_type == "free" and record.discount_percent not in (0, 100):
                raise ValidationError("Un beneficio gratis debe tener 0% o 100% de descuento.")

    @api.constrains("active", "plan_id", "benefit_scope")
    def _check_single_active_benefit_per_scope(self):
        for record in self:
            if not record.active or not record.plan_id or not record.benefit_scope:
                continue
            duplicate = self.search(
                [
                    ("id", "!=", record.id),
                    ("active", "=", True),
                    ("plan_id", "=", record.plan_id.id),
                    ("benefit_scope", "=", record.benefit_scope),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    "Cada plan solo puede tener un beneficio activo por modulo."
                )

    def apply_to_amount(self, amount):
        self.ensure_one()
        if self.benefit_type in ("free", "access"):
            return 0.0
        discount = min(max(self.discount_percent, 0.0), 100.0)
        return amount * (1 - discount / 100.0)
