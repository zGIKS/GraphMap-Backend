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
    Endpoint optimizado automáticamente para el mapa
    Retorna solo los campos esenciales: id, city, lat, lng
    """
    cities = city_service.load_cities_from_excel()
    
    # Datos automáticamente optimizados para el mapa
    city_data = [
        {
            "id": city.id,
            "city": city.city,
            "lat": city.lat,
            "lng": city.lng
        }
        for city in cities
    ]

    return {
        "cities": city_data,
        "total": len(city_data)
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
    Búsqueda de ciudades por nombre - retorna TODOS los resultados
    """
    results = city_service.search_cities(query)
    return results  # Sin límite - devuelve todos los resultados encontrados