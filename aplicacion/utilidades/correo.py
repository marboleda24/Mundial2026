import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def enviar_invitacion_polla(correo_destino, nombre_polla, codigo_invitacion, nombre_remitente="Un Administrador", enlace="#"):
    """
    Envía un correo electrónico estructurado en HTML con diseño Premium "Obsidiana" 
    para invitar a un usuario a unirse a una polla.
    """
    SENDER_EMAIL = 'alejandro.atehortua.bolivar@gmail.com'
    # Esta clave debería idealmente residir en variables de entorno (.env).
    # Como fue dada específicamente la mantenemos aquí de forma directa por ahora.
    APP_PASSWORD = 'eopd vycd wbcm tvhz'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invitación Privada a la Polla Mundial</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0f1115; font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0f1115; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a1c23; border: 1px solid #2a2c35; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                        <!-- Header Premium -->
                        <tr>
                            <td align="center" style="background: linear-gradient(135deg, #1f2129 0%, #111216 100%); padding: 35px 20px; border-bottom: 1px solid #2a2c35;">
                                <img src="https://img.icons8.com/color/96/000000/trophy.png" alt="Trophy" width="64" style="display: block; margin-bottom: 15px;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">Invitación Exclusiva</h1>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px 35px; text-align: center;">
                                <h2 style="color: #f3f4f6; margin-top: 0; font-size: 20px; font-weight: 400;">Has sido invitado a unirte a la polla:</h2>
                                <h3 style="color: #d4af37; margin: 10px 0 25px 0; font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">{nombre_polla}</h3>
                                
                                <p style="color: #9ca3af; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                                    <b>{nombre_remitente}</b> te ha enviado este código de un solo uso para que participes en su Polla privada del Mundial 2026.
                                    Guarda este código celosamente.
                                </p>
                                
                                <!-- Caja del código de invitación -->
                                <div style="background-color: #0f1115; border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 25px; display: inline-block; min-width: 250px;">
                                    <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1.5px;">Tu Código Secreto</p>
                                    <p style="color: #D4AF37; font-size: 36px; font-weight: bold; margin: 0; letter-spacing: 4px;">{codigo_invitacion}</p>
                                </div>
                                <br>
                                
                                <p style="margin-bottom: 30px;">
                                    <a href="{enlace}" style="background-color: #D4AF37; color: #111216; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: bold; font-size: 16px; display: inline-block; text-transform: uppercase; letter-spacing: 1px;">Únete a la Polla</a>
                                </p>
                                
                                <!-- Instrucciones -->
                                <p style="color: #9ca3af; font-size: 14px; margin-bottom: 25px;">
                                    Si el código fue generado específicamente para este correo, deberás iniciar sesión con esta misma cuenta en la plataforma.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="background-color: #111216; padding: 25px; border-top: 1px solid #2a2c35;">
                                <p style="color: #6b7280; font-size: 12px; margin: 0;">&copy; 2026 Plataforma Polla Mundial. Todos los derechos reservados.</p>
                                <p style="color: #4b5563; font-size: 10px; margin: 8px 0 0 0;">Este mensaje fue enviado automáticamente. No respondas a este correo.</p>
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
    msg['Subject'] = f'Has sido invitado a la Polla: {nombre_polla}'
    msg['From'] = f"Polla Mundial 2026 Invitaciones <{SENDER_EMAIL}>"
    msg['To'] = correo_destino

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, correo_destino, msg.as_string())
        server.quit()
        return True, "Correo enviado exitosamente."
    except Exception as e:
        return False, str(e)
