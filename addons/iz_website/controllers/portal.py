from datetime import timedelta
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class IZCustomerPortal(CustomerPortal):

    def _get_optional_fields(self):
        res = super()._get_optional_fields()
        custom_fields = ["iz_gender", "iz_fitness_goal", "iz_experience_level"]
        return list(set(res + custom_fields))

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation=partner_creation)
        partner = request.env.user.partner_id
        
        # --- 30-day gender update rule ---
        new_gender = data.get("iz_gender")
        if new_gender and new_gender != partner.iz_gender:
            if partner.iz_gender_last_update:
                days_since_update = (fields.Datetime.now() - partner.iz_gender_last_update).days
                if days_since_update < 30:
                    error["iz_gender"] = "error"
                    error_message.append(
                        _(
                            "Solo puedes cambiar tu género una vez cada 30 días. Faltan %s días.",
                            30 - days_since_update,
                        )
                    )
        return error, error_message

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        if post and request.httprequest.method == 'POST':
            if not partner.can_edit_vat() and 'country_id' not in post:
                post['country_id'] = str(partner.country_id.id)
                
        response = super().account(redirect=redirect, **post)
        
        # Inject custom dropdown choices into template qcontext
        if hasattr(response, "qcontext"):
            response.qcontext.update({
                'iz_gender_choices': [
                    ("male", "Masculino"),
                    ("female", "Femenino"),
                    ("prefer_not", "Prefiero no decirlo"),
                ],
                'iz_fitness_goal_choices': [
                    ("weight_loss", "Pérdida de peso"),
                    ("muscle_gain", "Aumento de masa muscular"),
                    ("general_fitness", "Mantenerme saludable"),
                    ("endurance", "Mejorar resistencia física"),
                ],
                'iz_experience_level_choices': [
                    ("beginner", "Principiante"),
                    ("intermediate", "Intermedio"),
                    ("advanced", "Avanzado"),
                ]
            })
        return response
