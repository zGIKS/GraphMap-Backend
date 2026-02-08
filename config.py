"""
Configuración centralizada de la aplicación usando variables de entorno
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


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
    # Allow specifying a single '*' to allow all origins. Otherwise provide
    # a comma-separated list of origins (e.g. http://localhost:3000,https://app.example.com)
    # If not set, defaults to empty (no origins allowed)
    _CORS_RAW: str = os.getenv("CORS_ORIGINS", "")
    # Optional regex for dynamic preview URLs, e.g. ^https://.*\.vercel\.app$
    CORS_ORIGIN_REGEX: Optional[str] = os.getenv("CORS_ORIGIN_REGEX")

    if _CORS_RAW.strip() == "*":
        CORS_ORIGINS: List[str] = ["*"]
    elif _CORS_RAW.strip() == "":
        CORS_ORIGINS: List[str] = []
    else:
        CORS_ORIGINS: List[str] = [s.strip() for s in _CORS_RAW.split(",") if s.strip()]

    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database/Files
    _DATASET_RAW: str = os.getenv("DATASET_PATH", "dataset.xlsx")
    DATASET_PATH: str = str(
        Path(_DATASET_RAW)
        if Path(_DATASET_RAW).is_absolute()
        else BASE_DIR / _DATASET_RAW
    )

    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8301"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"

    # API Keys
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL")


# Instancia global de configuración
settings = Settings()

# Si se permitió cualquier origen ('*'), no usar credenciales por seguridad
if settings.CORS_ORIGINS == ["*"] and settings.CORS_ALLOW_CREDENTIALS:
    settings.CORS_ALLOW_CREDENTIALS = False
