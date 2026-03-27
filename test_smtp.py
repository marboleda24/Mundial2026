import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Credenciales
SENDER_EMAIL = 'alejandro.atehortua.bolivar@gmail.com'
APP_PASSWORD = 'eopd vycd wbcm tvhz'

# Crear el mensaje premium HTML
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invitación a la Polla</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f1115; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0f1115; padding: 40px 0;">
        <tr>
            <td align="center">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a1c23; border: 1px solid #2a2c35; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="background: linear-gradient(135deg, #1f2129 0%, #111216 100%); padding: 30px; border-bottom: 1px solid #2a2c35;">
                            <!-- Trofeo Dorado de prueba simulando logo -->
                            <img src="https://img.icons8.com/color/96/000000/trophy.png" alt="Trophy" width="64" style="display: block; margin-bottom: 15px;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">Prueba de Servidor</h1>
                        </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <h2 style="color: #f3f4f6; margin-top: 0; font-size: 20px; font-weight: 500;">¡Conexión Exitosa!</h2>
                            <p style="color: #9ca3af; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                                La clave de aplicación de Gmail ha funcionado correctamente. Este es un vistazo a la estética <b>Premium Dark Mode</b> que tendrán las invitaciones finales.
                            </p>
                            
                            <div style="background-color: #0f1115; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 30px; display: inline-block;">
                                <p style="color: #9ca3af; font-size: 14px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px;">Tu Código Secreto Muestra</p>
                                <p style="color: #D4AF37; font-size: 32px; font-weight: bold; margin: 0; letter-spacing: 4px;">TEST-2026</p>
                            </div>
                            <br>
                            <a href="#" style="background-color: #D4AF37; color: #111216; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: bold; font-size: 16px; display: inline-block; text-transform: uppercase; letter-spacing: 1px;">Unirse a la Polla</a>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #111216; padding: 20px; border-top: 1px solid #2a2c35;">
                            <p style="color: #6b7280; font-size: 12px; margin: 0;">&copy; 2026 Plataforma Polla Mundial. Todos los derechos reservados.</p>
                            <p style="color: #4b5563; font-size: 10px; margin: 5px 0 0 0;">Este es un correo automático, por favor no respondas.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Prueba SMTP - Polla Mundial 2026'
msg['From'] = f"Polla Mundial 2026 <{SENDER_EMAIL}>"
msg['To'] = SENDER_EMAIL

html_part = MIMEText(html_content, 'html')
msg.attach(html_part)

try:
    print("Iniciando conexión con smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("Iniciando sesión...")
    server.login(SENDER_EMAIL, APP_PASSWORD)
    print("Enviando correo...")
    server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
    server.quit()
    print("¡EL CORREO SE ENVIÓ CORRECTAMENTE!")
    sys.exit(0)
except smtplib.SMTPAuthenticationError as e:
    print(f"Error de Autenticación en Gmail: Verifica si la contraseña de aplicación es correcta y si la cuenta no la ha revocado. Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(1)
