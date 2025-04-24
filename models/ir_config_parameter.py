import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def _set_mail_default_from(self, value):
        """
        Establece el valor del parámetro del sistema 'mail.default.from'.
        Llamado desde el archivo de datos XML durante la instalación/actualización.
        """
        param_key = 'mail.default.from'
        self.sudo().set_param(param_key, value)
        _logger.info("Parámetro del sistema '%s' establecido a '%s'", param_key, value)
