from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IronZoneExerciseGuide(models.Model):
    _name = "ironzone.exercise.guide"
    _description = "Guia de Ejercicio Iron Zone"
    _inherit = ["mail.thread", "mail.activity.mixin", "website.published.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True, tracking=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("published", "Publicada"),
            ("archived", "Archivada"),
        ],
        string="Estado",
        default="draft",
        required=True,
        tracking=True,
    )
    exercise_type = fields.Selection(
        [
            ("individual", "Individual sin maquina"),
            ("machine", "Con maquina"),
            ("group", "Grupal"),
        ],
        string="Tipo de ejercicio",
        default="individual",
        required=True,
        tracking=True,
    )
    difficulty = fields.Selection(
        [
            ("beginner", "Principiante"),
            ("intermediate", "Intermedio"),
            ("advanced", "Avanzado"),
        ],
        string="Nivel de dificultad",
        default="beginner",
        required=True,
    )
    author_id = fields.Many2one(
        "hr.employee",
        string="Entrenador autor",
        required=True,
        default=lambda self: self._default_author_id(),
        tracking=True,
    )
    author_user_id = fields.Many2one(
        "res.users",
        string="Usuario autor",
        related="author_id.user_id",
        store=True,
        readonly=True,
    )
    equipment_id = fields.Many2one(
        "maintenance.equipment",
        string="Maquina relacionada",
        domain=[("is_gym_machine", "=", True)],
        tracking=True,
    )
    event_ids = fields.Many2many(
        "event.event",
        "ironzone_guide_event_rel",
        "guide_id",
        "event_id",
        string="Clases relacionadas",
    )
    category_ids = fields.Many2many(
        "ironzone.exercise.category",
        "ironzone_guide_category_rel",
        "guide_id",
        "category_id",
        string="Categorias y etiquetas",
    )
    primary_muscle_group_id = fields.Many2one(
        "ironzone.exercise.category",
        string="Grupo muscular principal",
        domain=[("category_type", "=", "muscle")],
    )
    instructions = fields.Html(string="Instrucciones de uso", sanitize=True)
    recommendations = fields.Text(string="Recomendaciones")
    common_mistakes = fields.Text(string="Errores comunes")
    safety_notes = fields.Text(string="Notas de seguridad")
    image_1920 = fields.Image(string="Imagen de referencia", max_width=1920, max_height=1920)
    video_url = fields.Char(string="URL de video")
    video_file = fields.Binary(string="Video MP4", attachment=True)
    video_filename = fields.Char(string="Nombre del video")
    company_id = fields.Many2one(
        "res.company",
        string="Compania",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model
    def _default_author_id(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)

    def _is_exercise_admin(self):
        return self.env.user.has_group("iz_backend_theme.group_ironzone_admin")

    def _is_exercise_trainer(self):
        return self.env.user.has_group("iz_backend_theme.group_ironzone_trainers")

    def _current_employee(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        if self._is_exercise_trainer() and not self._is_exercise_admin():
            employee = self._current_employee()
            if not employee:
                raise ValidationError(_("Tu usuario debe estar vinculado a un empleado entrenador."))
            for vals in vals_list:
                requested_author_id = vals.get("author_id") or employee.id
                if requested_author_id != employee.id:
                    raise ValidationError(_("Un entrenador solo puede crear guias a su propio nombre."))
                vals["author_id"] = employee.id
        return super().create(vals_list)

    def write(self, vals):
        if (
            self._is_exercise_trainer()
            and not self._is_exercise_admin()
            and "author_id" in vals
            and any(guide.author_id.id != vals["author_id"] for guide in self)
        ):
            raise ValidationError(_("Un entrenador no puede cambiar el autor de una guia."))
        return super().write(vals)

    @api.constrains("exercise_type", "equipment_id")
    def _check_machine_required_for_machine_type(self):
        for guide in self:
            if guide.exercise_type == "machine" and not guide.equipment_id:
                raise ValidationError(_("Selecciona una maquina para las guias de tipo 'Con maquina'."))

    @api.constrains("video_url", "video_file")
    def _check_video_source(self):
        for guide in self:
            if guide.video_url and guide.video_file:
                raise ValidationError(_("Usa solo una fuente de video: archivo MP4 o URL, no ambas."))

    def action_publish(self):
        self.write({"state": "published", "is_published": True})

    def action_unpublish(self):
        self.write({"state": "draft", "is_published": False})

    def action_archive_guide(self):
        self.write({"state": "archived", "is_published": False, "active": False})
