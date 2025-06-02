import functools
from datetime import datetime
import logging
from flask import request, jsonify, make_response, g
from functools import wraps
import uuid

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

def require_headers_and_echo(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Проверка Authorization
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({"error": "Missing Authorization header"}), 401

        # Проверка X-Request-ID и генерация, если его нет
        x_request_id = request.headers.get('X-Request-ID')
        if not x_request_id:
            x_request_id = str(uuid.uuid4())
        # Сохраним в g для использования в after_request
        g.x_request_id = x_request_id
        g.auth_header = auth

        # Вызов основного обработчика
        response = f(*args, **kwargs)

        # Обеспечим, что response — объект Response
        resp = make_response(response)
        resp.headers['X-Request-ID'] = g.x_request_id
        resp.headers['Authorization'] = g.auth_header
        return resp
    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != "Bearer mock-token-123":
            return jsonify({"code": "UNAUTHORIZED", "message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated