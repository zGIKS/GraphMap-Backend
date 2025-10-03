[TOC]

# 1. Descripción del problema

Estados Unidos cuenta actualmente con una población superior a los 334 millones de habitantes (U.S. Census Bureau, 2024) distribuidos en miles de ciudades, pueblos y áreas metropolitanas conectadas por una vasta red vial y de transporte. Esta magnitud demográfica y territorial genera un ecosistema urbano complejo que demanda herramientas digitales de navegación y análisis geoespacial cada vez más precisas y escalables.

En el día a día, tanto ciudadanos como empresas enfrentan el reto de ubicar destinos y determinar las rutas óptimas para llegar a ellos, ya sea para transporte personal, logística de entregas, servicios de emergencia o planificación urbana. Herramientas como Google Maps han demostrado el valor de contar con aplicaciones que integren datos geográficos en tiempo real para buscar un punto de destino y calcular el camino más eficiente, permitiendo mejorar la movilidad y optimizar recursos.

Sin embargo, en escenarios académicos o de investigación algorítmica, existe una brecha entre los datasets geográficos brutos (que suelen presentarse solo como listas de coordenadas y distancias) y la capacidad de transformarlos en grafos navegables de gran escala que puedan ser explorados de manera interactiva. Problemas como la planificación de rutas entre miles de ciudades, el análisis de conectividad regional y la simulación de costos de transporte requieren no solo algoritmos robustos de grafos, sino también interfaces capaces de visualizar y manipular decenas de miles de nodos y aristas en tiempo real.

El proyecto GraphMap busca atender esta necesidad mediante el desarrollo de una solución que transforme datasets masivos de ciudades de EE. UU. en una red de proximidad geográfica y permita al usuario explorar interactivamente la topología resultante, simulando la funcionalidad esencial de “buscar el camino para llegar de un punto A a un punto B”. De este modo, se facilita el estudio, validación y aplicación de algoritmos de búsqueda y optimización en contextos de gran escala.



## 1.1 Contexto y Problemática Operativa

El presente proyecto parte de un archivo de datos, excel de extensión por `.xlsx`, que contiene miles de registros de ciudades de Estados Unidos con identificador, nombre y coordenadas geográficas. A partir de esta base, el backend tiene la tarea de cargar y normalizar los datos, construir una estructura de grafo que represente relaciones de vecindad realistas entre ciudades y exponer únicamente los campos esenciales que requiere el cliente para el renderizado: los nodos con `id`, `lat`, `lng` y las aristas con `source` y `target`. Este enfoque permite que el frontend, basado en WebGL, procese grandes volúmenes de información geográfica de manera eficiente.

La problemática operativa se centra en garantizar que la construcción y el servicio del grafo escalen adecuadamente para procesar miles de nodos y decenas de miles de aristas sin agotar los recursos de memoria o CPU. El sistema debe filtrar conexiones irreales que suelen surgir debido a efectos de la proyección cartográfica —por ejemplo, aristas interoceánicas entre puntos que en el plano aparecen cercanos, pero que en realidad se encuentran separados por grandes cuerpos de agua—. Asimismo, debe entregar respuestas compactas y consistentes para que el cliente WebGL pueda visualizar más de 5 000 nodos y alrededor de 16 000 aristas con baja latencia y mantener la interactividad en tiempo real. Otro desafío relevante es la calidad de los datos: el backend debe ser robusto frente a registros incompletos, identificadores duplicados o coordenadas extremas y, además, debe evitar reconstrucciones costosas utilizando mecanismos de caché, preprocesamiento off-line y compresión de las respuestas.

Un aspecto crítico es la tensión entre precisión geográfica y coste computacional. Calcular una topología de proximidad estricta a partir de coordenadas geodésicas implica operaciones mucho más costosas que aproximaciones simplificadas como el k-NN plano. Para equilibrar precisión y rendimiento, el backend adopta una estrategia híbrida: primero proyecta las coordenadas latitud/longitud a **Web Mercator**, que permite operar en un espacio euclidiano; después aplica la **triangulación de Delaunay** para generar una malla planar de proximidad inicial y, finalmente, calcula la **distancia geodésica** de cada arista candidata usando la **fórmula de Haversine**, filtrando aquellas que superan un umbral realista (por ejemplo, 500 km). El grafo resultante se representa como **lista de adyacencia**, lo que permite realizar recorridos y consultas en un tiempo proporcional a:

$$
\mathcal{O}(V + E)
$$

donde \(V\) es el número de nodos y \(E\) el número de aristas.

Los costos dominantes de este proceso corresponden a la **proyección Web Mercator** con complejidad lineal **O(n)**, la **triangulación de Delaunay** con:

 

$$ T_\text{Delaunay}(n) \in \mathcal{O}(n \log n) $$

 

y el cálculo de **distancias Haversine** sobre los aproximadamente **2n triángulos** generados por Delaunay:

 

$$ T_\text{Haversine}(n) \in \mathcal{O}(n) $$

 

El costo total de construcción del grafo es:

 

$$ T_\text{construcción}(n) \in \mathcal{O}(n \log n) $$

 

mientras que el uso de memoria se mantiene en:

 

$$ M(V,E) \in \mathcal{O}(V + E) \approx \mathcal{O}(3V) = \mathcal{O}(V) $$

 

(para grafos planares donde **E ≈ 3V**).

 

Las **consultas** posteriores (GET /graph/edges) operan en:

 

$$ T_\text{consulta}(E) \in \mathcal{O}(E) $$

 

pero gracias al **caché estático**, la construcción ocurre **una sola vez** al inicio del servidor.

Para el caso de estudio, que incluye **5 324 nodos** y **≈ 15 957 aristas**, estos costos son manejables siempre que se eviten reconstrucciones innecesarias y se implementen estrategias de caché. Este planteamiento operativo permite que el sistema ofrezca una visualización masiva, precisa e interactiva de grafos geográficos con capacidad de consulta en tiempo real, logrando un equilibrio entre rendimiento y fidelidad espacial.



## 1.2 Fundamentación Algorítmica

1. **Proyección Web Mercator**

$$
x = \frac{\text{lon} \times R}{180°}
$$

$$
y = \frac{\ln\left(\tan\left(\frac{90° + \text{lat}}{2} \times \frac{\pi}{180°}\right)\right)}{(\pi/180°)} \times \frac{R}{180°}
$$

Donde:
- $R = 20\,037\,508.34$ metros (rango de proyección Web Mercator)
- $\text{lat}$ está limitado entre $-85.0511°$ y $85.0511°$ (límites de la proyección)

**¿Por qué se usa?**
- Convierte coordenadas esféricas (lat/lon) a un plano euclidiano donde las distancias son aproximadamente lineales
- Permite aplicar algoritmos geométricos planos (Delaunay) sin distorsión excesiva en latitudes medias
- Es el estándar usado en mapas web (Google Maps, OpenStreetMap)

**¿Cómo se obtiene el O(n)?**
```python
# Líneas 35-39 de graph_builder.py
mercator_points = np.array([
    GeoUtils.lat_lon_to_mercator(lat, lon)  # O(1) por ciudad
    for _, lat, lon in cities_data           # n ciudades
])
```
- Se itera sobre **n ciudades** exactamente una vez
- Cada conversión es **O(1)** (solo operaciones aritméticas y logaritmo)
- **Total: O(n)**



2. **Triangulación de Delaunay**

$$
T_{\text{Delaunay}}(n) \in \mathcal{O}(n \log n)
$$

**¿Por qué se usa?**

- Genera una malla de triángulos que conecta puntos cercanos de forma óptima
- Maximiza el ángulo mínimo de los triángulos (evita triángulos degenerados)
- Produce **exactamente ~2n triángulos** y **~3n aristas** en el plano (teorema de Euler para grafos planares)
- Es el grafo planar de proximidad más natural para datos geográficos

**¿Cómo se obtiene el O(n log n)?**
- **Scipy utiliza el algoritmo Bowyer-Watson o divide y conquista**
- Divide el conjunto de puntos recursivamente → $\log n$ niveles
- En cada nivel procesa todos los puntos → $n$ operaciones
- **Total: O(n log n)**

**Teorema de Euler (grafos planares):**
Para un grafo planar conexo:
$$
V - E + F = 2
$$
Donde $F \approx 2n$ (triángulos), entonces:
$$
n - E + 2n = 2 \implies E \approx 3n
$$



3. **Distancia Haversine**

$$
a = \sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1) \cdot \cos(\text{lat}_2) \cdot \sin^2\left(\frac{\Delta\text{lon}}{2}\right)
$$

$$
c = 2 \cdot \arcsin(\sqrt{a})
$$

$$
d = R_{\text{Tierra}} \cdot c
$$

Donde:
- $R_{\text{Tierra}} = 6371$ km (radio medio de la Tierra)
- $\Delta\text{lat} = \text{lat}_2 - \text{lat}_1$ (en radianes)
- $\Delta\text{lon} = \text{lon}_2 - \text{lon}_1$ (en radianes)

**¿Por qué se usa?**
- Calcula la **distancia geodésica real** sobre la superficie esférica de la Tierra
- Más precisa que la distancia euclidiana en coordenadas proyectadas
- Permite filtrar conexiones irreales (> 500 km) para evitar aristas interoceánicas

**¿Cómo se obtiene el O(n)?**
```python
# Líneas 44-61 de graph_builder.py
for simplex in tri.simplices:        # ~2n triángulos (Delaunay planar)
    for i in range(3):
        for j in range(i + 1, 3):    # 3 aristas por triángulo
            # Calcular Haversine
            dist = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)  # O(1)
```
- **~2n triángulos** × **3 aristas/triángulo** = **~6n cálculos Haversine**
- Cada Haversine es **O(1)** (solo trigonometría básica)
- **Total: O(n)** (lineal en número de nodos)

**Nota:** Aunque se calculan ~6n distancias, el código evita duplicados al agregar aristas al grafo (línea 28-31 de `graph.py`).



4. **Complejidad Total de Construcción**

$$
T_{\text{construcción}}(n) = T_{\text{proyección}}(n) + T_{\text{Delaunay}}(n) + T_{\text{Haversine}}(n)
$$

$$
= \mathcal{O}(n) + \mathcal{O}(n \log n) + \mathcal{O}(n) = \mathcal{O}(n \log n)
$$

**El término dominante es Delaunay**, por lo que la complejidad total es **O(n log n)**.



5. **Complejidad de Memoria**

$$
M(V, E) \in \mathcal{O}(V + E)
$$

**Desglose:**
- **Nodos en lista de adyacencia:** $\mathcal{O}(V)$ → diccionario con $V$ claves
- **Aristas bidireccionales:** $\mathcal{O}(E)$ → cada arista se almacena 2 veces (u→v, v→u)

**Para grafos planares (Delaunay):**
$$
E \approx 3V \implies M(V, E) = \mathcal{O}(V + 3V) = \mathcal{O}(V)
$$


```python
# Estructura de lista de adyacencia
self.adj_list: Dict[int, List[Tuple[int, float]]] = {}
```



6. **Complejidad de Consultas**

$$
T_{\text{consulta}}(E) \in \mathcal{O}(E)
$$

**¿Dónde se aplica?**


```python
def get_graph_edges(self) -> List[Dict]:
    graph = self.build_city_graph()  # O(1) si está cacheado
    edges = graph.get_edges()        # O(E) - itera todas las aristas
    return edges
```

```python
for u in self.adj_list:           # O(V) nodos
    for v, dist in self.adj_list[u]:  # O(grado(u)) vecinos
        if edge not in visited:
            edges.append((u, v, dist))
```
- **Suma total de grados = 2E** (cada arista cuenta 2 veces)

- **Complejidad: O(V + 2E) = O(E)** (para grafos donde E ≥ V)

  


7. Impacto del Caché Estático


```python
class GraphService:
    _graph_cache: CityGraph = None  # Caché estático

    def build_city_graph(self) -> CityGraph:
        if GraphService._graph_cache is not None:
            return GraphService._graph_cache  # O(1)

        # Construcción: O(n log n)
        graph = GraphBuilder.build_delaunay_graph(cities_data, max_distance_km=500)
        GraphService._graph_cache = graph
        return graph
```

**Complejidad amortizada:**
- **Primera request:** $\mathcal{O}(n \log n)$
- **Requests subsecuentes:** $\mathcal{O}(1)$ para obtener el grafo + $\mathcal{O}(E)$ para iterar aristas
- **Promedio sobre k requests:** $\frac{\mathcal{O}(n \log n) + k \cdot \mathcal{O}(E)}{k} \approx \mathcal{O}(E)$ cuando $k \gg 1$



8. Filtrado por Distancia Máxima


```python
if max_distance_km is None or dist <= max_distance_km:
    graph.add_edge(id_map[idx_u], id_map[idx_v], dist)
```

**Impacto:**
- **Sin filtro:** E ≈ 3n aristas (Delaunay completo)
- **Con filtro (500 km):** E ≈ 3n aristas teóricas, pero **elimina ~30-40% de aristas largas** (Hawaii↔California, etc.)
- **Resultado observado:** 15,957 aristas para 5,324 nodos → **E/V ≈ 3** (confirma estructura planar)

**No afecta la complejidad asintótica**, pero **reduce el factor constante** en memoria y transferencia de datos.


Resumen de Complejidades por Operación

| Operación | Complejidad | Archivo .py |
|-----------|-------------|------------------------|
| Proyección Web Mercator | $\mathcal{O}(n)$ | `geo_utils.py:16-34` |
| Triangulación Delaunay | $\mathcal{O}(n \log n)$ | `graph_builder.py:41` |
| Cálculo Haversine (todas aristas) | $\mathcal{O}(n)$ | `graph_builder.py:44-61` |
| **Construcción total** | $\mathcal{O}(n \log n)$ | `graph_builder.py:15-63` |
| Almacenamiento (lista adyacencia) | $\mathcal{O}(V + E) = \mathcal{O}(V)$ | `graph.py:10-31` |
| Consulta de aristas | $\mathcal{O}(E)$ | `graph_service.py:40-60` |
| Caché (requests subsecuentes) | $\mathcal{O}(1)$ grafo + $\mathcal{O}(E)$ iteración | `graph_service.py:24-25` |

## 1.3 Relevancia y Objetivos del Estudio

1. ABET 4 - Responsabilidad y ética 

La capacidad de reconocer responsabilidades éticas y profesionales en situaciones de ingeniería y hacer juicios informados, que deben considerar el impacto de las soluciones de ingeniería en contextos globales, económicos, ambientales y sociales\



explicar los objetivos de aprender los algoritomos delaunay etc 

# 2. Descripción y visualización del conjunto de datos (dataset)

RESUMEN DE LO QUE SE HARA EN EL CAP

## 2.1 Origen de Dato

como se descargo 

https://simplemaps.com/

explicar a que se dedica simple maps xd

## 2.2 Características del dataset

explicar las columnas los tipos de datos que hay y las interfaces en el codigo sobre como se representan

## 2.3 Preprocesamiento y construcción del grafo

LOS ALGORITMOS EXPLICADOS ARRIBA

## 2.4 Estadísticas del grafo

LOS NODOS Y LAS CONEXIONES QUE YA EXPLOQUE ARRIBA

## 2.5 Visualización

PRIMERO INTRODUCCION LUEGO EXPLOICAR CADA GRAFICO O IMAGEN QUE REPRESENTA A QUE PERTENECE

**Figura 1.**

<img src="https://i.imgur.com/QOeAz9V.png"/>

**Figura 2.**

<img src="https://i.imgur.com/C0wTKk6.png"/>

**Figura 3.**

<img src="https://i.imgur.com/84qfCiq.png"/>

**Figura 4.**

<img src="https://i.imgur.com/mG9k4iM.png"/>

**Figura 5.**

<img src="https://i.imgur.com/YkFePGv.png"/>

# 3. Propuesta

RESUMEN DE LO QUE SE HARA EN EL CAP

## 3.1 Objetivo de la propuesta

QUE PRETENDEMOS RESOLVER Y PLANTEAR UN PROBLEM STATMENT CON PREGUNTA ASI COMO OPEN SOURCE

## 3.2 Técnicas a utilizar

LAS FORMULAS QUE SE USARON X2

# 4. Diseño del aplicativo

## 4.1 Arquitectura Tecnológica

## 4.2 Módulo de Procesamiento de Datos

## 4.3 Módulo de Lógica de Ruteo

## 4.4 Módulo de Interfaz y Visualización

# 5. Validación de resultados y pruebas

## 5.1 Proceso de ejecución de la aplicación

## 5.2 Casos de prueba seleccionados

## 5.3 Interpretación de resultados

## 5.4 Pruebas de robustez y límites



# 6. Conclusiones

COMPLETAR



# 7. Bibliografía

https://www.census.gov/library/stories/2024/12/population-estimates.html



https://imgur.com/a/GzTPesS
