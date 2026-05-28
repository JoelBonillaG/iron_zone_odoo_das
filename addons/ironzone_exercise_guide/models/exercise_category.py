from odoo import fields, models


class IronZoneExerciseCategory(models.Model):
    _name = "ironzone.exercise.category"
    _description = "Categoria de Ejercicios Iron Zone"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True, translate=True)
    code = fields.Char(string="Codigo")
    category_type = fields.Selection(
        [
            ("muscle", "Grupo muscular"),
            ("exercise", "Tipo de ejercicio"),
            ("equipment", "Tipo de maquina"),
            ("other", "Otro"),
        ],
        string="Tipo",
        default="muscle",
        required=True,
    )
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color")
    active = fields.Boolean(default=True)
    description = fields.Text(string="Descripcion")
