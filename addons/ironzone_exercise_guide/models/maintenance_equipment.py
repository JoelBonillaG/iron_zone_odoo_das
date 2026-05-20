from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    is_gym_machine = fields.Boolean(
        string="Maquina de gimnasio",
        help="Marca este equipo como una maquina disponible para guias de ejercicios.",
    )
    gym_zone = fields.Selection(
        [
            ("strength", "Zona de fuerza"),
            ("cardio", "Zona cardio"),
            ("functional", "Zona funcional"),
            ("studio", "Sala grupal"),
            ("pool", "Piscina"),
            ("other", "Otra"),
        ],
        string="Zona del gimnasio",
    )
    muscle_group_ids = fields.Many2many(
        "ironzone.exercise.category",
        "ironzone_machine_muscle_group_rel",
        "equipment_id",
        "category_id",
        string="Grupos musculares",
        domain=[("category_type", "=", "muscle")],
    )
    guide_ids = fields.One2many(
        "ironzone.exercise.guide",
        "equipment_id",
        string="Guias relacionadas",
    )
    guide_count = fields.Integer(
        string="Guias",
        compute="_compute_guide_count",
    )

    def _compute_guide_count(self):
        for equipment in self:
            equipment.guide_count = len(equipment.guide_ids)

    def action_view_exercise_guides(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Guias de ejercicios",
            "res_model": "ironzone.exercise.guide",
            "view_mode": "list,form",
            "domain": [("equipment_id", "=", self.id)],
            "context": {"default_equipment_id": self.id, "default_exercise_type": "machine"},
        }
