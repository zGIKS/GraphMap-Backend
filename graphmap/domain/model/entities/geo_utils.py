"""
Utilidades para cálculos geográficos y proyecciones cartográficas
"""
import numpy as np
from typing import Tuple


class GeoUtils:
    """Clase con métodos estáticos para conversiones y cálculos geográficos"""

    # Constantes
    MERCATOR_RANGE = 20037508.34  # Rango de proyección Web Mercator
    EARTH_RADIUS_KM = 6371.0      # Radio de la Tierra en kilómetros

    @staticmethod
    def lat_lon_to_mercator(lat: float, lon: float) -> Tuple[float, float]:
        """Convierte coordenadas geográficas (lat, lon) a proyección Web Mercator

        Args:
            lat: Latitud en grados
            lon: Longitud en grados

        Returns:
            Tupla (x, y) en coordenadas Web Mercator
        """
        # Convertir longitud
        x = lon * GeoUtils.MERCATOR_RANGE / 180.0

        # Convertir latitud (con protección contra valores extremos)
        lat = np.clip(lat, -85.0511, 85.0511)  # Límites de Web Mercator
        y = np.log(np.tan((90 + lat) * np.pi / 360.0)) / (np.pi / 180.0)
        y = y * GeoUtils.MERCATOR_RANGE / 180.0

        return (x, y)

    @staticmethod
    def haversine_distance(lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """Calcula distancia Haversine (en km) entre dos coordenadas geográficas

        Args:
            lat1, lon1: Coordenadas del primer punto (grados)
            lat2, lon2: Coordenadas del segundo punto (grados)

        Returns:
            Distancia en kilómetros
        """
        # Convertir grados a radianes
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)

        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Fórmula de Haversine
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return GeoUtils.EARTH_RADIUS_KM * c