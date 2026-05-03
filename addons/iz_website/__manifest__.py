{
    "name": "IZ Website",
    "version": "18.0.1.0.0",
    "summary": "Website customization for the Iron Zone project",
    "category": "Website",
    "author": "Iron Zone",
    "license": "LGPL-3",
    "depends": ["website", "website_sale"],
    "data": [
        "views/website_layout.xml",
        "views/website_footer.xml",
        "views/website_pages.xml",
        "views/website_sale_views.xml",
        "views/website_contact_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "iz_website/static/src/css/iron_zone.css",
        ],
    },
    "installable": True,
    "application": False,
}
