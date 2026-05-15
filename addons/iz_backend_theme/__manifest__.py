{
    "name": "IZ Backend Theme",
    "version": "18.0.1.0.0",
    "summary": "Modern backend theme for Iron Zone",
    "category": "Hidden",
    "author": "Iron Zone",
    "license": "LGPL-3",
    "depends": [
        "web",
        "contacts",
        "sale_management",
        "account",
        "website",
        "mass_mailing",
        "stock",
        "maintenance",
        "hr",
        "spreadsheet_dashboard",
        "event",
        "calendar"
    ],
    "data": [
        "data/security_groups.xml",
        "data/menu_access.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "iz_backend_theme/static/src/scss/backend_theme.scss",
            "iz_backend_theme/static/src/xml/apps_menu.xml",
        ],
    },
    "installable": True,
    "application": False,
}
