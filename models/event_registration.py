import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

from .qr_utils import generate_qr_code_base64

_logger = logging.getLogger(__name__)

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def get_qr_code_base64(self):
        """
        Genera un código QR para esta inscripción y devuelve una cadena Base64 
        con prefijo de URI de datos.
        """
        self.ensure_one()
        data_to_encode = f"REGISTRATION:{self.id}"
        return generate_qr_code_base64(data_to_encode)

    @api.model
    def check_registration_by_qr(self, qr_data):
        """
        Valida un código QR y marca la asistencia como confirmada.
        Este método está diseñado para ser llamado vía XML-RPC.
        
        Args:
            qr_data (str): Datos del QR en formato "REGISTRATION:ID"
            
        Returns:
            dict: Información del resultado de la validación
        """
        _logger.info("check_registration_by_qr: Recibidos datos QR: %s", qr_data)
        
        # Validar formato del QR
        if not qr_data or not qr_data.startswith('REGISTRATION:'):
            _logger.warning("check_registration_by_qr: Datos QR inválidos recibidos: %s", qr_data)
            raise UserError(_("Formato de QR inválido."))

        try:
            registration_id = int(qr_data.split(':')[1])
        except (IndexError, ValueError):
            _logger.warning("check_registration_by_qr: No se pudo extraer ID de: %s", qr_data)
            raise UserError(_("Formato de ID en QR inválido."))

        registration = self.env['event.registration'].browse(registration_id)

        if not registration.exists():
            _logger.warning("check_registration_by_qr: Inscripción ID %d no encontrada", registration_id)
            raise UserError(_("Inscripción no encontrada."))

        if registration.state == 'done':
            _logger.info("check_registration_by_qr: La inscripción ID %d ya está marcada como 'done'", registration.id)
            return {
                'status': 'warning',
                'message': _("Esta entrada ya fue validada anteriormente."),
                'attendee_name': registration.name,
                'event_name': registration.event_id.name,
            }

        if registration.state != 'open':
            _logger.warning("check_registration_by_qr: La inscripción ID %d no está en estado 'open', sino '%s'", registration.id, registration.state)
            raise UserError(_("Esta inscripción no está confirmada o ha sido cancelada."))

        try:
            registration.write({'state': 'done'})
            _logger.info("check_registration_by_qr: Inscripción ID %d marcada como 'done'.", registration.id)
            return {
                'status': 'ok',
                'message': _("Entrada validada correctamente."),
                'attendee_name': registration.name,
                'event_name': registration.event_id.name,
            }
        except AccessError as e:
             _logger.error("check_registration_by_qr: Error de acceso al intentar marcar como 'done' ID %d por usuario %d: %s", registration.id, self.env.uid, e)
             raise AccessError(_("No tienes permiso para modificar esta inscripción."))
        except Exception as e:
            _logger.error("check_registration_by_qr: Error desconocido al procesar inscripción ID %d: %s", registration.id, e)
            raise UserError(_("Error al validar la entrada. Contacta al administrador."))