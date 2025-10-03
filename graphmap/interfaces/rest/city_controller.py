"""
Controlador para los endpoints relacionados con ciudades
"""
from fastapi import APIRouter, Query
from typing import List, Optional
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
async def get_all_cities(
    lightweight: bool = Query(False, description="Solo campos esenciales para mapa"),
    limit: Optional[int] = Query(None, description="Limitar resultados")
):
    """
    🚀 OPTIMIZACIÓN: Endpoint con opciones de datos ligeros
    """
    cities = city_service.load_cities_from_excel()
    
    # Aplicar límite si se especifica
    if limit:
        cities = cities[:limit]
    
    # Modo lightweight: solo campos esenciales (reduce 60% el tamaño)
    if lightweight:
        city_data = [
            {
                "id": city.id,
                "city": city.city,
                "lat": city.lat,
                "lng": city.lng
            }
            for city in cities
        ]
    else:
        city_data = [city.dict() for city in cities]

    return {
        "cities": city_data,
        "total": len(city_data),
        "lightweight": lightweight
    }


@router.get("/count")
async def get_cities_count():
    """
    Endpoint que retorna el número total de ciudades
    """
    total = city_service.get_cities_count()
    return {"total_cities": total}


@router.get("/{query}", response_model=List[City])
async def get_cities_name(query: str, limit: int = Query(20, description="Máximo de resultados")):
    """
    🚀 OPTIMIZACIÓN: Búsqueda con límite automático
    """
    results = city_service.search_cities(query)
    return results[:limit]  # Limitar resultados para evitar respuestas gigantes