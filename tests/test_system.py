import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestSystemEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Перед запуском всех тестов пересоздаёт тестовую базу и наполняет её схемой и тестовыми данными.
        """
        cls.db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'test_mockserver.db')
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        conn = sqlite3.connect(cls.db_path)
        conn.executescript(schema)
        conn.close()
        ds = DataService()
        ds.save_to_db(cls.db_path)

    def setUp(self):
        self.app = create_app(config_class=TestConfig)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "OK")

    def test_metrics(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn("accounts", response.get_json())

if __name__ == '__main__':
    unittest.main()
