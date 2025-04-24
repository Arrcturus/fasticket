# Fasticket - Gestión de Eventos y Entradas para Odoo 16

## Resumen

Fasticket es un módulo para Odoo 16 diseñado para simplificar la gestión de eventos y la venta/validación de entradas. Permite crear eventos, configurar diferentes tipos de entradas, generar códigos QR únicos para cada asistente y validar dichos códigos.

## Funcionalidades Principales

*   **Gestión de Eventos:** Creación y configuración de eventos (fechas, ubicación, etc.) integrado con el módulo `website_event` de Odoo.
*   **Gestión de Entradas:** Definición de diferentes tipos de entradas para cada evento.
*   **Registro de Asistentes:** Gestión de las inscripciones de los asistentes a los eventos.
*   **Generación de Códigos QR:** Cada entrada de asistente genera automáticamente un código QR único que contiene la información necesaria para su validación.
*   **Plantilla de Ticket PDF:** Incluye una plantilla de informe QWeb para imprimir/descargar las entradas en formato PDF, mostrando la información del evento, del asistente y el código QR.
*   **Validación de QR (XML-RPC):** Proporciona un método en el modelo `event.registration` que puede ser llamado vía XML-RPC para validar un código QR y registrar la asistencia.
*   **Plantillas de Correo Personalizadas:** Actualiza las plantillas de correo electrónico estándar de eventos de Odoo para incluir el ticket con el código QR como adjunto.
*   **Configuración SMTP Dinámica:** Configura el servidor de correo saliente y el remitente por defecto de Odoo utilizando variables de entorno, ideal para despliegues con Docker. Esto se realiza mediante un `post_init_hook` para mantener las credenciales seguras y fuera del código fuente.
*   **Instalación de Dependencias:** Utiliza un `pre_init_hook` para instalar automáticamente las dependencias Python listadas en la clave `pip` del `__manifest__.py` (como `qrcode`).

## Instalación y Configuración

1.  **Clonar el Repositorio:** Clona este repositorio o copia la carpeta `fasticket` dentro de tu directorio de addons personalizados de Odoo.
2.  **Dependencias:** Asegúrate de que el módulo `website_event` de Odoo esté instalado. La dependencia Python `qrcode` se instalará automáticamente al instalar el módulo `fasticket` gracias al `pre_init_hook`.
3.  **Actualizar Lista de Aplicaciones:** Reinicia tu servidor Odoo y actualiza la lista de aplicaciones (activando el modo desarrollador si es necesario).
4.  **Instalar Módulo:** Busca "Fasticket" en la lista de aplicaciones e instálalo.

## Configuración de Docker (Ejemplo)

Este módulo está pensado para funcionar bien en un entorno Dockerizado usando Docker Compose.

*   **`compose.yaml`:** Define los servicios necesarios (Odoo, PostgreSQL, etc.) y monta el directorio de addons personalizados (incluyendo `fasticket`) dentro del contenedor de Odoo. También pasa las variables de entorno necesarias al servicio de Odoo. Puedes encontrar un archivo `compose.yaml` de ejemplo en la raíz de este repositorio (o donde lo hayas colocado).
*   **`.env`:** Este archivo contiene las variables de entorno sensibles, como las credenciales de la base de datos y, crucialmente, las credenciales SMTP (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`, `SMTP_SSL`).

**Ubicación de los Archivos Docker:**

*   Se recomienda colocar los archivos `compose.yaml` y `.env` en una **carpeta personal fuera del directorio del módulo `fasticket`**. Por ejemplo, en una carpeta raíz del proyecto desde donde ejecutes `docker compose up`.
*   El archivo `compose.yaml` **puede ser incluido** en tu repositorio de GitHub como referencia de configuración.
*   El archivo `.env` **NUNCA debe ser subido a GitHub** ni a ningún otro repositorio público, ya que contiene información sensible (contraseñas). Asegúrate de incluir `.env` en tu archivo `.gitignore`.

**Ejemplo de Variables en `.env` para SMTP:**

```dotenv
# PostgreSQL Credentials
POSTGRES_USER=odoo
POSTGRES_PASSWORD=tu_contraseña_segura

# SMTP Configuration (Usadas por el post_init_hook de Fasticket)
EMAIL_FROM=tu_email_remitente@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=tu_usuario_smtp@example.com
SMTP_PASSWORD=tu_contraseña_smtp
SMTP_SSL=False # O True si usas SSL/TLS directo (ej. puerto 465)
```

Al instalar o actualizar el módulo `fasticket`, el `post_init_hook` leerá estas variables de entorno y configurará el servidor de correo saliente en Odoo automáticamente.

## Uso

1.  Crea un nuevo evento desde el módulo de Eventos de Odoo.
2.  Configura los tipos de entradas para el evento.
3.  Cuando un asistente se registre (manualmente o a través del sitio web), se creará un registro en `event.registration`.
4.  Puedes imprimir el ticket con el QR desde el registro del asistente.
5.  Utiliza el método XML-RPC `validate_qr_code` del modelo `event.registration` para validar las entradas escaneando el QR.
