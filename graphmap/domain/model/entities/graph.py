"""
Entidad que representa un grafo con triangulación de Delaunay
"""
import numpy as np
from typing import List, Tuple


class CityGraph:
    """Grafo no dirigido que representa conexiones entre ciudades por proximidad"""

    def __init__(self):
        # Lista de adyacencia: {nodo: [(vecino, distancia), ...]}
        self.adj_list = {}

    def add_edge(self, u: int, v: int, weight: float):
        """Agrega arista bidireccional entre dos nodos con peso (distancia)"""
        if u not in self.adj_list:
            self.adj_list[u] = []
        if v not in self.adj_list:
            self.adj_list[v] = []
        # Evitar duplicados
        if not any(vec == v for vec, _ in self.adj_list[u]):
            self.adj_list[u].append((v, weight))
        if not any(vec == u for vec, _ in self.adj_list[v]):
            self.adj_list[v].append((u, weight))

    def get_edges(self) -> List[Tuple[int, int, float]]:
        """Retorna lista de aristas (u, v, distancia) sin duplicados"""
        edges = []
        visited = set()
        for u in self.adj_list:
            for v, dist in self.adj_list[u]:
                # Evitar aristas duplicadas en grafo no dirigido
                edge = tuple(sorted([u, v]))
                if edge not in visited:
                    visited.add(edge)
                    edges.append((u, v, dist))
        return edges

    def calculate_distance(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """Calcula distancia euclidiana entre dos coordenadas (lat, lon)"""
        return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

    def build_from_delaunay(self, cities_data: List[Tuple[int, float, float]]):
        """Construye grafo conectando cada ciudad con sus k vecinos más cercanos
        Args:
            cities_data: Lista de tuplas (id_ciudad, latitud, longitud)
        """
        n = len(cities_data)
        k = min(5, n - 1)  # Conectar cada nodo con 5 vecinos cercanos
        points = np.array([(lat, lon) for _, lat, lon in cities_data])
        id_map = [city_id for city_id, _, _ in cities_data]

        # Para cada ciudad, encontrar k vecinos más cercanos
        for i in range(n):
            lat1, lon1 = points[i]
            # Calcular distancias a todas las demás ciudades
            distances = []
            for j in range(n):
                if i != j:
                    lat2, lon2 = points[j]
                    dist = self.calculate_distance(lat1, lon1, lat2, lon2)
                    distances.append((j, dist))
            # Ordenar por distancia y tomar k más cercanos
            distances.sort(key=lambda x: x[1])
            for j, dist in distances[:k]:
                self.add_edge(id_map[i], id_map[j], dist)