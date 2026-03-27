from aplicacion import crear_aplicacion
from aplicacion.extensiones import db

app = crear_aplicacion()

with app.app_context():
    print("Creando tablas faltantes (CodigoInvitacion)...")
    db.create_all()
    print("Migración completada con éxito.")
