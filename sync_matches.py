import requests
from app import app, db, Partido

# --- CONFIGURACIÓN ---
API_TOKEN = "4iWfGL9c13i26q2GgELgpgFdUSiYILfF87V75JVSx1dXlAjeMYHNmOu5NLwz"
SEASON_ID = 26618 
FECHA_INICIO = "2026-06-11"
FECHA_FIN = "2026-07-19"

def sync_matches():
    """Sincroniza los partidos desde la API hacia la base de datos configurada en app.py."""
    
    with app.app_context():
        # Crear tablas si no existen (incluyendo tabla partidos ahora que es Modelo)
        db.create_all()
        
        print(f"--- Iniciando Sincronización del Mundial 2026 (Season {SEASON_ID}) ---")
        
        pagina = 1
        hay_mas_paginas = True
        total_importados = 0
        
        while hay_mas_paginas:
            url = f"https://api.sportmonks.com/v3/football/fixtures/between/{FECHA_INICIO}/{FECHA_FIN}"
            params = {
                'api_token': API_TOKEN,
                'filters': f'seasonIds:{SEASON_ID}',
                'include': 'participants;state',
                'page': pagina 
            }
            
            try:
                print(f"Consultando página {pagina}...")
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    for f in data['data']:
                        # Extraer datos
                        participants = f.get('participants', [])
                        local = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), {})
                        visitante = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), {})
                        estado_nombre = f.get('state', {}).get('short_name', 'NS')
                        
                        partido_id = f['id']
                        
                        # Buscar si existe
                        partido = Partido.query.get(partido_id)
                        if not partido:
                            partido = Partido(id=partido_id)
                            print(f"Nuevo partido: {partido_id}")
                        
                        # Actualizar campos
                        partido.nombre = f.get('name', 'Partido TBD')
                        partido.fecha = f['starting_at']
                        partido.local_nombre = local.get('name', 'Por definir')
                        partido.local_flag = local.get('image_path', '')
                        partido.visitante_nombre = visitante.get('name', 'Por definir')
                        partido.visitante_flag = visitante.get('image_path', '')
                        partido.estado = estado_nombre
                        
                        # Solo actualizamos goles si la API los trae (esto depende de la estructura exacta de scores)
                        # Por ahora asumimos que solo queremos la info base.
                        
                        db.session.add(partido)
                        total_importados += 1
                    
                    db.session.commit()
                    print(f"Página {pagina} procesada.")
                    
                    hay_mas_paginas = data.get('pagination', {}).get('has_more', False)
                    if hay_mas_paginas:
                        pagina += 1
                else:
                    print("No se encontraron datos.")
                    hay_mas_paginas = False
                    
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print("-" * 50)
        print(f"¡FINALIZADO! Se han sincronizado {total_importados} partidos.")

if __name__ == "__main__":
    sync_matches()
