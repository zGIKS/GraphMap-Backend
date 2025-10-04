"""
Entidad que representa un grafo no dirigido con lista de adyacencia
"""
from typing import List, Tuple, Dict, Set


class CityGraph:
    """Grafo no dirigido que representa conexiones entre ciudades por proximidad"""

    def __init__(self):
        # Lista de adyacencia: {nodo: [(vecino, distancia), ...]}
        self.adj_list: Dict[int, List[Tuple[int, float]]] = {}

    def add_edge(self, u: int, v: int, weight: float):
        """Agrega arista bidireccional entre dos nodos con peso (distancia)

        Args:
            u: ID del primer nodo
            v: ID del segundo nodo
            weight: Peso de la arista (distancia)
        """
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
        """Retorna lista de aristas (u, v, distancia) sin duplicados

        Returns:
            Lista de tuplas (nodo_origen, nodo_destino, distancia)
        """
        edges = []
        visited: Set[Tuple[int, int]] = set()

        for u in self.adj_list:
            for v, dist in self.adj_list[u]:
                # Evitar aristas duplicadas en grafo no dirigido
                edge = tuple(sorted([u, v]))
                if edge not in visited:
                    visited.add(edge)
                    edges.append((u, v, dist))

        return edges

    def get_neighbors(self, node: int) -> List[Tuple[int, float]]:
        """Retorna los vecinos de un nodo con sus distancias

        Args:
            node: ID del nodo

        Returns:
            Lista de tuplas (vecino, distancia)
        """
        return self.adj_list.get(node, [])

    def num_nodes(self) -> int:
        """Retorna el número de nodos en el grafo"""
        return len(self.adj_list)

    def num_edges(self) -> int:
        """Retorna el número de aristas en el grafo"""
        return len(self.get_edges())