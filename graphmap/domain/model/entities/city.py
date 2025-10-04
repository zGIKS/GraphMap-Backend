from pydantic import BaseModel
from typing import Optional


class City(BaseModel):
    """Entidad que representa una ciudad con todos sus datos del dataset"""
    city: str
    city_ascii: str
    lat: float
    lng: float
    country: str
    iso2: str
    iso3: str
    admin_name: str
    capital: str
    population: Optional[int] = None
    id: int