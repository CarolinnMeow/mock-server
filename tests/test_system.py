import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db

class TestSystemEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Инициализация тестовой среды"""
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.get_json()["status"], ["OK", "DEGRADED"])

    def test_metrics(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("accounts", json_data)
        self.assertIn("physical", json_data["accounts"])
        self.assertIn("legal", json_data["accounts"])
        self.assertIn("requests_total", json_data)
        self.assertIn("memory_usage", json_data)

if __name__ == '__main__':
    unittest.main()
