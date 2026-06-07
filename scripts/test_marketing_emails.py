# ══════════════════════════════════════════════════════════════════
# SCRIPT DE PRUEBAS DE CORREOS TRANSACCIONALES - IRON ZONE GYM
# ══════════════════════════════════════════════════════════════════
# Para ejecutar este script cargando la dirección desde el archivo .env,
# ejecuta en tu consola de PowerShell desde la raíz del proyecto:
#
# $testEmail = (Get-Content .env | Select-String "TEST_EMAIL=").Line.Split("=")[1].Trim()
# Get-Content scripts/test_marketing_emails.py | docker exec -i -e TEST_EMAIL="$testEmail" iron_zone_odoo odoo shell -c /etc/odoo/odoo.conf -d iron_zone --no-http --stop-after-init
# ══════════════════════════════════════════════════════════════════

import os
import datetime
from odoo.exceptions import ValidationError

# 1. OBTENER DIRECCIÓN DE CORREO DESTINATARIO
# Se lee dinámicamente de la variable de entorno TEST_EMAIL configurada en el .env del host.
TEST_EMAIL = os.environ.get('TEST_EMAIL') or 'ejemplo@ironzone.com'

# 2. ELIGE LA PLANTILLA QUE DESEAS PROBAR (Cambia este string por cualquiera de la lista de abajo)
TEMPLATE_TO_TEST = 'womens_day'

# Opciones válidas para TEMPLATE_TO_TEST:
# ------------------------------------------------------------------
# 'womens_day'        -> Correo Especial: Día de la Mujer (Femenino)
# 'mens_day'          -> Correo Especial: Día del Hombre (Masculino)
# 'birthday'          -> Felicitación de Cumpleaños
# 'welcome_birthday'  -> Bienvenida + Cumpleaños Hoy (Banner unificado)
# 'welcome_standard'  -> Bienvenida Estándar (Sin cumpleaños)
# 'goal_muscle_gain'  -> Novedades / Rutinas: Aumento de Masa Muscular
# 'goal_weight_loss'  -> Novedades / Rutinas: Pérdida de Peso
# 'goal_endurance'    -> Novedades / Rutinas: Resistencia Física
# 'goal_general'      -> Novedades / Rutinas: Fitness General
# 'level_beginner'    -> Nivel: Principiante
# 'level_intermediate'-> Nivel: Intermedio
# 'level_advanced'    -> Nivel: Avanzado
# 'membership_expiry' -> Aviso de Vencimiento de Membresía
# 'seasonal'          -> Campaña Especial de Temporada / Eventos
# ------------------------------------------------------------------

print("\n" + "="*60)
print("INICIANDO PRUEBA DE CAMPAÑA DE CORREO: %s" % TEMPLATE_TO_TEST.upper())
print("DESTINATARIO DILIGENCIADO: %s" % TEST_EMAIL)
print("="*60 + "\n")

# A. Buscar o crear el contacto de prueba
partner = env['res.partner'].with_context(iz_skip_automation=True).search([('email', '=', TEST_EMAIL)], limit=1)
if not partner:
    print("[+] Creando nuevo socio de prueba...")
    partner = env['res.partner'].with_context(iz_skip_automation=True).create({
        'name': 'Test User',
        'email': TEST_EMAIL,
    })

# Obtener fecha de hoy de acuerdo a zona horaria local del socio
today_date = env['res.partner']._fields['iz_birthdate'].context_today(partner)

# B. Configurar perfil según la plantilla seleccionada
print("[+] Configurando atributos de perfil de socio para la prueba...")
if TEMPLATE_TO_TEST == 'womens_day':
    partner.write({'iz_gender': 'female'})
    template_ref = 'iz_website.mail_template_womens_day'

elif TEMPLATE_TO_TEST == 'mens_day':
    partner.write({'iz_gender': 'male'})
    template_ref = 'iz_website.mail_template_mens_day'

elif TEMPLATE_TO_TEST == 'birthday':
    partner.write({'iz_birthdate': today_date.replace(year=today_date.year - 25)}) # 25 años hoy
    template_ref = 'iz_website.mail_template_birthday'

elif TEMPLATE_TO_TEST == 'welcome_birthday':
    partner.write({'iz_birthdate': today_date.replace(year=today_date.year - 25)}) # Cumpleaños hoy
    template_ref = 'iz_website.mail_template_welcome'

elif TEMPLATE_TO_TEST == 'welcome_standard':
    partner.write({'iz_birthdate': today_date.replace(year=today_date.year - 25, month=today_date.month - 1 or 12)}) # No es su cumpleaños
    template_ref = 'iz_website.mail_template_welcome'

elif TEMPLATE_TO_TEST == 'goal_muscle_gain':
    partner.write({'iz_fitness_goal': 'muscle_gain'})
    template_ref = 'iz_website.mail_template_goal_muscle_gain'

elif TEMPLATE_TO_TEST == 'goal_weight_loss':
    partner.write({'iz_fitness_goal': 'weight_loss'})
    template_ref = 'iz_website.mail_template_goal_weight_loss'

elif TEMPLATE_TO_TEST == 'goal_endurance':
    partner.write({'iz_fitness_goal': 'endurance'})
    template_ref = 'iz_website.mail_template_goal_endurance'

elif TEMPLATE_TO_TEST == 'goal_general':
    partner.write({'iz_fitness_goal': 'general_fitness'})
    template_ref = 'iz_website.mail_template_goal_general_fitness'

elif TEMPLATE_TO_TEST == 'level_beginner':
    partner.write({'iz_experience_level': 'beginner'})
    template_ref = 'iz_website.mail_template_level_beginner'

elif TEMPLATE_TO_TEST == 'level_intermediate':
    partner.write({'iz_experience_level': 'intermediate'})
    template_ref = 'iz_website.mail_template_level_intermediate'

elif TEMPLATE_TO_TEST == 'level_advanced':
    partner.write({'iz_experience_level': 'advanced'})
    template_ref = 'iz_website.mail_template_level_advanced'

elif TEMPLATE_TO_TEST == 'membership_expiry':
    template_ref = 'iz_website.mail_template_membership_expiry'

elif TEMPLATE_TO_TEST == 'seasonal':
    template_ref = 'iz_website.mail_template_seasonal'

else:
    raise ValueError("Plantilla no soportada: %s" % TEMPLATE_TO_TEST)

# Confirmar cambios en la base de datos
env.cr.commit()

# C. Obtener la plantilla de Odoo
print("[+] Obteniendo plantilla desde la base de datos: %s" % template_ref)
try:
    template = env.ref(template_ref)
except ValueError:
    print("[ERROR] No se pudo encontrar la plantilla '%s'. ¿Ya actualizaste el módulo 'iz_website'?" % template_ref)
    raise

# D. Forzar el envío del correo real
print("[+] Despachando correo transaccional...")
# Inyectar el contexto de cumpleaños si se está probando welcome_birthday
ctx = {}
if TEMPLATE_TO_TEST == 'welcome_birthday':
    ctx['is_birthday_today'] = True
    ctx['is_birthday'] = True

# Despachamos un único correo y forzamos auto_delete=False para inspección
mail_id = template.with_context(**ctx).send_mail(partner.id, force_send=True, email_values={'auto_delete': False})
env.cr.commit()  # Asegura que Odoo procese el envío

mail = env['mail.mail'].browse(mail_id)

if mail.state == 'sent':
    print("\n" + "="*60)
    print("¡CORREO ENVIADO CON ÉXITO!")
    print("ID del Mensaje Odoo: %s" % mail_id)
else:
    print("\n" + "="*60)
    print("❌ ERROR: EL CORREO NO SE PUDO ENVIAR")
    print("Estado actual: %s" % mail.state)
    print("Razón del fallo: %s" % (mail.failure_reason or 'Error de conexión o destinatario inválido.'))
print("Verifica tu bandeja de entrada en: %s" % TEST_EMAIL)
print("="*60 + "\n")
