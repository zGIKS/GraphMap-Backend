"""
Controlador para los endpoints relacionados con el grafo de proximidad
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict
from graphmap.domain.services.graph_service import GraphService
from graphmap.domain.services.pathfinding_service import PathfindingService
from graphmap.domain.services.city_service import CityService

# Crear un router para los endpoints del grafo
router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)

# Instanciar servicios
graph_service = GraphService()
city_service = CityService()


@router.get("/edges")
async def get_graph_edges():
    """
    Endpoint que retorna las conexiones del grafo
    """
    edges = graph_service.get_graph_edges()
    
    # Datos automáticamente optimizados para conexiones
    optimized_edges = [
        {
            "source": edge["source"],
            "target": edge["target"]
        }
        for edge in edges
    ]
    
    return {
        "edges": optimized_edges,
        "total_edges": len(optimized_edges)
    }


@router.get("/summary")
async def get_graph_summary() -> Dict:
    """
    Endpoint que retorna el resumen del grafo (nodos y aristas)
    """
    summary = graph_service.get_graph_summary()
    return summary


@router.get("/shortest-path")
async def find_shortest_path(
    start_id: int = Query(..., description="ID de la ciudad origen", ge=0),
    goal_id: int = Query(..., description="ID de la ciudad destino", ge=0)
) -> Dict:
    """
    Endpoint que encuentra el camino más corto entre dos ciudades usando A*
    """
    # Construir grafo y cargar ciudades (con caché)
    graph = graph_service.build_city_graph()
    cities = city_service.load_cities_from_excel()

    # Inicializar servicio de pathfinding
    pathfinding = PathfindingService(graph, cities)

    # Ejecutar A*
    result = pathfinding.a_star(start_id, goal_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró camino entre ciudad {start_id} y ciudad {goal_id}, o las ciudades no existen en el grafo"
        )

    return result