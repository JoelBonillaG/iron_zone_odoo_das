{
    "name": "Training Plans",
    "version": "1.0",
    "category": "Fitness/Gym",
    "summary": "Manage training plans and workouts for gym members",
    "author": "Iron Zone",
    "depends": ["base", "hr", "event", "calendar", "website", "portal"],
    "data": [
        "views/training_plan_views.xml",
        "views/employee_event_portal_templates.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
