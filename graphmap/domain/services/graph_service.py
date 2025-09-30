"""
Servicio para manejar operaciones relacionadas con grafos de ciudades
"""
from typing import List, Dict, Tuple
from graphmap.domain.model.entities.graph import CityGraph
from graphmap.domain.services.city_service import CityService


class GraphService:
    """Servicio para construir y consultar el grafo de ciudades"""

    def __init__(self):
        self.city_service = CityService()
        self.graph = None

    def build_city_graph(self) -> CityGraph:
        """Construye el grafo de ciudades usando conexiones por proximidad"""
        # Cargar ciudades
        cities = self.city_service.load_cities_from_excel()

        # Preparar datos: (id, lat, lng)
        cities_data = [(city.id, city.lat, city.lng) for city in cities]

        # Construir grafo
        self.graph = CityGraph()
        self.graph.build_from_delaunay(cities_data)

        return self.graph

    def get_graph_edges(self) -> List[Dict]:
        """Retorna las aristas del grafo en formato JSON"""
        if self.graph is None:
            self.build_city_graph()

        edges = self.graph.get_edges()
        return [
            {
                "source": u,
                "target": v,
                "distance": round(dist, 6)
            }
            for u, v, dist in edges
        ]

    def get_graph_summary(self) -> Dict:
        """Retorna resumen del grafo: número de nodos y aristas"""
        if self.graph is None:
            self.build_city_graph()

        num_nodes = len(self.graph.adj_list)
        num_edges = len(self.graph.get_edges())

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges
        }