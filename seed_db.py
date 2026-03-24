from aplicacion import crear_aplicacion
from aplicacion.extensiones import db
from aplicacion.modelos import Equipo, Partido, Torneo
from datetime import datetime, timedelta, timezone

app = crear_aplicacion()

def sembrar_datos_prueba():
    with app.app_context():
        # Asegurar un torneo
        torneo = Torneo.query.filter_by(id=26618).first()
        if not torneo:
            torneo = Torneo(id=26618, nombre="Mundial 2026 Test", ano=2026, estado="Activo")
            db.session.add(torneo)
            db.session.commit()
            
        print("Creando equipos base...")
        equipos_data = [
            {"id": 1, "nombre": "Colombia", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/2/21/Flag_of_Colombia.svg"},
            {"id": 2, "nombre": "Argentina", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_Argentina.svg"},
            {"id": 3, "nombre": "Brasil", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/0/05/Flag_of_Brazil.svg"},
            {"id": 4, "nombre": "Francia", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg"},
            {"id": 5, "nombre": "España", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/8/89/Bandera_de_Espa%C3%B1a.svg"},
            {"id": 6, "nombre": "Alemania", "bandera_url": "https://upload.wikimedia.org/wikipedia/commons/b/ba/Flag_of_Germany.svg"},
        ]
        
        for e in equipos_data:
            equipo = db.session.get(Equipo, e["id"])
            if not equipo:
                db.session.add(Equipo(**e))
                
        db.session.commit()
        
        print("Creando partidos de prueba...")
        ahora = datetime.now(timezone.utc)
        partidos_data = [
            {
                "id": 9001, "torneo_id": torneo.id, "equipo_local_id": 1, "equipo_visitante_id": 2, 
                "fecha_hora": ahora + timedelta(days=2), "estado": "No Iniciado", "jornada": "Grupo A"
            },
            {
                "id": 9002, "torneo_id": torneo.id, "equipo_local_id": 3, "equipo_visitante_id": 4, 
                "fecha_hora": ahora + timedelta(days=3), "estado": "No Iniciado", "jornada": "Grupo B"
            },
            {
                "id": 9003, "torneo_id": torneo.id, "equipo_local_id": 5, "equipo_visitante_id": 6, 
                "fecha_hora": ahora + timedelta(days=4), "estado": "No Iniciado", "jornada": "Grupo C"
            },
            # Partido ya finalizado para testear el motor de reglas
            {
                "id": 9004, "torneo_id": torneo.id, "equipo_local_id": 1, "equipo_visitante_id": 3, 
                "fecha_hora": ahora - timedelta(days=1), "estado": "FT", "jornada": "Grupo F",
                "goles_local_real": 2, "goles_visitante_real": 1
            }
        ]
        
        for p in partidos_data:
            partido = db.session.get(Partido, p["id"])
            if not partido:
                db.session.add(Partido(**p))
                
        db.session.commit()
        print("¡Datos de prueba inyectados correctamente! Ahora podrás ver los partidos en la aplicación.")

if __name__ == '__main__':
    sembrar_datos_prueba()
