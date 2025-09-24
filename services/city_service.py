"""
Servicio para manejar operaciones relacionadas con ciudades
"""
from typing import List
import pandas as pd
from fastapi import HTTPException
from entities.city import City


class CityService:
    """Servicio para manejar la lógica de negocio relacionada con ciudades"""
    
    def __init__(self, excel_file_path: str = "dataset.xlsx"):
        """
        Inicializa el servicio con la ruta del archivo Excel
        
        Args:
            excel_file_path: Ruta al archivo Excel con los datos de ciudades
        """
        self.excel_file_path = excel_file_path
    
    def load_cities_from_excel(self) -> List[City]:
        """
        Carga todas las ciudades desde el archivo Excel
        
        Returns:
            Lista de objetos City con todos los datos del Excel
            
        Raises:
            HTTPException: Si hay error al leer el archivo
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(self.excel_file_path)
            
            # Convertir el DataFrame a una lista de objetos City
            cities = []
            for _, row in df.iterrows():
                city = City(
                    city=str(row["city"]),
                    city_ascii=str(row["city_ascii"]),
                    lat=float(row["lat"]),
                    lng=float(row["lng"]),
                    country=str(row["country"]),
                    iso2=str(row["iso2"]),
                    iso3=str(row["iso3"]),
                    admin_name=str(row["admin_name"]),
                    capital=str(row["capital"]),
                    population=int(row["population"]) if pd.notna(row["population"]) else None,
                    id=int(row["id"])
                )
                cities.append(city)
            
            return cities
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error loading data from Excel: {str(e)}"
            )
    
    def get_cities_count(self) -> int:
        """
        Obtiene el número total de ciudades
        
        Returns:
            Número total de ciudades en el dataset
        """
        cities = self.load_cities_from_excel()
        return len(cities)
    
    def get_cities_by_country(self, country: str) -> List[City]:
        """
        Obtiene ciudades filtradas por país
        
        Args:
            country: Nombre del país para filtrar
            
        Returns:
            Lista de ciudades del país especificado
        """
        all_cities = self.load_cities_from_excel()
        return [city for city in all_cities if city.country.lower() == country.lower()]