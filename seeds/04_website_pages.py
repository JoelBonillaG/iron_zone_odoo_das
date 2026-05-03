import os
import base64
from config import connect

def upload_image(models, uid, file_path, name):
    if not os.path.exists(file_path): return None
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return models.execute_kw('iron_zone', uid, 'admin123', 'ir.attachment', 'create', [{
        'name': name, 'datas': data, 'public': True, 'res_model': 'website', 'res_id': 1,
    }])

def run():
    uid, models = connect()
    print("Finalizing UI Perfection: Header, Footer, Shop and Cart Dark Mode...")

    SITE_IMG_PATH = os.path.join(os.path.dirname(__file__), "images", "site")
    hero_path = os.path.join(SITE_IMG_PATH, "hero.jpg")
    hero_att_id = upload_image(models, uid, hero_path, "hero_gym")
    hero_url = f"/web/image/{hero_att_id}" if hero_att_id else "/web/image/res.company/1/logo"

    # GLOBAL CSS ENGINE
    GLOBAL_ASSETS = """
        <style id="iron_zone_engine">
            :root { --iron-orange: #FF5722; --iron-dark: #0b0b0b; --iron-card: #161616; --iron-border: #2a2a2a; }
            body, #wrapwrap, main, #wrap { background-color: var(--iron-dark) !important; color: #e0e0e0 !important; }
            .bg-light, .bg-white, .bg-200, .card, .modal-content, .offcanvas { background-color: var(--iron-card) !important; color: #e0e0e0 !important; border-color: var(--iron-border) !important; }
            header, #top, .navbar, .o_header_standard, .o_header_affix { background-color: #000 !important; border-bottom: 1px solid var(--iron-border) !important; }
            header .nav-link { color: #aaa !important; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }
            header .nav-link:hover, header .nav-link.active { color: var(--iron-orange) !important; }
            header .navbar-brand { display: flex !important; align-items: center !important; }
            header .navbar-brand img, header .navbar-brand span { display: block !important; visibility: visible !important; max-height: 50px !important; width: auto !important; filter: brightness(0) invert(1) !important; }
            header .fa, header .oi { color: white !important; }
            .my_cart_quantity { background-color: var(--iron-orange) !important; border: 1px solid white !important; }
            .oe_product_cart { background-color: var(--iron-card) !important; border: 1px solid var(--iron-border) !important; border-radius: 15px !important; overflow: hidden; }
            .oe_product_image { background-color: #1a1a1a !important; }
            .o_wsale_product_information { background: transparent !important; }
            .o_wsale_products_item_title a { color: white !important; font-weight: 700 !important; }
            .table { color: #e0e0e0 !important; }
            .table thead th { border-bottom: 2px solid var(--iron-border) !important; color: var(--iron-orange) !important; }
            .td-product_name strong { color: white !important; }
            #cart_products, .js_cart_summary { background-color: var(--iron-card) !important; border: 1px solid var(--iron-border) !important; border-radius: 15px !important; padding: 20px !important; }
            .input-group .form-control { background-color: #222 !important; color: white !important; border: 1px solid var(--iron-border) !important; }
            .s_share a { background: #222 !important; color: white !important; border: 1px solid #333 !important; border-radius: 50%; width: 40px; height: 40px; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; }
            .s_share a:hover { border-color: var(--iron-orange) !important; color: var(--iron-orange) !important; }
            .btn-primary, .btn_cta, .btn-secondary { background-color: var(--iron-orange) !important; border: none !important; border-radius: 50px !important; font-weight: 800 !important; color: white !important; }
            .text-iron { color: var(--iron-orange) !important; }
            .avatar-circle { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white !important; }
        </style>
        <script id="iron_zone_js">
            document.addEventListener('DOMContentLoaded', function() {
                let interval;
                document.body.addEventListener('mousedown', function(e) {
                    if (e.target.closest('.js_add_cart_json')) {
                        const btn = e.target.closest('.js_add_cart_json');
                        if (btn.querySelector('.fa-plus') || btn.querySelector('.fa-minus')) {
                            interval = setInterval(() => btn.click(), 150);
                        }
                    }
                });
                document.body.addEventListener('mouseup', () => clearInterval(interval));
            });
        </script>
    """

    FOOTER_ARCH = """
        <data inherit_id="website.layout" name="Iron Zone Footer" active="True">
            <xpath expr="//div[@id='footer']" position="replace">
                <div id="footer" class="oe_structure oe_structure_solo bg-black text-white pt64 pb32" t-ignore="true" t-if="not no_footer">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-5 mb-5">
                                <h3 class="text-iron fw-bold mb-4">IRON ZONE</h3>
                                <p class="text-white-50 lh-lg" style="max-width: 400px;">El templo del fitness en Ambato. Equipamiento de élite, comunidad imparable.</p>
                                <div class="mt-5 small text-muted">
                                    <p class="mb-1">© 2026 <span t-field="res_company.name"/></p>
                                    <p>Diseñado con ❤️ por el equipo de ingeniería.</p>
                                </div>
                            </div>
                            <div class="col-lg-3 mb-5">
                                <h6 class="text-white fw-bold text-uppercase mb-4" style="letter-spacing: 2px;">Explorar</h6>
                                <ul class="list-unstyled">
                                    <li><a href="/" class="text-white-50 text-decoration-none">Inicio</a></li>
                                    <li><a href="/shop" class="text-white-50 text-decoration-none">Tienda</a></li>
                                    <li><a href="/aboutus" class="text-white-50 text-decoration-none">Nosotros</a></li>
                                </ul>
                            </div>
                            <div class="col-lg-4">
                                <h6 class="text-white fw-bold text-uppercase mb-4" style="letter-spacing: 2px;">Contáctanos</h6>
                                <ul class="list-unstyled text-white-50">
                                    <li class="mb-3 d-flex align-items-start"><i class="fa fa-map-marker text-iron mt-1 me-3"/><span><span t-field="res_company.street"/>, <span t-field="res_company.city"/></span></li>
                                    <li class="mb-3 d-flex align-items-center"><i class="fa fa-envelope text-iron me-3"/><span t-field="res_company.email"/></li>
                                    <li class="mb-3 d-flex align-items-center"><i class="fa fa-phone text-iron me-3"/><span t-field="res_company.phone"/></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </xpath>
        </data>
    """

    SHARE_ARCH = """
        <data inherit_id="website_sale.product" active="True" name="Iron Share Buttons">
            <xpath expr="//div[@id='o_product_terms_and_share']" position="replace">
                <div id="o_product_terms_and_share" class="mt-4 pt-4 border-top">
                    <div class="s_share text-start">
                        <h6 class="text-white-50 mb-3 small fw-bold text-uppercase">Compartir Producto:</h6>
                        <a t-attf-href="https://wa.me/?text={{product.name}}" target="_blank" class="s_share_whatsapp"><i class="fa fa-whatsapp"/></a>
                        <a t-attf-href="mailto:?subject={{product.name}}" class="s_share_email"><i class="fa fa-envelope"/></a>
                    </div>
                </div>
            </xpath>
        </data>
    """

    try:
        layout_ids = models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'search', [[('key', '=', 'website.layout')]])
        if layout_ids:
            css_key = "iron_zone.global_assets"
            arch_css = f"""<data inherit_id="website.layout" name="Iron Assets"><xpath expr="//head" position="inside">{GLOBAL_ASSETS}</xpath></data>"""
            css_ids = models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'search', [[('key', '=', css_key)]])
            if css_ids: models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'write', [css_ids, {"arch": arch_css}])
            else: models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'create', [{'name': 'Iron Assets', 'key': css_key, 'type': 'qweb', 'arch': arch_css, 'inherit_id': layout_ids[0]}])
        
        prod_share_ids = models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'search', [[('key', '=', 'website_sale.product_share_buttons')]])
        if prod_share_ids: models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'write', [prod_share_ids, {"arch": SHARE_ARCH}])
        
        models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'write', [models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'search', [[('key', '=', 'website.header_text_element')]]), {"arch": "<t/>"}])
        models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'write', [models.execute_kw('iron_zone', uid, 'admin123', 'ir.ui.view', 'search', [[('key', '=', 'website.footer_custom')]]), {"arch": FOOTER_ARCH}])
        
        print("Done: UI Perfected with Dark Mode Shop/Cart, Logo Fixed, and Long-press active.")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__": run()
