"""
Controlador para los endpoints relacionados con el grafo de proximidad
"""
from fastapi import APIRouter, Query
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
async def get_graph_edges(lightweight: bool = Query(False, description="Solo source/target sin distancias")):
    """
    🚀 OPTIMIZACIÓN: Endpoint con modo ligero para máximo rendimiento
    """
    edges = graph_service.get_graph_edges()
    
    # Modo lightweight: solo conexiones sin distancias (reduce 30% el tamaño)
    if lightweight:
        light_edges = [
            {
                "source": edge["source"],
                "target": edge["target"]
            }
            for edge in edges
        ]
        return {
            "edges": light_edges,
            "total_edges": len(light_edges),
            "lightweight": True
        }
    
    return {
        "edges": edges,
        "total_edges": len(edges),
        "lightweight": False
    }


@router.get("/summary")
async def get_graph_summary() -> Dict:
    """
    Endpoint que retorna el resumen del grafo (nodos y aristas)
    """
    summary = graph_service.get_graph_summary()
    return summary