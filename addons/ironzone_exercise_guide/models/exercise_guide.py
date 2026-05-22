from urllib.parse import parse_qs, urlparse

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
    requires_subscription = fields.Boolean(
        string="Requiere suscripcion activa",
        help="Si se activa, solo socios con una suscripcion activa y pagada podran ver esta guia en el portal.",
        tracking=True,
    )
    allowed_plan_ids = fields.Many2many(
        "iz.subscription.plan",
        "ironzone_guide_subscription_plan_rel",
        "guide_id",
        "plan_id",
        string="Planes permitidos",
        help="Si se deja vacio, cualquier plan activo y pagado permite ver la guia.",
    )
    instructions = fields.Html(string="Instrucciones de uso", sanitize=True)
    recommendations = fields.Text(string="Recomendaciones")
    common_mistakes = fields.Text(string="Errores comunes")
    safety_notes = fields.Text(string="Notas de seguridad")
    image_1920 = fields.Image(string="Imagen de referencia", max_width=1920, max_height=1920)
    video_url = fields.Char(string="URL de video")
    video_file = fields.Binary(string="Video MP4", attachment=True)
    video_filename = fields.Char(string="Nombre del video")
    video_embed_url = fields.Char(string="URL embebida", compute="_compute_video_embed_fields")
    video_is_direct = fields.Boolean(string="Video directo", compute="_compute_video_embed_fields")
    reference_url = fields.Char(string="Fuente tecnica")
    media_credit = fields.Char(string="Credito multimedia")
    company_id = fields.Many2one(
        "res.company",
        string="Compania",
        default=lambda self: self.env.company,
        required=True,
    )
    is_editor = fields.Boolean(
        string="Puede editar",
        compute="_compute_is_editor",
        help="True si el usuario actual puede editar esta guia (autor o admin)",
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

    @api.depends("video_url")
    def _compute_video_embed_fields(self):
        for guide in self:
            guide.video_embed_url = False
            guide.video_is_direct = False
            if not guide.video_url:
                continue

            parsed = urlparse(guide.video_url)
            host = (parsed.netloc or "").lower()
            path = parsed.path or ""
            clean_url = guide.video_url.split("?", 1)[0].lower()

            if clean_url.endswith((".mp4", ".webm", ".ogg")):
                guide.video_embed_url = guide.video_url
                guide.video_is_direct = True
            elif "youtube.com" in host:
                video_id = parse_qs(parsed.query).get("v", [False])[0]
                if "/embed/" in path:
                    guide.video_embed_url = guide.video_url
                elif video_id:
                    guide.video_embed_url = "https://www.youtube.com/embed/%s" % video_id
            elif "youtu.be" in host:
                video_id = path.strip("/").split("/")[0]
                if video_id:
                    guide.video_embed_url = "https://www.youtube.com/embed/%s" % video_id
            elif "vimeo.com" in host:
                video_id = path.strip("/").split("/")[0]
                if video_id:
                    guide.video_embed_url = "https://player.vimeo.com/video/%s" % video_id

    def _is_accessible_for_partner(self, partner):
        self.ensure_one()
        if not self.requires_subscription:
            return True
        if not partner or partner._name != "res.partner":
            return False
        plan, subscription = partner.sudo()._get_current_subscription_plan()
        if not plan or not subscription:
            return False
        if not self.allowed_plan_ids:
            return True
        return plan in self.allowed_plan_ids

    @api.model
    def _get_portal_accessible_domain(self, partner):
        public_domain = [
            ("is_published", "=", True),
            ("state", "=", "published"),
            ("active", "=", True),
            ("requires_subscription", "=", False),
        ]
        if not partner or partner._name != "res.partner":
            return public_domain

        plan, subscription = partner.sudo()._get_current_subscription_plan()
        if not plan or not subscription:
            return public_domain

        return [
            ("is_published", "=", True),
            ("state", "=", "published"),
            ("active", "=", True),
            "|",
            ("requires_subscription", "=", False),
            "|",
            ("allowed_plan_ids", "=", False),
            ("allowed_plan_ids", "in", [plan.id]),
        ]

    @api.depends('author_user_id')
    def _compute_is_editor(self):
        for guide in self:
            user = self.env.user
            guide.is_editor = bool(
                user.has_group("iz_backend_theme.group_ironzone_admin")
                or (guide.author_user_id and guide.author_user_id.id == user.id)
            )

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
