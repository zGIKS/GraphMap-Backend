from fastapi import FastAPI
from controllers.city_controller import router as city_router

app = FastAPI(
    title="Mi API FastAPI",
    description="Una API simple con FastAPI y Swagger",
    version="1.0.0"
)

# Incluir los routers de los controladores
app.include_router(city_router)

@app.get("/")
async def root():
    """
    Endpoint raíz que proporciona información básica sobre la API
    """
    return {
        "message": "¡Bienvenido a GraphMap Backend API!",
        "version": "1.0.0",
        "endpoints": {
            "cities": "/cities",
            "cities_count": "/cities/count",
            "cities_by_country": "/cities/by-country/{country}",
            "search_cities": "/cities/search",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    return {"status": "healthy", "message": "API is running correctly"}
