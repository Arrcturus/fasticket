import base64
import qrcode
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

def generate_qr_code_base64(data_to_encode):
    """
    Genera un código QR para los datos proporcionados y devuelve
    una cadena Base64 con prefijo de URI de datos.
    
    Args:
        data_to_encode (str): Datos a codificar en el QR
        
    Returns:
        str: Imagen QR en formato base64 con prefijo data URI o False si hay error
    """
    if not data_to_encode:
        _logger.warning("No se proporcionaron datos para generar el QR")
        return False

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
        return 'data:image/png;base64,' + img_base64.decode('utf-8')

    except Exception as e:
        _logger.error("Error al generar QR: %s", e, exc_info=True)
        return False