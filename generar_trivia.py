import os
from datetime import date
from aplicacion import crear_aplicacion
from aplicacion.extensiones import db
from aplicacion.modelos import ConfiguracionGlobal, PreguntaTrivia
from aplicacion.integraciones.llm_factory import LLMFactory

def generar_trivia_hoy():
    print("--- INICIANDO GENERACIÓN DE TRIVIA DIARIA IA ---")
    
    app = crear_aplicacion()
    with app.app_context():
        # Verificar si ya existe trivia para hoy
        hoy = date.today()
        existe = PreguntaTrivia.query.filter_by(fecha_para_mostrar=hoy).first()
        if existe:
            print(f"Ya existe una trivia registrada para el día {hoy}. Abortando.")
            return

        # Consultar Configuración Global
        proveedor_conf = ConfiguracionGlobal.query.filter_by(clave='LLM_PROVEEDOR').first()
        api_key_conf = ConfiguracionGlobal.query.filter_by(clave='LLM_API_KEY').first()

        if not proveedor_conf or not api_key_conf or not proveedor_conf.valor or not api_key_conf.valor:
            # Insertar pregunta genérica de contingencia si no hay IA configurada
            print("El Super Admin no ha configurado la IA. Creando pregunta de contingencia clásica...")
            trivia = PreguntaTrivia(
                fecha_para_mostrar=hoy,
                pregunta="¿En qué año se celebró el primer Mundial de Fútbol?",
                opcion_a="1920",
                opcion_b="1930",
                opcion_c="1940",
                opcion_d="1950",
                opcion_correcta="B",
                explicacion="El primer Mundial se celebró en Uruguay en 1930, con la victoria del país anfitrión.",
                proveedor_generador="fallback_manual"
            )
            db.session.add(trivia)
            db.session.commit()
            print("Pregunta clásica de contingencia generada.")
            return

        proveedor = proveedor_conf.valor
        api_key = api_key_conf.valor
        
        print(f"Contactando a la Inteligencia Artificial mediante: {proveedor}...")
        
        # Llamar a la Fábrica Agnostica
        data = LLMFactory.generar_trivia(proveedor, api_key)
        
        if data and isinstance(data, dict):
            try:
                trivia = PreguntaTrivia(
                    fecha_para_mostrar=hoy,
                    pregunta=data['pregunta'],
                    opcion_a=data['opcion_a'],
                    opcion_b=data['opcion_b'],
                    opcion_c=data['opcion_c'],
                    opcion_d=data['opcion_d'],
                    opcion_correcta=data['opcion_correcta'].upper(),
                    explicacion=data['explicacion'],
                    proveedor_generador=proveedor
                )
                db.session.add(trivia)
                db.session.commit()
                print(f"¡EXITO! La Inteligencia Artificial ({proveedor}) ha creado la trivia de hoy exitosamente.")
            except Exception as e:
                print(f"Error procesando los datos devueltos por la IA: {e}")
        else:
            print(f"Fallo crítico: El proveedor {proveedor} no retornó un JSON válido o rechazó el token.")

if __name__ == '__main__':
    generar_trivia_hoy()
