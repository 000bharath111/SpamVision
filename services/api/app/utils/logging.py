# app/utils/logging.py
import logging
import sys
import json
from pythonjsonlogger import jsonlogger

def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
