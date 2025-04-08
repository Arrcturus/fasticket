from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Ticket(models.Model):
    _name = 'fasticket.ticket'
    _description = 'Descripcion de ticket'

    name = fields.Char("Nombre del Ticket")
    event_id = fields.Many2one('fasticket.event', string="Evento", required=True)
    price = fields.Float("Precio del Ticket", required=True)
    quantity = fields.Integer("Cantidad de Tickets", required=True)
    # Campos relacionados con la venta de entradas
    left = fields.Integer("Cantidad de Tickets Disponibles", compute='_compute_left', store=True)
    sold = fields.Integer("Cantidad de Tickets Vendidos", default=0)
    is_sold_out = fields.Boolean("Agotado", compute='_compute_left', store=True)

    # Campo computado para tickets disponibles
    @api.depends('quantity', 'sold')
    def _compute_left(self):
        for record in self:
            record.left = record.quantity - record.sold
            record.is_sold_out = record.left <= 0

    # Método para validar la cantidad de entradas
    @api.constrains('quantity')
    def _check_ticket_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("La cantidad de entradas debe ser mayor a cero.")

    # Método para validar el precio de las entradas
    @api.constrains('price')
    def _check_ticket_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError("El precio de las entradas debe ser mayor a cero.")

    # Método para validar las entradas vendidas
    @api.constrains('sold')
    def _check_ticket_sold(self):
        for record in self:
            if record.sold < 0 or record.sold > record.quantity:
                raise ValidationError("La cantidad de entradas vendidas no puede ser negativa ni mayor que la cantidad total.")

