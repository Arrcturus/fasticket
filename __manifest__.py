# -*- coding: utf-8 -*-
{
    'name': "fasticket",

    'summary': """
        Plantilla Arthur: Resumen en una frase/línea de lo que hace el módulo""",

    'description': """
        Plantilla Arthur: Descripción larga de lo que hace el módulo
    """,

    'author': "Arthur",
    'website': "https://www.github.com/Arrcturus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/restart.xml',
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
