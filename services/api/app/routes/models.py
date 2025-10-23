# app/routes/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class PredictRequest(BaseModel):
    text: str = Field(..., example="Free entry to win 1000 rupees")
    threshold: Optional[float] = Field(None, description="Optional override threshold")

class PredictResponse(BaseModel):
    text: str
    label: str
    spam_probability: Optional[float] = None
    model_version: Optional[str] = None

class UploadResponse(BaseModel):
    version: str
    message: str

class ModelMetadata(BaseModel):
    version: str
    path: str
    created_at: str
    metrics: Optional[Dict[str, Any]] = None
    threshold: Optional[float] = None

class RetrainRequest(BaseModel):
    dataset_path: Optional[str] = None
    augment: Optional[bool] = True
