# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import predict, admin
from .config import settings
from .utils.logging import configure_logging
from .ml.persist import load_active_model_lazy
from .utils.metrics import setup_metrics

# configure logging
configure_logging()

app = FastAPI(title="SMS Spam Platform API", version="0.1")

# CORS - allow frontend origin(s) - adjust in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# mount frontend build (if present at ../../frontend/build)
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# setup prometheus metrics endpoint if configured
setup_metrics(app)

# lazy load model into memory on startup (non-blocking load; use load_active_model_lazy)
@app.on_event("startup")
def startup_event():
    # this will make the first model load lazy and optionally pre-load model metadata
    load_active_model_lazy()
    app.state.started = True
