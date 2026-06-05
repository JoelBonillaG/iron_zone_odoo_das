from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    trainer_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Entrenador",
        tracking=True,
    )
    horario = fields.Datetime(
        string="Horario",
        compute="_compute_horario",
        inverse="_inverse_horario",
        store=True,
        tracking=True,
    )
    cupo_maximo = fields.Integer(
        string="Cupo Máximo",
        compute="_compute_cupo_maximo",
        inverse="_inverse_cupo_maximo",
        store=True,
        tracking=True,
    )
    cupo_disponible = fields.Integer(
        string="Cupo Disponible",
        compute="_compute_cupo_disponible",
        store=True,
    )
    sala_espacio = fields.Char(
        string="Sala/Espacio",
        tracking=True,
    )
    dificultad = fields.Selection(
        selection=[
            ("beginner", "Principiante"),
            ("intermediate", "Intermedio"),
            ("advanced", "Avanzado"),
        ],
        string="Nivel de Dificultad",
        default="beginner",
        tracking=True,
    )
    inscritos_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Inscritos",
        compute="_compute_inscritos",
        store=True,
    )
    subscription_plan_ids = fields.Many2many(
        comodel_name="iz.subscription.plan",
        string="Planes Permitidos",
        help="Planes de suscripción que otorgan beneficios o descuentos para este evento. Si está vacío, ningún plan otorga beneficios.",
    )

    @api.depends("date_begin")
    def _compute_horario(self):
        for event in self:
            event.horario = event.date_begin

    def _inverse_horario(self):
        for event in self:
            event.date_begin = event.horario

    @api.depends("seats_max")
    def _compute_cupo_maximo(self):
        for event in self:
            event.cupo_maximo = event.seats_max

    def _inverse_cupo_maximo(self):
        for event in self:
            event.seats_max = event.cupo_maximo
            if event.cupo_maximo > 0:
                event.seats_limited = True

    @api.depends("seats_available")
    def _compute_cupo_disponible(self):
        for event in self:
            event.cupo_disponible = event.seats_available

    @api.depends("registration_ids.partner_id", "registration_ids.state")
    def _compute_inscritos(self):
        for event in self:
            active_registrations = event.registration_ids.filtered(lambda r: r.state != "cancel")
            event.inscritos_ids = active_registrations.mapped("partner_id")
