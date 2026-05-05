{
    "name": "Training Plans",
    "version": "1.0",
    "category": "Fitness/Gym",
    "summary": "Manage training plans and workouts for gym members",
    "author": "Iron Zone",
    "depends": ["base", "hr", "event", "calendar"],
    "data": [
        "views/training_plan_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
