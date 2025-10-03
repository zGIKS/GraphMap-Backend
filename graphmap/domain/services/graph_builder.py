"""
Servicio para construir grafos usando diferentes algoritmos de triangulación
"""
import numpy as np
from scipy.spatial import Delaunay
from typing import List, Tuple
from graphmap.domain.model.entities.graph import CityGraph
from graphmap.domain.model.entities.geo_utils import GeoUtils


class GraphBuilder:
    """Constructor de grafos de proximidad geográfica"""

    @staticmethod
    def build_delaunay_graph(cities_data: List[Tuple[int, float, float]], max_distance_km: float = None) -> CityGraph:
        """Construye grafo usando triangulación de Delaunay con proyección Web Mercator

        Args:
            cities_data: Lista de tuplas (id_ciudad, latitud, longitud)
            max_distance_km: Distancia máxima en km para conectar ciudades (None = sin límite)

        Returns:
            CityGraph con conexiones basadas en Delaunay
        """
        graph = CityGraph()

        if len(cities_data) < 3:
            # Delaunay requiere al menos 3 puntos
            return graph

        # Guardar coordenadas originales (lat, lon) para cálculo de distancias
        original_coords = np.array([(lat, lon) for _, lat, lon in cities_data])
        id_map = [city_id for city_id, _, _ in cities_data]

        # Paso 1: Convertir coordenadas geográficas a proyección Web Mercator
        mercator_points = np.array([
            GeoUtils.lat_lon_to_mercator(lat, lon)
            for _, lat, lon in cities_data
        ])

        # Paso 2: Calcular triangulación de Delaunay en coordenadas proyectadas
        tri = Delaunay(mercator_points)

        # Paso 3: Extraer aristas y calcular distancias reales con Haversine
        for simplex in tri.simplices:
            # Cada simplex es un triángulo con 3 vértices
            # Conectar cada par de vértices del triángulo
            for i in range(3):
                for j in range(i + 1, 3):
                    idx_u, idx_v = simplex[i], simplex[j]

                    # Usar coordenadas ORIGINALES para calcular distancia real
                    lat1, lon1 = original_coords[idx_u]
                    lat2, lon2 = original_coords[idx_v]

                    # Calcular distancia real en km usando Haversine
                    dist = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)

                    # Filtrar por distancia máxima si se especificó
                    if max_distance_km is None or dist <= max_distance_km:
                        graph.add_edge(id_map[idx_u], id_map[idx_v], dist)

        return graph