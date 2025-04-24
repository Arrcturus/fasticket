# filepath: /mnt/extra-addons/fasticket/models/mail_template_update.py
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _update_event_mail_templates(self):
        """
        Actualiza las plantillas de correo relacionadas con eventos para usar el informe personalizado.
        """
        templates_to_update = {
            'event.event_registration_mail_template_badge': 'fasticket.action_report_event_registration_badge',
            'event.event_subscription': 'fasticket.action_report_event_registration_badge',
        }

        for template_id, report_ref in templates_to_update.items():
            template = self.env.ref(template_id, raise_if_not_found=False)
            if template:
                template.sudo().write({'report_template': self.env.ref(report_ref).id})
                _logger.info("Plantilla de correo '%s' actualizada con el informe '%s'.", template_id, report_ref)
            else:
                _logger.warning("La plantilla de correo '%s' no existe y no se pudo actualizar.", template_id)