# -*- coding: utf-8 -*-
{
    'name': "fasticket",

    'summary': """
        Módulo para la gestión de eventos y venta de entradas""",

    'description': """
        Este módulo permite gestionar eventos y la venta de entradas de manera eficiente.
        Incluye funcionalidades para crear eventos, gestionar entradas, y realizar ventas.
        Además, permite la gestión de estados de eventos y entradas.
        Funcionalidades:
        - Crear y gestionar eventos
        - Crear y gestionar entradas
        - Realizar ventas de entradas
        - Gestión de estados de eventos y entradas
        - Validaciones para entradas y eventos
        - Reportes de ventas y entradas
        - Integración con el sistema de Odoo
        - Interfaz de usuario amigable
    """,

    'author': "Arthur",
    'website': "https://www.github.com/Arrcturus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'website', 'website_sale', 'event', 'website_event', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/event_link_wizard_view.xml',
        'views/ticket.xml',
        'views/event.xml',
        'views/restart.xml',
        'views/website_templates.xml',
        'views/menu.xml',
        # El menú siempre va abajo del todo
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    

    'assets': {
        'web.assets_backend': [
            'fasticket/static/src/css/style.scss',
        ],
    }
}
