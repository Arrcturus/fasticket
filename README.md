# Fasticket - Gestión de Eventos y Entradas con Códigos QR para Odoo 16

![Fasticket Logo](static/description/icon.png)

## Descripción

Fasticket es un módulo integrado para Odoo 16 que moderniza la gestión de eventos y entradas. Permite crear eventos, generar entradas con códigos QR únicos, enviar confirmaciones por correo electrónico y validar la asistencia mediante escaneo de códigos QR.

## Características Principales

- **📅 Gestión completa de eventos**: Integración perfecta con el módulo `website_event` de Odoo
- **🎟️ Entradas personalizables**: Define diferentes tipos de entradas para cada evento
- **🔄 Registro automatizado**: Gestión simplificada de las inscripciones
- **📱 Códigos QR únicos**: Generación automática de códigos QR para cada entrada
- **📄 Tickets en PDF**: Plantilla profesional para las entradas, con información del evento y código QR
- **✅ Validación por escaneo**: API XML-RPC para validar entradas mediante escaneo de códigos QR
- **📧 Correos personalizados**: Plantillas de correo electrónico con tickets adjuntos
- **⚙️ Configuración SMTP automática**: Configuración del servidor de correo mediante variables de entorno
- **📦 Instalación sin complicaciones**: Dependencias Python instaladas automáticamente

## Requisitos

- Odoo 16.0
- Módulo `website_event` instalado
- Acceso a servidor SMTP para el envío de correos (opcional, pero recomendado)

## Instalación

1. **Clonar o descargar el módulo**
   ```bash
   git clone https://github.com/tu-usuario/fasticket.git /ruta/a/addons/fasticket
   ```
   
2. **Añadir al path de addons de Odoo**
   - Añade la ruta al directorio donde has clonado/descargado el módulo en tu archivo de configuración de Odoo (`odoo.conf`):
     ```
     addons_path = /ruta/original/addons,/ruta/a/addons
     ```

3. **Reiniciar Odoo y actualizar la lista de aplicaciones**
   - Reinicia el servidor Odoo
   - En modo desarrollador, actualiza la lista de aplicaciones (Ajustes > Actualizar Lista de Aplicaciones)

4. **Instalar el módulo**
   - Busca "Fasticket" en la lista de aplicaciones e instálalo

## Configuración

### Configuración Manual

1. **Servidor de correo**
   - Ve a Ajustes > Técnico > Correo electrónico > Servidores de Correo Saliente
   - Configura tu servidor SMTP para el envío de entradas por correo

2. **Plantillas de correo**
   - Las plantillas se actualizan automáticamente durante la instalación para incluir los tickets con QR

### Configuración con Docker

Para entornos Docker, el módulo puede configurarse automáticamente mediante variables de entorno:

1. **Archivo `compose.yaml`** (ejemplo):
   ```yaml
   version: '3.8'
   services:
     odoo:
       image: odoo:16
       depends_on:
         - db
       ports:
         - "8069:8069"
       volumes:
         - ./addons:/mnt/extra-addons
       environment:
         - HOST=db
         - USER=${POSTGRES_USER}
         - PASSWORD=${POSTGRES_PASSWORD}
         # Variables para configuración SMTP
         - SMTP_SERVER=${SMTP_SERVER}
         - SMTP_PORT=${SMTP_PORT}
         - SMTP_USER=${SMTP_USER}
         - SMTP_PASSWORD=${SMTP_PASSWORD}
         - EMAIL_FROM=${EMAIL_FROM}
         - SMTP_SSL=${SMTP_SSL}
     
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=postgres
         - POSTGRES_USER=${POSTGRES_USER}
         - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
       volumes:
         - odoo-db-data:/var/lib/postgresql/data
   
   volumes:
     odoo-db-data:
   ```

2. **Archivo `.env`** (ejemplo):
   ```dotenv
   # PostgreSQL
   POSTGRES_USER=odoo
   POSTGRES_PASSWORD=myodoopassword
   
   # SMTP
   EMAIL_FROM=noreply@miempresa.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=micorreo@gmail.com
   SMTP_PASSWORD=micontraseña
   SMTP_SSL=False
   ```

⚠️ **IMPORTANTE**: Nunca incluyas el archivo `.env` en repositorios públicos. Añádelo a tu `.gitignore`.

## Uso del Módulo

### Crear Eventos y Entradas

1. Ve a Eventos > Eventos > Crear
2. Configura la información del evento (nombre, fechas, ubicación)
3. Define los tipos de entradas disponibles
4. Publica el evento si deseas que esté disponible en el sitio web

### Registrar Asistentes

- **Manual**: Añade asistentes desde el backoffice (Eventos > Eventos > [Tu Evento] > Asistentes)
- **Automático**: Los usuarios pueden registrarse desde el sitio web si el evento está publicado

### Tickets y Códigos QR

- Los tickets con códigos QR se generan automáticamente para cada registro
- Puedes enviarlos por correo, descargarlos como PDF o imprimirlos
- Cada código QR contiene un identificador único para el registro

### Validación de Entradas

#### Mediante API XML-RPC

```python
import xmlrpc.client

url = 'https://tu-odoo.com'
db = 'nombre-bd'
username = 'usuario'
password = 'contraseña'

# Autenticación
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

# Llamada al método de validación
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
result = models.execute_kw(
    db, uid, password,
    'event.registration', 'check_registration_by_qr',
    ['REGISTRATION:123']  # Datos del QR escaneado
)

print(result)
# Resultado: {'status': 'ok', 'message': 'Entrada validada correctamente', ...}
```

#### Desde Frontend (Ejemplo con JavaScript)

```javascript
async function validarQR(qrData) {
    try {
        const response = await fetch('/api/validate-ticket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ qr_data: qrData })
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error validando ticket:', error);
    }
}
```

## Solución de Problemas

### Correos no enviados

Si los correos quedan en estado "saliente" pero no se envían:
1. Verifica la configuración SMTP (servidor, puerto, credenciales)
2. Comprueba que el trabajo programado "Enviar correos pendientes" esté activo
3. Para envío inmediato, modifica la frecuencia del cron job o implementa envío forzado

### Errores en la generación de QR

1. Asegúrate de que la dependencia `qrcode` está instalada correctamente
2. Verifica los permisos de escritura en el directorio temporal

## Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

Desarrollado por [Arthur](https://github.com/Arrcturus)