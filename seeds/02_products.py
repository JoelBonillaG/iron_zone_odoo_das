import base64
import os
from config import DB, PASSWORD, connect, create, search_read


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "search_read",
        [domain],
        {"fields": fields or ["id"], "limit": 1},
    )
    return records[0] if records else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def get_model_fields(uid, models, model):
    return models.execute_kw(DB, uid, PASSWORD, model, "fields_get", [], {"attributes": ["type"]})


def unpublish_duplicate_templates(uid, models, product_names, product_fields):
    publish_field = "website_published" if "website_published" in product_fields else "is_published"

    for name in product_names:
        templates = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.template",
            "search_read",
            [[("name", "=", name)]],
            {"fields": ["id", "name", publish_field], "order": "id asc"},
        )
        if len(templates) <= 1:
            continue

        canonical = templates[0]
        duplicate_ids = [record["id"] for record in templates[1:]]
        if duplicate_ids:
            models.execute_kw(
                DB,
                uid,
                PASSWORD,
                "product.template",
                "write",
                [duplicate_ids, {publish_field: False}],
            )
            print(
                f"  Unpublished {len(duplicate_ids)} duplicate(s) for '{name}'. "
                f"Canonical template kept: {canonical['id']}"
            )


def run():
    uid, models = connect()
    product_fields = get_model_fields(uid, models, "product.template")
    
    # Path for images
    IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images", "products")
    LOGO_PATH  = os.path.join(os.path.dirname(__file__), "IronZone.png")

    def get_image(filename):
        # Try original filename (e.g. .png)
        path = os.path.join(IMAGE_PATH, filename)
        if not os.path.exists(path):
            # Try .svg version
            svg_filename = filename.rsplit('.', 1)[0] + '.svg'
            path = os.path.join(IMAGE_PATH, svg_filename)
        
        if not os.path.exists(path):
            path = LOGO_PATH # Final fallback to logo
        
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    print("Syncing eCommerce categories...")
    categ_memberships, _ = create_or_update(uid, models, "product.public.category", [("name", "=", "Membresías")], {"name": "Membresías"})
    categ_classes, _ = create_or_update(uid, models, "product.public.category", [("name", "=", "Clases")], {"name": "Clases"})
    categ_equipment, _ = create_or_update(uid, models, "product.public.category", [("name", "=", "Equipamiento")], {"name": "Equipamiento"})
    categ_suppliments, _ = create_or_update(uid, models, "product.public.category", [("name", "=", "Suplementos")], {"name": "Suplementos"})

    # Odoo 17/18 convention:
    # - type="consu" + is_storable=True  => Storable Product (Stockable)
    # - type="consu" + is_storable=False => Consumable Product
    # - type="service"                   => Service
    PRODUCTS = [
        {"name": "Membresía Mensual",          "list_price": 35.00,  "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 1 mes", "public_categ_ids": [(6, 0, [categ_memberships])], "_img": "membership_basic.png"},
        {"name": "Membresía Trimestral",       "list_price": 90.00,  "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 3 meses", "public_categ_ids": [(6, 0, [categ_memberships])], "_img": "membership_trim.png"},
        {"name": "Membresía Anual",            "list_price": 300.00, "standard_price": 0.0,  "type": "service", "description_sale": "Acceso ilimitado por 12 meses", "public_categ_ids": [(6, 0, [categ_memberships])], "_img": "membership_gold.png"},
        {"name": "Clase de Spinning",          "list_price": 8.00,   "standard_price": 2.0,  "type": "service", "description_sale": "Clase grupal de spinning 60 mins", "public_categ_ids": [(6, 0, [categ_classes])], "_img": "spinning.png"},
        {"name": "Clase de CrossFit",          "list_price": 10.00,  "standard_price": 3.0,  "type": "service", "description_sale": "Clase grupal de CrossFit 60 mins", "public_categ_ids": [(6, 0, [categ_classes])], "_img": "crossfit.png"},
        {"name": "Entrenamiento Personal",     "list_price": 25.00,  "standard_price": 15.0, "type": "service", "description_sale": "Sesión personalizada 1v1", "public_categ_ids": [(6, 0, [categ_classes])], "_img": "personal_trainer.png"},
        {"name": "Guantes de Boxeo",           "list_price": 45.00,  "standard_price": 20.0, "type": "consu", "is_storable": True, "description_sale": "Guantes profesionales", "public_categ_ids": [(6, 0, [categ_equipment])], "_stock": 15, "_img": "gloves.png"},
        {"name": "Botella Proteína Whey 1kg",  "list_price": 38.00,  "standard_price": 25.0, "type": "consu", "is_storable": True, "description_sale": "Proteína whey, 30 porciones", "public_categ_ids": [(6, 0, [categ_suppliments])], "_stock": 20, "_img": "protein.png"},
        {"name": "Cuerda para Saltar",         "list_price": 12.00,  "standard_price": 4.0,  "type": "consu", "is_storable": True, "description_sale": "Cuerda de velocidad ajustable", "public_categ_ids": [(6, 0, [categ_equipment])], "_stock": 50, "_img": "rope.png"},
        {"name": "Agua Mineral",               "list_price": 1.00,   "standard_price": 0.5,  "type": "consu", "is_storable": False, "description_sale": "Agua mineral sin gas", "public_categ_ids": [(6, 0, [categ_suppliments])], "_img": "water.png"},
        {"name": "Plan Nutrición + Gym",       "list_price": 75.00,  "standard_price": 10.0, "type": "service", "description_sale": "Plan nutricional + Mensualidad", "public_categ_ids": [(6, 0, [categ_memberships])], "_img": "combo_plan.png"},
    ]

    PRODUCT_CONTENT = {
        "Membresía Mensual": {
            "description_sale": "Acceso ilimitado por 1 mes a zona de fuerza, cardio y clases base.",
            "description_ecommerce": """
                <p>Ideal para clientes que quieren comenzar con flexibilidad y acceso completo al club.</p>
                <ul>
                    <li>Ingreso libre durante el horario habitual.</li>
                    <li>Acceso a musculación, cardio y zonas funcionales.</li>
                    <li>Perfecta para evaluar rutina y constancia durante el primer mes.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Una entrada sólida al ecosistema Iron Zone</h3>
                        <p>Esta membresía está diseñada para quienes quieren entrenar con libertad, conocer el ambiente del gimnasio y construir hábito con una inversión inicial contenida.</p>
                    </div>
                </section>
            """,
        },
        "Membresía Trimestral": {
            "description_sale": "Acceso ilimitado por 3 meses con mejor relación costo / permanencia.",
            "description_ecommerce": """
                <p>Recomendada para clientes que ya decidieron comprometerse con una etapa real de progreso físico.</p>
                <ul>
                    <li>Mejor costo promedio mensual.</li>
                    <li>Tiempo suficiente para medir avances tangibles.</li>
                    <li>Buena opción para combinar con nutrición o clases guiadas.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Más consistencia, mejor retorno</h3>
                        <p>Tres meses permiten estructurar rutina, alimentación y seguimiento con un horizonte más realista para clientes que quieren resultados sostenibles.</p>
                    </div>
                </section>
            """,
        },
        "Membresía Anual": {
            "description_sale": "Acceso ilimitado por 12 meses para clientes que priorizan continuidad.",
            "description_ecommerce": """
                <p>El plan más conveniente para quienes entrenan con visión de largo plazo y quieren estabilidad total.</p>
                <ul>
                    <li>Doce meses de acceso al ecosistema del gimnasio.</li>
                    <li>Ideal para procesos de recomposición, fuerza o pérdida de grasa.</li>
                    <li>Base ideal para clientes recurrentes y comunidad fiel.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>La opción para clientes comprometidos</h3>
                        <p>Una membresía anual permite trabajar hábitos, rendimiento y objetivos con continuidad, reduciendo la fricción de renovación y reforzando la permanencia.</p>
                    </div>
                </section>
            """,
        },
        "Clase de Spinning": {
            "description_sale": "Sesión grupal de spinning de 60 minutos guiada por instructor.",
            "description_ecommerce": """
                <p>Trabajo cardiovascular dinámico para clientes que buscan intensidad, ritmo y motivación grupal.</p>
                <ul>
                    <li>Duración aproximada de 60 minutos.</li>
                    <li>Excelente para resistencia y quema calórica.</li>
                    <li>Requiere reserva previa según disponibilidad.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Energía, ritmo y constancia</h3>
                        <p>Spinning es una clase con alto componente cardiovascular, ideal para complementar procesos de acondicionamiento y mejorar adherencia mediante sesiones grupales.</p>
                    </div>
                </section>
            """,
        },
        "Clase de CrossFit": {
            "description_sale": "Clase grupal de CrossFit de 60 minutos con trabajo funcional.",
            "description_ecommerce": """
                <p>Orientada a clientes que buscan fuerza, capacidad cardiovascular y variedad de estímulos en una sola sesión.</p>
                <ul>
                    <li>Entrenamiento funcional de alta intensidad.</li>
                    <li>Escalable según nivel del cliente.</li>
                    <li>Ideal para quienes valoran comunidad y reto físico.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Rendimiento integral</h3>
                        <p>CrossFit combina técnica, potencia y acondicionamiento general. Es una categoría con alto valor percibido y buena retención cuando se gestiona bien la experiencia del alumno.</p>
                    </div>
                </section>
            """,
        },
        "Entrenamiento Personal": {
            "description_sale": "Sesión 1 a 1 con planificación enfocada en objetivos concretos.",
            "description_ecommerce": """
                <p>Servicio premium para clientes que necesitan guía individual, seguimiento técnico y progresión más precisa.</p>
                <ul>
                    <li>Sesión personalizada con entrenador.</li>
                    <li>Ideal para principiantes, readaptación o metas específicas.</li>
                    <li>Mayor control sobre técnica, volumen y progresión.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Atención individual de alto valor</h3>
                        <p>Este servicio fortalece la propuesta del gimnasio para clientes que quieren acompañamiento experto, foco y una experiencia más exclusiva.</p>
                    </div>
                </section>
            """,
        },
        "Guantes de Boxeo": {
            "description_sale": "Guantes de boxeo para entrenamiento técnico, saco y acondicionamiento.",
            "description_ecommerce": """
                <p>Accesorio esencial para clientes que entrenan box, cardio combat o sesiones funcionales con golpeo.</p>
                <ul>
                    <li>Uso recomendado en prácticas recreativas y entrenamiento guiado.</li>
                    <li>Buena opción de upsell para clases o trabajo en saco.</li>
                    <li>La disponibilidad depende del inventario del club.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Equipamiento útil y fácil de vender</h3>
                        <p>Un producto físico con demanda natural cuando el gimnasio ofrece entrenamientos funcionales o de box. En la web conviene dejar claro su contexto de uso y la disponibilidad por stock.</p>
                    </div>
                </section>
            """,
        },
        "Botella Proteína Whey 1kg": {
            "description_sale": "Proteína whey de 1 kg con 30 porciones para soporte nutricional.",
            "description_ecommerce": """
                <p>Suplemento orientado a clientes que buscan complementar recuperación y consumo proteico diario.</p>
                <ul>
                    <li>Presentación de 1 kg.</li>
                    <li>Aproximadamente 30 porciones.</li>
                    <li>Producto físico sujeto a stock real.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Complemento comercial del servicio principal</h3>
                        <p>Los suplementos fortalecen el ticket promedio del gimnasio cuando se presentan con lenguaje claro, responsable y alineado al objetivo del cliente.</p>
                    </div>
                </section>
            """,
        },
        "Cuerda para Saltar": {
            "description_sale": "Cuerda de velocidad ajustable para trabajo cardiovascular y coordinación.",
            "description_ecommerce": """
                <p>Accesorio versátil para clientes que entrenan dentro y fuera del gimnasio.</p>
                <ul>
                    <li>Útil para calentamientos y cardio de alta eficiencia.</li>
                    <li>Fácil de incorporar en rutinas funcionales.</li>
                    <li>Producto físico gestionado con inventario real.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Accesorio práctico, portable y rentable</h3>
                        <p>Una cuerda para saltar es simple, útil y fácil de vender tanto a clientes nuevos como a quienes quieren reforzar sus rutinas fuera del club.</p>
                    </div>
                </section>
            """,
        },
        "Agua Mineral": {
            "description_sale": "Bebida rápida para hidratación inmediata antes, durante o después del entrenamiento.",
            "description_ecommerce": """
                <p>Producto de alta rotación pensado para conveniencia del cliente dentro del ecosistema del gimnasio.</p>
                <ul>
                    <li>Compra rápida y directa.</li>
                    <li>Ideal para acompañar clases o sesiones largas.</li>
                    <li>Consumible no almacenado como producto físico estricto.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Venta de apoyo con rotación constante</h3>
                        <p>Aunque es un producto simple, aporta conveniencia al cliente y puede complementar compras mayores dentro del catálogo del gimnasio.</p>
                    </div>
                </section>
            """,
        },
        "Plan Nutrición + Gym": {
            "description_sale": "Paquete combinado de asesoría nutricional y acceso al gimnasio.",
            "description_ecommerce": """
                <p>Propuesta integral para clientes que quieren acompañar entrenamiento con una guía alimentaria básica.</p>
                <ul>
                    <li>Combina membresía con componente de nutrición.</li>
                    <li>Mejora el valor percibido del servicio.</li>
                    <li>Ideal para campañas y ofertas de captación.</li>
                </ul>
            """,
            "website_description": """
                <section class="s_text_block">
                    <div class="container">
                        <h3>Oferta híbrida para diferenciar el gimnasio</h3>
                        <p>Este paquete ayuda a vender transformación y acompañamiento, no solo acceso al espacio. Es una oferta especialmente útil para adquisición de nuevos clientes.</p>
                    </div>
                </section>
            """,
        },
    }
    
    try:
        stock_locations = search_read(uid, models, "stock.location", [("usage", "=", "internal")], ["id"])
        stock_location_id = stock_locations[0]["id"] if stock_locations else False
    except Exception as e:
        print("Warning: stock.location error", e)
        stock_location_id = False

    created_count = 0
    updated_count = 0
    for p in PRODUCTS:
        stock_to_add = p.pop("_stock", None)
        img_file     = p.pop("_img", None)
        
        p["sale_ok"]     = True
        p["purchase_ok"] = True
        p["is_published"] = True
        if "website_published" in product_fields:
            p["website_published"] = True
        p.update(PRODUCT_CONTENT.get(p["name"], {}))

        if p.get("is_storable"):
            # Keep website stock strict for physical goods when website_sale_stock is installed.
            if "allow_out_of_stock_order" in product_fields:
                p["allow_out_of_stock_order"] = False
            if "available_threshold" in product_fields:
                p["available_threshold"] = 3
            if "out_of_stock_message" in product_fields:
                p["out_of_stock_message"] = "Producto temporalmente agotado. Revisa disponibilidad en recepcion."

        # Add image
        if img_file:
            p["image_1920"] = get_image(img_file)

        template_id, created = create_or_update(
            uid,
            models,
            "product.template",
            [("name", "=", p["name"])],
            p,
            fields=["id", "name"],
        )

        if stock_to_add and stock_location_id and p.get("is_storable"):
            products = search_read(uid, models, "product.product", [("product_tmpl_id", "=", template_id)], ["id"])
            if products:
                product_id = products[0]["id"]
                quant = search_one(
                    uid,
                    models,
                    "stock.quant",
                    [("product_id", "=", product_id), ("location_id", "=", stock_location_id)],
                    fields=["id"],
                )
                quant_values = {
                    "product_id": product_id,
                    "location_id": stock_location_id,
                    "inventory_quantity": stock_to_add,
                }
                if quant:
                    models.execute_kw(DB, uid, PASSWORD, "stock.quant", "write", [[quant["id"]], quant_values])
                    quant_id = quant["id"]
                else:
                    quant_id = create(uid, models, "stock.quant", quant_values)
                if quant_id:
                    try:
                        # Odoo's action_apply_inventory returning None crashes XML-RPC unless allow_none=True
                        models.execute_kw(DB, uid, PASSWORD, "stock.quant", "action_apply_inventory", [[quant_id]])
                    except Exception as e:
                        if "cannot marshal None" not in str(e):
                            raise

        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        print(f"  {action} product/service: {p['name']} (Type: {p['type']}, Cost: {p['standard_price']})")

    unpublish_duplicate_templates(uid, models, [p["name"] for p in PRODUCTS], product_fields)
    print(f"Done: {created_count} created, {updated_count} updated.")

if __name__ == "__main__":
    run()
