# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo import api, SUPERUSER_ID
import ast
import logging
import os
import subprocess
import sys

_logger = logging.getLogger(__name__)

#----------- PRE INIT HOOKS ---------------#

def pre_hook_function(cr):
    """Hook pre-instalación para instalar dependencias Python."""
    pip_packages = read_pip_requirements()
    if pip_packages:
        install_python_dependencies(pip_packages)

def read_pip_requirements():
    """Lee los requisitos pip del archivo __manifest__.py."""
    manifest_path = os.path.join(os.path.dirname(__file__), '__manifest__.py')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as file:
            manifest_content = file.read()
            manifest_data = ast.literal_eval(manifest_content)
            return manifest_data.get('pip', None)
    except Exception as e:
        _logger.error(f"Error leyendo __manifest__.py: {e}")
        return None

def install_python_dependencies(pip_packages):
    """Instala los paquetes Python necesarios."""
    try:
        for package in pip_packages:
            _logger.info(f"Instalando paquete Python: {package}")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                   capture_output=True, text=True)
            if result.returncode != 0:
                _logger.error(f"Error instalando {package}: {result.stderr}")
            else:
                _logger.info(f"Paquete instalado correctamente: {package}")
    except Exception as e:
        _logger.error(f"Error en el proceso de instalación: {e}")

#----------- POST INIT HOOKS ---------------#

def update_mail_templates(cr, registry):
    """Configura las plantillas de correo de eventos."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Actualizando plantillas de correo de eventos...")
    try:
        env['mail.template']._update_event_mail_templates()
        _logger.info("Plantillas de correo actualizadas correctamente.")
    except Exception as e:
        _logger.error(f"Error actualizando plantillas: {e}", exc_info=True)

def setup_fasticket_mail(cr, registry):
    """Configura el servidor de correo desde variables de entorno."""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrMailServer = env['ir.mail_server']
    IrConfigParameter = env['ir.config_parameter'].sudo()

    # Variables de entorno para configuración SMTP
    env_vars = {
        'smtp_host': os.environ.get('SMTP_SERVER'),
        'smtp_port': os.environ.get('SMTP_PORT'),
        'smtp_user': os.environ.get('SMTP_USER'),
        'smtp_password': os.environ.get('SMTP_PASSWORD'),
        'smtp_ssl': os.environ.get('SMTP_SSL', 'False').lower(),
        'email_from': os.environ.get('EMAIL_FROM'),
    }
    
    # Validar variables requeridas
    required_vars = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'email_from']
    if not all(env_vars.get(var) for var in required_vars):
        _logger.warning("Configuración SMTP incompleta. No se configuró el servidor de correo.")
        return
    
    # Configurar el servidor de correo
    try:
        configure_mail_server(IrMailServer, IrConfigParameter, env_vars)
    except Exception as e:
        _logger.error(f"Error configurando servidor SMTP: {e}", exc_info=True)

def configure_mail_server(IrMailServer, IrConfigParameter, config):
    """Configura el servidor de correo con los valores proporcionados."""
    try:
        smtp_port = int(config['smtp_port'])
    except ValueError:
        _logger.error(f"Puerto SMTP inválido: {config['smtp_port']}")
        return
    
    # Determinar tipo de encriptación
    smtp_encryption = 'none'
    if config['smtp_ssl'] == 'true':
        smtp_encryption = 'ssl'
    elif smtp_port == 587:
        smtp_encryption = 'starttls'
    
    # Buscar servidor existente o crear uno nuevo
    server_name = "Gmail Fasticket (Auto Env)"
    existing_server = IrMailServer.search([('smtp_user', '=', config['smtp_user'])], limit=1)
    
    server_values = {
        'name': server_name,
        'smtp_host': config['smtp_host'],
        'smtp_port': smtp_port,
        'smtp_user': config['smtp_user'],
        'smtp_pass': config['smtp_password'],
        'smtp_encryption': smtp_encryption,
        'sequence': 5,
        'active': True,
    }
    
    if existing_server:
        _logger.info(f"Actualizando servidor de correo: {server_name}")
        existing_server.write(server_values)
    else:
        _logger.info(f"Creando servidor de correo: {server_name}")
        IrMailServer.create(server_values)
    
    # Configurar remitente por defecto
    _logger.info(f"Configurando remitente por defecto: {config['email_from']}")
    IrConfigParameter.set_param('mail.default.sender', config['email_from'])
    _logger.info("Configuración de correo completada correctamente.")

# Hook principal que ejecuta todos los post-init hooks
def run_post_init_hooks(cr, registry):
    """Ejecuta todos los hooks post-inicialización en orden."""
    _logger.info("Iniciando hooks post-instalación...")
    update_mail_templates(cr, registry)
    setup_fasticket_mail(cr, registry)
    _logger.info("Hooks post-instalación completados correctamente.")
