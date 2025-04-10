from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Event(models.Model):
    _name = 'fasticket.event'
    _description = 'Descripcion de event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre del Evento", required=True, tracking=True)
    description = fields.Text("Descripcion del Evento", tracking=True)
    # Campos relacionados con el evento
    date = fields.Date(string="Fecha del Evento", required=True, tracking=True)
    location = fields.Char(string="Ubicacion del Evento", required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado')
    ], string="Estado", default='draft', tracking=True)

    # Campos relacionados con la venta de entradas
    ticket_ids = fields.One2many('fasticket.ticket', 'event_id', string="Entradas")
    
    # Campo para vinculación con evento de Odoo
    odoo_event_id = fields.Many2one('event.event', string="Evento Odoo", tracking=True)
    
    # Método para validar la fecha del evento
    @api.constrains('date')
    def _check_event_date(self):
        for record in self:
            if record.date < datetime.now().date():
                raise ValidationError("La fecha del evento no puede ser anterior a la fecha actual.")
                
    # Método para validar el estado del evento
    @api.constrains('state')
    def _check_event_state(self):
        for record in self:
            if record.state not in ['draft', 'confirmed', 'canceled']:
                raise ValidationError("El estado del evento no es válido.")
                
    # Acción para vincular con evento Odoo
    def action_link_to_odoo_event(self):
        self.ensure_one()
        return {
            'name': 'Vincular con Evento Odoo',
            'type': 'ir.actions.act_window',
            'res_model': 'fasticket.event.link.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_event_id': self.id},
        }
    
    # Acción para ver el evento vinculado
    def action_view_odoo_event(self):
        self.ensure_one()
        if not self.odoo_event_id:
            return self.action_link_to_odoo_event()
        
        return {
            'name': 'Evento Odoo',
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
            'res_id': self.odoo_event_id.id,
            'view_mode': 'form',
        }
