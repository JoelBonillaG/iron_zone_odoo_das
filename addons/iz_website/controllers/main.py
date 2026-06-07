from datetime import date, datetime

from odoo import http
from odoo.exceptions import UserError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request


class IzSignupController(AuthSignupHome):
    """Extends the default Odoo signup to capture IZ-specific profile fields
    and enforce the minimum age of 14 years."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _iz_compute_age(birthdate_str):
        """Return (age_years, error_message).  error_message is None on success."""
        if not birthdate_str:
            return None, None  # field not filled – handled by required attr
        try:
            bd = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Fecha de nacimiento inválida."
        today = date.today()
        age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        if age < 14:
            return age, "Debes tener al menos 14 años para registrarte en Iron Zone."
        return age, None

    @staticmethod
    def _iz_validate_required_fields(params):
        missing = []
        if not (params.get("iz_gender") or "").strip():
            missing.append("Género")
        if not (params.get("iz_birthdate") or "").strip():
            missing.append("Fecha de nacimiento")
        if not (params.get("iz_fitness_goal") or "").strip():
            missing.append("Objetivo fitness")
        if not (params.get("iz_experience_level") or "").strip():
            missing.append("Nivel de experiencia")
        if missing:
            return "Completa los campos obligatorios: %s." % ", ".join(missing)
        return None

    # ------------------------------------------------------------------
    # Override – add IZ fields to signup
    # ------------------------------------------------------------------

    def _prepare_signup_values(self, qcontext):
        """Inject iz_* fields into the values that will create res.partner/res.users."""
        values = super()._prepare_signup_values(qcontext)

        params = request.params
        iz_gender = params.get("iz_gender", "").strip() or False
        iz_birthdate = params.get("iz_birthdate", "").strip() or False
        iz_fitness_goal = params.get("iz_fitness_goal", "").strip() or False
        iz_experience_level = params.get("iz_experience_level", "").strip() or False

        if iz_gender:
            values["iz_gender"] = iz_gender
        if iz_birthdate:
            values["iz_birthdate"] = iz_birthdate
        if iz_fitness_goal:
            values["iz_fitness_goal"] = iz_fitness_goal
        if iz_experience_level:
            values["iz_experience_level"] = iz_experience_level

        # Always subscribe new users to the mailing list
        values["iz_subscribed"] = True

        return values

    # ------------------------------------------------------------------
    # Override GET – pass selection choices to template
    # ------------------------------------------------------------------

    def get_auth_signup_qcontext(self):
        qcontext = super().get_auth_signup_qcontext()
        qcontext.setdefault("iz_gender_choices", [
            ("male", "Masculino"),
            ("female", "Femenino"),
            ("prefer_not", "Prefiero no decirlo"),
        ])
        qcontext.setdefault("iz_fitness_goal_choices", [
            ("weight_loss", "Perder peso"),
            ("muscle_gain", "Ganar masa muscular"),
            ("general_fitness", "Mantenerme saludable"),
            ("endurance", "Mejorar resistencia física"),
        ])
        qcontext.setdefault("iz_experience_level_choices", [
            ("beginner", "Principiante"),
            ("intermediate", "Intermedio"),
            ("advanced", "Avanzado"),
        ])
        draft = request.session.get("iz_signup_draft") or {}
        for key in ("login", "name", "email", "phone",
                    "iz_gender", "iz_birthdate", "iz_fitness_goal", "iz_experience_level"):
            if draft.get(key) and not qcontext.get(key):
                qcontext[key] = draft[key]
        if draft:
            qcontext["show_clear_draft"] = True
        return qcontext

    # ------------------------------------------------------------------
    # Override POST – validate age before creating user
    # ------------------------------------------------------------------

    @http.route()
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        is_post = request.httprequest.method == "POST" and not qcontext.get("token")

        if is_post:
            request.session["iz_signup_draft"] = {
                "login": request.params.get("login", ""),
                "name": request.params.get("name", ""),
                "email": request.params.get("email", ""),
                "phone": request.params.get("phone", ""),
                "iz_gender": request.params.get("iz_gender", ""),
                "iz_birthdate": request.params.get("iz_birthdate", ""),
                "iz_fitness_goal": request.params.get("iz_fitness_goal", ""),
                "iz_experience_level": request.params.get("iz_experience_level", ""),
            }

        response = super().web_auth_signup(*args, **kw)

        if is_post:
            qcontext2 = self.get_auth_signup_qcontext()
            if not qcontext2.get("error"):
                request.session.pop("iz_signup_draft", None)
            signup_login = (request.params.get("login") or "").strip()
            if signup_login:
                try:
                    user = self.env["res.users"].search([("login", "=", signup_login)], limit=1)
                    if user:
                        self.env["mail.mail"].search([
                            ("model", "=", "res.users"),
                            ("res_id", "=", user.id),
                        ]).unlink()
                except Exception:
                    pass

        return response
