"""
Controlador para los endpoints relacionados con el grafo de proximidad
"""
from fastapi import APIRouter
from typing import Dict
from graphmap.domain.services.graph_service import GraphService

# Crear un router para los endpoints del grafo
router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)

# Instanciar servicio
graph_service = GraphService()


@router.get("/edges")
async def get_graph_edges():
    """
    Endpoint optimizado automáticamente para conexiones del mapa
    Retorna solo source y target (sin distancias)
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