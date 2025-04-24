import base64
import qrcode
from io import BytesIO
import logging

from odoo import models, fields, api, _ # Añadir _ para traducciones
from odoo.exceptions import UserError, AccessError # Añadir excepciones

_logger = logging.getLogger(__name__)

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def get_qr_code_base64(self):
        """
        Genera un código QR para esta inscripción (usando su ID) y devuelve
        una cadena Base64 con prefijo de URI de datos COMO STRING.
        """
        self.ensure_one()

        data_to_encode = f"REGISTRATION:{self.id}"

        if not data_to_encode:
            _logger.warning("No se pudo obtener el ID para generar QR para la inscripción ID %d", self.id)
            return False # Devuelve False si no hay datos

        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(data_to_encode)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            img_base64 = base64.b64encode(img_byte_arr)

            # --- CAMBIO CLAVE AQUÍ ---
            # Decodifica los bytes base64 a utf-8 y añade el prefijo como string
            return 'data:image/png;base64,' + img_base64.decode('utf-8')
            # --- FIN CAMBIO CLAVE ---

        except Exception as e:
            _logger.error("Error al generar QR para la inscripción ID %d: %s", self.id, e, exc_info=True)
            return False # Devuelve False en caso de error
        

    # --- NUEVO MÉTODO PARA VALIDACIÓN RPC ---
    @api.model
    def check_registration_by_qr(self, qr_data):
        """
        Busca una inscripción por su identificador QR ('REGISTRATION:ID')
        y la marca como 'done' si está 'open'.
        Este método está pensado para ser llamado vía RPC (XML-RPC o JSON-RPC estándar).

        :param qr_data: El string leído del QR (ej: 'REGISTRATION:123')
        :return: dict: {'status': 'ok'/'error', 'message': '...', 'attendee_name': '...', 'event_name': '...'}
        :raises: AccessError si el usuario RPC no tiene permisos.
                 UserError si los datos son inválidos o la entrada no se puede validar.
        """
        _logger.info(f"Llamada RPC check_registration_by_qr recibida con datos: {qr_data}")

        if not qr_data or not isinstance(qr_data, str) or not qr_data.startswith('REGISTRATION:'):
            _logger.warning("check_registration_by_qr: Datos QR inválidos recibidos: %s", qr_data)
            # Es mejor lanzar UserError para RPC que devolver un dict de error simple
            raise UserError(_("Formato de QR inválido."))

        try:
            registration_id = int(qr_data.split(':')[1])
        except (IndexError, ValueError):
            _logger.warning("check_registration_by_qr: No se pudo extraer ID de: %s", qr_data)
            raise UserError(_("Formato de ID en QR inválido."))

        # Usamos sudo() temporalmente para buscar, pero la escritura debe respetar permisos si es necesario
        # O mejor, asegurarse que el usuario RPC tenga permisos de lectura en event.registration
        registration = self.env['event.registration'].browse(registration_id)

        if not registration.exists():
            _logger.warning("check_registration_by_qr: Inscripción no encontrada para ID: %d", registration_id)
            raise UserError(_("Inscripción no encontrada."))

        _logger.info(f"check_registration_by_qr: Encontrada inscripción ID {registration.id}, Estado: {registration.state}")

        if registration.state == 'done':
            raise UserError(_("Esta entrada ya ha sido utilizada."))
        elif registration.state == 'cancel':
             raise UserError(_("Esta entrada está cancelada."))
        elif registration.state != 'open':
            # Otros estados como 'draft' tampoco deberían ser válidos para check-in
            raise UserError(_("Esta entrada no está confirmada o no es válida para el check-in (Estado: %s).") % registration.state)

        # Si llegamos aquí, la entrada está 'open' y es válida. La marcamos como 'done'.
        try:
            # La escritura debe hacerse con el usuario RPC para trazabilidad y permisos
            # Si el usuario RPC no tiene permisos de escritura, esto fallará (lo cual es bueno)
            registration.write({'state': 'done'})
            _logger.info(f"check_registration_by_qr: Inscripción ID {registration.id} marcada como 'done'.")
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
            _logger.error("check_registration_by_qr: Error inesperado al marcar como 'done' ID %d: %s", registration.id, e, exc_info=True)
            raise UserError(_("Error inesperado al procesar la entrada."))

    # --- FIN NUEVO MÉTODO ---