from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Ticket(models.Model):
    _name = 'fasticket.ticket'
    _description = 'Descripcion de ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre del Ticket", tracking=True)
    event_id = fields.Many2one('fasticket.event', string="Evento", required=True)
    price = fields.Float("Precio del Ticket", required=True, tracking=True)
    quantity = fields.Integer("Cantidad de Tickets", required=True, tracking=True)
    # Campos relacionados con la venta de entradas
    left = fields.Integer("Cantidad de Tickets Disponibles", compute='_compute_left', store=True)
    sold = fields.Integer("Cantidad de Tickets Vendidos", default=0, tracking=True)
    is_sold_out = fields.Boolean("Agotado", compute='_compute_left', store=True)
    
    # Campo para vincular con producto
    product_id = fields.Many2one('product.product', string="Producto asociado", tracking=True)
    # Campo para evento odoo (para tickets relacionados con eventos de odoo)
    odoo_event_ticket_id = fields.Many2one('event.event.ticket', string="Ticket de Evento Odoo", tracking=True)
    event_odoo_id = fields.Many2one(
        'event.event', 
        string="Evento Odoo Relacionado", 
        related='event_id.odoo_event_id', 
        store=True
    )

    # Campo computado para tickets disponibles
    @api.depends('quantity', 'sold')
    def _compute_left(self):
        for record in self:
            record.left = record.quantity - record.sold
            record.is_sold_out = record.left <= 0
            # Si hay un producto asociado, actualizar su disponibilidad
            if record.product_id:
                record.product_id.sudo().write({
                    'virtual_available': record.left
                })
            # Si hay un ticket de evento asociado, actualizar su disponibilidad
            if record.odoo_event_ticket_id:
                seats_available = record.odoo_event_ticket_id.seats_max - record.odoo_event_ticket_id.seats_reserved
                if seats_available != record.left:
                    record.odoo_event_ticket_id.sudo().write({
                        'seats_max': record.quantity,
                        'seats_available': record.left
                    })

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
    
    # Acción para crear/vincular producto
    def action_create_product(self):
        self.ensure_one()
        if self.product_id:
            return {
                'name': 'Producto',
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'view_mode': 'form',
            }
        
        # Crear el producto como servicio (sin intentar gestionar inventario)
        product_vals = {
            'name': f"Ticket: {self.name} - {self.event_id.name}",
            'type': 'service',
            'list_price': self.price,
            'standard_price': 0.0,
            'sale_ok': True,
            'purchase_ok': False,
            'website_published': True,
            'description_sale': f"Entrada para {self.event_id.name} que tendrá lugar el {self.event_id.date} en {self.event_id.location}.",
        }
        
        product = self.env['product.product'].create(product_vals)
        self.product_id = product.id
        
        return {
            'name': 'Producto',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': product.id,
            'view_mode': 'form',
        }

    def _update_product_inventory(self, product):
        """Actualiza el inventario del producto para reflejar la cantidad de tickets disponibles"""
        # Crear un movimiento de inventario para establecer la cantidad disponible
        inventory_vals = {
            'name': f'Inicialización de inventario para {product.name}',
            'product_id': product.id,
            'product_qty': self.left,  # Cantidad disponible de tickets
            'location_id': self.env.ref('stock.stock_location_stock').id,  # Ubicación de origen
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,  # Ubicación destino
            'product_uom_id': product.uom_id.id,  # Unidad de medida
        }
        
        # Verificar si estamos en una versión de Odoo que usa 'stock.inventory'
        if 'stock.inventory' in self.env:
            # Odoo 14.0 o anterior usa 'stock.inventory'
            inventory = self.env['stock.inventory'].create({
                'name': f'Inicialización de inventario para {product.name}',
                'product_ids': [(4, product.id)],
                'line_ids': [(0, 0, inventory_vals)],
            })
            inventory.action_validate()
        else:
            # Odoo 15.0+ usa 'stock.quant'
            quant = self.env['stock.quant'].create({
                'product_id': product.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'inventory_quantity': self.left,
            })
            quant.action_apply_inventory()