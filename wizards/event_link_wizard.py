from odoo import models, fields, api

class EventLinkWizard(models.TransientModel):
    _name = 'fasticket.event.link.wizard'
    _description = 'Asistente para vincular con eventos de Odoo'
    
    event_id = fields.Many2one('fasticket.event', string="Evento FasTicket", required=True)
    odoo_event_id = fields.Many2one('event.event', string="Evento Odoo")
    create_new = fields.Boolean("Crear nuevo evento en Odoo")
    create_tickets = fields.Boolean("Crear tickets en el evento de Odoo", default=True)
    
    @api.onchange('event_id')
    def _onchange_event_id(self):
        # Sugerir un evento existente con nombre similar
        if self.event_id:
            similar_event = self.env['event.event'].search([
                ('name', 'ilike', self.event_id.name)
            ], limit=1)
            if similar_event:
                self.odoo_event_id = similar_event.id
    
    def action_link(self):
        self.ensure_one()
        if self.create_new:
            # Crear nuevo evento en Odoo
            odoo_event = self.env['event.event'].create({
                'name': self.event_id.name,
                'date_begin': self.event_id.date,
                'date_end': self.event_id.date,
                'description': self.event_id.description,
                'address_id': self.env.company.partner_id.id,
                'auto_confirm': True,
                'website_published': True,
            })
            self.odoo_event_id = odoo_event.id
        
        # Vincular eventos
        self.event_id.write({'odoo_event_id': self.odoo_event_id.id})
        
        # Crear tickets correspondientes si se solicita
        if self.create_tickets:
            for ticket in self.event_id.ticket_ids:
                # Verificar si ya existe un ticket con el mismo nombre
                existing_tickets = self.env['event.event.ticket'].search([
                    ('event_id', '=', self.odoo_event_id.id),
                    ('name', '=', ticket.name)
                ])
                
                if existing_tickets:
                    # Actualizar ticket existente
                    existing_tickets[0].write({
                        'price': ticket.price,
                        'seats_max': ticket.quantity,
                    })
                    ticket.odoo_event_ticket_id = existing_tickets[0].id
                else:
                    # Crear nuevo ticket
                    odoo_ticket = self.env['event.event.ticket'].create({
                        'name': ticket.name,
                        'event_id': self.odoo_event_id.id,
                        'price': ticket.price,
                        'seats_max': ticket.quantity,
                    })
                    ticket.odoo_event_ticket_id = odoo_ticket.id
        
        return {'type': 'ir.actions.act_window_close'}