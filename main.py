from fastapi import FastAPI
from graphmap.interfaces.rest.city_controller import router as city_router

app = FastAPI(
    title="Mi API FastAPI",
    description="Una API simple con FastAPI y Swagger",
    version="1.0.0"
)

# Incluir los routers de los controladores
app.include_router(city_router)

@app.get("/GraphMap")
async def GraphMap():
    """
    Endpoint raíz que proporciona información básica sobre la API
    """
    return {
        "message": "¡Bienvenido a GraphMap Backend API!",
        "version": "1.0.0",
    }

