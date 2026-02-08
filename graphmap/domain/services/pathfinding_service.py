"""
Servicio para encontrar el camino más corto entre ciudades usando A*

ANÁLISIS DE COMPLEJIDAD BIG O:

1. ALGORITMO A*:
   - Complejidad temporal: O(E log V)
     * E = número de aristas en el grafo
     * V = número de vértices (ciudades)
     * log V proviene de las operaciones del heap (heappush/heappop)

   - Complejidad espacial: O(V)
     * Almacena g_score, f_score, came_from para cada nodo visitado
     * El heap open_set puede contener hasta V elementos

2. HEURÍSTICA HAVERSINE:
   - Complejidad: O(1) - cálculo trigonométrico constante

3. RECONSTRUCCIÓN DEL CAMINO:
   - Complejidad: O(k) donde k = longitud del camino (k << V)

4. LOOKUP DE CIUDAD POR ID:
   - Complejidad: O(1) - acceso directo por hash map

TOTAL: O(E log V) - Óptimo para búsqueda de caminos en grafos ponderados
"""
import heapq
from typing import List, Dict, Optional
from graphmap.domain.model.entities.graph import CityGraph
from graphmap.domain.model.entities.city import City
from graphmap.domain.model.entities.geo_utils import GeoUtils


class PathfindingService:
    """Servicio para cálculo de caminos óptimos entre ciudades usando A*"""

    def __init__(self, graph: CityGraph, cities: List[City]):
        """
        Inicializa el servicio de búsqueda de caminos

        Args:
            graph: Grafo de ciudades construido con Delaunay
            cities: Lista completa de ciudades del dataset
        """
        self.graph = graph
        # Mapeo id -> city para acceso O(1)
        self.city_id_map = {city.id: city for city in cities}

    def _heuristic(self, city_id1: int, city_id2: int) -> float:
        """
        Heurística admisible: distancia Haversine (línea recta)
        Esta heurística NUNCA sobreestima la distancia real

        Complejidad: O(1)

        Args:
            city_id1: ID de la primera ciudad
            city_id2: ID de la segunda ciudad

        Returns:
            Distancia en km (heurística admisible)
        """
        city1 = self.city_id_map[city_id1]
        city2 = self.city_id_map[city_id2]
        return GeoUtils.haversine_distance(
            city1.lat, city1.lng,
            city2.lat, city2.lng
        )

    def a_star(self, start_id: int, goal_id: int) -> Optional[Dict]:
        """
        Algoritmo A* para encontrar el camino más corto entre dos ciudades.

        COMPLEJIDAD TEMPORAL: O(E log V)
        - E = número de aristas en el grafo
        - V = número de vértices (ciudades)
        - log V viene de las operaciones de heap (heappush/heappop)

        COMPLEJIDAD ESPACIAL: O(V)
        - Almacena g_score, f_score, came_from, open_set

        Args:
            start_id: ID de la ciudad origen
            goal_id: ID de la ciudad destino

        Returns:
            Dict con:
                - path: Lista con info de ciudades [{id, city, lat, lng}, ...]
                - distance: Distancia total en km
                - cities_explored: Número de ciudades exploradas
            None si no hay camino o las ciudades no existen
        """
        # Validar que las ciudades existan en el grafo - O(1)
        if start_id not in self.city_id_map or goal_id not in self.city_id_map:
            return None

        start = start_id
        goal = goal_id

        # g_score: costo real acumulado desde start hasta cada nodo
        g_score = {start: 0.0}

        # f_score: g(n) + h(n) - estimación total del costo
        f_score = {start: self._heuristic(start, goal)}

        # Priority queue: (f_score, city_id)
        # heapq mantiene el elemento con menor f_score en la raíz
        open_set = [(f_score[start], start)]

        # Para reconstruir el camino
        came_from = {}

        # Contador de ciudades exploradas (para análisis)
        cities_explored = 0

        # Bucle principal A*
        # En el peor caso, explora todos los nodos: O(V log V)
        # En cada nodo, revisa sus vecinos: O(E)
        # Complejidad total: O((V + E) log V) = O(E log V) en grafos conexos
        while open_set:
            # Extraer nodo con menor f_score (O(log V))
            current_f, current = heapq.heappop(open_set)
            cities_explored += 1

            # Si llegamos al objetivo, reconstruir camino
            if current == goal:
                return self._reconstruct_path(came_from, current, g_score[goal], cities_explored)

            # Explorar vecinos (O(grado promedio del nodo))
            for neighbor, edge_weight in self.graph.get_neighbors(current):
                # Calcular nuevo costo tentativo
                tentative_g = g_score[current] + edge_weight

                # Si encontramos un camino mejor (o es la primera vez)
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Actualizar mejor camino conocido
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)

                    # Agregar a open_set (O(log V))
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # No hay camino
        return None

    def _reconstruct_path(
        self,
        came_from: Dict[int, int],
        current: int,
        total_distance: float,
        cities_explored: int
    ) -> Dict:
        """
        Reconstruye el camino desde el objetivo hasta el inicio

        Complejidad: O(k) donde k es el largo del camino (k << V)

        Args:
            came_from: Diccionario de padres
            current: Nodo actual (objetivo)
            total_distance: Distancia total del camino
            cities_explored: Ciudades exploradas durante la búsqueda

        Returns:
            Dict con información del camino incluyendo coordenadas
        """
        path = []
        city_current = self.city_id_map[current]
        path.append({
            "id": city_current.id,
            "city": city_current.city,
            "lat": city_current.lat,
            "lng": city_current.lng
        })

        # Reconstruir desde goal hacia start
        while current in came_from:
            current = came_from[current]
            city = self.city_id_map[current]
            path.append({
                "id": city.id,
                "city": city.city,
                "lat": city.lat,
                "lng": city.lng
            })

        # Invertir para obtener start -> goal
        path.reverse()

        return {
            "path": path,
            "distance": round(total_distance, 2),
            "cities_explored": cities_explored,
            "path_length": len(path)
        }
