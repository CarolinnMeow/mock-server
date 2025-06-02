import functools
from datetime import datetime
import logging
from flask import request


def log_endpoint(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Call {func.__name__} | {request.method} {request.path}")
        return func(*args, **kwargs)
    return wrapper

def serialize_row(row):
    return dict(row) if row else {}

def get_iso_date():
    return datetime.now().isoformat()
