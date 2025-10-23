# app/ml/persist.py
import os
import json
import joblib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger("app.persist")
BASE_MODELS_DIR = os.getenv("MODEL_DIR", "/app/models")

class ModelWrapper:
    """
    Holds pipeline object and metadata dict
    """
    def __init__(self, pipeline, metadata: Dict[str, Any]):
        self.pipeline = pipeline
        self.metadata = metadata

_ACTIVE_MODEL = None

def _metadata_path(version: str) -> str:
    return os.path.join(BASE_MODELS_DIR, version, "metadata.json")

def _artifact_path(version: str) -> str:
    return os.path.join(BASE_MODELS_DIR, version, "artifact.joblib")

def save_model_artifact(version: str, artifact_path: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Copy or move artifact into registry and write metadata.json
    """
    dest_dir = os.path.join(BASE_MODELS_DIR, version)
    os.makedirs(dest_dir, exist_ok=True)
    dest_artifact = os.path.join(dest_dir, "artifact.joblib")
    # if user provided artifact at artifact_path, move/copy; here we just ensure it's present
    if artifact_path != dest_artifact:
        # copy binary
        with open(artifact_path, "rb") as src, open(dest_artifact, "wb") as dst:
            dst.write(src.read())
    meta = metadata or {}
    meta.setdefault("version", version)
    meta.setdefault("path", dest_artifact)
    meta.setdefault("created_at", datetime.utcnow().isoformat())
    # write metadata
    with open(_metadata_path(version), "w") as f:
        json.dump(meta, f, indent=2)
    logger.info("Saved model artifact for %s", version)
    return dest_artifact

def list_models() -> List[Dict[str, Any]]:
    out = []
    base = Path(BASE_MODELS_DIR)
    if not base.exists():
        return []
    for p in base.iterdir():
        if p.is_dir():
            meta_file = p / "metadata.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                except Exception:
                    meta = {"version": p.name, "path": str(p / "artifact.joblib")}
            else:
                meta = {"version": p.name, "path": str(p / "artifact.joblib")}
            out.append(meta)
    return out

def activate_model_version(version: str) -> bool:
    meta_file = Path(BASE_MODELS_DIR) / version / "metadata.json"
    if not meta_file.exists():
        return False
    meta = json.loads(meta_file.read_text())
    artifact = meta.get("path", "")
    if not Path(artifact).exists():
        return False
    # load model to verify
    try:
        pipeline = joblib.load(artifact)
        global _ACTIVE_MODEL
        _ACTIVE_MODEL = ModelWrapper(pipeline=pipeline, metadata=meta)
        logger.info("Activated model version %s", version)
        return True
    except Exception as e:
        logger.exception("Failed to activate model %s: %s", version, e)
        return False

def load_active_model_lazy():
    """
    Called at startup to set up active model if present (doesn't eagerly load in some setups).
    """
    global _ACTIVE_MODEL
    if _ACTIVE_MODEL is None:
        models = list_models()
        # if any model has metadata 'active' True pick that; otherwise pick latest by created_at
        active = None
        for m in models:
            if m.get("active") is True:
                active = m
                break
        if active is None and models:
            # pick latest by created_at
            models_sorted = sorted(models, key=lambda x: x.get("created_at",""), reverse=True)
            active = models_sorted[0]
        if active:
            try:
                artifact = active.get("path")
                pipe = joblib.load(artifact)
                _ACTIVE_MODEL = ModelWrapper(pipeline=pipe, metadata=active)
                logger.info("Loaded active model %s", active.get("version"))
            except Exception as e:
                logger.exception("Failed to load active model: %s", e)
    return _ACTIVE_MODEL

def load_active_model() -> Optional[ModelWrapper]:
    global _ACTIVE_MODEL
    if _ACTIVE_MODEL is None:
        return load_active_model_lazy()
    return _ACTIVE_MODEL
