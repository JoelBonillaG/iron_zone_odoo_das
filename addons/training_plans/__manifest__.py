{
    "name": "Training Plans",
    "version": "1.0",
    "category": "Fitness/Gym",
    "summary": "Manage training plans and workouts for gym members",
    "license": "LGPL-3",
    "description": """
Training Plans
==============

Provides an employee-focused view for Iron Zone instructors to manage their
assigned events, review registrations, and update event status from the
Human Resources menu.
""",
    "author": "Iron Zone",
    "depends": ["base", "hr", "event", "calendar", "website", "portal"],
    "data": [
        "security/training_plan_security.xml",
        "views/training_plan_views.xml",
        "views/employee_event_portal_templates.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
