# services/worker/worker.py
"""
RQ worker tasks for SMS Spam Platform.

Functions:
 - heavy_rescore(text, log_id=None)
 - retrain_job(dataset_path=None, augment=True)

These are importable by RQ as "worker.heavy_rescore" and "worker.retrain_job".
This file expects that the API package `app` (services/api/app) is on PYTHONPATH,
so imports like `from app.ml import persist` work.

Run example (project root):
  PYTHONPATH=services/api python -m rq worker --with-scheduler spampipeline

or when using docker, see Dockerfile below.

"""

import os
import logging
import traceback
from typing import Optional
import time

# Attempt to import application modules (must set PYTHONPATH so `app` package is importable)
try:
    from app.ml import persist as model_persist
    from app.ml import train as train_mod
    from app.ml.embeddings import SentenceTransformerVectorizer
    from app.db.session import get_db_session
    from app.db.models import PredictionLog, ReviewItem, ModelVersion
    from app.config import settings
except Exception as e:
    # Import errors will be raised when the worker is invoked if PYTHONPATH not set.
    # We still define functions so RQ can import the module, but they will raise if called.
    model_persist = None
    train_mod = None
    SentenceTransformerVectorizer = None
    get_db_session = None
    PredictionLog = None
    ReviewItem = None
    ModelVersion = None
    settings = None

# optional heavy model cache
_HEAVY_MODEL_CACHE = {}

logger = logging.getLogger("worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

def _detect_device():
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def _load_heavy_model_for_version(meta):
    """
    If model metadata contains a heavy model path (meta['heavy_path']), load it with joblib or other loader.
    If not, fall back to the standard pipeline in meta['path'].
    Cache results in _HEAVY_MODEL_CACHE keyed by version.
    """
    if model_persist is None:
        raise RuntimeError("app package not importable. Ensure PYTHONPATH contains services/api")
    ver = meta.get("version")
    if ver in _HEAVY_MODEL_CACHE:
        return _HEAVY_MODEL_CACHE[ver]

    # prefer heavy_path if provided
    heavy_path = meta.get("heavy_path") or meta.get("path")
    if not heavy_path or not os.path.exists(heavy_path):
        raise FileNotFoundError(f"Model artifact not found: {heavy_path}")

    # load with joblib (handles sklearn pipelines and many model artifacts)
    try:
        import joblib
        logger.info("Loading heavy model artifact for version %s from %s", ver, heavy_path)
        model = joblib.load(heavy_path)
        _HEAVY_MODEL_CACHE[ver] = model
        return model
    except Exception as e:
        logger.exception("Failed to load heavy model: %s", e)
        raise

def heavy_rescore(text: str, log_id: Optional[int] = None):
    """
    Heavy rescoring job:
    - Loads heavy model (if configured) or active pipeline
    - Computes probability (if available) or hard label
    - Updates PredictionLog (score, label_pred)
    - If heavy score indicates spam and previous was ham, create a ReviewItem (for human review)
    """
    start = time.time()
    try:
        if model_persist is None:
            raise RuntimeError("app package not importable. Ensure PYTHONPATH contains services/api")

        wrapper = model_persist.load_active_model()
        if wrapper is None:
            logger.warning("No active model available for heavy_rescore")
            return {"status": "no_model"}

        meta = wrapper.metadata or {}
        version = meta.get("version")
        # determine which artifact to use for heavy scoring
        try:
            model = _load_heavy_model_for_version(meta)
        except Exception:
            logger.warning("Falling back to active pipeline for heavy scoring")
            model = wrapper.pipeline

        # compute probability or label
        prob = None
        label = None
        if hasattr(model, "predict_proba"):
            try:
                prob = float(model.predict_proba([text])[0][1])
            except Exception as e:
                # sometimes heavy model may require different input preprocessing; try pipeline from wrapper
                logger.exception("predict_proba failed on heavy model: %s", e)
                try:
                    prob = float(wrapper.pipeline.predict_proba([text])[0][1])
                except Exception:
                    prob = None
        if prob is not None:
            thr = meta.get("threshold", settings.DEFAULT_THRESHOLD if settings else 0.5)
            label = "spam" if prob >= thr else "ham"
        else:
            try:
                pred = int(model.predict([text])[0])
                label = "spam" if pred == 1 else "ham"
            except Exception as e:
                logger.exception("predict failed during heavy_rescore: %s", e)
                label = None

        # update DB record if provided
        session = None
        try:
            session = get_db_session()
            if log_id is not None and session is not None:
                log = session.query(PredictionLog).filter(PredictionLog.id == log_id).first()
                if log:
                    log.score = prob
                    log.label_pred = label
                    # preserve existing label_true if any
                    session.add(log)
                    session.commit()
                    logger.info("Updated PredictionLog id=%s with heavy score=%s label=%s", log_id, prob, label)
                    # if heavy says spam while original was ham (or original score low), create review item
                    try:
                        # If original recorded label_pred != 'spam' but heavy label is spam -> review
                        if (log.label_pred is None or log.label_pred == 'ham') and label == 'spam':
                            ri = ReviewItem(text=text, score=prob, model_version=version, status="pending")
                            session.add(ri)
                            session.commit()
                            logger.info("Created ReviewItem id=%s for log id=%s", ri.id, log_id)
                    except Exception:
                        logger.exception("Failed to create ReviewItem")
                else:
                    # create a new log if none exists
                    log = PredictionLog(text=text, score=prob, label_pred=label, model_version=version)
                    session.add(log)
                    session.commit()
                    logger.info("Created new PredictionLog id=%s as none existed for provided log_id", log.id)
            else:
                # no log_id provided; insert a prediction log
                log = PredictionLog(text=text, score=prob, label_pred=label, model_version=version)
                session.add(log)
                session.commit()
                logger.info("Inserted PredictionLog id=%s in heavy_rescore (no log_id passed)", log.id)
        except Exception as e:
            logger.exception("DB update failed in heavy_rescore: %s", e)
            if session:
                session.rollback()
        finally:
            # do not close session scoped session; depends on app patterns
            pass

        elapsed = time.time() - start
        logger.info("heavy_rescore completed in %.2fs for version=%s", elapsed, version)
        return {"status": "ok", "prob": prob, "label": label}
    except Exception as e:
        logger.exception("heavy_rescore failed: %s", e)
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()}


def retrain_job(dataset_path: Optional[str] = None, augment: bool = True):
    """
    Retrain job kicked off from API admin. Uses train_mod.train_and_save to perform training.
    Steps:
     - call train.train_and_save(dataset_path, augment=augment) -> (version, metadata)
     - persist.activate_model_version(version)
     - write ModelVersion record to DB (or update existing)
    """
    try:
        if train_mod is None or model_persist is None:
            raise RuntimeError("app package not importable. Ensure PYTHONPATH contains services/api")

        logger.info("Starting retrain job. dataset=%s augment=%s", dataset_path, augment)
        version, metadata = train_mod.train_and_save(dataset_path, version=None, augment=augment)
        logger.info("Training finished. version=%s", version)

        # model_persist.save_model_artifact has already been called inside train_and_save, but ensure activation
        activated = model_persist.activate_model_version(version)
        logger.info("Activated model version=%s -> %s", version, activated)

        # write record into DB model_versions table
        try:
            session = get_db_session()
            # deactivate other models if any
            session.query(ModelVersion).update({ModelVersion.active: False})
            mv = session.query(ModelVersion).filter(ModelVersion.version == version).first()
            if mv is None:
                mv = ModelVersion(version=version, path=metadata.get("path"), metrics=metadata.get("metrics"), threshold=metadata.get("threshold", 0.5), active=True)
                session.add(mv)
            else:
                mv.path = metadata.get("path")
                mv.metrics = metadata.get("metrics")
                mv.threshold = metadata.get("threshold", 0.5)
                mv.active = True
                session.add(mv)
            session.commit()
            logger.info("Saved ModelVersion record for %s", version)
        except Exception as e:
            logger.exception("Failed updating ModelVersion DB record: %s", e)
            if session:
                session.rollback()

        return {"status": "ok", "version": version, "activated": activated}
    except Exception as e:
        logger.exception("retrain_job failed: %s", e)
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()}

# convenience: allow direct invocation for local debugging
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    print("Worker module loaded. Run RQ worker pointing to this module, or call functions directly for testing.")
