"""
Configuración centralizada de la aplicación usando variables de entorno
"""
import os
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Settings:
    """Clase de configuración centralizada"""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE", "GraphMap API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION: str = os.getenv(
        "API_DESCRIPTION",
        "API para gestión de ciudades y grafos de proximidad geográfica"
    )

    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database/Files
    DATASET_PATH: str = os.getenv("DATASET_PATH", "dataset.xlsx")

    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"


# Instancia global de configuración
settings = Settings()