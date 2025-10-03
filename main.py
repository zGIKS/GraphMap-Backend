from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
from graphmap.interfaces.rest.city_controller import router as city_router
from graphmap.interfaces.rest.graph_controller import router as graph_router
from config import settings

# Crear aplicación FastAPI con configuración centralizada
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# 🚀 OPTIMIZACIÓN: Compresión automática (reduce 70-80% el tamaño)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configurar CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Incluir los routers de los controladores
app.include_router(city_router)
app.include_router(graph_router)

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

