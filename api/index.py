"""
Entrypoint serverless para Vercel.
"""
import logging
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

try:
    from main import app as app  # noqa: F401
except Exception as exc:
    logger.exception("Failed to bootstrap FastAPI app")
    app = FastAPI(title="GraphMap Bootstrap Error")

    @app.get("/{path:path}")
    async def bootstrap_error(path: str):
        debug_enabled = os.getenv("ENVIRONMENT", "development") != "production"
        payload = {
            "error": "Application bootstrap failed",
            "path": path,
        }
        if debug_enabled:
            payload["exception_type"] = type(exc).__name__
            payload["exception"] = str(exc)
        return JSONResponse(status_code=500, content=payload)
