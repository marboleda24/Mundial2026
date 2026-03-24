from abc import ABC, abstractmethod

class ProveedorAPI(ABC):
    """Interfaz abstracta para múltiples proveedores de datos deportivos (Adapters)"""

    def __init__(self, api_key):
        self.api_key = api_key

    @abstractmethod
    def obtener_equipos(self, api_torneo_id):
        """
        Extrae y normaliza los equipos del torneo.
        Debe retornar:
        [
            {
                'id_proveedor': str,
                'nombre': str,
                'bandera_url': str
            }, ...
        ]
        """
        pass

    @abstractmethod
    def obtener_partidos(self, api_torneo_id):
        """
        Extrae y normaliza los partidos del torneo.
        Debe retornar:
        [
            {
                'id_proveedor': str,
                'equipo_local_id': str,
                'equipo_visitante_id': str,
                'fecha_hora': datetime,
                'estado': str (preferiblemente 'NS' No Iniciado o 'FT' Finalizado),
                'goles_local_real': int o None,
                'goles_visitante_real': int o None,
                'jornada': str
            }, ...
        ]
        """
        pass
