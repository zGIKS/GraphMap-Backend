"""
Servicio para manejar operaciones relacionadas con grafos de ciudades
"""
from typing import List, Dict
from graphmap.domain.model.entities.graph import CityGraph
from graphmap.domain.services.city_service import CityService
from graphmap.domain.services.graph_builder import GraphBuilder


class GraphService:
    """Servicio para construir y consultar el grafo de ciudades"""

    # Caché estático del grafo para evitar reconstruirlo en cada request
    _graph_cache: CityGraph = None
    # 🚀 OPTIMIZACIÓN: Cache de aristas formateadas (evita re-formatear en cada request)
    _edges_cache: List[Dict] = None

    def __init__(self):
        self.city_service = CityService()

    def build_city_graph(self) -> CityGraph:
        """Construye el grafo de ciudades usando triangulación de Delaunay (con caché)"""
        # Retornar desde caché si ya existe
        if GraphService._graph_cache is not None:
            return GraphService._graph_cache

        # Cargar ciudades
        cities = self.city_service.load_cities_from_excel()

        # Preparar datos: (id, lat, lng)
        cities_data = [(city.id, city.lat, city.lng) for city in cities]

        # Construir grafo usando el builder
        graph = GraphBuilder.build_delaunay_graph(cities_data)

        # Guardar en caché
        GraphService._graph_cache = graph
        return graph

    def get_graph_edges(self) -> List[Dict]:
        """🚀 OPTIMIZACIÓN: Retorna aristas con caché de formateo"""
        
        # Usar caché si existe
        if GraphService._edges_cache is not None:
            return GraphService._edges_cache
        
        # Construir y formatear solo una vez
        graph = self.build_city_graph()
        edges = graph.get_edges()
        
        GraphService._edges_cache = [
            {
                "source": u,
                "target": v,
                "distance": round(dist, 6)
            }
            for u, v, dist in edges
        ]
        
        return GraphService._edges_cache

    def get_graph_summary(self) -> Dict:
        """Retorna resumen del grafo: número de nodos y aristas"""
        graph = self.build_city_graph()

        return {
            "num_nodes": graph.num_nodes(),
            "num_edges": graph.num_edges()
        }