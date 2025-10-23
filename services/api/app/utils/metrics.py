# app/utils/metrics.py
from prometheus_client import Counter, Histogram
from fastapi import FastAPI
from prometheus_client import make_asgi_app
import logging

logger = logging.getLogger("app.metrics")
PREDICT_COUNTER = Counter("predict_requests_total", "Total predict requests")
PREDICT_LATENCY = Histogram("predict_latency_seconds", "Predict latency in seconds")

def increment_predict_counter():
    PREDICT_COUNTER.inc()

def observe_latency(val: float):
    PREDICT_LATENCY.observe(val)

def setup_metrics(app: FastAPI):
    try:
        prometheus_app = make_asgi_app()
        # mount at /metrics
        app.mount("/metrics", prometheus_app)
        logger.info("Mounted /metrics endpoint")
    except Exception as e:
        logger.exception("Failed to mount metrics: %s", e)
