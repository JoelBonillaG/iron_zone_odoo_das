{
    'name': 'Gestión de Tareas Iron Zone',
    'version': '1.0',
    'summary': 'Módulo para la gestión y asignación de tareas con dashboard',
    'description': """
        Módulo para crear, asignar, dar seguimiento a tareas.
        Incluye vistas Kanban, Lista, Formulario, Calendario, y Tablero de reportes (Dashboard).
    """,
    'category': 'Productivity',
    'author': 'Iron Zone',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
