from odoo import http, _
from odoo.http import request

class FasticketWebsite(http.Controller):
    @http.route(['/fasticket/events'], type='http', auth="public", website=True)
    def fasticket_events(self, **post):
        # Mostrar eventos de fasticket con integración a los eventos de Odoo
        events = request.env['fasticket.event'].sudo().search([
            ('state', '=', 'confirmed')
        ])
        return request.render('fasticket.fasticket_events', {
            'events': events
        })
    
    @http.route(['/fasticket/event/<model("fasticket.event"):event>'], type='http', auth="public", website=True)
    def fasticket_event(self, event, **post):
        tickets = request.env['fasticket.ticket'].sudo().search([
            ('event_id', '=', event.id),
            ('left', '>', 0)
        ])
        return request.render('fasticket.fasticket_event_detail', {
            'event': event,
            'tickets': tickets
        })
    
    @http.route(['/fasticket/comprar_ticket/<model("fasticket.ticket"):ticket>'], type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def comprar_ticket_directo(self, ticket, **post):
        quantity = int(post.get('quantity', 1))
        
        # Validaciones básicas
        if quantity <= 0 or quantity > ticket.left:
            return request.redirect('/fasticket/event/%s' % ticket.event_id.id)
        
        # Si el ticket tiene producto relacionado, redirigir a la página del producto
        if ticket.product_id:
            return request.redirect('/shop/product/%s' % ticket.product_id.id)
        
        # Si el evento tiene un evento Odoo relacionado, redirigir al registro del evento
        if ticket.event_id.odoo_event_id:
            return request.redirect('/event/%s/register' % ticket.event_id.odoo_event_id.id)
        
        # De lo contrario, crear el carrito de compra directamente
        # (Esta parte necesitaría más desarrollo)
        return request.redirect('/fasticket/event/%s' % ticket.event_id.id)