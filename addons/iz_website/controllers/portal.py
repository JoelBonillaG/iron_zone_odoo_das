from datetime import timedelta
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class IZCustomerPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "iz_gender", "iz_fitness_goal", "iz_experience_level"]

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        """
        Extiende la ruta nativa /my/account para incluir los campos iz_*
        y aplicar la regla de 30 días para el cambio de género.
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            
            # --- Regla de 30 días para el género ---
            new_gender = post.get('iz_gender')
            if new_gender and new_gender != partner.iz_gender:
                if partner.iz_gender_last_update:
                    # Validar diferencia en días
                    days_since_update = (fields.Datetime.now() - partner.iz_gender_last_update).days
                    if days_since_update < 30:
                        error['iz_gender'] = 'error'
                        error_message.append(f"Solo puedes cambiar tu género una vez cada 30 días. Faltan {30 - days_since_update} días.")

            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                
                # Para evitar que actualicen el birthdate si lo inyectan por post
                values.pop('iz_birthdate', None)

                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                
                values.update({'zip': values.pop('zipcode', '')})
                
                # Actualizar partner
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        # Si es GET o hubo error, proveer diccionarios de opciones al template
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
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

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
