import os
from datetime import datetime, timezone
from aplicacion import crear_aplicacion
from aplicacion.extensiones import db
from aplicacion.modelos import Partido, Equipo, Torneo
from aplicacion.integraciones import obtener_adaptador

# --- CONFIGURACIÓN DE PROVEEDORES (MULTI-API) ---
# Hemos cambiado a Football-Data.org (ID: "footballdata")
PROVEEDOR_ACTIVO = "footballdata" 
# Modifica esta cadena con tu token gratuito creado en football-data.org
API_KEY = os.environ.get("FOOTBALL_API_KEY", "1f0345e601be416db95eabbf090149a2")

# En football-data.org, la copa del mundo suele usar el código 'WC' o '2000'
API_TORNEO_ID = "WC" 

app = crear_aplicacion()

def asegurar_torneo():
    torneo = Torneo.query.filter_by(nombre="Mundial 2026").first()
    if not torneo:
        torneo = Torneo(
            nombre="Mundial 2026", 
            ano=2026, 
            estado="Activo", 
            proveedor_api=PROVEEDOR_ACTIVO,
            api_torneo_id=API_TORNEO_ID,
            comentarios="Generado para uso inteligente Multi-API"
        )
        db.session.add(torneo)
        db.session.commit()
    # Si la config de BD es distinta al script, actualizamos por consistencia
    if torneo.proveedor_api != PROVEEDOR_ACTIVO or torneo.api_torneo_id != API_TORNEO_ID:
        torneo.proveedor_api = PROVEEDOR_ACTIVO
        torneo.api_torneo_id = API_TORNEO_ID
        db.session.commit()
        
    return torneo

def sync_matches():
    """Sincroniza los partidos mediante el patrón Adapter garantizando independencia."""
    
    with app.app_context():
        # Precaución ante tablas no creadas
        db.create_all()
        torneo = asegurar_torneo()
        
        print("-" * 60)
        print(f"> Iniciando Sincronizacion Inteligente Multi-API")
        print(f"> Torneo: {torneo.nombre} ({torneo.api_torneo_id})")
        print(f"> Proveedor Activo (DB): {torneo.proveedor_api.upper()}")
        print("-" * 60)
        
        if API_KEY == "pega_aqui_tu_token_gratis_football_data":
            print("[ERROR GRAVE] Abre el archivo sync_matches.py y reemplaza `pega_aqui_tu_token_gratis_football_data` con tu Token.")
            print("Para conseguir uno ve a: https://www.football-data.org/client/register")
            return

        # 1. Instanciar Adapter Dinámicamente según BD
        try:
            adapter = obtener_adaptador(torneo.proveedor_api, API_KEY)
        except ValueError as e:
            print(f"[ERROR] Error fatal de sistema: {e}")
            return
            
        # 2. Extracción de Equipos
        print("> Conectando a la API para capturar Selecciones / Equipos...")
        equipos_api = adapter.obtener_equipos(torneo.api_torneo_id)
        
        if not equipos_api:
            print("[ADVERTENCIA] No se retornaron equipos. ¿Quizas el ID de Torneo (WC) no esta disponible para tu plan?")
            return
            
        equipos_insertados = 0
        for eq_data in equipos_api:
            try:
                pid = int(eq_data['id_proveedor'])
            except: 
                continue # Saltar si el id_proveedor incluye strings raros en otras apis
                
            equipo = db.session.get(Equipo, pid)
            if not equipo:
                equipo = Equipo(
                    id=pid,
                    nombre=eq_data['nombre'],
                    bandera_url=eq_data['bandera_url'],
                    comentarios=f"Sincronizado vía {torneo.proveedor_api}"
                )
                db.session.add(equipo)
                equipos_insertados += 1
        db.session.commit()
        print(f"[*] Se validaron {len(equipos_api)} selecciones terrestres. Fueron creadas {equipos_insertados} nuevas.")
        
        # 3. Extracción de Calendarios y Marcadores
        print("\n> Conectando a la API para actualizar Partidos y Scores en vivo...")
        partidos_api = adapter.obtener_partidos(torneo.api_torneo_id)
        
        partidos_insertados = 0
        partidos_actualizados = 0
        
        for pa_data in partidos_api:
            try:
                p_id = int(pa_data['id_proveedor'])
            except: 
                continue
                
            partido = db.session.get(Partido, p_id)
            es_nuevo = False
            
            if not partido:
                partido = Partido(id=p_id)
                es_nuevo = True
                
            partido.torneo_id = torneo.id
            partido.equipo_local_id = int(pa_data['equipo_local_id'])
            partido.equipo_visitante_id = int(pa_data['equipo_visitante_id'])
            partido.fecha_hora = pa_data['fecha_hora']
            partido.estado = pa_data['estado']
            partido.goles_local_real = pa_data['goles_local_real']
            partido.goles_visitante_real = pa_data['goles_visitante_real']
            partido.jornada = pa_data['jornada']
            partido.comentarios = f"Sincronizado multi-api UTC {datetime.now(timezone.utc).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M')}"
            
            if es_nuevo:
                db.session.add(partido)
                partidos_insertados += 1
            else:
                partidos_actualizados += 1
                
        db.session.commit()
        print(f"[*] Se sincronizo el calendario. {partidos_insertados} Registrados / {partidos_actualizados} Actualizados.")
        print("-" * 60)
        print("[EXITO] Arquitectura Multi-API corriendo a la perfeccion. Sincronizacion finalizada exitosamente.")

if __name__ == "__main__":
    sync_matches()
