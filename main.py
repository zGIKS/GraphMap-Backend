from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from graphmap.interfaces.rest.city_controller import router as city_router
from graphmap.interfaces.rest.graph_controller import router as graph_router

app = FastAPI(
    title="GraphMap API",
    description="API para gestión de ciudades y grafos de proximidad geográfica",
    version="1.0.0"
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

