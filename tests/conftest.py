import pytest
import os
import sqlite3
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Перед запуском всех тестов пересоздаёт тестовую базу и наполняет её схемой и тестовыми данными.
    """
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'test_mockserver.db')
    # Удаляем старую базу, если есть
    if os.path.exists(db_path):
        os.remove(db_path)
    # Создаём схему
    schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.close()
    # Генерируем и сохраняем тестовые данные
    ds = DataService()
    ds.save_to_db(db_path)

@pytest.fixture
def client():
    app = create_app(config_class=TestConfig)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
