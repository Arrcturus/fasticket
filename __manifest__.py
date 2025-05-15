# -*- coding: utf-8 -*-
{
    'name': "Fasticket",

    'summary': """
        Gestión de eventos y entradas con códigos QR""",

    'description': """
        Módulo para gestionar eventos y entradas. Características principales:
        - Generación de códigos QR para entradas
        - Validación de asistentes mediante escaneo
        - Personalización de plantillas de correo
        - Configuración automática de servidor SMTP
    """,

    'author': "Arthur",
    'website': "https://www.github.com/Arrcturus",
    'category': 'Events',
    'version': '0.1',

    'depends': [
        'base',
        'website_event'
    ],

    'data': [
        'views/restart.xml',
        'report/event_ticket_report_templates.xml',
        'views/menu.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'pip': [
        'qrcode'
    ],

    'pre_init_hook': 'pre_hook_function',
    'post_init_hook': 'run_post_init_hooks',

    'assets': {
        'web.assets_backend': [
            'fasticket/static/src/css/style.scss',
        ],
        'web.report_assets_common': [
            'fasticket/static/src/css/ticket/ticket_style.scss',
        ],
    },

    'images': [
        'static/description/icon.png',
    ],

    'application': True,  # Marca como aplicación principal
    'installable': True,
}
