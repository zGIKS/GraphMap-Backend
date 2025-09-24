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


@router.get("/by-country/{country}", response_model=List[City])
async def get_cities_by_country(country: str):
    """
    Endpoint que retorna ciudades filtradas por país
    
    Args:
        country: Nombre del país para filtrar ciudades
    """
    cities = city_service.get_cities_by_country(country)
    if not cities:
        raise HTTPException(
            status_code=404, 
            detail=f"No cities found for country: {country}"
        )
    return cities


@router.get("/search", response_model=List[City])
async def search_cities(
    q: Optional[str] = Query(None, description="Buscar ciudades por nombre"),
    country: Optional[str] = Query(None, description="Filtrar por país"),
    limit: Optional[int] = Query(100, description="Límite de resultados", ge=1, le=1000)
):
    """
    Endpoint para buscar ciudades con filtros opcionales
    
    Args:
        q: Término de búsqueda para el nombre de la ciudad
        country: Filtrar por país específico
        limit: Número máximo de resultados a retornar
    """
    all_cities = city_service.load_cities_from_excel()
    
    # Aplicar filtros
    filtered_cities = all_cities
    
    # Filtrar por país si se especifica
    if country:
        filtered_cities = [
            city for city in filtered_cities 
            if city.country.lower() == country.lower()
        ]
    
    # Filtrar por nombre de ciudad si se especifica
    if q:
        filtered_cities = [
            city for city in filtered_cities 
            if q.lower() in city.city.lower() or q.lower() in city.city_ascii.lower()
        ]
    
    # Aplicar límite
    filtered_cities = filtered_cities[:limit]
    
    return filtered_cities