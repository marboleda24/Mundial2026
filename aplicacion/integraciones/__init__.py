from .sportmonks import SportMonksAdapter
from .footballdata import FootballDataAdapter

def obtener_adaptador(proveedor: str, api_key: str):
    """
    Factory para obtener el Adapter adecuado de la API deportiva basado en la configuración del Torneo.
    """
    proveedor = proveedor.lower().strip()
    
    if proveedor == 'footballdata':
        return FootballDataAdapter(api_key)
    elif proveedor == 'sportmonks':
        return SportMonksAdapter(api_key)
    else:
        raise ValueError(f"Proveedor API no soportado: {proveedor}. Opciones: 'footballdata', 'sportmonks'")
