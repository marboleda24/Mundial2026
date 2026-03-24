import requests
from datetime import datetime, timezone
from .api_base import ProveedorAPI

class SportMonksAdapter(ProveedorAPI):
    BASE_URL = "https://api.sportmonks.com/v3"

    def __init__(self, api_key):
        super().__init__(api_key)

    def _consultar(self, endpoint, includes=""):
        elementos = []
        pagina = 1
        hay_mas = True
        
        while hay_mas:
            url = f"{self.BASE_URL}/{endpoint}"
            params = {'api_token': self.api_key, 'page': pagina}
            if includes: params['include'] = includes
            
            resp = requests.get(url, params=params)
            if resp.status_code != 200:
                print(f"Error SportMonks {endpoint}: {resp.text}")
                break
                
            data = resp.json()
            if 'data' in data and len(data['data']) > 0:
                elementos.extend(data['data'])
            
            hay_mas = data.get('pagination', {}).get('has_more', False)
            if hay_mas: pagina += 1
            else: break
            
        return elementos

    def obtener_equipos(self, api_torneo_id):
        # Sportmonks V3: /football/teams/seasons/{id} o desde fixtures
        # Extraemos equipos a partir de los participantes de los fixtures del torneo para ser prácticos
        fixtures = self._consultar(f"football/fixtures/between/2026-06-01/2026-07-30", includes="participants")
        
        equipos_vistos = set()
        resultado = []
        
        for f in fixtures:
            # Filtrar manual por season
            if str(f.get('season_id')) != str(api_torneo_id): continue
            
            for p in f.get('participants', []):
                pid = str(p['id'])
                if pid not in equipos_vistos:
                    equipos_vistos.add(pid)
                    resultado.append({
                        'id_proveedor': pid,
                        'nombre': p.get('name', 'TBD'),
                        'bandera_url': p.get('image_path', '')
                    })
        return resultado

    def obtener_partidos(self, api_torneo_id):
        # Filtramos un rango amplio para todo el mundial
        fixtures = self._consultar(f"football/fixtures/between/2026-06-01/2026-07-30", includes="participants;state;round;scores")
        
        partidos = []
        for f in fixtures:
            if str(f.get('season_id')) != str(api_torneo_id): continue
            
            # Identificar Local vs Visitante
            parts = f.get('participants', [])
            local_ext = next((p for p in parts if p.get('meta', {}).get('location') == 'home'), {})
            visit_ext = next((p for p in parts if p.get('meta', {}).get('location') == 'away'), {})
            
            l_id = str(local_ext.get('id', '0'))
            v_id = str(visit_ext.get('id', '0'))
            
            if l_id == '0' or v_id == '0': continue
            
            estado_api = f.get('state', {}).get('short_name', 'NS')
            
            # Extracción del Round
            nombre_jornada = f.get('round', {}).get('name', "Etapa Regular")
            
            # Fecha
            try:
                fecha_obj = datetime.strptime(f['starting_at'], "%Y-%m-%d %H:%M:%S")
            except:
                fecha_obj = datetime.now(timezone.utc).replace(tzinfo=None)
                
            # Goles
            g_loc = None
            g_vis = None
            scores = f.get('scores', [])
            # Asumiendo 'type_id' u otra lógica en la API v3 para full time
            # Por simplicidad buscaremos lo que tenga 'participant_id'
            for s in scores:
                if str(s.get('participant_id')) == l_id and s.get('description') == 'CURRENT':
                    g_loc = s.get('score', {}).get('goals')
                elif str(s.get('participant_id')) == v_id and s.get('description') == 'CURRENT':
                    g_vis = s.get('score', {}).get('goals')

            partidos.append({
                'id_proveedor': str(f['id']),
                'equipo_local_id': l_id,
                'equipo_visitante_id': v_id,
                'fecha_hora': fecha_obj,
                'estado': estado_api, # NS o FT etc
                'goles_local_real': g_loc,
                'goles_visitante_real': g_vis,
                'jornada': nombre_jornada
            })
            
        return partidos
