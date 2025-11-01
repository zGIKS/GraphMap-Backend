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
