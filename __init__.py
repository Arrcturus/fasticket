# -*- coding: utf-8 -*-

from . import controllers
from . import models


from odoo import api, SUPERUSER_ID
import ast
import os
import subprocess
import sys

import logging
_logger = logging.getLogger(__name__)

#-----------------------HOOKS-----------------#

#----------- PRE INIT HOOKS ---------------#

def pre_hook_function(env):
    install_packages(read_pip())


def read_pip():
    manifest_path = os.path.join(os.path.dirname(__file__), '__manifest__.py')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as file:
            manifest_content = file.read()
            manifest_data = ast.literal_eval(manifest_content)
            pip_content = manifest_data.get('pip', None)
            if pip_content:
                _logger.info(f"Paquetes pip detectados en el manifest: {pip_content}")
                return pip_content
            else:
                _logger.info("No se ha detectado ningún paquete pip para instalar.")
                return None
    except Exception as e:
        _logger.error(f"Error leyendo __manifest__.py: {e}")
        return None

def install_packages(pip_packages):
    if pip_packages:
        try:
            for package in pip_packages:
                result = subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True, text=True)
                if result.returncode != 0:
                    _logger.error(f"Failed to install packages: {result.stderr}")
                else:
                    _logger.info(f"Successfully installed packages: {result.stdout}")
        except Exception as e:
            _logger.error(f"Failed to install packages: {e}")

#----------- POST INIT HOOKS ---------------#
# El hook update_mail_templates se ejecuta después de la instalación del módulo

def update_mail_templates(cr, registry):
    """
    Hook post-instalación para configurar las plantillas de correo de eventos.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Ejecutando post_init_hook para actualizar plantillas de correo de eventos...")
    try:
        # Llama al método que ya existe en el modelo mail.template
        env['mail.template']._update_event_mail_templates()
        _logger.info("Llamada a _update_event_mail_templates completada desde el hook.")
    except Exception as e:
        _logger.error("Error durante la ejecución de _post_init_hook para actualizar plantillas de correo: %s", e, exc_info=True)

def setup_fasticket_mail(cr, registry):
    """
    Configura el servidor de correo saliente y el remitente por defecto
    leyendo las variables de entorno. Se ejecuta después de update_mail_templates.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrMailServer = env['ir.mail_server']
    IrConfigParameter = env['ir.config_parameter'].sudo() # Necesita sudo para escribir

    # Leer variables de entorno
    smtp_host = os.environ.get('SMTP_SERVER')
    smtp_port_str = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    smtp_ssl_str = os.environ.get('SMTP_SSL', 'False').lower() # Default a 'False' si no está
    email_from = os.environ.get('EMAIL_FROM')

    if not all([smtp_host, smtp_port_str, smtp_user, smtp_password, email_from]):
        _logger.warning("Faltan variables de entorno SMTP/EMAIL_FROM. No se configurará el servidor de correo de Fasticket.")
        return

    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        _logger.error(f"Valor inválido para SMTP_PORT: {smtp_port_str}. Debe ser un número.")
        return

    # Determinar encriptación basada en SMTP_SSL y puerto
    smtp_encryption = 'none'
    if smtp_ssl_str == 'true':
         smtp_encryption = 'ssl'
    elif smtp_port == 587:
         smtp_encryption = 'starttls'


    server_name = "Gmail Fasticket (Auto Env)"
    # Buscar si ya existe un servidor con ese nombre o usuario para evitar duplicados
    existing_server = IrMailServer.search([('smtp_user', '=', smtp_user)], limit=1)

    server_values = {
        'name': server_name,
        'smtp_host': smtp_host,
        'smtp_port': smtp_port,
        'smtp_user': smtp_user,
        'smtp_pass': smtp_password,
        'smtp_encryption': smtp_encryption,
        'sequence': 5, # Darle prioridad alta
        'active': True,
    }

    if existing_server:
        _logger.info(f"Actualizando servidor de correo existente: {server_name}")
        existing_server.write(server_values)
    else:
        _logger.info(f"Creando nuevo servidor de correo: {server_name}")
        IrMailServer.create(server_values)

    # Establecer el remitente por defecto
    _logger.info(f"Estableciendo mail.default.sender a: {email_from}")
    IrConfigParameter.set_param('mail.default.sender', email_from)

    _logger.info("Configuración de correo de Fasticket completada desde variables de entorno.")

# --- NUEVA FUNCIÓN CONTENEDORA ---
def run_post_init_hooks(cr, registry):
    """Función contenedora que ejecuta todos los post-init hooks en orden."""
    _logger.info("Ejecutando post-init hooks combinados...")
    update_mail_templates(cr, registry)
    setup_fasticket_mail(cr, registry)
    _logger.info("Post-init hooks combinados completados.")
# --- FIN NUEVA FUNCIÓN CONTENEDORA ---
