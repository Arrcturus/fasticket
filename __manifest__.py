# -*- coding: utf-8 -*-
{
    'name': "fasticket",

    'summary': """
        Módulo para gestionar eventos y entradas""",

    'description': """
        Módulo para gestionar eventos y entradas. Este módulo permite crear eventos, 
        gestionar entradas y llevar un control de los asistentes. 
        Además, incluye una funcionalidad de reinicio de eventos para facilitar la gestión de los mismos. 
        El módulo está diseñado para ser fácil de usar y personalizable según las necesidades del usuario. 
        También incluye una interfaz web para facilitar la gestión de eventos y entradas desde cualquier dispositivo.
    """,

    'author': "Arthur",
    'website': "https://www.github.com/Arrcturus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_event'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/restart.xml',
        'views/menu.xml',
        'report/event_ticket_report_templates.xml',
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
        'web.report_assets_common': [
            'fasticket/static/src/css/ticket/ticket_style.scss',
        ],
    }
}
