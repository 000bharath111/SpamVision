from celery import shared_task
from app.ml.train import retrain_model
from app.utils.logging import logger


@shared_task
def retrain_task():
    """
    Background retraining of the spam detection model.
    """
    logger.info("Starting background retraining task...")
    try:
        result = retrain_model()
        logger.info("Retraining complete.")
        return result
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        raise
