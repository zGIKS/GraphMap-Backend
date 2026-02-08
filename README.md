# GraphMap-Backend

## Resumen del Proyecto

**GraphMap** es un sistema backend desarrollado en Python que transforma datasets geográficos masivos de ciudades de Estados Unidos en grafos navegables de proximidad, permitiendo la visualización interactiva y el cálculo de rutas óptimas en tiempo real. El proyecto aborda la necesidad de herramientas digitales precisas para análisis geoespacial y navegación, similar a Google Maps, pero enfocado en contextos académicos y de investigación algorítmica.

### ¿Qué Problema Soluciona?

En un contexto donde Estados Unidos cuenta con más de 334 millones de habitantes distribuidos en miles de ciudades conectadas por una vasta red vial, GraphMap resuelve el desafío de convertir datos geográficos brutos (coordenadas lat/lon) en estructuras de grafos navegables que permitan:

- **Visualización interactiva** de miles de nodos y aristas en tiempo real
- **Cálculo de rutas óptimas** entre ciudades usando algoritmos de búsqueda
- **Análisis de conectividad regional** y topología geográfica
- **Simulación de costos de transporte** y planificación urbana

El sistema filtra conexiones irreales (como aristas interoceánicas) y garantiza precisión geográfica mientras mantiene rendimiento computacional eficiente.

### ¿Cómo Funciona?

El backend utiliza una arquitectura cliente-servidor desacoplada con API REST, procesando un dataset de 5,324 ciudades estadounidenses para construir un grafo de proximidad mediante:

1. **Proyección Web Mercator**: Convierte coordenadas esféricas (lat/lon) a un plano euclidiano  
   $$
   x = \frac{\text{lon} \times R}{180°}, \quad y = \frac{\ln\left(\tan\left(\frac{90° + \text{lat}}{2} \times \frac{\pi}{180°}\right)\right)}{(\pi/180°)} \times \frac{R}{180°}
   $$

2. **Triangulación de Delaunay**: Genera una malla planar óptima de conexiones cercanas  
   $$
   T_{\text{Delaunay}}(n) \in \mathcal{O}(n \log n)
   $$

3. **Filtrado por Distancia Haversine**: Calcula distancias geodésicas reales y filtra conexiones > 500 km  
   $$
   d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1) \cdot \cos(\text{lat}_2) \cdot \sin^2\left(\frac{\Delta\text{lon}}{2}\right)}\right)
   $$

4. **Búsqueda de Rutas con A***: Encuentra caminos óptimos usando heurística admisible  
   $$
   T_{\text{A*}} \in \mathcal{O}(E \log V)
   $$

### Arquitectura Técnica

- **Backend**: FastAPI + Uvicorn para APIs REST de alto rendimiento
- **Procesamiento**: SciPy/NumPy para algoritmos geométricos, Pandas para datos
- **Estructura de Datos**: Lista de adyacencia con complejidad $\mathcal{O}(V + E)$
- **Cache**: Construcción única del grafo con respuestas $\mathcal{O}(1)$ subsiguientes

### Estadísticas del Grafo Resultante

| Métrica | Valor |
|---------|-------|
| Nodos (ciudades) | 5,324 |
| Aristas (conexiones) | 15,957 |
| Relación E/V | 2.99 ≈ 3 (planar) |
| Distancia máxima | 500 km |
| Distancia promedio | 187.3 km |

### Complejidades Algorítmicas

| Operación | Complejidad | Archivo |
|-----------|-------------|---------|
| Proyección Web Mercator | $\mathcal{O}(n)$ | `geo_utils.py` |
| Triangulación Delaunay | $\mathcal{O}(n \log n)$ | `graph_builder.py` |
| Cálculo Haversine | $\mathcal{O}(n)$ | `graph_builder.py` |
| **Construcción total** | $\mathcal{O}(n \log n)$ | `graph_builder.py` |
| Consulta de aristas | $\mathcal{O}(E)$ | `graph_service.py` |
| Búsqueda A* | $\mathcal{O}(E \log V)$ | `pathfinding_service.py` |

### Instalación y Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000/docs` con documentación Swagger automática.

### Tecnologías Utilizadas

- **Python 3.12+**
- **FastAPI** - Framework web asíncrono
- **SciPy/NumPy** - Computación científica
- **Pandas** - Manipulación de datos
- **OpenAI** - Servicio de chatbot (opcional)

### Despliegue con Vercel Serverless

Vercel es una plataforma de despliegue que utiliza **funciones serverless** para ejecutar aplicaciones web sin necesidad de gestionar servidores dedicados. Las funciones serverless son piezas de código que se ejecutan en respuesta a eventos específicos (como solicitudes HTTP) y se escalan automáticamente según la demanda.

#### Cómo Funciona Vercel Serverless:

1. **Funciones como Servicio (FaaS)**: Cada endpoint de la API (como `/cities/` o `/graph/edges`) se convierte en una función serverless independiente que se ejecuta solo cuando se recibe una solicitud HTTP.

2. **Escalado Automático**: Vercel escala automáticamente el número de instancias de funciones según el tráfico. Si hay muchas solicitudes simultáneas, se crean más instancias; si el tráfico baja, se reducen.

3. **Tiempo de Ejecución Limitado**: Cada función tiene un tiempo máximo de ejecución (por defecto 10 segundos para hobby plan, hasta 300 segundos para pro). Esto es ideal para APIs rápidas como GraphMap, pero limita operaciones pesadas.

4. **Configuración con `vercel.json`**: El archivo `vercel.json` configura el despliegue:
   ```json
   {
     "version": 2,
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/api/index.py"
       }
     ]
   }
   ```
   - Todas las rutas (`/(.*)`) se redirigen a `/api/index.py`, que es el punto de entrada de la función serverless.
   - Vercel detecta automáticamente que es una aplicación Python y usa el runtime correspondiente.

5. **Ventajas para GraphMap**:
   - **Cero Mantenimiento**: No hay que gestionar servidores, actualizaciones o escalado.
   - **Pago por Uso**: Solo pagas por las ejecuciones reales (número de requests y duración).
   - **Integración con Git**: Despliegues automáticos desde GitHub/GitLab.
   - **Cache Global**: Vercel tiene una CDN global que acelera las respuestas.

6. **Limitaciones**:
   - **Estado Efímero**: Las funciones no mantienen estado entre ejecuciones. GraphMap usa cache estático en memoria, pero en serverless, el cache se reinicia en cada cold start.
   - **Tiempo de Inicio (Cold Start)**: La primera solicitud puede ser más lenta (~1-3 segundos) mientras se inicializa la función.
   - **Límites de Recursos**: Memoria limitada (hasta 3008 MB), CPU compartido.

### Contribuidores

- Dante Mateo Aleman Romano (U202319963)
- Neil Aldrin Wilhelm Curipaco Huayllani (U20231B866)

**Curso**: Complejidad Algorítmica - Sección 1398  
**Docente**: Abraham Sopla Maslucán  
**Institución**: Universidad Peruana de Ciencias Aplicadas (UPC)
