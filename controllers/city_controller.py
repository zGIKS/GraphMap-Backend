"""
Controlador para los endpoints relacionados con ciudades
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.city_service import CityService
from entities.city import City

# Crear un router para los endpoints de ciudades
router = APIRouter(
    prefix="/cities",
    tags=["cities"],
    responses={404: {"description": "Not found"}},
)

# Instanciar el servicio
city_service = CityService()


@router.get("/", response_model=List[City])
async def get_all_cities():
    """
    Endpoint que retorna todos los datos de ciudades del archivo Excel
    """
    return city_service.load_cities_from_excel()


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