# -*- coding: utf-8 -*-
# from odoo import http


# class Fasticket(http.Controller):
#     @http.route('/fasticket/fasticket', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fasticket/fasticket/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fasticket.listing', {
#             'root': '/fasticket/fasticket',
#             'objects': http.request.env['fasticket.fasticket'].search([]),
#         })

#     @http.route('/fasticket/fasticket/objects/<model("fasticket.fasticket"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fasticket.object', {
#             'object': obj
#         })
