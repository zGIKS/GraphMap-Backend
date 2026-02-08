from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
import importlib
import logging
from config import settings

logger = logging.getLogger(__name__)

# Crear aplicación FastAPI con configuración centralizada
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configurar CORS Middleware (debe ir antes de otros middlewares)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

#  Compresión automática (reduce 70-80% el tamaño)
app.add_middleware(GZipMiddleware, minimum_size=1000)

def _include_router(module_path: str, attr: str = "router") -> None:
    try:
        module = importlib.import_module(module_path)
        router = getattr(module, attr)
        app.include_router(router)
    except Exception:
        logger.exception("Failed to include router: %s", module_path)


# Incluir routers de forma resiliente para evitar caídas globales en serverless
_include_router("graphmap.interfaces.rest.city_controller")
_include_router("graphmap.interfaces.rest.graph_controller")
_include_router("graphmap.interfaces.rest.chatbot_controller")

@app.get("/")
async def root():
    """
    Redirige a la documentación de Swagger
    """
    return RedirectResponse(url="/docs")


@app.get("/GraphMap")
async def graphmap_info():
    """
    Endpoint que proporciona información básica sobre la API
    """
    return {
        "message": "¡Bienvenido a GraphMap Backend API!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
