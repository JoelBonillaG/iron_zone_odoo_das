from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _iz_configure_site(self):
        website = self.search([], limit=1)
        if not website:
            return

        spanish = self.env["res.lang"].with_context(active_test=False).search(
            [("code", "in", ["es_EC", "es_419", "es_ES"])],
            limit=1,
        )
        if spanish and not spanish.active:
            spanish.active = True

        values = {
            "auto_redirect_lang": False,
            "homepage_url": False,
            "name": "Iron Zone",
        }
        if spanish:
            values["default_lang_id"] = spanish.id
            values["language_ids"] = [(6, 0, [spanish.id])]
        website.write(values)

        self._iz_publish_page(website, "website.homepage", "/")
        self._iz_publish_page(website, "website.aboutus", "/aboutus")
        self._iz_publish_page(website, "website.contactus", "/contactus")

        self._iz_configure_menus(website, spanish)

    @api.model
    def _iz_publish_page(self, website, view_xmlid, url):
        view = self.env.ref(view_xmlid, raise_if_not_found=False)
        if not view:
            return

        page_model = self.env["website.page"]
        pages = page_model.search([("url", "=", url)])
        values = {
            "view_id": view.id,
            "website_id": website.id,
            "is_published": True,
            "header_visible": True,
            "footer_visible": True,
        }
        if pages:
            pages.write(values)
        else:
            page_model.create(dict(values, url=url))

    @api.model
    def _iz_configure_menus(self, website, spanish=False):
        menu_model = self.env["website.menu"]
        roots = website.menu_id
        if not roots:
            roots = menu_model.create({
                "name": "Menu principal",
                "url": "/",
                "website_id": website.id,
                "sequence": 0,
            })

        labels = {
            "/": ("Inicio", 10),
            "/shop": ("Tienda", 20),
            "/event": ("Eventos", 30),
            "/aboutus": ("Nosotros", 40),
            "/exercise-guides": ("Guia de ejercicios", 50),
            "/contactus": ("Contacto", 60),
        }

        for root in roots:
            root.name = "Menu principal"
            if spanish:
                root.with_context(lang=spanish.code).name = "Menu principal"
            for url, (label, sequence) in labels.items():
                matching_menus = menu_model.search(
                    [("parent_id", "=", root.id), ("url", "=", url)],
                    order="sequence, id",
                )
                menu = matching_menus[:1]
                duplicates = matching_menus - menu
                if duplicates:
                    duplicates.unlink()
                if menu:
                    menu.write({"name": label, "sequence": sequence})
                else:
                    menu = menu_model.create({
                        "name": label,
                        "url": url,
                        "parent_id": root.id,
                        "website_id": root.website_id.id,
                        "sequence": sequence,
                    })
                if spanish:
                    menu.with_context(lang=spanish.code).name = label
