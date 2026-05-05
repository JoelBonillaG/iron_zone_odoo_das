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
    "depends": ["base", "hr", "event", "calendar"],
    "data": [
        "views/training_plan_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
