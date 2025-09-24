from fastapi import FastAPI

app = FastAPI(
    title="Mi API FastAPI",
    description="Una API simple con FastAPI y Swagger",
    version="1.0.0"
)

@app.get("/")
async def hello_world():
    return {"message": "Hello World!"}
