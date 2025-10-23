# app/config.py
from pydantic import BaseSettings, AnyUrl
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "sms-spam-platform"
    DEBUG: bool = True
    # Model & storage
    MODEL_DIR: str = os.getenv("MODEL_DIR", "/app/models")
    # DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./spam.db")
    # Redis for RQ
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    # Default threshold
    DEFAULT_THRESHOLD: float = 0.5
    # Gray zone for heavy rescoring
    GRAY_ZONE_LOW: float = 0.35
    GRAY_ZONE_HIGH: float = 0.75
    # SHAP usage
    ENABLE_SHAP: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
