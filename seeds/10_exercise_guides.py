"""
10_exercise_guides.py
---------------------
Seeds realistic gym machines, exercise guides, guide benefits, and demo access
for the Iron Zone exercise guide module.

Depends on:
- 02_subscription_config.py for subscription plans
- 06_employees.py for trainer employees
- 07_event_classes.py for group classes
- 08_subscription_post_process.py for subscription plan assignment
"""
import base64
import os
import urllib.parse
import urllib.request

from config import DB, PASSWORD, connect, create


IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images", "events")


def search_read(uid, models, model, domain, fields, **kwargs):
    options = {"fields": fields}
    options.setdefault("context", {"active_test": False})
    options.update(kwargs)
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], options)


def search_one(uid, models, model, domain, fields=None):
    rows = search_read(uid, models, model, domain, fields or ["id"], limit=1)
    return rows[0] if rows else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def model_exists(uid, models, model):
    try:
        models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})
        return True
    except Exception:
        return False


def get_model_fields(uid, models, model):
    return models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})


def xmlid_to_res_id(uid, models, xmlid):
    module, name = xmlid.split(".", 1)
    record = search_one(
        uid,
        models,
        "ir.model.data",
        [("module", "=", module), ("name", "=", name)],
        fields=["res_id"],
    )
    return record["res_id"] if record else False


def ensure_seed_user_can_manage_guides(uid, models):
    group_id = xmlid_to_res_id(uid, models, "iz_backend_theme.group_ironzone_admin")
    if not group_id:
        print("  Iron Zone admin group not found; guide creation may fail.")
        return
    user = search_one(uid, models, "res.users", [("id", "=", uid)], fields=["id", "groups_id"])
    if not user:
        return
    if group_id not in (user.get("groups_id") or []):
        models.execute_kw(DB, uid, PASSWORD, "res.users", "write", [[uid], {"groups_id": [(4, group_id)]}])
        print("  Seed user granted Iron Zone admin permissions for guide setup.")


def image_base64(filename=None, url=None):
    if url:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "IronZoneAcademicSeed/1.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                return base64.b64encode(response.read()).decode("utf-8")
        except Exception as exc:
            print(f"  Image download failed, using local fallback: {url} ({exc})")

    filename = filename or "musculacion_personalizada.jpg"
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "IronZone.png")
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def commons_file_url(filename):
    return "https://commons.wikimedia.org/wiki/Special:Redirect/file/%s" % urllib.parse.quote(filename)


def ensure_exercise_categories(uid, models):
    categories = [
        {
            "name": "Pecho",
            "code": "CHEST",
            "category_type": "muscle",
            "sequence": 10,
            "description": "Ejercicios enfocados en pectorales y empuje horizontal.",
        },
        {
            "name": "Espalda",
            "code": "BACK",
            "category_type": "muscle",
            "sequence": 20,
            "description": "Ejercicios de traccion para dorsales, trapecio y espalda media.",
        },
        {
            "name": "Piernas",
            "code": "LEGS",
            "category_type": "muscle",
            "sequence": 30,
            "description": "Trabajo de cuadriceps, isquiotibiales, gluteos y pantorrillas.",
        },
        {
            "name": "Hombros",
            "code": "SHOULDERS",
            "category_type": "muscle",
            "sequence": 40,
            "description": "Guias para deltoides, estabilidad escapular y empujes verticales.",
        },
        {
            "name": "Core y abdomen",
            "code": "CORE",
            "category_type": "muscle",
            "sequence": 50,
            "description": "Control del tronco, estabilidad y ejercicios abdominales.",
        },
        {
            "name": "Brazos",
            "code": "ARMS",
            "category_type": "muscle",
            "sequence": 55,
            "description": "Ejercicios para biceps, triceps y antebrazos.",
        },
        {
            "name": "Gluteos",
            "code": "GLUTES",
            "category_type": "muscle",
            "sequence": 58,
            "description": "Activacion y fuerza de gluteos para patrones de cadera.",
        },
        {
            "name": "Fuerza",
            "code": "STRENGTH",
            "category_type": "exercise",
            "sequence": 60,
            "description": "Ejercicios orientados a fuerza y tecnica de carga.",
        },
        {
            "name": "Cardio",
            "code": "CARDIO",
            "category_type": "exercise",
            "sequence": 70,
            "description": "Ejercicios cardiovasculares y de resistencia.",
        },
        {
            "name": "Movilidad",
            "code": "MOBILITY",
            "category_type": "exercise",
            "sequence": 80,
            "description": "Movilidad, respiracion, rango articular y recuperacion.",
        },
        {
            "name": "Peso libre",
            "code": "FREE_WEIGHT",
            "category_type": "equipment",
            "sequence": 90,
            "description": "Ejercicios con mancuernas, barras o implementos libres.",
        },
        {
            "name": "Bajo impacto",
            "code": "LOW_IMPACT",
            "category_type": "exercise",
            "sequence": 100,
            "description": "Alternativas suaves para acondicionamiento y retorno progresivo.",
        },
    ]

    print("Syncing exercise categories...")
    for category in categories:
        _, created = create_or_update(
            uid,
            models,
            "ironzone.exercise.category",
            [("code", "=", category["code"])],
            category,
            fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} category: {category['name']}")


def category_ids_by_code(uid, models):
    rows = search_read(uid, models, "ironzone.exercise.category", [], ["id", "code", "name", "category_type"])
    return {row["code"]: row["id"] for row in rows if row.get("code")}


def plan_ids_by_code(uid, models):
    if not model_exists(uid, models, "iz.subscription.plan"):
        return {}
    rows = search_read(uid, models, "iz.subscription.plan", [], ["id", "code"])
    return {row["code"]: row["id"] for row in rows if row.get("code")}


def employee_ids_by_name(uid, models):
    rows = search_read(
        uid,
        models,
        "hr.employee",
        [("active", "=", True)],
        ["id", "name"],
    )
    return {row["name"]: row["id"] for row in rows}


def event_ids_by_name(uid, models):
    rows = search_read(
        uid,
        models,
        "event.event",
        [("active", "=", True)],
        ["id", "name"],
    )
    return {row["name"]: row["id"] for row in rows}


def ensure_equipment_categories(uid, models):
    categories = [
        "Maquinas de fuerza",
        "Cardio",
        "Bancos y soportes",
        "Peso libre",
    ]
    category_ids = {}
    for name in categories:
        category_id, _ = create_or_update(
            uid,
            models,
            "maintenance.equipment.category",
            [("name", "=", name)],
            {"name": name},
            fields=["id", "name"],
        )
        category_ids[name] = category_id
    return category_ids


def ensure_machines(uid, models, categories):
    fields = get_model_fields(uid, models, "maintenance.equipment")
    equipment_categories = ensure_equipment_categories(uid, models)
    machines = [
        {
            "name": "Prensa de piernas 45 grados",
            "gym_zone": "strength",
            "equipment_category": "Maquinas de fuerza",
            "muscles": ["LEGS"],
            "note": "Equipo para trabajo guiado de cuadriceps, gluteos e isquiotibiales. Revisar bloqueo del asiento y recorrido antes de usar.",
        },
        {
            "name": "Polea alta dorsal",
            "gym_zone": "strength",
            "equipment_category": "Maquinas de fuerza",
            "muscles": ["BACK"],
            "note": "Maquina de traccion vertical para espalda. La carga debe permitir control escapular y rango completo sin balanceo.",
        },
        {
            "name": "Bicicleta de spinning",
            "gym_zone": "cardio",
            "equipment_category": "Cardio",
            "muscles": ["LEGS"],
            "note": "Bicicleta indoor para trabajo cardiovascular. Ajustar altura del sillin y manubrio antes de iniciar.",
        },
        {
            "name": "Banco plano de press",
            "gym_zone": "strength",
            "equipment_category": "Bancos y soportes",
            "muscles": ["CHEST", "SHOULDERS"],
            "note": "Banco para press con barra o mancuernas. Verificar estabilidad, seguros y acompaniamiento en cargas altas.",
        },
        {
            "name": "Caminadora profesional",
            "gym_zone": "cardio",
            "equipment_category": "Cardio",
            "muscles": ["LEGS"],
            "note": "Equipo cardiovascular para caminata o carrera. Usar clip de seguridad y empezar con velocidad progresiva.",
        },
        {
            "name": "Remo sentado en polea baja",
            "gym_zone": "strength",
            "equipment_category": "Maquinas de fuerza",
            "muscles": ["BACK"],
            "note": "Estacion de traccion horizontal para espalda media. Ajustar asiento y mantener torso estable.",
        },
        {
            "name": "Extension de piernas",
            "gym_zone": "strength",
            "equipment_category": "Maquinas de fuerza",
            "muscles": ["LEGS"],
            "note": "Maquina guiada para cuadriceps. Alinear el eje de la rodilla y controlar la extension.",
        },
        {
            "name": "Curl femoral sentado",
            "gym_zone": "strength",
            "equipment_category": "Maquinas de fuerza",
            "muscles": ["LEGS"],
            "note": "Equipo para isquiotibiales. Ajustar almohadilla y evitar levantar la cadera durante el movimiento.",
        },
        {
            "name": "Eliptica profesional",
            "gym_zone": "cardio",
            "equipment_category": "Cardio",
            "muscles": ["LEGS"],
            "note": "Equipo cardiovascular de bajo impacto para calentamiento, resistencia y recuperacion activa.",
        },
        {
            "name": "Rack de mancuernas",
            "gym_zone": "strength",
            "equipment_category": "Peso libre",
            "muscles": ["CHEST", "SHOULDERS", "ARMS"],
            "note": "Zona de peso libre para ejercicios con mancuernas. Mantener orden y elegir cargas controlables.",
        },
    ]

    machine_ids = {}
    print("Syncing gym machines...")
    for machine in machines:
        values = {
            "name": machine["name"],
            "is_gym_machine": True,
        }
        if "gym_zone" in fields:
            values["gym_zone"] = machine["gym_zone"]
        if "note" in fields:
            values["note"] = machine["note"]
        equipment_category_id = equipment_categories.get(machine.get("equipment_category"))
        if equipment_category_id and "category_id" in fields:
            values["category_id"] = equipment_category_id
        muscle_ids = [categories[code] for code in machine["muscles"] if code in categories]
        if "muscle_group_ids" in fields:
            values["muscle_group_ids"] = [(6, 0, muscle_ids)]
        machine_id, created = create_or_update(
            uid,
            models,
            "maintenance.equipment",
            [("name", "=", machine["name"])],
            values,
            fields=["id", "name"],
        )
        machine_ids[machine["name"]] = machine_id
        action = "Created" if created else "Updated"
        print(f"  {action} machine: {machine['name']}")
    return machine_ids


def html_steps(*steps):
    items = "".join(f"<li>{step}</li>" for step in steps)
    return f"<ol>{items}</ol>"


def ensure_guide_benefits(uid, models, plans):
    if not model_exists(uid, models, "iz.subscription.benefit"):
        return

    benefits = [
        {
            "name": "Guías técnicas avanzadas",
            "plan_code": "IZ_P01",
            "sequence": 30,
            "benefit_scope": "general",
            "benefit_type": "free",
            "discount_percent": 0.0,
            "description": "Acceso a guías técnicas con máquina y progresiones intermedias.",
        },
        {
            "name": "Biblioteca completa de guías",
            "plan_code": "IZ_PR01",
            "sequence": 30,
            "benefit_scope": "general",
            "benefit_type": "free",
            "discount_percent": 0.0,
            "description": "Acceso a todas las guías publicadas, incluyendo contenido premium.",
        },
        {
            "name": "Guías integrales de entrenamiento",
            "plan_code": "IZ_I01",
            "sequence": 30,
            "benefit_scope": "general",
            "benefit_type": "free",
            "discount_percent": 0.0,
            "description": "Acceso a guías técnicas, movilidad y recomendaciones de entrenamiento complementario.",
        },
    ]

    print("Syncing guide subscription benefits...")
    for benefit in benefits:
        plan_id = plans.get(benefit.pop("plan_code"))
        if not plan_id:
            continue
        benefit["plan_id"] = plan_id
        try:
            _, created = create_or_update(
                uid,
                models,
                "iz.subscription.benefit",
                [("plan_id", "=", plan_id), ("name", "=", benefit["name"])],
                benefit,
                fields=["id", "name"],
            )
            action = "Created" if created else "Updated"
            print(f"  {action} guide benefit: {benefit['name']}")
        except Exception as exc:
            print(f"  Skipped guide benefit '{benefit['name']}': {exc}")


def ensure_guides(uid, models, categories, machines, employees, events, plans):
    default_author = employees.get("Carlos Mendez") or employees.get("Sofia Garcia")
    if not default_author:
        print("  No trainer employees found; skipping exercise guides.")
        return

    guides = [
        {
            "name": "Prensa de piernas: tecnica segura para principiantes",
            "author": "Carlos Mendez",
            "exercise_type": "machine",
            "difficulty": "beginner",
            "machine": "Prensa de piernas 45 grados",
            "muscle": "LEGS",
            "categories": ["LEGS", "STRENGTH"],
            "image": "musculacion_personalizada.jpg",
            "image_url": commons_file_url("Young man using a leg press machine at the gym.jpg"),
            "media_credit": "Wikimedia Commons, archivo 'Young man using a leg press machine at the gym.jpg', CC BY 2.0",
            "video_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
            "reference_url": "https://www.fitloop.app/exercises/leg-press",
            "requires_subscription": False,
            "instructions": html_steps(
                "Ajusta el respaldo para que la cadera quede apoyada y la zona lumbar no se despegue del asiento.",
                "Coloca los pies al ancho de hombros sobre la plataforma, con puntas ligeramente abiertas.",
                "Desbloquea la maquina y baja la plataforma de forma controlada hasta un rango comodo.",
                "Empuja con toda la planta del pie sin bloquear completamente las rodillas al final.",
                "Respira de forma estable y detente si sientes dolor articular o perdida de control.",
            ),
            "recommendations": "Comienza con carga ligera, prioriza rango controlado y pide revision del entrenador en las primeras sesiones.",
            "common_mistakes": "Bajar demasiado perdiendo la pelvis, juntar las rodillas, rebotar al final del recorrido o bloquear rodillas con carga alta.",
            "safety_notes": "No retires los seguros hasta estar bien posicionado. Evita cargas maximas sin supervision.",
        },
        {
            "name": "Jalon en polea alta para espalda",
            "author": "Carlos Mendez",
            "exercise_type": "machine",
            "difficulty": "intermediate",
            "machine": "Polea alta dorsal",
            "muscle": "BACK",
            "categories": ["BACK", "STRENGTH"],
            "image": "crossfit.jpg",
            "image_url": commons_file_url("Back Pull down.jpg"),
            "media_credit": "Wikimedia Commons, archivo 'Back Pull down.jpg'",
            "video_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
            "reference_url": "https://muscularstrength.com/article/how-to-lat-pulldown",
            "requires_subscription": True,
            "plans": ["IZ_P01", "IZ_PR01", "IZ_I01"],
            "instructions": html_steps(
                "Ajusta el soporte de muslos para mantener el cuerpo estable durante la traccion.",
                "Toma la barra con agarre ligeramente mas amplio que los hombros.",
                "Inicia el movimiento bajando los hombros y juntando suavemente las escapulas.",
                "Lleva la barra hacia la parte alta del pecho sin inclinarte excesivamente hacia atras.",
                "Regresa con control hasta extender brazos sin perder tension en la espalda.",
            ),
            "recommendations": "Piensa en llevar los codos hacia abajo, no en tirar solo con los biceps. Mantén cuello relajado.",
            "common_mistakes": "Jalar detras de la nuca, balancear el tronco, usar impulso o encoger hombros en cada repeticion.",
            "safety_notes": "Si aparece molestia en hombro, reduce carga y cambia el agarre.",
        },
        {
            "name": "Ajuste correcto de bicicleta de spinning",
            "author": "Sofia Garcia",
            "exercise_type": "machine",
            "difficulty": "beginner",
            "machine": "Bicicleta de spinning",
            "muscle": "LEGS",
            "categories": ["LEGS", "CARDIO"],
            "event": "Spinning 18:00",
            "image": "spinig.jpg",
            "image_url": commons_file_url("Spin Cycle Indoor Cycling Class at a Gym.JPG"),
            "media_credit": "Wikimedia Commons, LocalFitness, 'Spin Cycle Indoor Cycling Class at a Gym.JPG', CC BY-SA 3.0",
            "video_url": "https://www.youtube.com/watch?v=csNeUKYBW0E",
            "reference_url": "https://www.consumerreports.org/video/view/healthy-living/fitness/4034139134001/how-to-fit-your-spin-bike/",
            "requires_subscription": False,
            "instructions": html_steps(
                "Coloca el sillin a la altura aproximada de la cadera cuando estas de pie junto a la bicicleta.",
                "Al pedalear, la rodilla debe quedar ligeramente flexionada en el punto mas bajo.",
                "Ajusta el manubrio para mantener espalda larga y hombros relajados.",
                "Verifica que las correas o calas sujeten bien el pie antes de aumentar la cadencia.",
                "Empieza con resistencia baja durante el calentamiento y aumenta de forma progresiva.",
            ),
            "recommendations": "Llega unos minutos antes de clase para ajustar la bicicleta sin apuro.",
            "common_mistakes": "Sillin demasiado bajo, manubrio muy lejos, pedalear con cadera inestable o subir resistencia sin control.",
            "safety_notes": "No retires los pies de los pedales hasta que la rueda se detenga completamente.",
        },
        {
            "name": "Plancha abdominal basica",
            "author": "Sofia Garcia",
            "exercise_type": "individual",
            "difficulty": "beginner",
            "muscle": "CORE",
            "categories": ["CORE", "STRENGTH"],
            "image": "pilates.jpg",
            "image_url": commons_file_url("Yoga PLank.jpg"),
            "media_credit": "Wikimedia Commons, lululemon athletica, 'Yoga PLank.jpg'",
            "video_url": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
            "reference_url": "https://physicalliving.com/how-to-do-a-plank-proper-plank-form/",
            "requires_subscription": False,
            "instructions": html_steps(
                "Apoya antebrazos en el suelo con codos debajo de los hombros.",
                "Extiende piernas y mantiene el cuerpo en linea recta desde cabeza hasta talones.",
                "Contrae abdomen y gluteos sin elevar demasiado la cadera.",
                "Respira de forma corta y controlada durante todo el tiempo de trabajo.",
                "Termina la serie antes de perder la postura.",
            ),
            "recommendations": "Empieza con bloques de 15 a 25 segundos y aumenta gradualmente.",
            "common_mistakes": "Hundimiento lumbar, elevar cadera, aguantar la respiracion o mirar demasiado hacia adelante.",
            "safety_notes": "Si hay dolor lumbar, reduce el tiempo o apoya rodillas.",
        },
        {
            "name": "Sentadilla libre: patron base",
            "author": "Carlos Mendez",
            "exercise_type": "individual",
            "difficulty": "intermediate",
            "muscle": "LEGS",
            "categories": ["LEGS", "STRENGTH"],
            "event": "Funcional Boot Camp",
            "image": "funcional_boot_camp.jpg",
            "image_url": commons_file_url("A U.S. Air Force Airman performs a squat exercise.jpg"),
            "media_credit": "Wikimedia Commons, U.S. Air Force, 'A U.S. Air Force Airman performs a squat exercise.jpg', public domain",
            "video_url": "https://www.youtube.com/watch?v=aclHkVaku9U",
            "reference_url": "https://www.nerdfitness.com/blog/strength-training-101-how-to-squat-properly/",
            "requires_subscription": True,
            "plans": ["IZ_B01", "IZ_P01", "IZ_PR01", "IZ_I01"],
            "instructions": html_steps(
                "Ubica los pies al ancho de hombros con puntas ligeramente abiertas.",
                "Inicia llevando cadera hacia atras y rodillas en direccion de los pies.",
                "Mantén el pecho activo y la espalda neutra durante el descenso.",
                "Baja hasta un rango donde puedas mantener talones apoyados y control.",
                "Sube empujando el suelo y extendiendo cadera y rodillas al mismo tiempo.",
            ),
            "recommendations": "Practica primero sin peso. Usa una caja como referencia si pierdes profundidad o equilibrio.",
            "common_mistakes": "Rodillas colapsando hacia adentro, talones levantados, redondear espalda o bajar sin control.",
            "safety_notes": "Evita cargar barra si el patron sin peso aun no es estable.",
        },
        {
            "name": "Press en banco con mancuernas",
            "author": "Carlos Mendez",
            "exercise_type": "machine",
            "difficulty": "intermediate",
            "machine": "Banco plano de press",
            "muscle": "CHEST",
            "categories": ["CHEST", "SHOULDERS", "STRENGTH"],
            "image": "musculacion_personalizada.jpg",
            "image_url": commons_file_url("Bench Press (4517332).jpg"),
            "media_credit": "Wikimedia Commons, U.S. Army, 'Bench Press (4517332).jpg', public domain",
            "video_url": "https://www.youtube.com/watch?v=VmB1G1K7v94",
            "reference_url": "https://www.verywellfit.com/how-to-do-the-dumbbell-bench-press-3498297",
            "requires_subscription": True,
            "plans": ["IZ_PR01", "IZ_I01"],
            "instructions": html_steps(
                "Sientate con las mancuernas sobre los muslos y recuestate manteniendo control.",
                "Apoya pies firmes en el suelo y junta ligeramente las escapulas.",
                "Baja las mancuernas hasta que los codos queden cerca de 45 grados respecto al torso.",
                "Empuja hacia arriba sin chocar las mancuernas y sin perder la posicion de hombros.",
                "Finaliza la serie llevando las mancuernas a los muslos antes de sentarte.",
            ),
            "recommendations": "Usa una carga que permita controlar la bajada. Pide asistencia para pesos altos.",
            "common_mistakes": "Abrir demasiado los codos, arquear en exceso la espalda, rebotar abajo o soltar mancuernas al piso.",
            "safety_notes": "No hagas intentos maximos sin acompanamiento.",
        },
        {
            "name": "Caminadora: inicio seguro para nuevos socios",
            "author": "Sofia Garcia",
            "exercise_type": "machine",
            "difficulty": "beginner",
            "machine": "Caminadora profesional",
            "muscle": "LEGS",
            "categories": ["LEGS", "CARDIO"],
            "image": "hiit.jpg",
            "image_url": commons_file_url("Young man running on treadmill during sports training in a gym.jpg"),
            "media_credit": "Wikimedia Commons, archivo 'Young man running on treadmill during sports training in a gym.jpg'",
            "video_url": "https://www.youtube.com/watch?v=76XnbF5DBFY",
            "reference_url": "https://www.consumerreports.org/health/fitness-exercise/how-to-use-a-treadmill-safely-a1126839260/",
            "requires_subscription": False,
            "instructions": html_steps(
                "Sube con la banda detenida y coloca el clip de seguridad en la ropa.",
                "Empieza caminando entre 3 y 5 minutos para adaptarte a la banda.",
                "Aumenta velocidad o inclinacion de una variable a la vez.",
                "Mantén mirada al frente y evita sujetarte fuerte de los pasamanos.",
                "Reduce velocidad progresivamente antes de bajar.",
            ),
            "recommendations": "Para acondicionamiento general, combina intervalos suaves con caminata continua.",
            "common_mistakes": "Saltar sobre la banda en movimiento, mirar el celular, aumentar velocidad muy rapido o bajar sin detener.",
            "safety_notes": "Usa el clip de seguridad y no entrenes con mareo o dolor agudo.",
        },
        {
            "name": "Respiracion y movilidad inicial para yoga",
            "author": "Sofia Garcia",
            "exercise_type": "group",
            "difficulty": "beginner",
            "muscle": "CORE",
            "categories": ["CORE", "MOBILITY"],
            "event": "Yoga Principiantes",
            "image": "yoga.jpg",
            "image_url": commons_file_url("US Army 52840 Soldiers learn to connect mind, body, soul through breathing.jpg"),
            "media_credit": "Wikimedia Commons, U.S. Army, 'Soldiers learn to connect mind, body, soul through breathing.jpg', public domain",
            "video_url": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
            "reference_url": "https://www.yogajournal.com/practice/beginners/how-to/beginners-guide-pranayama/",
            "requires_subscription": False,
            "instructions": html_steps(
                "Sientate con espalda larga y hombros relajados.",
                "Inhala por nariz expandiendo costillas y abdomen de forma suave.",
                "Exhala lento, permitiendo que el cuerpo reduzca tension.",
                "Moviliza cuello, hombros y columna con movimientos pequenos y controlados.",
                "Mantén cada postura en un rango sin dolor.",
            ),
            "recommendations": "Ideal antes de clases suaves, pilates o sesiones de recuperacion.",
            "common_mistakes": "Forzar amplitud, contener la respiracion o comparar tu rango con el de otros alumnos.",
            "safety_notes": "Si hay mareo, vuelve a respiracion normal y descansa.",
        },
        {
            "name": "Remo sentado: espalda estable y controlada",
            "author": "Carlos Mendez",
            "exercise_type": "machine",
            "difficulty": "intermediate",
            "machine": "Remo sentado en polea baja",
            "muscle": "BACK",
            "categories": ["BACK", "STRENGTH"],
            "image": "musculacion_personalizada.jpg",
            "image_url": commons_file_url("Seated cable row exercise.jpg"),
            "media_credit": "Wikimedia Commons, archivo 'Seated cable row exercise.jpg' si esta disponible; fallback local si no.",
            "video_url": "https://www.youtube.com/watch?v=GZbfZ033f74",
            "reference_url": "https://exrx.net/WeightExercises/BackGeneral/CBStraightBackSeatedRow",
            "requires_subscription": True,
            "plans": ["IZ_P01", "IZ_PR01", "IZ_I01"],
            "instructions": html_steps(
                "Ajusta el asiento para que los pies queden firmes y la espalda pueda mantenerse neutra.",
                "Toma el agarre con hombros bajos y brazos extendidos sin encorvarte.",
                "Inicia la traccion llevando los codos hacia atras y juntando ligeramente las escapulas.",
                "Acerca el agarre al torso sin balancear el cuerpo ni perder la postura.",
                "Regresa lento hasta extender los brazos manteniendo control en la espalda.",
            ),
            "recommendations": "Usa una carga que te permita pausar un instante al final de la traccion.",
            "common_mistakes": "Redondear la espalda, tirar con impulso, elevar hombros o llevar los codos demasiado abiertos.",
            "safety_notes": "Si sientes molestia lumbar, reduce carga y revisa la posicion del tronco.",
        },
        {
            "name": "Extension de piernas: control de cuadriceps",
            "author": "Sofia Garcia",
            "exercise_type": "machine",
            "difficulty": "beginner",
            "machine": "Extension de piernas",
            "muscle": "LEGS",
            "categories": ["LEGS", "STRENGTH"],
            "image": "musculacion_personalizada.jpg",
            "image_url": commons_file_url("Leg extension machine exercise.jpg"),
            "media_credit": "Wikimedia Commons, archivo 'Leg extension machine exercise.jpg' si esta disponible; fallback local si no.",
            "video_url": "https://www.youtube.com/watch?v=YyvSfVjQeL0",
            "reference_url": "https://exrx.net/WeightExercises/Quadriceps/LVLegExtension",
            "requires_subscription": False,
            "instructions": html_steps(
                "Ajusta el respaldo para que la espalda quede apoyada y la rodilla alineada con el eje de la maquina.",
                "Coloca la almohadilla sobre la parte baja de la tibia, no sobre el tobillo directamente.",
                "Extiende las rodillas de forma controlada hasta sentir contraccion en cuadriceps.",
                "Evita bloquear fuerte la articulacion al final del movimiento.",
                "Baja lento hasta la posicion inicial sin dejar caer la carga.",
            ),
            "recommendations": "Ideal como ejercicio tecnico con cargas moderadas, especialmente despues del calentamiento.",
            "common_mistakes": "Usar impulso, despegar la cadera del asiento, cargar demasiado o bloquear rodillas agresivamente.",
            "safety_notes": "Si hay dolor anterior de rodilla, reduce rango y consulta al entrenador.",
        },
    ]

    print("Syncing exercise guides...")
    for guide in guides:
        author_id = employees.get(guide.pop("author"), default_author)
        values = {
            "name": guide["name"],
            "author_id": author_id,
            "exercise_type": guide["exercise_type"],
            "difficulty": guide["difficulty"],
            "equipment_id": False,
            "event_ids": [(5, 0, 0)],
            "category_ids": [(6, 0, [])],
            "primary_muscle_group_id": False,
            "allowed_plan_ids": [(5, 0, 0)],
            "instructions": guide["instructions"],
            "recommendations": guide["recommendations"],
            "common_mistakes": guide["common_mistakes"],
            "safety_notes": guide["safety_notes"],
            "video_url": guide["video_url"],
            "image_1920": image_base64(guide["image"], guide.get("image_url")),
            "requires_subscription": guide.get("requires_subscription", False),
            "state": "published",
            "is_published": True,
        }
        muscle_id = categories.get(guide.get("muscle"))
        if muscle_id:
            values["primary_muscle_group_id"] = muscle_id
        category_ids = [categories[code] for code in guide.get("categories", []) if code in categories]
        if category_ids:
            values["category_ids"] = [(6, 0, category_ids)]
        machine_id = machines.get(guide.get("machine"))
        if machine_id:
            values["equipment_id"] = machine_id
        event_id = events.get(guide.get("event"))
        if event_id:
            values["event_ids"] = [(6, 0, [event_id])]
        plan_ids = [plans[code] for code in guide.get("plans", []) if code in plans]
        if plan_ids:
            values["allowed_plan_ids"] = [(6, 0, plan_ids)]

        _, created = create_or_update(
            uid,
            models,
            "ironzone.exercise.guide",
            [("name", "=", guide["name"])],
            values,
            fields=["id", "name"],
        )
        action = "Created" if created else "Updated"
        print(f"  {action} guide: {guide['name']}")


def run():
    uid, models = connect()
    if not model_exists(uid, models, "ironzone.exercise.guide"):
        print("ironzone.exercise.guide not found. Install ironzone_exercise_guide first.")
        return

    ensure_seed_user_can_manage_guides(uid, models)
    ensure_exercise_categories(uid, models)

    categories = category_ids_by_code(uid, models)
    plans = plan_ids_by_code(uid, models)
    employees = employee_ids_by_name(uid, models)
    events = event_ids_by_name(uid, models)

    machines = ensure_machines(uid, models, categories)
    ensure_guide_benefits(uid, models, plans)
    ensure_guides(uid, models, categories, machines, employees, events, plans)
    print("Done: exercise guide demo data synced.")


if __name__ == "__main__":
    run()
