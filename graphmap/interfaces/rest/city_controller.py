"""
Controlador para los endpoints relacionados con ciudades
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from graphmap.domain.services.city_service import CityService
from graphmap.domain.services.graph_service import GraphService
from graphmap.domain.model.entities.city import City

# Crear un router para los endpoints de ciudades
router = APIRouter(
    prefix="/cities",
    tags=["cities"],
    responses={404: {"description": "Not found"}},
)

# Instanciar servicios
city_service = CityService()
graph_service = GraphService()


@router.get("/")
async def get_all_cities():
    """
    Endpoint que retorna ciudades y aristas del grafo de proximidad
    """
    # Cargar ciudades
    cities = city_service.load_cities_from_excel()

    # Construir grafo y obtener aristas
    edges = graph_service.get_graph_edges()
    summary = graph_service.get_graph_summary()

    return {
        "cities": [city.dict() for city in cities],
        "edges": edges,
        "graph_info": summary
    }


@router.get("/count")
async def get_cities_count():
    """
    Endpoint que retorna el número total de ciudades
    """
    total = city_service.get_cities_count()
    return {"total_cities": total}


@router.get("/{query}", response_model=List[City])
async def get_cities_name(query: str):
    """
    Endpoint que busca ciudades por nombre
    """
    return city_service.search_cities(query)