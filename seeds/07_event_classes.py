from config import DB, PASSWORD, connect, create
from datetime import datetime, timedelta
import os
import base64
import json


DEFAULT_PASSWORD = "admin123"

COMPANY_ADDRESS = {
    "street": "Av. Cevallos y Montalvo 245",
    "city": "Ambato",
    "phone": "+593 3 282 4450",
    "email": "contacto@ironzone.ec",
}

CLASSES = [
    {
        "name": "CrossFit AM",
        "instructor": "Carlos Mendez",
        "capacity": 20,
        "price": 12.0,
        "time": "06:00",
        "stage": "Nuevo",
        "description": "¡Despierta tu cuerpo y mente con CrossFit AM! Este programa de acondicionamiento físico de alta intensidad está diseñado para llevarte al límite. Combinamos movimientos funcionales constantemente variados, incluyendo levantamiento de pesas olímpico, ejercicios gimnásticos y entrenamiento cardiovascular riguroso. Cada sesión es un desafío nuevo que te ayudará a desarrollar fuerza, resistencia, agilidad y potencia. Únete a nuestra comunidad madrugadora y empieza tu día con la energía al máximo. No importa tu nivel actual, nuestros entrenadores adaptarán los ejercicios para que progreses de forma segura.",
        "image": "crossfit.jpg",
    },
    {
        "name": "Yoga Principiantes",
        "instructor": "Sofia Garcia",
        "capacity": 15,
        "price": 8.0,
        "time": "07:00",
        "stage": "Nuevo",
        "description": "Descubre la paz interior y la flexibilidad en nuestra clase de Yoga para Principiantes. Ideal para quienes dan sus primeros pasos en esta disciplina milenaria. Aprenderás las asanas (posturas) fundamentales, técnicas de respiración (pranayama) y relajación profunda. Nuestro enfoque guiado te permitirá conectar cuerpo y mente en un ambiente libre de juicios y lleno de tranquilidad. Aumenta tu flexibilidad, reduce el estrés diario y mejora tu postura con la ayuda de nuestra instructora experta. Ven con ropa cómoda y déjate llevar por esta experiencia revitalizante.",
        "image": "yoga.jpg",
    },
    {
        "name": "Spinning 18:00",
        "instructor": "Carlos Mendez",
        "capacity": 25,
        "price": 10.0,
        "time": "18:00",
        "stage": "Nuevo",
        "description": "Prepárate para sudar y quemar calorías al ritmo de la mejor música en nuestra sesión de Spinning. Esta clase de ciclismo indoor de alta energía te transportará a través de rutas virtuales con subidas intensas, sprints explosivos y descensos recuperadores. Mejora tu capacidad cardiovascular y tonifica tus piernas de manera divertida y desafiante. La motivación del grupo y de nuestro instructor te empujarán a dar ese esfuerzo extra. Es la manera perfecta de liberar tensiones después de un largo día de trabajo. ¡Ajusta tu bicicleta y prepárate para pedalear con fuerza!",
        "image": "spinig.jpg",
    },
    {
        "name": "Zumba Cardio",
        "instructor": "Sofia Garcia",
        "capacity": 30,
        "price": 8.0,
        "time": "19:00",
        "stage": "Nuevo",
        "description": "¡La fiesta más saludable te espera en Zumba Cardio! Olvídate de que estás haciendo ejercicio mientras te mueves al ritmo vibrante de la música latina e internacional. Esta clase combina movimientos de baile con rutinas aeróbicas para crear un entrenamiento dinámico, emocionante y súper efectivo. Mejorarás tu coordinación, quemarás calorías a montones y liberarás endorfinas que te harán sentir increíble. No necesitas saber bailar, solo tener ganas de divertirte y mover todo el cuerpo. Ven a contagiarte de alegría y energía positiva con nosotros.",
        "image": "zumba.jpg",
    },
    {
        "name": "Pilates Avanzado",
        "instructor": "Sofia Garcia",
        "capacity": 12,
        "price": 14.0,
        "time": "09:00",
        "stage": "Nuevo",
        "description": "Lleva tu práctica al siguiente nivel con nuestra clase de Pilates Avanzado. Diseñada para quienes ya dominan los principios básicos, esta sesión intensificará el trabajo en tu 'powerhouse' (core). Realizaremos secuencias fluidas y complejas que exigen mayor control, equilibrio y precisión en cada movimiento. Fortalecerás la musculatura profunda, mejorarás drásticamente tu flexibilidad y perfeccionarás tu alineación postural. Experimentarás un entrenamiento integral que desafiará tu mente y cuerpo, esculpiendo tu figura de manera armoniosa y elegante. ¡Exígete más y nota la diferencia!",
        "image": "pilates.jpg",
    },
    {
        "name": "HIIT Entrenamiento",
        "instructor": "Carlos Mendez",
        "capacity": 20,
        "price": 12.0,
        "time": "17:30",
        "stage": "Nuevo",
        "description": "Maximiza tus resultados en tiempo récord con HIIT (High Intensity Interval Training). Esta sesión alterna ráfagas de ejercicio intenso con breves períodos de recuperación, llevando tu frecuencia cardíaca a su punto óptimo para la quema de grasa. Es un entrenamiento exigente que acelerará tu metabolismo incluso horas después de haber terminado. Mejorarás tu resistencia cardiovascular y muscular de forma espectacular. Diseñado para personas motivadas que buscan un reto real. Prepárate para dar tu 100% y descubrir de lo que realmente eres capaz.",
        "image": "hiit.jpg",
    },
    {
        "name": "Boxeo Tecnica",
        "instructor": "Carlos Mendez",
        "capacity": 10,
        "price": 15.0,
        "time": "18:30",
        "stage": "Nuevo",
        "description": "Domina el arte del boxeo en nuestra clase enfocada en la técnica. Aprenderás los fundamentos esenciales: paradas, desplazamientos, jabs, crosses, ganchos y uppercuts, siempre con un enfoque en la ejecución correcta. No solo es un excelente ejercicio cardiovascular que tonifica todo el cuerpo, sino que también fomenta la disciplina, la concentración y la confianza en uno mismo. Practicaremos frente al espejo, con sacos y manoplas para afinar tus reflejos y potencia. Ideal tanto para principiantes que quieren aprender desde cero como para quienes desean perfeccionar su estilo.",
        "image": "boxeo.jpg",
    },
    {
        "name": "Yoga Avanzado",
        "instructor": "Sofia Garcia",
        "capacity": 15,
        "price": 12.0,
        "time": "08:00",
        "stage": "Reservado",
        "description": "Profundiza en tu práctica espiritual y física en nuestra clase de Yoga Avanzado. Exploraremos asanas desafiantes, incluyendo inversiones, equilibrios de brazos y flexiones profundas, requiriendo fuerza, concentración y fluidez. La clase también abarca prácticas de pranayama complejas y períodos más largos de meditación profunda para lograr un estado de conciencia plena. Está dirigida a practicantes con experiencia que buscan superar sus límites y encontrar una mayor armonía interna. Acompáñanos en este viaje de autodescubrimiento y expansión personal.",
        "image": "yoga.jpg",
    },
    {
        "name": "Natacion Adultos",
        "instructor": "Sofia Garcia",
        "capacity": 16,
        "price": 18.0,
        "time": "10:00",
        "stage": "Nuevo",
        "description": "Sumérgete en la salud y el bienestar con nuestras clases de Natación para Adultos. Ya sea que quieras perder el miedo al agua, aprender a nadar desde cero o perfeccionar tus estilos (crol, espalda, pecho, mariposa), tenemos un espacio para ti. La natación es el ejercicio cardiovascular más completo y de menor impacto, ideal para proteger tus articulaciones mientras fortaleces todos los grupos musculares. Recibe atención personalizada en un ambiente seguro y relajado. Disfruta de la sensación de ingravidez y los beneficios terapéuticos del agua.",
        "image": "natacion_adultos.jpg",
    },
    {
        "name": "Entrenamiento en Grupo",
        "instructor": "Carlos Mendez",
        "capacity": 22,
        "price": 9.0,
        "time": "16:00",
        "stage": "Nuevo",
        "description": "Descubre el poder de la comunidad en nuestro Entrenamiento en Grupo. Estas sesiones de acondicionamiento físico general combinan fuerza, resistencia y movilidad en rutinas variadas para que nunca te aburras. La energía colectiva es el motor principal: entrenar junto a otros te motivará a superar la pereza y alcanzar tus metas. Fomentamos un ambiente de compañerismo, apoyo mutuo y competencia sana. Es perfecto para cualquier nivel, ya que los ejercicios pueden escalarse según tus capacidades. ¡Ven a hacer amigos mientras te pones en forma!",
        "image": "funcional_boot_camp.jpg",
    },
    {
        "name": "Tae Kwon Do Ninos",
        "instructor": "Carlos Mendez",
        "capacity": 18,
        "price": 10.0,
        "time": "15:00",
        "stage": "Reservado",
        "description": "Inicia a tus hijos en el fascinante mundo del Tae Kwon Do. Más que un deporte de combate, es una escuela de vida que inculca valores fundamentales como el respeto, la disciplina, la perseverancia y el autocontrol. Los niños aprenderán técnicas de defensa personal, mejorarán su coordinación motriz, elasticidad y agilidad mental a través de juegos y ejercicios adaptados a su edad. Todo en un entorno seguro y divertido donde canalizarán su energía de forma positiva. Fomenta la autoconfianza y el desarrollo integral de los más pequeños.",
        "image": "taekwondo_ninos.jpg",
    },
    {
        "name": "Danza Contemporanea",
        "instructor": "Sofia Garcia",
        "capacity": 20,
        "price": 11.0,
        "time": "11:00",
        "stage": "Reservado",
        "description": "Libera tus emociones y exprésate a través del movimiento en nuestras clases de Danza Contemporánea. Esta disciplina fusiona elementos del ballet clásico con técnicas modernas, priorizando la fluidez, la conexión con el suelo y la improvisación. Exploraremos el uso del peso del cuerpo, la respiración y el espacio para crear coreografías emotivas y orgánicas. No importa tu complexión física o si tienes experiencia previa, lo importante es tu disposición para explorar y sentir. Descubre una forma hermosa y artística de ejercitar tu cuerpo y alma.",
        "image": "danza_contemporanea.jpg",
    },
    {
        "name": "Musculacion Personalizada",
        "instructor": "Carlos Mendez",
        "capacity": 8,
        "price": 20.0,
        "time": "12:00",
        "stage": "Anunciado",
        "description": "Alcanza tus objetivos específicos de hipertrofia o tonificación en nuestra sesión de Musculación Personalizada. Con un cupo limitado a solo 8 personas, garantizamos una atención casi individualizada por parte de nuestro entrenador. Evaluaremos tus metas, nivel actual y posibles limitaciones para diseñar un plan de entrenamiento adaptado estrictamente a ti. Aprenderás la biomecánica correcta de cada ejercicio de levantamiento, asegurando resultados óptimos y previniendo lesiones. Si buscas un cambio físico real y medible, este es el lugar para empezar.",
        "image": "musculacion_personalizada.jpg",
    },
    {
        "name": "Acuagym",
        "instructor": "Sofia Garcia",
        "capacity": 25,
        "price": 13.0,
        "time": "14:00",
        "stage": "Anunciado",
        "description": "Refréscate y ejercítate sin impacto en nuestras clases de Acuagym. Aprovechando la resistencia natural que ofrece el agua, realizarás un trabajo cardiovascular y de tonificación muscular sumamente efectivo pero gentil con tus articulaciones. Es la opción perfecta para personas en procesos de rehabilitación, mujeres embarazadas, adultos mayores o cualquiera que busque una alternativa divertida al gimnasio tradicional. Mejora tu circulación, flexibilidad y capacidad aeróbica al ritmo de música animada. ¡Siente los beneficios de entrenar en el medio acuático!",
        "image": "acuagym.jpg",
    },
    {
        "name": "Funcional Boot Camp",
        "instructor": "Carlos Mendez",
        "capacity": 15,
        "price": 12.0,
        "time": "06:30",
        "stage": "Anunciado",
        "description": "¡Únete a nuestro Funcional Boot Camp y transforma tu cuerpo! Inspirado en el entrenamiento militar, este programa intensivo al aire libre o en sala te llevará a superar tus límites. Combina calistenia, ejercicios con peso corporal, carreras y circuitos de agilidad. Construirás una resistencia de hierro, ganarás fuerza funcional aplicable a tu día a día y forjarás una mentalidad inquebrantable. Prepárate para sudar, ensuciarte y trabajar en equipo para superar cada obstáculo. No prometemos que será fácil, pero te garantizamos que valdrá la pena.",
        "image": "funcional_boot_camp.jpg",
    },
    {
        "name": "Meditacion Mindfulness",
        "instructor": "Sofia Garcia",
        "capacity": 12,
        "price": 7.0,
        "time": "19:30",
        "stage": "Anunciado",
        "description": "Encuentra tu oasis de calma en medio del caos diario con nuestra clase de Meditación Mindfulness. Aprende a vivir el momento presente con atención plena y sin juicios. Guiados por nuestra instructora, practicaremos diferentes técnicas de respiración consciente, escaneo corporal y visualización para calmar la mente y reducir la ansiedad y el estrés. Desarrollarás herramientas prácticas para manejar las emociones, mejorar la concentración y fomentar un profundo estado de bienestar y serenidad interior. Date el regalo de una pausa regeneradora para tu salud mental.",
        "image": "meditacion.jpg",
    },
]

STAGE_SEQUENCE = {
    "Nuevo": 10,
    "Reservado": 20,
    "Anunciado": 30,
}

CLASS_NAMES = [class_info["name"] for class_info in CLASSES]


def odoo_datetime(value):
    return value.replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "search_read",
        [domain],
        {"fields": fields or ["id"], "limit": 1, "context": {"active_test": False}},
    )
    return records[0] if records else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def xmlid_to_res_id(uid, models, xmlid, required=True):
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid,
        models,
        "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    if not record:
        if not required:
            print(f"  Warning: external ID not found, skipped: {xmlid}")
            return None
        raise RuntimeError(f"External ID not found: {xmlid}")
    return record["res_id"]


def ensure_user_groups(uid, models, user_id, group_xmlids):
    group_ids = []
    for xmlid in group_xmlids:
        group_id = xmlid_to_res_id(uid, models, xmlid, required=False)
        if group_id:
            group_ids.append(group_id)
    if not group_ids:
        return
    commands = []
    if "base.group_user" in group_xmlids:
        portal_group_id = xmlid_to_res_id(uid, models, "base.group_portal", required=False)
        if portal_group_id:
            commands.append((3, portal_group_id))
    commands.extend((4, group_id) for group_id in group_ids)
    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.users",
        "write",
        [[user_id], {"groups_id": commands}],
    )


def ensure_instructor_user(uid, models, user_id):
    ensure_user_groups(
        uid,
        models,
        user_id,
        [
            "base.group_user",
            "event.group_event_registration_desk",
            "iz_backend_theme.group_ironzone_trainers",
        ],
    )


def ensure_event_admin_rule(uid, models):
    event_model_id = xmlid_to_res_id(uid, models, "event.model_event_event")
    admin_group_id = xmlid_to_res_id(uid, models, "base.group_system")
    create_or_update(
        uid,
        models,
        "ir.rule",
        [("name", "=", "Administrador ve todos los eventos"), ("model_id", "=", event_model_id)],
        {
            "name": "Administrador ve todos los eventos",
            "model_id": event_model_id,
            "groups": [(4, admin_group_id)],
            "domain_force": "[(1, '=', 1)]",
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        },
        fields=["id"],
    )

def ensure_event_stages(uid, models):
    stage_ids = {}
    for stage_name, sequence in STAGE_SEQUENCE.items():
        stage_id, _ = create_or_update(
            uid,
            models,
            "event.stage",
            [("name", "=", stage_name)],
            {"name": stage_name, "sequence": sequence},
            fields=["id", "name"],
        )
        stage_ids[stage_name] = stage_id

    old_stage_ids = models.execute_kw(
        DB, uid, PASSWORD, "event.stage", "search",
        [[("name", "not in", list(STAGE_SEQUENCE.keys()))]],
    )
    deletable = []
    for sid in old_stage_ids:
        count = models.execute_kw(DB, uid, PASSWORD, "event.event", "search_count", [[("stage_id", "=", sid)]])
        if count == 0:
            deletable.append(sid)
    if deletable:
        models.execute_kw(DB, uid, PASSWORD, "event.stage", "unlink", [deletable])
        print(f"Deleted {len(deletable)} old event stage(s).")

    return stage_ids


def archive_old_demo_events(uid, models):
    print("Skipping archive of unrelated events; existing manual events are preserved.")


def ensure_user_for_employee(uid, models, employee):
    if employee.get("user_id"):
        user_id = employee["user_id"][0]
        ensure_instructor_user(uid, models, user_id)
        return user_id

    login = employee.get("work_email") or f"{employee['name'].lower().replace(' ', '.')}@ironzone.com"
    partner_id, _ = create_or_update(
        uid,
        models,
        "res.partner",
        [("email", "=", login)],
        {"name": employee["name"], "email": login, "active": True},
        fields=["id"],
    )
    user_id, _ = create_or_update(
        uid,
        models,
        "res.users",
        [("login", "=", login)],
        {
            "name": employee["name"],
            "login": login,
            "email": login,
            "partner_id": partner_id,
            "password": DEFAULT_PASSWORD,
            "active": True,
        },
        fields=["id", "name"],
    )
    ensure_instructor_user(uid, models, user_id)
    models.execute_kw(DB, uid, PASSWORD, "hr.employee", "write", [[employee["id"]], {"user_id": user_id}])
    return user_id


def run():
    uid, models = connect()
    ensure_event_admin_rule(uid, models)
    archive_old_demo_events(uid, models)

    # Get company info
    company_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.company",
        "search",
        [[]],
        {"limit": 1},
    )[0]
    
    company_data = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.company",
        "read",
        [[company_id], ["name", "phone", "email", "street", "city", "country_id"]],
    )[0]

    # Get or create location address
    location_partner_id, _ = create_or_update(
        uid,
        models,
        "res.partner",
        [("name", "=", "Iron Zone - Sede Ambato")],
        {
            "name": "Iron Zone - Sede Ambato",
            "type": "other",
            "street": COMPANY_ADDRESS.get("street", ""),
            "city": COMPANY_ADDRESS.get("city", ""),
            "email": COMPANY_ADDRESS.get("email", ""),
            "phone": COMPANY_ADDRESS.get("phone", ""),
            "country_id": company_data.get("country_id", (False,))[0],
        },
        fields=["id"],
    )

    instructor_user_ids = {}
    print("Mapping instructors from employees...")
    for class_info in CLASSES:
        instructor_name = class_info["instructor"]
        if instructor_name in instructor_user_ids:
            continue

        instructor = search_one(
            uid,
            models,
            "hr.employee",
            [("name", "=", instructor_name), ("active", "=", True)],
            fields=["id", "name", "work_email", "user_id"],
        )
        if instructor:
            user_id = ensure_user_for_employee(uid, models, instructor)
            instructor_user_ids[instructor_name] = user_id
            print(f"  Found instructor: {instructor_name} (Employee ID: {instructor['id']}, User ID: {user_id})")
        else:
            print(f"  Warning: Instructor not found: {instructor_name}")

    print("Fetching all members/customers...")
    all_members = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [[("customer_rank", ">", 0), ("active", "=", True)]],
        {"fields": ["id", "name", "email"], "limit": 100},
    )
    member_ids = {member["name"]: member["id"] for member in all_members}
    print(f"  Found {len(member_ids)} members")

    stage_ids = ensure_event_stages(uid, models)

    print("Configurando producto para los boletos...")
    product_id, _ = create_or_update(
        uid,
        models,
        "product.product",
        [("name", "=", "Boleto de Clase")],
        {
            "name": "Boleto de Clase",
            "type": "service",
            "list_price": 0.0,
        },
        fields=["id"]
    )

    created_count = 0
    updated_count = 0
    event_ids = {}
    print("Syncing group classes...")
    base_date = datetime.now() + timedelta(days=1)

    for idx, class_info in enumerate(CLASSES):
        event_date = base_date + timedelta(days=idx % 7)
        hour, minute = [int(part) for part in class_info["time"].split(":")]
        event_datetime = event_date.replace(hour=hour, minute=minute)
        instructor_user_id = instructor_user_ids.get(class_info["instructor"])

        img_base64 = False
        image_filename = class_info.get("image")
        if image_filename:
            image_path = os.path.join(os.path.dirname(__file__), "images", "events", image_filename)
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode("utf-8")

        # CSS para ocultar el banner pixelado solo en la página de detalles
        desc_html = '<div style="font-size: 1.3rem; line-height: 1.8; color: #cfcfcf; padding: 15px;">'
        desc_html += f'<p>{class_info.get("description", "")}</p></div>'

        values = {
            "name": class_info["name"],
            "description": desc_html,
            "seats_limited": True,
            "seats_available": class_info["capacity"],
            "seats_max": class_info["capacity"],
            "date_begin": odoo_datetime(event_datetime),
            "date_end": odoo_datetime(event_datetime + timedelta(hours=1)),
            "user_id": instructor_user_id or False,
            "stage_id": stage_ids.get(class_info.get("stage", "Nuevo")),
            "website_published": True,
            "website_menu": False,
            "address_id": location_partner_id,
            "event_type_id": False,
        }

        event_id, created = create_or_update(
            uid,
            models,
            "event.event",
            [("name", "=", class_info["name"])],
            values,
            fields=["id", "name"],
        )
        event_ids[class_info["name"]] = event_id

        if img_base64:
            attachment_id, att_created = create_or_update(
                uid,
                models,
                "ir.attachment",
                [("res_model", "=", "event.event"), ("res_id", "=", event_id), ("name", "=", "event_cover")],
                {
                    "name": "event_cover",
                    "datas": img_base64,
                    "res_model": "event.event",
                    "res_id": event_id,
                    "type": "binary",
                    "public": True,
                },
                fields=["id"]
            )
            cover_properties = {
                "background_color_class": "o_cc3",
                "background-image": f"url('/web/image/{attachment_id}')",
                "opacity": "0.4",
                "resize_class": "cover_auto"
            }
        else:
            cover_properties = {
                "background_color_class": "o_cc3",
                "background-image": "none",
                "opacity": "1.0",
                "resize_class": "cover_auto"
            }
        models.execute_kw(DB, uid, PASSWORD, "event.event", "write", [[event_id], {"cover_properties": json.dumps(cover_properties)}])

        ticket_values = {
            "name": "Entrada General",
            "event_id": event_id,
            "seats_max": class_info["capacity"],
            "price": class_info.get("price", 0.0),
            "product_id": product_id,
        }
        create_or_update(
            uid,
            models,
            "event.event.ticket",
            [("event_id", "=", event_id), ("name", "=", "Entrada General")],
            ticket_values,
            fields=["id"]
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

        action = "Created" if created else "Updated"
        print(f"  {action} class: {class_info['name']} - Instructor: {class_info['instructor']}")

    print("Registering members to classes...")
    registrations_created = 0
    for idx, (member_name, member_id) in enumerate(member_ids.items()):
        num_classes = 3 + (idx % 2)
        for class_offset in range(num_classes):
            class_idx = (idx + class_offset) % len(CLASSES)
            class_info = CLASSES[class_idx]
            event_id = event_ids.get(class_info["name"])
            if not event_id:
                continue

            values = {
                "event_id": event_id,
                "partner_id": member_id,
                "name": member_name,
            }
            ticket = search_one(
                uid,
                models,
                "event.event.ticket",
                [("event_id", "=", event_id), ("name", "=", "Entrada General")],
                fields=["id"],
            )
            if ticket:
                values["event_ticket_id"] = ticket["id"]
            _, created = create_or_update(
                uid,
                models,
                "event.registration",
                [("event_id", "=", event_id), ("partner_id", "=", member_id)],
                values,
                fields=["id"],
            )
            if created:
                registrations_created += 1

    print(f"Done: {created_count} classes created, {updated_count} updated.")
    print(f"Registered: {registrations_created} member registrations created.")


if __name__ == "__main__":
    run()
