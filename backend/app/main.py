import os
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent
_project_dir = _backend_dir.parent
if str(_project_dir) not in sys.path:
    sys.path.insert(0, str(_project_dir))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.utils.logger import logger

import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LCA Platform application")
    init_db()
    logger.info("Database initialized")
    from backend.app.services.dataset_service import load_datasets
    try:
        load_datasets()
        logger.info("Datasets loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load datasets at startup: {e}")
    yield
    logger.info("Shutting down LCA Platform application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Driven Life Cycle Assessment Platform for Sustainable Metal Production",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.debug(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION, "app": settings.APP_NAME}


from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.datasets import router as datasets_router
from backend.app.api.v1.predictions import router as predictions_router
from backend.app.api.v1.environmental import router as environmental_router
from backend.app.api.v1.circularity import router as circularity_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.dashboard import router as dashboard_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(environmental_router, prefix="/api/v1")
app.include_router(circularity_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>LCA Platform API</h1><p>Frontend not found. API available at /docs</p>")
