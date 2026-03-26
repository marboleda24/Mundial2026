import requests
from datetime import datetime, timezone
from .api_base import ProveedorAPI

# Traducciones de equipos al español
TRANSLATIONS_TEAMS = {
    "Argentina": "Argentina",
    "Brazil": "Brasil",
    "France": "Francia",
    "England": "Inglaterra",
    "Spain": "España",
    "Germany": "Alemania",
    "Portugal": "Portugal",
    "Netherlands": "Países Bajos",
    "Italy": "Italia",
    "Belgium": "Bélgica",
    "Croatia": "Croacia",
    "Uruguay": "Uruguay",
    "Colombia": "Colombia",
    "Mexico": "México",
    "United States": "Estados Unidos",
    "Morocco": "Marruecos",
    "Japan": "Japón",
    "Senegal": "Senegal",
    "South Korea": "Corea del Sur",
    "Australia": "Australia",
    "Denmark": "Dinamarca",
    "Switzerland": "Suiza",
    "Ecuador": "Ecuador",
    "Chile": "Chile",
    "Peru": "Perú",
    "Iran": "Irán",
    "Saudi Arabia": "Arabia Saudita",
    "Canada": "Canadá",
    "Costa Rica": "Costa Rica",
    "Poland": "Polonia",
    # Agregar más si es necesario
}

# Traducciones de fases/jornadas
TRANSLATIONS_STAGES = {
    "GROUP_STAGE": "Fase de Grupos",
    "ROUND_OF_16": "Octavos de Final",
    "QUARTER_FINALS": "Cuartos de Final",
    "SEMI_FINALS": "Semifinales",
    "FINAL": "Final",
    "THIRD_PLACE": "Tercer Puesto",
    # Agregar más
}

class FootballDataAdapter(ProveedorAPI):
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key):
        super().__init__(api_key)
        self.headers = {"X-Auth-Token": self.api_key}

    def obtener_equipos(self, api_torneo_id):
        url = f"{self.BASE_URL}/competitions/{api_torneo_id}/teams"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            print(f"Error FootballData Equipos: {resp.text}")
            return []
        
        data = resp.json()
        equipos = []
        for t in data.get('teams', []):
            nombre_original = t.get('name', 'TBD')
            nombre_traducido = TRANSLATIONS_TEAMS.get(nombre_original, nombre_original)
            equipos.append({
                'id_proveedor': str(t['id']),
                'nombre': nombre_traducido,
                'bandera_url': t.get('crest', '')
            })
        return equipos

    def obtener_partidos(self, api_torneo_id):
        url = f"{self.BASE_URL}/competitions/{api_torneo_id}/matches"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            print(f"Error FootballData Partidos: {resp.text}")
            return []
        
        data = resp.json()
        partidos = []
        for m in data.get('matches', []):
            home = m.get('homeTeam', {})
            away = m.get('awayTeam', {})
            if not home.get('id') or not away.get('id'): 
                continue
            
            estado_api = m.get('status')
            # Mapeo a nuestro estándar ('NS' = No Iniciado, 'FT' = Finalizado)
            estado_local = 'NS'
            if estado_api in ['FINISHED', 'AWARDED']:
                estado_local = 'FT'
            elif estado_api in ['IN_PLAY', 'PAUSED']:
                estado_local = 'EN JUEGO'
            elif estado_api in ['CANCELED', 'POSTPONED']:
                estado_local = 'CANCELADO'

            score = m.get('score', {}).get('fullTime', {})
            g_loc = score.get('home')
            g_vis = score.get('away')

            # Parsear fecha UTC ISO8601 a datetime nativo (Naive UTC para DB clásica)
            # Ej: "2022-11-20T16:00:00Z"
            fecha_str = m.get('utcDate')
            try:
                # python 3.7+ fromisoformat soporta poco la Z, hacemos un replace para limpiar The Z.
                fecha_obj = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).replace(tzinfo=None)
            except:
                fecha_obj = datetime.now(timezone.utc).replace(tzinfo=None)

            jornada = m.get('matchday')
            nombre_jornada = f"Jornada {jornada}" if jornada else m.get('stage', 'Fase de Grupos')
            nombre_jornada = TRANSLATIONS_STAGES.get(nombre_jornada, nombre_jornada)

            partidos.append({
                'id_proveedor': str(m['id']),
                'equipo_local_id': str(home['id']),
                'equipo_visitante_id': str(away['id']),
                'fecha_hora': fecha_obj,
                'estado': estado_local,
                'goles_local_real': g_loc,
                'goles_visitante_real': g_vis,
                'jornada': nombre_jornada
            })
        return partidos
