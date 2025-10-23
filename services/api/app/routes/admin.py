# app/routes/admin.py
import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from typing import List
from ..routes.models import UploadResponse, ModelMetadata, RetrainRequest
from ..ml.persist import save_model_artifact, list_models, activate_model_version
from ..tasks.tasks import enqueue_retrain
from ..config import settings
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger("app.admin")

@router.post("/upload", response_model=UploadResponse)
async def upload_model(file: UploadFile = File(...), version: str = Form(...), threshold: float = Form(None)):
    """
    Upload a pre-trained model artifact (joblib). The file will be stored under models/<version>/artifact.joblib
    and metadata.json will be written alongside it.
    """
    if not file.filename.endswith(".joblib"):
        raise HTTPException(400, "Only .joblib model artifacts are allowed for now.")

    target_dir = os.path.join(settings.MODEL_DIR, version)
    os.makedirs(target_dir, exist_ok=True)
    artifact_path = os.path.join(target_dir, "artifact.joblib")

    # write file
    with open(artifact_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    # save minimal metadata
    metadata = {"version": version, "path": artifact_path, "created_at": datetime.utcnow().isoformat(), "threshold": float(threshold) if threshold is not None else None}
    save_model_artifact(version, artifact_path, metadata=metadata)
    logger.info("Uploaded model %s", version)
    return UploadResponse(version=version, message="Uploaded")

@router.get("/models", response_model=List[ModelMetadata])
def get_models():
    return list_models()

@router.post("/activate/{version}")
def activate(version: str):
    ok = activate_model_version(version)
    if not ok:
        raise HTTPException(404, "Version not found")
    return {"message": f"Activated model {version}"}

@router.post("/retrain")
def retrain(req: RetrainRequest, background_tasks: BackgroundTasks):
    # Enqueue retrain job to worker (async)
    job_id = enqueue_retrain(dataset_path=req.dataset_path, augment=req.augment)
    return {"message": "Retrain scheduled", "job_id": job_id}
