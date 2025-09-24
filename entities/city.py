from pydantic import BaseModel, computed_field
from typing import Optional
import numpy as np


class City(BaseModel):
    """Entidad que representa una ciudad con todos sus datos del dataset"""
    city: str
    city_ascii: str
    lat: float
    lng: float
    country: str
    iso2: str
    iso3: str
    admin_name: str
    capital: str
    population: Optional[int] = None
    id: int

    @computed_field
    @property
    def mercator_x(self) -> float:
        """
        Función calculada automáticamente - O(1) - Conversión lineal
        Convierte longitud a coordenada X de Mercator
        """
        # Radio terrestre en metros (WGS84)
        radio_tierra = 6378137.0
        # Conversión directa: X = Radio × longitud_en_radianes
        return radio_tierra * np.radians(self.lng)

    @computed_field
    @property
    def mercator_y(self) -> float:
        """
        Función calculada automáticamente - O(1) - Transformación logarítmica
        Convierte latitud a coordenada Y de Mercator usando fórmula de proyección
        """
        # Radio terrestre en metros
        radio_tierra = 6378137.0
        # Convertir latitud a radianes
        latitud_radianes = np.radians(self.lat)
        # Fórmula Mercator: Y = R × ln(tan(π/4 + lat/2))
        # Esta fórmula "estira" las coordenadas cerca de los polos
        return radio_tierra * np.log(np.tan(np.pi/4 + latitud_radianes/2))

    def convertir_a_mercator(self):
        """
        Método de instancia - O(1) - Transformación geográfica a 2D
        Convierte las coordenadas geográficas de esta ciudad a sistema Mercator

        Returns:
            tuple: (coordenada_x, coordenada_y) en metros desde el meridiano 0° y ecuador
        """
        radio_tierra = 6378137.0  # Radio WGS84 en metros

        # Longitud -> X: conversión lineal simple
        coordenada_x = radio_tierra * np.radians(self.lng)

        # Latitud -> Y: transformación logarítmica para proyección cilíndrica
        latitud_radianes = np.radians(self.lat)
        coordenada_y = radio_tierra * np.log(np.tan(np.pi/4 + latitud_radianes/2))

        return (coordenada_x, coordenada_y)

    @staticmethod
    def proyeccion_mercator(latitud, longitud):
        """
        Función estática - O(1) - Algoritmo de proyección cartográfica
        Transforma cualquier coordenada geográfica a sistema Mercator (como Google Maps)

        Args:
            latitud (float): Latitud en grados (-90 a +90)
            longitud (float): Longitud en grados (-180 a +180)

        Returns:
            tuple: (x, y) coordenadas en metros en proyección Mercator

        Nota:
            - X representa distancia horizontal desde meridiano Greenwich
            - Y representa distancia vertical desde ecuador (distorsionada hacia polos)
        """
        radio_tierra = 6378137.0  # Radio terrestre estándar WGS84

        # Conversión de longitud (lineal): X = R × longitud_radianes
        x = radio_tierra * np.radians(longitud)

        # Conversión de latitud (logarítmica): Y = R × ln(tan(π/4 + lat_radianes/2))
        latitud_radianes = np.radians(latitud)
        y = radio_tierra * np.log(np.tan(np.pi/4 + latitud_radianes/2))

        return (x, y)