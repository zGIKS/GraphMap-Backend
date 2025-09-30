"""
Controlador para los endpoints relacionados con ciudades
"""
from fastapi import APIRouter
from typing import List
from graphmap.domain.services.city_service import CityService
from graphmap.domain.model.entities.city import City

# Crear un router para los endpoints de ciudades
router = APIRouter(
    prefix="/cities",
    tags=["cities"],
    responses={404: {"description": "Not found"}},
)

# Instanciar servicio
city_service = CityService()


@router.get("/")
async def get_all_cities():
    """
    Endpoint que retorna solo la lista de ciudades (sin grafo)
    """
    # Cargar ciudades (desde caché si ya fueron cargadas)
    cities = city_service.load_cities_from_excel()

    return {
        "cities": [city.dict() for city in cities],
        "total": len(cities)
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