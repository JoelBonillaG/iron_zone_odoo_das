from odoo import models, fields, api

class Task(models.Model):
    _name = 'iz_tasks.task'
    _description = 'Tarea'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_deadline asc, priority desc, id desc'

    name = fields.Char(string='Tarea', required=True, tracking=True)
    description = fields.Html(string='Descripción de la Tarea')
    
    user_id = fields.Many2one(
        'res.users', 
        string='Responsable', 
        default=lambda self: self.env.user,
        tracking=True
    )
    
    date_deadline = fields.Date(string='Fecha Límite', tracking=True)
    
    state = fields.Selection([
        ('creada', 'Creada'),
        ('en_proceso', 'En Proceso'),
        ('finalizada', 'Finalizada')
    ], string='Estado', default='creada', tracking=True, group_expand='_expand_states')
    
    priority = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ], string='Prioridad', default='media', tracking=True)

    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
