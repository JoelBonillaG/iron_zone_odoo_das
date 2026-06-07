import json
from datetime import date, datetime

from odoo import http, _
from markupsafe import Markup
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError, ValidationError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import werkzeug
from werkzeug.urls import url_encode


class IzWebsiteSaleAddress(WebsiteSale):
    @http.route()
    def shop_address_submit(self, *args, **kwargs):
        request.update_env(
            context=dict(
                request.env.context,
                no_vat_validation=True,
                tracking_disable=True,
            )
        )
        try:
            return super().shop_address_submit(*args, **kwargs)
        except ValidationError as exc:
            message = exc.args[0] if exc.args else str(exc)
            return json.dumps({
                "invalid_fields": ["vat"],
                "messages": [message],
            })


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
    # Override POST – complete signup without Odoo's welcome email
    # ------------------------------------------------------------------

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if not request.env['ir.http']._verify_request_recaptcha_token('signup'):
                    raise UserError(_("Suspicious activity detected by Google reCaptcha."))

                # Save draft before processing
                if not qcontext.get('token'):
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

                self.do_signup(qcontext)

                # Set user to public if they were not signed in by do_signup (mfa enabled)
                if request.session.uid is None:
                    public_user = request.env.ref('base.public_user')
                    request.update_env(user=public_user)

                # DO NOT send Odoo's default welcome email.
                # Send IZ welcome email directly.
                partner_email = (request.params.get("email") or "").strip()
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    [('login', '=', qcontext.get('login'))], limit=1
                )
                if not user_sudo and partner_email:
                    user_sudo = User.sudo().search(
                        [('email', '=', partner_email)], limit=1
                    )
                if not user_sudo:
                    login_domain = User._get_login_domain(qcontext.get('login'))
                    user_sudo = User.sudo().search(login_domain, order=User._get_login_order(), limit=1)
                
                if user_sudo:
                    partner = user_sudo.sudo().partner_id
                    if partner and partner.email:
                        template = request.env.ref("iz_website.mail_template_welcome", raise_if_not_found=False)
                        if template:
                            try:
                                today = date.today()
                                is_bday = bool(partner.iz_birthdate and partner.iz_birthdate.month == today.month and partner.iz_birthdate.day == today.day)
                                ctx = {"partner": partner, "is_birthday": is_bday, "is_birthday_today": is_bday}
                                template.sudo().with_context(**ctx).send_mail(partner.id, force_send=True)
                                partner.sudo().write({"iz_welcome_sent": True})
                            except Exception as e:
                                import logging
                                _logger = logging.getLogger(__name__)
                                _logger.error("Error sending IZ welcome email: %s", str(e))
                        else:
                            import logging
                            _logger = logging.getLogger(__name__)
                            _logger.error("IZ welcome template not found: iz_website.mail_template_welcome")
                    else:
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.error("Partner not found or no email for user: %s", user_sudo.login)
                else:
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.error("User not found after signup with login: %s", qcontext.get('login'))

                # Clear draft on success
                request.session.pop("iz_signup_draft", None)

                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search_count([("login", "=", qcontext.get("login"))], limit=1):
                    qcontext['error'] = _("Another user is already registered using this email address.")
                else:
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.warning("%s", e)
                    qcontext['error'] = _("Could not create a new account.") + Markup('<br/>') + str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
