from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Event(models.Model):
    _name = 'fasticket.event'
    _description = 'Descripcion de event'

    name = fields.Char("Nombre del Evento", required=True)
    description = fields.Text("Descripcion del Evento")
    # Campos relacionados con el evento
    date = fields.Date(string="Fecha del Evento", required=True)
    location = fields.Char(string="Ubicacion del Evento", required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado')
    ], string="Estado", default='draft')

    # Campos relacionados con la venta de entradas
    ticket_ids = fields.One2many('fasticket.ticket', 'event_id', string="Entradas")
    
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
